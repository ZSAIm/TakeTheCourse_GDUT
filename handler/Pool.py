
import time
import threading

from base import delayer
from handler.Opa import UserOp

import gui
import llogger

import xlrd


CAPTCHA_URL = 'http://jxfw.gdut.edu.cn/yzm?d=%d'
POST_LOGIN = 'http://jxfw.gdut.edu.cn/new/login'

Delayer = delayer.Delayer()


UNKNOWN = object()
READY = object()
UNREADY = object()

LOGINNING = object()
TAKING = object()
VERIFYING = object()

TIMING_TAKE = object()

IDLE = object()
RUNNING = object()
SUCCESS = object()

DONE = object()

FAILURE = object()

PULLING = object()

def status2str(status):
    return {
        READY: '准备就绪',
        UNREADY: '未就绪',
        UNKNOWN: '未知',
        LOGINNING: '登录中',
        TAKING: '选课中',
        VERIFYING: '校验中',
        TIMING_TAKE: '延时中',
        PULLING: '拉取中',
        IDLE: '空闲中',
        DONE: '完成',
        FAILURE: '失败'
    }.get(status, '未知')

# √×○

class UserPool(object):
    def __init__(self):
        self.queue = []
        self.members = {}
        self.__inspector__ = None

        self.statusbar_thread = threading.Thread(target=self.statusBarTiming)
        self.statusbar_thread.start()
        # UserOp.pool = self
    def statusBarTiming(self):
        while True:
            total = str(len(self.queue))
            gui.frame_main.status_bar.SetStatusText(total, 1)

            ready = 0
            for i in self.queue:
                if i.getStatus() == READY:
                    ready += 1
            gui.frame_main.status_bar.SetStatusText(str(ready), 3)

            taking = 0
            for i in self.queue:
                if i.getStatus() == TAKING or i.getStatus() == TIMING_TAKE:
                    taking += 1
            gui.frame_main.status_bar.SetStatusText(str(taking), 5)

            done = 0
            for i in self.queue:
                if i.getStatus() == DONE:
                    done += 1

            gui.frame_main.status_bar.SetStatusText(str(done), 7)

            cur_time = time.asctime(time.localtime())
            gui.frame_main.status_bar.SetStatusText(cur_time, 9)

            time.sleep(0.5)


    def inspector(self):
        while True:
            pass
            time.sleep(0.1)

    def add(self, account, password, keys):

        usrop = UserOp(self, account, password, keys)

        if account not in self.members:
            self.members[account] = usrop
            self.queue.append(usrop)
            data = (account, status2str(usrop.getStatus()), u'×', u'○', u'○', u'○')
            gui.frame_main.listctrl_member.Append(data)
            llogger.ok(account, '成员添加成功。')
        else:
            llogger.warning(account, '成员已存在与列表中，请不要重复添加。')

        return usrop

    def loadFromXlsx(self, filename):
        book = xlrd.open_workbook(filename)
        sheet0 = book.sheet_by_index(0)
        table_head = sheet0.row_values(0)
        for i in range(1, sheet0.nrows):
            words = sheet0.row_values(i)
            self.add(str(int(words[0])), words[1], words[2])

    def runLoginAll(self):
        for i in self.queue:
            if not i.loadCookie():
                threading.Thread(target=i.login).start()
                # i.login()

    def runTakeAll(self):
        for i in self.queue:
            threading.Thread(target=i.takeCourse).start()

    def runVerifyAll(self):
        for i in self.queue:
            threading.Thread(target=i.verify).start()

    def getUserOp(self, account):
        return self.members.get(account, None)

    def getUserIndex(self, user):
        return self.queue.index(user.op)

    def remove(self, userop):
        index = self.queue.index(userop)
        self.delete(index)

    def delete(self, index):
        item = self.queue.pop(index)
        del self.members[item.user.account]
        gui.frame_main.listctrl_member.DeleteItem(index)
        llogger.ok(item.user.account, '成员删除成功。')

    def exit(self):
        for i in self.queue:
            i.cancelGetNotice()