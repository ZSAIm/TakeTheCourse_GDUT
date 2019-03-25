
import urllib.request, urllib.parse, urllib.error
import random
import threading
import time
import http.cookiejar
import socket
import gzip, zlib
import queue
from handler.Error import UrlOpTimeOutError

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/68.0.3440.84 Safari/537.36',
    'Host': 'jxfw.gdut.edu.cn',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'jxfw.gdut.edu.cn'
}



def raw_decompress(data, headers):
    encoding = headers.get('Content-Encoding')

    if encoding == 'gzip':
        data = gzip.decompress(data)
    elif encoding == 'deflate':
        data = zlib.decompress(data)

    return data


class UrlRequestOp(object):
    def __init__(self):
        self.opener = None

        self.cookiejar = None

        self.timeout = 10

        self.__branch_threads__ = []
        self.__ret_queue__ = queue.LifoQueue()

        self.__queue_lock__ = threading.Lock()

        self.proxy = None

        self.retry_time_ms = random.randrange(1000, 3000)

        self.buildOpener()

        self.timeout_flags = {}

    def loadUrlop(self, _from):
        self.opener = _from.opener
        self.cookiejar = _from.cookiejar
        self.proxy = _from.proxy

    def install(self, opener=None, cookiejar=None, proxy=None):
        if cookiejar:
            self.cookiejar = cookiejar
        if proxy:
            self.proxy = proxy

        if not opener:
            if proxy or cookiejar:
                self.buildOpener(self.cookiejar, self.proxy)
        else:
            self.opener = opener

    def loadCookieJar(self, cookiejar):
        self.cookiejar = cookiejar


    def setNewCookieJar(self):
        self.cookiejar = http.cookiejar.MozillaCookieJar()
        self.buildOpener(self.cookiejar, self.proxy)

    def newRetryTime(self):
        self.retry_time_ms = random.randrange(1000, 3000)

    def setProxy(self, proxy):
        self.proxy = proxy
        self.buildOpener(self.cookiejar, proxy)

    def clearProxy(self):
        self.proxy = None
        self.buildOpener(self.cookiejar, None)

    def buildOpener(self, cookiejar=None, proxy=None):
        self.opener, self.cookiejar = self.getNewOpener(cookiejar, proxy)

    def getNewOpener(self, cookiejar=None, proxy=None):
        processor = []
        if not cookiejar:
            cookiejar = http.cookiejar.MozillaCookieJar()

        processor.append(urllib.request.HTTPCookieProcessor(cookiejar))

        if proxy:
            processor.append(urllib.request.ProxyHandler(proxy))

        opener = urllib.request.build_opener(*processor)
        opener.addheaders = list(DEFAULT_HEADERS.items())

        return opener, cookiejar

    def __timeout_setflag__(self, id):
        self.timeout_flags[id][1] = True

    def cancelTimeOut_flag(self, id):
        self.timeout_flags[id][0].cancel()
        del self.timeout_flags[id]

    def request(self, branch_num=0, isolate=False, max_retry=0, **kwargs):

        opener_cookiejars = []

        for i in range(branch_num+1):
            opener = self.opener
            cookiejar = self.cookiejar

            if isolate:
                opener, cookiejar = self.getNewOpener()

            opener_cookiejars.append((opener, cookiejar))

            thread = threading.Thread(target=self.__request__, args=(i, opener, kwargs,))
            self.__branch_threads__.append(thread)
            thread.start()

            time.sleep(random.random() / 10.0)

        timeout_id = object()
        self.timeout_flags[timeout_id] = [None, False]

        timer = threading.Timer(kwargs.get('timeout', self.timeout), self.__timeout_setflag__, args=(timeout_id,))
        timer.setName('TimeOutFlagSetter')
        self.timeout_flags[timeout_id][0] = timer
        timer.start()

        er_kw = {
            'user': getattr(self, 'user', None),
            'msg': kwargs
        }


        while True:
            if self.timeout_flags[timeout_id][1]:
                self.cancelTimeOut_flag(timeout_id)
                raise UrlOpTimeOutError(er_kw)

            for i in self.__branch_threads__:
                if i.isAlive():
                   break
            else:
                self.cancelTimeOut_flag(timeout_id)
                if not self.__ret_queue__.empty():
                    id, raw, res = self.__ret_queue__.get()
                    opener, cookiejar = opener_cookiejars[id]

                    self.install(opener=opener, cookiejar=cookiejar)

                    self.clearBranch()
                    return raw, res

                else:
                    if max_retry == -1 or max_retry > 0:
                        if max_retry != -1:
                            max_retry -= 1
                        time.sleep(self.retry_time_ms / 1000.0)
                        self.newRetryTime()

                        return self.request(branch_num, isolate, max_retry, **kwargs)
                    else:
                        raise UrlOpTimeOutError(er_kw)

            time.sleep(0.01)

    def clearBranch(self):
        self.__branch_threads__ = []
        while not self.__ret_queue__.empty():
            _ = self.__ret_queue__.get()

    def __request__(self, id, opener, kwargs):

        req_params = {
            'url': kwargs.get('url'),
            'data': kwargs.get('data', None),
            'headers': kwargs.get('headers', {}),
            'origin_req_host': kwargs.get('origin_req_host', None),
            'unverifiable': kwargs.get('unverifiable', False),
            'method': kwargs.get('method', None)
        }
        timeout = kwargs.get('timeout', 5)

        if req_params['data'] is not None:
            req_params['data'] = urllib.parse.urlencode(req_params['data']).encode()

        try:
            req = urllib.request.Request(**req_params)
            if not self.__ret_queue__.empty():
                return

            res = opener.open(req, timeout=timeout)
            raw = raw_decompress(res.read(), res.info())

        except Exception as e:
            print(e)
            pass

        else:
            self.__ret_queue__.put((id, raw, res))


