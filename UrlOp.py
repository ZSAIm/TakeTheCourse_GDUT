import gzip
import zlib
import urllib.request, urllib.parse
import urllib.error
import logging
import time
import socket
import threading
import queue
import http.cookiejar
from WaitLock import WaitLock

socket.setdefaulttimeout(3)
MAX_RETRIES = 5
WAIT_TIME = 0.05

# TIMEOUT = 0
#


def raw_decompress(data, headers):
    encoding = headers.get('Content-Encoding')
    if encoding == 'gzip':
        data = gzip.decompress(data)
    elif encoding == 'deflate':
        data = zlib.decompress(data)
    return data
    # return str(data, encoding='utf-8')


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/68.0.3440.84 Safari/537.36',
    # 'Host': 'jxfw.gdut.edu.cn',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1'
}

class UrlOp:
    def __init__(self, opener=None, cookiejar=None, id=None):
        self.opener = opener
        self.cookiejar = cookiejar
        self.proxy_handler = None
        self.id = id
        self.ip = None
        self.__urlop_retries = 0

        self.request_threads = []

        self.wait = WaitLock(timeout=3, obj=self, key='running')
        self.running = False

        self.ret_queue = queue.LifoQueue()

        self.empty_timeout = True
        self.proxy_invalid = False

    def request(self, url, data=None, headers={},
                 origin_req_host=None, unverifiable=False,
                 method=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, branch=0, independent=False):

        # self.request()
        self.running = True
        self.empty_timeout = True

        for i in range(branch + 1):
            thd = threading.Thread(target=self.__request,
                                   args=(url, data, headers, origin_req_host, unverifiable, method, timeout, independent,))
            self.request_threads.append(thd)
            thd.start()

        while True:
            while len(self.request_threads):
                self.request_threads = list(filter(lambda x: x.isAlive() is True, self.request_threads))
                time.sleep(0.01)
            if self.ret_queue.empty() is False:

                ret = self.ret_queue.get()

                while self.ret_queue.empty() is False:
                    if ret[0] is not None:
                        ret = self.ret_queue.get()
                    else:
                        self.ret_queue.get()
                self.running = False
                self.wait.release()
                if len(ret) == 4 and independent is True:
                    self.opener, self.cookiejar = ret[2:]
                return ret[:2]
            else:
                self.running = False
                self.wait.release()
                return None, None

    def __request(self, url, data=None, headers={},
                 origin_req_host=None, unverifiable=False,
                 method=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, independence=False):

        if self.ret_queue.empty() is False and self.empty_timeout is False:
            return
        if data is not None:
            data_str = urllib.parse.urlencode(data).encode('utf-8')
        else:
            data_str = None
        try:
            req = urllib.request.Request(url, data_str, headers, origin_req_host, unverifiable, method)
            self.wait.acquire()
            if independence is True:
                opener, cookiejar = self.build_new_opener()
            else:
                opener, cookiejar = self.opener, self.cookiejar

            res = opener.open(req, timeout=timeout)

            raw = raw_decompress(res.read(), res.info())
        except urllib.error.URLError as e:
            # if getattr(e, 'code', None) == 403:
            #     pass
            if self.__urlop_retries >= MAX_RETRIES:
                self.ret_queue.put((None, None))
                return

            time.sleep(WAIT_TIME)
            self.__urlop_retries += 1
            self.__request(url, data, headers, origin_req_host, unverifiable, method, timeout)
            return

        except socket.error as e:
            if self.__urlop_retries >= MAX_RETRIES*2:
                self.ret_queue.put((None, None))
                return
            time.sleep(WAIT_TIME)
            self.__urlop_retries += 1
            self.__request(url, data, headers, origin_req_host, unverifiable, method, timeout)
            return
        else:
            if not raw:
                if self.__urlop_retries >= MAX_RETRIES:
                    self.ret_queue.put((None, res, opener, cookiejar))
                    return
                self.__urlop_retries += 1
                self.__request(url, data, headers, origin_req_host, unverifiable, method, timeout)
                # self.ret_queue.put((None, res))
                return
            self.empty_timeout = False
            self.ret_queue.put((raw, res, opener, cookiejar))
            return
        finally:
            self.__urlop_retries = 0

    def build_new_opener(self):
        cookiejar = http.cookiejar.MozillaCookieJar('cookies/%s.txt' % self.id)
        if self.proxy_handler is None:
            new_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookiejar))
        else:
            new_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookiejar), self.proxy_handler)
        new_opener.addheaders = list(HEADERS.items())
        return new_opener, cookiejar


