import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
# import html5lib
from UrlOp import UrlOp
import http.cookiejar
import json, time
import logging
import os, gzip, zlib
import threading
import random
import re

# logging.basicConfig(level=logging.ERROR,
#                     format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/68.0.3440.84 Safari/537.36',
    # 'Host': 'www.xicidaili.com',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1'
}

PROXY_URL = ['http://www.xicidaili.com/nn/%s']
# PROXY_URL = ['http://www.xicidaili.com/nn/%s', 'http://www.xicidaili.com/nt/%s', 'http://www.xicidaili.com/wn/%s',
#              'http://www.xicidaili.com/wt/%s', 'http://www.xicidaili.com/qq/%s']
PROXY_URL1 = ['http://www.89ip.cn/index_%s.html']

PROXY_URL2 = ['https://www.kuaidaili.com/free/inha/%s']

PROXY_URL3 = ['http://www.66ip.cn/mo.php?sxb=&tqsl=50']

MAX_THREAD = 100

class ProxyCollection(UrlOp):
    def __init__(self):
        UrlOp.__init__(self)
        self.cookiejar = http.cookiejar.CookieJar()
        self.origin = UrlOp(urllib.request.build_opener())
        HEADERS.update({'Referer': 'http://www.ip138.com/'})
        self.origin.opener.addheaders = list(HEADERS.items())

        raw = None
        while raw is None:
            raw, res = self.origin.request('http://2018.ip138.com/ic.asp', method='GET', branch=1)
            time.sleep(0.1)

        self.origin.ip, self.origin.position = self.spilit_ip(str(raw, encoding='gb2312'))
        self.opener = self.origin.opener
        self.id = 0
        self.urlop_retries = 0

        self.proxys = []
        self.valid = []
        self.threads = []

        self.proxy_op_lock = threading.Lock()
        self.urlop_lock = threading.Lock()

        self._point = 0
        self.thread_monitor = None

    def get_anonymous_len(self):
        _count = 0
        for i in self.valid:
            if i.real_ip != self.origin.ip:
                _count += 1

        return _count

    def statur_monitor(self):
        while len(self.threads) != 0:
            self.threads = list(filter(lambda x: x.isAlive() is True, self.threads))
            time.sleep(0.5)

    def pop(self, anonymous=False):
        with self.proxy_op_lock:
            while len(self.threads) != 0:
                time.sleep(0.5)
            if len(self.valid) == 0:
                return None
                raise IndexError
            ret = self.valid[self._point]

            if anonymous is True:
                for i in range(len(self.valid)):
                    tmp = self.valid[(self._point + i) % len(self.valid)]
                    if tmp.real_ip != self.origin.ip:
                        ret = tmp
                        self._point = self.valid.index(ret)

                        break
                else:
                    ret = None
            # else:
            self._point += 1
            if self._point >= len(self.valid):
                self._point = 0

            return ret

    def collect(self):
        logging.info('collecting proxys ...')
        with self.proxy_op_lock:
            self.proxys = []
            self.valid = []
            for i in range(len(PROXY_URL)):
                self.__get_data(1, 0, PROXY_URL[i])

            # for i in range(len(PROXY_URL1)):
            #     for j in range(2):
            #         self.__get_data(j+1, 1, PROXY_URL1[i])
            #
            # for i in range(len(PROXY_URL2)):
            #     for j in range(2):
            #         self.__get_data(j+1, 2, PROXY_URL2[i])
            #
            # for i in range(len(PROXY_URL3)):
            #     self.__get_data(1, 3, PROXY_URL3[i])

            logging.info('testing the proxys running...')
            self.batch_test()

    def __get_data(self, page, type, url):

        if type == 3:
            raw, _ = self.request(url, method='GET')
            if raw is None:
                return
            res = re.findall('([0-9]{1,}\.[0-9]{1,}\.[0-9]{1,}\.[0-9]{1,}:[0-9]{1,})', str(raw, encoding='gb2312'))
            for i in res:
                self.proxys.append(ProxyInfo.load_soup(i, type))
            # soup = BeautifulSoup(str(raw, encoding='gb2312'))
            pass
        else:
            raw, _ = self.request(url % str(page), method='GET')
            if raw is None:
                return
            soup = BeautifulSoup(str(raw, encoding='utf-8'))
            for i in soup.tbody.find_all('tr'):
                tds = i.find_all('td')
                if len(tds) > 0:
                    self.proxys.append(ProxyInfo.load_soup(tds, type))



    def test(self, proxy_info):
        if self.thread_monitor is None or self.thread_monitor.isAlive() is False:
            self.thread_monitor = threading.Thread(target=self.statur_monitor)
            self.thread_monitor.start()

        while len(self.threads) >= MAX_THREAD:
            time.sleep(1)
        thd = threading.Thread(target=self.__test, args=(proxy_info,))
        self.threads.append(thd)
        thd.start()

    def spilit_ip(self, raw):

        soup = BeautifulSoup(raw)
        # ret_ip_p = soup.find_all('code')
        str_msg = soup.center.string
        # if len(ret_ip_p) == 0:
        #     return None, None
        # ip = ret_ip_p[0].string
        # position = ret_ip_p[1].string
        ip = re.search('\[([0-9]{1,}\.[0-9]{1,}\.[0-9]{1,}\.[0-9]{1,})\]', str_msg).group(1)

        position = str_msg.split('：')[-1]
        return ip, position

    def __test(self, proxy_info):
        logging.info('testing ip: %s:%s - %s' % (proxy_info.ip, proxy_info.port, proxy_info.position))
        handler = urllib.request.ProxyHandler({proxy_info.protocal: '%s:%s' % (proxy_info.ip, proxy_info.port)})
        opener = urllib.request.build_opener(handler)
        HEADERS.update({'Referer': 'http://www.ip138.com/'})
        opener.addheaders = list(HEADERS.items())

        op = UrlOp(opener)
        # raw, res = op.request('http://www.ip.cn/', method='GET', timeout=3)
        raw, res = op.request('http://2018.ip138.com/ic.asp', method='GET', timeout=3)

        if raw is None:
            return None, None
        if 'ip' not in res.geturl():
            return None, None

        ip, position = self.spilit_ip(str(raw))

        proxy_info.real_ip = ip
        proxy_info.real_position = position
        if ip != self.origin.ip:
            if proxy_info not in self.valid:
                self.valid.append(proxy_info)
        # print(ip, position, proxy_info.ip, self.origin.ip)
        # logging.info('respond ip: %s:%s - %s' % (proxy_info.real_ip, proxy_info.port, proxy_info.real_position))

    def save(self):
        # logging.info('waiting for saving ...')

        while len(self.threads) > 0:
            # with self.lock:
                # self.threads = list(filter(lambda x: x.isAlive() is True, self.threads))
            time.sleep(1)

        logging.info('proxy saving ...')
        if len(self.valid) == 0:
            txt = ''
            random.shuffle(self.valid)
            with open('proxys/%s.json' % time.strftime("%Y-%m-%d %H.%M.%S", time.localtime()), 'w') as f:
                for i in self.proxys:
                    txt += '\n' + i.dump()
                f.write(txt)

        txt = ''
        with open('proxys/valid.json', 'w') as f:
            for i in self.valid:
                txt += '\n' + i.dump()
            f.write(txt)
        logging.info('proxy saved successfully.')

    def load(self):
        if os.path.exists('proxys/valid.json') is True:
            with open('proxys/valid.json') as f:
                json_raw = f.read()
            for i in json_raw.split('\n'):
                if i.strip() != '':
                    self.valid.append(ProxyInfo.load_json(json.loads(i)))
        proxy_files = os.listdir('proxys')
        lastest_file = None
        for i in range(len(proxy_files)-1, -1, -1):
            if '.json' in proxy_files[i] and 'valid.json' != proxy_files[i]:
                lastest_file = proxy_files[i]
                break
        if os.path.exists('proxys/%s' % lastest_file) is True:
            with open('proxys/%s' % lastest_file, 'r') as f:
                json_raw = f.read()
            for i in json_raw.split('\n'):
                if i.strip() != '':
                    self.proxys.append(ProxyInfo.load_json(json.loads(i)))

    def batch_test(self):
        for i in range(len(self.proxys)):
            self.test(self.proxys.pop())

    def valid_test(self):
            tmp = self.valid[:]
            self.valid = []
            for i in tmp:
                self.test(i)

    def clear_proxy_cache(self):
        for i in os.listdir('proxys/'):
            if i != 'valid.json' and '.json' in i:
                os.remove(os.path.join('proxys/', i))

    def wait_free(self):
        while self.thread_monitor is not None and self.thread_monitor.isAlive() is True:
            time.sleep(1)

class ProxyInfo:
    def __init__(self):

        self.country = None
        self.ip = None
        self.port = None
        self.position = None
        self.type = None
        self.protocal = None
        self.response_time = None
        self.access_time = None
        self.lifetime = None
        self.check_time = None

        self.real_ip = None
        self.real_position = None

    def dump(self):
        dump_dict = {
            'country': self.country,
            'ip': self.ip,
            'port': self.port,
            'position': self.position,
            'type': self.type,
            'protocal': self.protocal,
            'response_time': self.response_time,
            'access_time': self.access_time,
            'lifetime': self.lifetime,
            'check_time': self.check_time,
            'real_ip': self.real_ip,
            'real_pos': self.real_position
        }
        return json.dumps(dump_dict)

    @staticmethod
    def load_json(_json):
        tmp = ProxyInfo()
        tmp.country = _json.get('country')
        tmp.ip = _json.get('ip')
        tmp.port = _json.get('port')
        tmp.position = _json.get('position')
        tmp.type = _json.get('type')
        tmp.protocal = _json.get('protocal')
        tmp.response_time = _json.get('response_time')
        tmp.access_time = _json.get('access_time')
        tmp.lifetime = _json.get('lifetime')
        tmp.check_time = _json.get('check_time')
        tmp.real_ip = _json.get('real_ip')
        tmp.real_position = _json.get('real_pos')
        return tmp

    @staticmethod
    def load_soup(raw_soup, type):
        tmp = ProxyInfo()
        if type == 0:

            try:
                tmp.country = raw_soup[0].img.get('alt')
            except:
                tmp.country = None
            tmp.ip = raw_soup[1].string
            tmp.port = raw_soup[2].string
            try:
                tmp.position = raw_soup[3].a.string
            except:
                tmp.position = None
            tmp.type = raw_soup[4].string
            tmp.protocal = raw_soup[5].string.lower()
            tmp.response_time = raw_soup[6].div.get('title')
            tmp.access_time = raw_soup[7].div.get('title')
            tmp.lifetime = raw_soup[8].string
            tmp.check_time = raw_soup[9].string
        elif type == 1:
            tmp.ip = raw_soup[0].string.strip()
            tmp.port = raw_soup[1].string.strip()
            tmp.position = raw_soup[2].string.strip() + ' ' + raw_soup[3].string.strip()
            tmp.check_time = raw_soup[4].string.strip()
        elif type == 2:
            tmp.ip = raw_soup[0].string.strip()
            tmp.port = raw_soup[1].string.strip()
            tmp.type = raw_soup[2].string.strip()
            tmp.protocal = raw_soup[3].string.strip()
            tmp.position = raw_soup[4].string.strip()
            tmp.response_time = raw_soup[5].string.strip()
            tmp.check_time = raw_soup[6].string.strip()
        elif type == 3:
            tmp.ip, tmp.port = raw_soup.split(':')
        return tmp

# a = ProxyCollection()
# # # # pass
# a.load()
# # a.batch_test(20, 0)
# # for i in a.proxys:
# #     print(i.ip, i.position)
# #     a.test(i)
# # pass
# # a.clear_proxy_cache()
# # for j in range(5):
# #     # a.proxys = []
# #     for i in range(1):
# #         a.get_data(j, i+1)
# # # a.save()
# # a.valid_test()
# a.update_lastest()
# a.batch_test()
# a.save()
# print(a.get_anonymous_len())
# print(a.pop(differ=True).real_ip)


