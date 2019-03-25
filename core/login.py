
from base.urlop import UrlRequestOp
import time
import io
import captcha.killer
import json
import traceback

from handler import Pool
from handler.Error import LoginBasicException, UrlOpTimeOutError

import llogger

CAPTCHA_URL = 'http://jxfw.gdut.edu.cn/yzm?d=%d'
POST_LOGIN = 'http://jxfw.gdut.edu.cn/new/login'



MAX_RETRY = -1

class Login(UrlRequestOp):
    def __init__(self, user):
        UrlRequestOp.__init__(self)
        self.user = user
        self.counter = 0

    def run(self):
        llogger.normal(self.user.account, '开始登录。')
        self.user.status = Pool.LOGINNING
        try:
            self.__run__()
        except LoginBasicException as e:
            traceback.print_exc()
        except UrlOpTimeOutError as e:
            traceback.print_exc()
            # traceback.format_exc()
        else:
            pass

    def __run__(self):

        self.setNewCookieJar()

        self.counter += 1

        self.makePostData()

        res = self.postLogin()
        self.parseRespond(res)

    def makePostData(self):
        global MAX_RETRY
        raw, res = self.request(url=CAPTCHA_URL % (time.time() * 1000), method='GET',
                                branch_num=1, isolate=True, max_retry=MAX_RETRY)

        if 'image' in res.info()['Content-Type']:

            fp = io.BytesIO()
            fp.write(raw)

            verifycode = captcha.killer.get(fp)
            self.user.setVerifyCode(verifycode)

        else:
            raise LoginBasicException(self.user, raw)

    def postLogin(self):
        global MAX_RETRY
        raw, res = self.request(branch_num=0, method='POST', url=POST_LOGIN, data=self.user.getPostData(),
                                max_retry=MAX_RETRY)

        return bytes.decode(raw) if isinstance(raw, bytes) else raw

    def parseRespond(self, text):
        try:
            res_json = json.loads(text)
        except json.JSONDecodeError as e:

            raise LoginBasicException(self.user, e.msg, e)

        if '登录成功' in res_json['message']:
            self.succeed()
            llogger.ok(self.user.account, '登录成功。', text)
        else:
            raise LoginBasicException(self.user, text)

    def succeed(self):
        self.user.op.getReady()


