import urllib.request
import http.cookiejar
import threading
import time
import logging
import json
import configparser
from Login import Login
import TakeCourse
from UrlOp import UrlOp
import os
from Proxy import ProxyCollection, ProxyInfo
from CrackCaptcha import CrackCaptcha
# from WaitLock import WaitLock

FORCE_TAKE = False
SAFE = False

MAX_RETRIES = 3
MAX_RETRIES_TIMEOUT = 5
TIME_WAIT = 0.1
TIME_RETAKE = 5

RELOGIN = -1
SUCCESS = 0



class PoolOp:
    def __init__(self):
        self.members = []
        self.max_member = 20
        self.crack_captcha = CrackCaptcha()
        self.proxy_op = ProxyCollection()
        self.queue = {}
        self.verify_queue = []
        self.__point = 0

        self.proxy_req_lock = threading.Lock()
        self.runing_lock = threading.Lock()

        self.member_running_lock = threading.Lock()

        self.monitor = None

        # self.launch_monitor()


    def launch_monitor(self):
        if self.monitor is None or self.monitor.isAlive() is False:
            self.monitor = threading.Thread(target=self.__monitor)
            self.monitor.start()


    def __monitor(self):
        _count = 0
        while True:
            with self.runing_lock:
                if len(self.members) == 0:
                    break
                # with self.
                with self.member_running_lock:
                    for i, j in self.queue.items():
                        if j.isAlive() is False:
                            index = self.members.index(i)
                            # if i.end is False:
                            print('thread [%s] died. - try to restart.' % i.id)
                            self.run(index)
                            break
                if len(self.queue) == 0:
                    break
                _count += 1
                time.sleep(1)
                if _count % 100 == 0:
                    self.save_op_result()

        # save_msg
        self.save_op_result()

    def save_op_result(self):
        _dump_dict = {}
        for i in self.members:
            if os.path.exists('log/%s' % i.id) is False:
                os.mkdir('log/%s' % i.id)
            with open('log/%s/%s.txt' % (i.id, int(time.time())), 'w') as f:
                f.write(json.dumps(i.result_msgs))
            # _dump_dict[i.id] = i.result_msgs
            # _dump_list.append(i.result_msgs)

        # with open('log/%s.txt' % int(time.time()), 'w') as f:
        #     f.write(json.dumps(_dump_dict))


    def batch_run(self):
        with self.runing_lock:
            for i in range(len(self.members)):
                self.run(i)

    def __launch(self, index):
        thd = threading.Thread(target=self.members[index].run)
        self.queue[self.members[index]] = thd
        # self.members[index].running_thread = thd
        thd.start()

    def run(self, index=None, max_batch_size=50):
        self.launch_monitor()
        if index is None:
            while max_batch_size <= len(self.queue):
                time.sleep(TIME_WAIT)
            if self.members[self.__point] in self.queue:
                if self.queue[self.members[self.__point]].isAlive() is False:
                    self.__launch(self.__point)
            else:
                self.__launch(self.__point)

            self.__point += 1
            if self.__point >= len(self.members):
                self.__point = 0

        else:
            self.__launch(index)

    def batch_verify(self):
        logging.info('[all] - batch verifying ...' )
        for m in range(MAX_RETRIES):
            while self.monitor.isAlive() is True or len(self.queue) != 0:
                time.sleep(TIME_WAIT)
            for i, j in enumerate(self.members):
                if j.succeed is False:
                    logging.info('[%s] - verifying ...' % (j.id))
                    if j.verify() is False:
                        j.retries_count += 1
                        self.run(i)
                        self.launch_monitor()

    def init_proxy(self):
        self.proxy_op.load()
        self.proxy_op.valid_test()
        self.proxy_op.save()
        self.proxy_op.wait_free()

    def build_member(self, account, password, keys):
        self.proxy_op.wait_free()
        mem = MemberOp(self, account, password, keys)
        self.members.append(mem)
        mem.build_opener(cookiejar=mem.load_cookie())
        return mem

    def __del__(self):
        del self.crack_captcha

    # def get_proxy(self):
    #
    #     _proxy = self.proxy_op.pop(anonymous=anonymous)
    #
    # def build_proxy_handler(self, anonymous=True):
    #     tmp = self.proxy_op._point
    #     _proxy = self.proxy_op.pop(anonymous=anonymous)
    #     # print(tmp, self.proxy_op._point)
    #     if tmp >= self.proxy_op._point:
    #         # print(tmp, self.proxy_op._point)
    #         return None
    #     if _proxy is None:
    #         return None
    #
    #     return urllib.request.ProxyHandler({'http': '%s:%s' % (_proxy.ip, _proxy.port)})

    def get_next_proxy(self, member, anonymous=True):
        _proxy = self.proxy_op.pop(anonymous=anonymous)

        if _proxy is None:
            return False
        try:
            if self.proxy_op.valid.index(member.proxy_info) >= self.proxy_op.valid.index(_proxy):
                return False
        except:
            pass
        # member.proxy_info = _proxy
        return _proxy

    def proxy_request(self, member):
        _count = 0
        # tmp = self.proxy_op._point
        _proxy = self.get_next_proxy(member)
        if _proxy is False:
            return False

        proxy_handler = urllib.request.ProxyHandler({'http': '%s:%s' % (_proxy.ip, _proxy.port)})
        # if tmp >= self.proxy_op._point:
        #     # print(tmp, self.proxy_op._point)
        #     return None
        # if _proxy is None:
        #     return None

        # proxy_handler = self.build_proxy_handler()

        tmp = member.proxy_handler
        for i, j in enumerate(self.members):
            if tmp is j.proxy_handler:
                # print(j.id)
                j.build_opener(proxy_handler)
                j.proxy_info = _proxy
                _count += 1
                if _count >= 10 and len(self.members) != i+1:
                    _next = self.get_next_proxy(member)
                    if _next is False:
                        proxy_handler = urllib.request.ProxyHandler({'http': '%s:%s' % (_next.ip, _next.port)})
                    else:
                        proxy_handler = urllib.request.ProxyHandler({'http': '%s:%s' % (_proxy.ip, _proxy.port)})

                    _count = 0

    def dequeue(self, member):
        del self.queue[member]

    def verify_enqueue(self, member):
        self.dequeue(member)
        self.verify_queue.append(member)

    def isEnd(self):
        return len(self.members) != 0 and len(self.queue) == 0 and self.monitor.isAlive() is False


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/68.0.3440.84 Safari/537.36',
    'Host': 'jxfw.gdut.edu.cn',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1'
}


class MemberOp(UrlOp):
    def __init__(self, pool, account, password, keys):
        UrlOp.__init__(self)
        self.account = account
        self.password = password
        self.keys = keys
        self.id = int(account)
        self.retries_count = 0
        self.retries = 0

        self.pool = pool
        self.succeed = False
        # http.cookiejar.MozillaCookieJar('cookies/%s.txt' % self.id)
        self.cookiejar = None
        self.opener = None
        self.proxy_handler = None

        self.login_op = Login(self, account, password)
        self.take_course_op = TakeCourse.TakeCourse(self, self.keys)

        self.proxy_info = ProxyInfo()
        self.proxy_info.ip = self.pool.proxy_op.origin.ip
        self.proxy_info.real_ip = self.pool.proxy_op.origin.ip
        # self.running_thread = None

        self.result_msgs = []
        self.pass_login = False

        # self.load_config()

    def load_cookie(self):
        if os.path.exists('cookies/%s.txt' % self.id) is False:
            return False
        cookiejar = http.cookiejar.MozillaCookieJar()
        cookiejar.load('cookies/%s.txt' % self.id, ignore_discard=True, ignore_expires=True)
        logging.info('[%s] - (%s) - load from cookie.' % (self.id, self.proxy_info.real_ip))
        self.pass_login = True
        return cookiejar


    def verify(self):
        if self.succeed is False:
            self.take_course_op.selected = TakeCourse.Courses()
            raw_json = self.take_course_op.get_selected_course()
            if raw_json is None:
                return False
            self.take_course_op.selected.append(raw_json)
            cur = self.take_course_op.selected[self.keys]
            if cur:
                logging.info('[%s] - take "%s - %s" course successfully.' % (self.id, cur[0].kcmc, cur[0].teaxm))
                self.succeed = True
                return True
            else:
                logging.error('[%s] - failed to take that course.-> retry, %d time(s) left' % (self.id,
                              MAX_RETRIES - self.retries_count))

            return False
        else:
            return True


    def run(self):
        with self.pool.member_running_lock:
            thd = threading.Thread(target=self.launch)
            self.pool.queue[self] = thd
            thd.start()

    def take_processor(self):
        result = False

        while result is False:
            result, msg_take = self.take_course_op.run(FORCE_TAKE)
            self.result_msgs.append((result, msg_take))
            if self.take_course_op.relogin is True:
                self.take_course_op.relogin = False
                return None
            if self.take_course_op.wait_retake is True:
                self.take_course_op.wait_retake = False
                time.sleep(TIME_RETAKE)
                continue
            if result is False:
                logging.info('[%s] - failed to take course. msg: %s' % (self.id, msg_take))
                self.retries += 1

                if self.proxy_handler is None:
                    time.sleep(3)
                    continue
                if self.retries >= MAX_RETRIES_TIMEOUT:
                    self.proxy_req()
                    return False
                else:
                    continue

        else:
            return True


    def launch(self):
        if self.succeed is False:
            while True:
                if self.pass_login is True:
                    result = self.take_processor()
                    if result is False:
                        return
                    if result is None:
                        # self.take_course_op.relogin = False
                        self.pass_login = False
                        continue
                    break

                logging.info('[%s] - (%s) - login running...' % (self.id, self.proxy_info.real_ip))
                msg = self.login_op.run()

                if self.proxy_invalid is True:
                    self.proxy_req()
                    return
                if msg is None:
                    if self.proxy_handler is None:
                        time.sleep(3)
                        continue
                    self.retries += 1
                    if self.retries >= MAX_RETRIES_TIMEOUT:
                        self.proxy_req()
                    else:
                        continue
                    return
                if msg['code'] == 0:
                    self.cookiejar.save(ignore_discard=True, ignore_expires=True)
                    self.retries = 0
                    logging.info('[%s] - (%s) - sign in successfully.' % (self.id, self.proxy_info.ip))
                    # result = False
                    result = self.take_processor()
                    if result is False:
                        return
                    if self.take_course_op.relogin is True:
                        self.take_course_op.relogin = False
                        continue
                    break
                else:
                    logging.info('[%s] - failed to sign in. msg: %s, ->retry' % (self.id, msg.get('message')))
                    time.sleep(TIME_WAIT)

            self.leave()

    # def take_op(self):

    def build_opener(self, proxy_handler=None, cookiejar=None):
        # if self.running is True:
        with self.wait:
            self.proxy_handler = proxy_handler
            if cookiejar is None:
                cookiejar = http.cookiejar.MozillaCookieJar('cookies/%s.txt' % self.id)
                cookie_processor = urllib.request.HTTPCookieProcessor(cookiejar)
                self.cookiejar = cookiejar
            else:
                cookie_processor = urllib.request.HTTPCookieProcessor(cookiejar)
                self.cookiejar = cookiejar

            if proxy_handler is not None:
                self.ip = proxy_handler.proxies['http']
                self.opener = urllib.request.build_opener(cookie_processor, proxy_handler)

            else:
                self.opener = urllib.request.build_opener(cookie_processor)

            self.opener.addheaders = list(HEADERS.items())



    def proxy_req(self):
        self.proxy_invalid = False
        self.retries_count = 0
        # old_proxy = self.proxy_handler
        old_proxy = self.proxy_info
        if self.proxy_info is not None and self.proxy_info.real_ip != self.ip:
            self.ip = self.proxy_info.real_ip
        else:

            with self.pool.proxy_req_lock:

                if old_proxy == self.proxy_info:

                    if self.pool.proxy_request(self) is False:
                        # if self.proxy_handler is None:
                        #     logging.info('[%s] - (%s) - No more proxy. ->leave' % (self.id, self.pool.proxy_op.origin.ip))
                        # else:
                        logging.info('[%s] - (%s) - No more proxy. ->leave' % (self.id, self.proxy_info.real_ip))
                        self.leave()
                        return
                    # if old_proxy is None:
                    #     logging.info('[%s] - request proxy change.(%s) -> (%s)' % (
                    #         self.id, self.pool.proxy_op.origin.ip, self.proxy_info.real_ip))
                    # else:
                    logging.info('[%s] - request proxy change.(%s) -> (%s)' % (
                        self.id, old_proxy.real_ip, self.proxy_info.real_ip))
        self.run()

    def leave(self):
        logging.info('[%s] - leave .' % self.id)
        self.pool.verify_enqueue(self)
