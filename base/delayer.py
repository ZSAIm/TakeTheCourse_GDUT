
import time
import threading
from random import randint

__delayer__ = None

def init():
    global __delayer__
    __delayer__ = Delayer()


def timingRun(*args, **kwargs):
    global __delayer__
    return __delayer__.timingRun(*args, **kwargs)

def cancelTiming(user):
    global __delayer__
    return __delayer__.cancelTiming(user)


class Delayer(object):
    def __init__(self):

        self.executors = {}

        self._thread = None
        self.exec_lock = threading.Lock()

    def downCounter(self):
        while True:
            tmp = self.executors.copy()
            with self.exec_lock:
                for i, j in tmp.items():
                    self.executors[i].sec -= 1
                    if j.sec < 1 or not j.thread.isAlive():
                        self.executors[i].sec = 0
                        del self.executors[i]

            if not self.executors:
                break

            time.sleep(1)

    def timingRun(self, user, foo, sec, msg='', args=None, kwargs=None):
        if not self._thread or not self._thread.isAlive():
            self._thread = threading.Thread(target=self.downCounter)
            self._thread.start()

        if isinstance(sec, list) or isinstance(sec, tuple):
            sec = randint(sec[0] * 1000, sec[1] * 1000) / 1000.0

        timer = threading.Timer(sec, foo, args=args, kwargs=kwargs)
        timer.setName(user.account)

        info = DelayerInfo(user, foo, sec, msg, timer)

        timer.start()
        user.op._thread = timer

        with self.exec_lock:
            self.executors[user.account] = info

        return sec

    def cancelTiming(self, user):
        with self.exec_lock:
            if user.account in self.executors:
                self.executors[user.account].thread.cancel()
                del self.executors[user.account]
                return True
            else:
                return False


class DelayerInfo(object):
    def __init__(self, user, foo, sec, msg, thread):
        self.user = user
        self.foo = foo
        self.sec = sec
        self.msg = msg
        self.thread = thread

    def getName(self):
        return self.user

    def getFoo(self):
        return self.foo

    def getDelayTime(self):
        return self.sec

    def getMessage(self):
        return self.msg

    def getThreadObj(self):
        return self.thread


if not __delayer__:
    init()