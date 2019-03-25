
from base import delayer
import llogger

class UrlOpTimeOutError(Exception):
    def __init__(self, req_kwargs):
        self.req_kwargs = req_kwargs
        if req_kwargs.get('user'):
            llogger.error(req_kwargs.get('user').account, 'Urllib请求超时。', req_kwargs.get('msg', ''))
        else:
            llogger.error('NULL', 'Urllib请求超时。', req_kwargs.get('msg', ''))



class LoginBasicException(Exception):
    def __init__(self, user, msg, from_err=None):
        self.user = user

        self.msg = bytes.decode(msg) if isinstance(msg, bytes) else msg

        self.from_err = from_err
        self.handleError()

    def handleError(self):
        for i, j in self.getHandlers().items():
            if i in self.msg:
                return j()
        else:
            return self.UnknownErrorHandler()

    def getHandlers(self):
        return {
            '您的帐号或密码不正确': self.UserValueErrorHandler,
            '验证码不正确': self.VerifyCodeErrorHandler,
            '连接已过期': self.LoginExpireErrorHandler,
            '请输入验证码': self.UnloginErrorHandler,
        }

    def UserValueErrorHandler(self):
        self.user.op.reInit()
        self.user.op.fail()
        llogger.error(self.user.account, '帐号或密码不正确，登录失败中止。', self.msg)

    def VerifyCodeErrorHandler(self):
        self.user.op.reInit()
        delayer.timingRun(self.user, self.user.op.login, (0, 0.5), self.msg)
        llogger.warning(self.user.account, '验证码识别错误，登录失败。', self.msg)

    def LoginExpireErrorHandler(self):
        self.user.op.reInit()
        delayer.timingRun(self.user, self.user.op.login, (0, 0.5), self.msg)
        llogger.warning(self.user.account, '连接已过期，登录失败。', self.msg)

    def UnloginErrorHandler(self):
        llogger.warning(self.user.account, '操作失败: 账号已离线，重新登录。', self.msg)
        self.user.op.reInit()
        delayer.timingRun(self.user, self.user.op.login, (0, 0.5), self.msg)

    def UnknownErrorHandler(self):

        print('UnknownError in LoginBasicException: ', self.msg)
        llogger.error(self.user.account, '登录发生未知错误。', self.msg)


# class IsAvlBasicException(Exception):


class TakerBasicException(Exception):
    def __init__(self, user, msg, from_err=None, course=None):
        self.user = user
        self.msg = msg
        self.from_err = from_err

        self.course = course

        self.handleError()


    def handleError(self):
        for i, j in self.getHandlers().items():
            if i in self.msg:
                return j()
        else:
            return self.UnknownErrorHandler()

    def getHandlers(self):
        return {
            '请输入验证码': self.UnloginErrorHandler,
            '您已被迫退出': self.UnloginErrorHandler,
            '选了': self.RepeatErrorHandler,
            '超出选课要求门数': self.ExceedErrorHandler,
            '不是选课时间': self.TakingTimeErrorHandler,
            '没有开设该课程': self.CourseNotFoundErrorHandler

        }

    def UnloginErrorHandler(self):
        llogger.warning(self.user.account, '操作失败:[%s]-"账号已离线，重新登录"。' % self.course, self.msg)
        self.user.op.reInit()
        delayer.timingRun(self.user, self.user.op.login, (0, 0.5), self.msg)

    def RepeatErrorHandler(self):
        llogger.warning(self.user.account, '操作失败:[%s]-"已经选了该课程"。' % self.course, self.msg)
        self.user.op.taker.selected.append(self.course)
        delayer.timingRun(self.user, self.user.op.takeCourse, (0, 0.5), self.msg)

    def ExceedErrorHandler(self):
        llogger.warning(self.user.account, '操作失败:[%s]-"超出选课要求门数"。' % self.course, self.msg)
        self.user.op.done()

    def TakingTimeErrorHandler(self):
        llogger.warning(self.user.account, '操作等待:[%s]-"当前不是选课时间"。' % self.course, self.msg)
        self.user.op.onTimingtake()
        delayer.timingRun(self.user, self.user.op.takeCourse, self.user.delay_range, self.msg)

    def CourseNotFoundErrorHandler(self):
        llogger.warning(self.user.account, '操作失败:[%s]-"没有开设该课程"。' % self.course, self.msg)
        self.user.op.taker.pullCourses()
        delayer.timingRun(self.user, self.user.op.takeCourse, self.user.delay_range, self.msg)

    def UnknownErrorHandler(self):
        # print('UnknownError in TakerBasicException: ', self.msg)
        llogger.error(self.user.account, '操作发生未知信息。', self.msg)



class PullerBasicException(Exception):
    def __init__(self, user, msg, from_err=None):
        self.user = user
        self.msg = msg
        self.from_err = from_err

        self.handleError()

    def handleError(self):
        for i, j in self.getHandlers().items():
            if i in self.msg:
                return j()
        else:
            return self.UnknownErrorHandler()

    def getHandlers(self):
        return {
            '请输入验证码': self.UnloginErrorHandler,
            '您已被迫退出': self.UnloginErrorHandler
        }

    def UnloginErrorHandler(self):
        llogger.warning(self.user.account, '拉取失败: 账号已离线，重新登录。', self.msg)
        self.user.op.reInit()
        delayer.timingRun(self.user, self.user.op.login, (0, 0.5), self.msg)

    def UnknownErrorHandler(self):
        print('UnknownError in TakerBasicException: ', self.msg)
        llogger.error(self.user.account, '操作发生未知信息。', self.msg)


class VerifyBasicException(Exception):
    def __init__(self, user, msg, from_err=None):
        self.user = user
        self.msg = msg
        self.from_err = from_err

        self.handleError()

    def handleError(self):
        for i, j in self.getHandlers().items():
            if i in self.msg:
                return j()
        else:
            return self.UnknownErrorHandler()

    def getHandlers(self):
        return {
            '请输入验证码': self.UnloginErrorHandler,
            '您已被迫退出': self.UnloginErrorHandler
        }

    def UnloginErrorHandler(self):
        llogger.warning(self.user.account, '操作失败: 账号已离线，重新登录。', self.msg)
        self.user.op.reInit()
        delayer.timingRun(self.user, self.user.op.login, (0, 0.5), self.msg)

    def UnknownErrorHandler(self):
        print('UnknownError in TakerBasicException: ', self.msg)
        llogger.error(self.user.account, '操作发生未知信息。', self.msg)