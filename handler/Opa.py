
import threading
import os, time
import json
import traceback

from base.urlop import UrlRequestOp
from core import login, course
from handler.struct.user import UserData
from handler import Pool

from handler.Error import LoginBasicException, UrlOpTimeOutError, PullerBasicException
import gui

import llogger


NOTICE_URL = 'http://jxfw.gdut.edu.cn/notice!getNotice.action?_=%d'


def get_cdatetime():
    return time.asctime(time.localtime())


class UserOp(UrlRequestOp, object):
    def __init__(self, parent, account, password, keys):
        UrlRequestOp.__init__(self)

        self.parent = parent
        self.user = UserData(account, password, keys, self)

        self.loginer = login.Login(self.user)

        self.taker = course.Taker(self.user)
        self._thread = None

        self._get_notice_thread = None
        self.assign_thread_lock = threading.Lock()

    def login(self):
        with self.assign_thread_lock:
            if self._thread and self._thread.isAlive() and self._thread != threading.current_thread():
                return
            if self.user.status == Pool.TAKING or self.user.status == Pool.TIMING_TAKE:
                return
            self._thread = threading.current_thread()
        self.reInit()
        # print(self._thread)
        self.loginer.run()

    def takeCourse(self):
        with self.assign_thread_lock:
            if self._thread and self._thread.isAlive() and self._thread != threading.current_thread():
                return
            if self.user.status == Pool.DONE:
                return
            self._thread = threading.current_thread()
        # print(self._thread)
        if self.user.ready:
            self.taker.run()
        else:
            if self.getStatus() == Pool.DONE:
                return
            self.reInit()
            self.login()
            self.join()
            if self.getStatus() != Pool.FAILURE:
                self.takeCourse()


    def saveCookie(self):
        self.loginer.cookiejar.save('cookies/%s.txt' % self.user.account, ignore_discard=True, ignore_expires=True)

    def loadCookie(self):
        if os.path.exists('cookies/%s.txt' % self.user.account):
            self.setNewCookieJar()
            self.cookiejar.load('cookies/%s.txt' % self.user.account, ignore_discard=True, ignore_expires=True)
            self.buildOpener(self.cookiejar, self.proxy)
            self.loginer.loadUrlop(self)
            self.getReady()
            llogger.ok(self.user.account, '加载Cookie成功。[未验证]')
            return True
        else:
            return False

    def verify(self):
        self.user.status = Pool.VERIFYING
        self.taker.puller.pullSelected()
        targets = self.taker.getTargets()
        if targets:
            tar_str = ''
            for i in targets:
                tar_str += '[%s]' % i.__str__()
            llogger.error(self.user.account, '以下目标未成功: {%s}' % tar_str)
            self.fail()
        else:
            self.done()

    def getStatus(self):
        return self.user.status

    def onTimingtake(self):
        self.user.status = Pool.TIMING_TAKE

    def fail(self):
        self.user.status = Pool.FAILURE
        self.cancelGetNotice()
        llogger.error(self.user.account, '任务失败，停止工作。成功选取[%d]项' % self.user.success_counter)

    def done(self):
        self.user.status = Pool.DONE
        self.cancelGetNotice()
        llogger.ok(self.user.account, '完成任务，停止工作。成功选取[%d]项' % self.user.success_counter)


    def getReady(self):
        self.user.status = Pool.READY
        self.user.ready = True
        self.saveCookie()
        self.loadUrlop(self.loginer)
        self.taker.loadUrlop(self.loginer)

        self.timingGetNotice()

    def reInit(self):
        self.user.status = Pool.UNREADY
        self.user.ready = False
        self.cancelGetNotice()

    def join(self, exec_foo=None, args=()):
        if exec_foo:
            threading.Thread(target=self.__join__, args=(exec_foo, args)).start()
        else:
            self.__join__(exec_foo, args)

    def __join__(self, exec_foo=None, args=()):
        while True:
            with self.assign_thread_lock:
                if not self._thread or not self._thread.isAlive() or self._thread == threading.current_thread():
                    break
            time.sleep(0.01)

        if exec_foo:
            exec_foo(*args)

    def timingGetNotice(self):
        if not self._get_notice_thread or not self._get_notice_thread.isAlive():
            llogger.normal(self.user.account, '[%ds]后拉取通知。' % self.user.timer_refresh)
            self._get_notice_thread = threading.Timer(self.user.timer_refresh, self.getNotice, args=(False,))
            self._get_notice_thread.start()

    def cancelGetNotice(self):

        while True:
            if self._get_notice_thread:
                self._get_notice_thread.cancel()
                if not self._get_notice_thread or not self._get_notice_thread.isAlive() \
                        or self._get_notice_thread == threading.current_thread():
                    break
            else:
                break
            time.sleep(0.01)

    def getNotice(self, once=True):

        try:
            res = self.__getNotice__()
            llogger.ok(self.user.account, '拉取通知成功。', res)
            self.user.status = Pool.READY

        except LoginBasicException as e:
            traceback.print_exc()
        except PullerBasicException as e:
            traceback.print_exc()
        except UrlOpTimeOutError as e:
            traceback.print_exc()
            if not once:
                # self.cancelGetNotice()
                self._get_notice_thread = None
                self.timingGetNotice()
        else:
            if not once:
                # self.cancelGetNotice()
                self._get_notice_thread = None
                self.timingGetNotice()


    def __getNotice__(self):
        raw, res = self.request(branch_num=0, method='GET',
                                url=NOTICE_URL % (time.time() * 1000), max_retry=3)

        text = bytes.decode(raw) if isinstance(raw, bytes) else raw

        try:
            res_json = json.loads(text)
        except json.JSONDecodeError as e:
            llogger.warning(self.user.account, '拉取通知失败。', text)
            raise PullerBasicException(self.user, text, e)

        return res_json

    def set_MemberView_Item(self):
        cur_status = self.getStatus()
        index = self.parent.getUserIndex(self.user)
        gui.frame_main.listctrl_member.SetItem(index, 2, Pool.status2str(cur_status))

        gui.frame_main.listctrl_member.SetItem(index, 3, '√' if cur_status == Pool.READY else '×')

        gui.frame_main.listctrl_member.SetItem(index, 6, get_cdatetime())