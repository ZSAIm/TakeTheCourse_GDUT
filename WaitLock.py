import time


class WaitLock:
    def __init__(self, obj=None, timeout=None, key=None):
        self.__wait_lock = False
        self.__in_wait = False
        self.timeout = timeout

        self.obj = obj
        self.key = key

    def __enter__(self):
        # print '__enter__'
        self.__request_wait()
        if self.key is not None:
            if self.timeout is not None:
                return self.__wait_res_key_timeout()
            else:
                return self.__wait_res_key()
        elif self.timeout is not None:
            return self.__wait_res_timeout()
        else:
            return self.__wait_res()


    def __exit__(self, exc_type, exc_val, exc_tb):
        # print '__exit__'
        self.__release_wait()

    def __request_wait(self):
        while self.__wait_lock is True:
            time.sleep(0.1)
        self.__wait_lock = True

    def acquire(self):
        while self.__wait_lock:
            self.__in_wait = True
            time.sleep(0.1)
        self.__in_wait = False

    def __wait_res(self):
        while self.__in_wait is False:
            time.sleep(0.1)
        return True

    def __wait_res_key(self):
        while self.__in_wait is False:
            if getattr(self.obj, self.key) is False:
                return False
            time.sleep(0.1)
        return True

    def __wait_res_key_timeout(self):
        _count = 0
        while self.__in_wait is False:
            _count += 1
            if _count >= 10 * self.timeout:
                return False
            if getattr(self.obj, self.key) is False:
                return False
            time.sleep(0.1)
        return True

    def __wait_res_timeout(self):
        _count = 0
        while self.__in_wait is False:
            _count += 1
            if _count >= 10 * self.timeout:
                return False
            time.sleep(0.1)
        return True

    def __release_wait(self):
        self.__wait_lock = False

    def setKey(self, key):
        self.key = key

    def release(self):
        self.__wait_lock = False