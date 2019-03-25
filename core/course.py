

from base.urlop import UrlRequestOp
import json
import math, time
from random import randint
import traceback
from bs4 import BeautifulSoup


from base import delayer
from handler import Pool
from handler.Error import TakerBasicException, UrlOpTimeOutError, PullerBasicException
import llogger
import gui

ITEM_EACH_PAGE = 150
MAX_RETRY = -1

OPTIONAL_URL = 'http://jxfw.gdut.edu.cn/xsxklist!getDataList.action'
SELECTED_URL = 'http://jxfw.gdut.edu.cn/xsxklist!getXzkcList.action'
FOO_JS_URL = 'http://jxfw.gdut.edu.cn/xsxklist!xsmhxsxk.action'

USER_COURSE_URL = 'http://jxfw.gdut.edu.cn/xsgrkbcx!getDataList.action'
COURSE_DATECODE_URL = 'http://jxfw.gdut.edu.cn/xsgrkbcx!getXsgrbkList.action'


ADD_COURSE_URL = 'http://jxfw.gdut.edu.cn/xsxklist!getAdd.action'
CANCEL_COURSE_URL = 'http://jxfw.gdut.edu.cn/xsxklist!getCancel.action'

KEYWORD_TAKE_FOO = 'xsxklist!getAdd.action'


class SeasonCode:
    def __init__(self):
        self.selected_index = None
        self._list = []
        self._dict = {}

    def extract(self, bs4):
        for i in bs4.find_all('option'):
            if i.has_attr('selected'):
                self.selected_index = len(self._list)
            self._list.append(i.get_text())
            self._dict[i.get_text()] = i.get('value')

    def isEmpty(self):
        return not self._list

    def getCode(self, selected_index):
        return self._dict[self._list[selected_index]]

    def getAll(self):
        for i in self._list:
            yield self._dict[i], i

    def getCodeFromSeason(self, season):
        return self._dict[season]

    def setSeletedIndex(self, index):
        self.selected_index = index


class Puller(object):
    def __init__(self, user, urlop):
        self.urlop = urlop
        self.user = user

        self.season_code = SeasonCode()

        self.selected = CoursePool()
        self.optional = CoursePool()

        self.user_course = CoursePool()

    def pullCourses(self):
        llogger.normal(self.user.account, '开始拉取选课课程信息。')

        self.pullOptional()
        self.pullSelected()

    def pullOptional(self):
        llogger.normal(self.user.account, '开始拉取可选课程信息。')
        self.user.status = Pool.PULLING
        try:
            self.optional = CoursePool()
            cur_page = 1

            total_res = []
            res = self.__getOptional__(cur_page)
            total_res.append(res)
            rows = res.get('rows')
            llogger.ok(self.user.account, '可选课程拉取成功。', res)
            if not rows:
                return
            self.optional.extract(rows=rows)
            total = int(res.get('total', -1))
            self.optional.total = total

            if total == -1:
                raise Exception('RespondUnknown', res)
            page_num = int(math.ceil(total * 1.0 / ITEM_EACH_PAGE))

            for i in range(page_num - 1):
                cur_page += 1
                res = self.__getOptional__(cur_page)
                total_res.append(res)
                rows = res.get('rows')
                self.optional.extract(rows=rows)

            llogger.ok(self.user.account, '可选课程拉取成功: 共[%d]项' % self.optional.total, total_res)
            self.user.status = Pool.READY

        except TakerBasicException as e:
            traceback.print_exc()
            self.user.op.join(exec_foo=self.pullOptional)


    def pullSelected(self):
        llogger.normal(self.user.account, '开始拉取已选课程信息。')
        self.user.status = Pool.PULLING
        try:
            self.selected = CoursePool()
            res = self.__getSelected__()

            self.selected.extract(rows=res)

            llogger.ok(self.user.account, '已选课程拉取成功。', res)
            self.user.status = Pool.READY
        except TakerBasicException as e:
            traceback.print_exc()
            # time.sleep(randint(0, 500) / 1000.0)
            self.user.op.join(exec_foo=self.pullSelected)

    def __getOptional__(self, page):
        data = {
            'page': page,
            'rows': ITEM_EACH_PAGE,
            'sort': 'kcrwdm',
            'order': 'asc'
        }

        raw, res = self.urlop.request(url=OPTIONAL_URL, max_retry=-1, branch_num=1, method='POST', data=data)

        text = bytes.decode(raw) if isinstance(raw, bytes) else raw

        try:
            course_raw = json.loads(text)
        except json.JSONDecodeError as e:
            raise TakerBasicException(self.user, text, e)

        return course_raw

    def __getSelected__(self):
        data = {
            'sort': 'kcrwdm',
            'order': 'asc'
        }

        raw, res = self.urlop.request(url=SELECTED_URL, max_retry=-1, branch_num=1, method='POST', data=data)

        text = bytes.decode(raw) if isinstance(raw, bytes) else raw

        try:
            course_raw = json.loads(text)
        except json.JSONDecodeError as e:
            raise TakerBasicException(self.user, text, e)

        return course_raw


    def pullDateCode(self):
        try:
            self.season_code = SeasonCode()
            self.__getDateCode__()
        except PullerBasicException as e:
            traceback.print_exc()
            # self.pullDateCode()
            # self.user.op.join(exec_foo=self.pullDateCode)
        except UrlOpTimeOutError as e:
            traceback.print_exc()


    def __getDateCode__(self):
        raw, res = self.urlop.request(url=COURSE_DATECODE_URL, max_retry=2, branch_num=1, method='GET')

        text = bytes.decode(raw) if isinstance(raw, bytes) else raw

        bs4 = BeautifulSoup(text, "html.parser")
        bs4 = bs4.find('select', id='xnxqdm')

        if bs4:
            self.season_code.extract(bs4)
        else:
            raise PullerBasicException(self.user, text)


    def pullUserCourse(self):
        llogger.normal(self.user.account, '开始拉取个人课程信息。')
        self.user.status = Pool.PULLING

        if self.season_code.isEmpty():
            self.pullDateCode()
            self.user.op.join()
            if self.season_code.isEmpty():
                self.pullDateCode()
                if self.season_code.isEmpty():
                    return


        try:
            self.user_course = CoursePool()
            cur_page = 1
            total_res = []
            res = self.__getUserCourse__(cur_page)
            total_res.append(res)
            rows = res.get('rows')
            if not rows:
                return
            self.user_course.extract(rows=rows)
            total = int(res.get('total', -1))
            self.user_course.total = total

            if total == -1:
                raise Exception('RespondUnknown', res)
            page_num = int(math.ceil(total * 1.0 / ITEM_EACH_PAGE))

            for i in range(page_num - 1):
                cur_page += 1
                res = self.__getUserCourse__(cur_page)
                total_res.append(res)
                rows = res.get('rows')
                self.user_course.extract(rows=rows)

            llogger.ok(self.user.account, '拉取个人课程成功: 共[%d]项' % self.user_course.total, total_res)
            self.user.status = Pool.READY
        except PullerBasicException as e:
            traceback.print_exc()
            # self.user.op.join(exec_foo=self.pullUserCourse)
        # finally:



    def displayUserCourse(self):
        gui.frame_configure.listctrl_optional.initUserCourseColumn()
        self.pullUserCourse()

        gui.frame_configure.choice_season.Clear()
        for i, j in self.season_code.getAll():
            gui.frame_configure.choice_season.Append(j)

        gui.frame_configure.choice_season.SetSelection(self.season_code.selected_index)

        for i in self.user_course.getAll():

            data = (i.kcmc, i.jxbmc, i.pkrs, i.teaxms, i.zc, i.xq, i.jcdm,
                    i.jxcdmc, i.pkrq, i.kxh, i.jxhjmc, i.sknrjj)
            gui.frame_configure.listctrl_optional.Append(data)
        # else:
        #     pass

    def displayCourse(self):
        gui.frame_configure.listctrl_optional.initOptionColumn()
        gui.frame_configure.listctrl_selected.initSelectedColumn()

        if not self.optional.getAll():
            self.pullCourses()

        for i in self.optional.getAll():
            data = (i.kcmc, i.xf, i.teaxm, i.pkrs, i.jxbrs, i.kcflmc)
            gui.frame_configure.listctrl_optional.Append(data)

        for i in self.selected.getAll():
            data = (i.kcmc, i.xf, i.teaxm, i.pkrs, i.jxbrs, i.kcflmc)
            gui.frame_configure.listctrl_selected.Append(data)


    def __getUserCourse__(self, page):
        data = {
            'zc': '',   # 全部周
            'xnxqdm': self.season_code.getCode(self.season_code.selected_index),
            'page': page,
            'rows': 100,
            'sort': 'pkrq', # 排课日期
            'order': 'asc'
        }

        raw, res = self.urlop.request(url=USER_COURSE_URL, max_retry=2, branch_num=1, method='POST', data=data)

        text = bytes.decode(raw) if isinstance(raw, bytes) else raw

        try:
            course_raw = json.loads(text)
        except json.JSONDecodeError as e:
            raise PullerBasicException(self.user, text, e)

        return course_raw



class Taker(UrlRequestOp):
    def __init__(self, user):
        UrlRequestOp.__init__(self)
        self.user = user

        self.counter = 0

        self.stop_flag = False

        self.puller = Puller(self.user, self)

    def run(self):
        self.user.status = Pool.TAKING
        self.counter += 1

        try:
            self.__run__()
        except TakerBasicException as e:
            traceback.print_exc()
        except UrlOpTimeOutError as e:
            traceback.print_exc()

    def __run__(self):

        if not self.puller.optional.getAll():
            self.puller.pullCourses()

        targets = self.getTargets()
        self.user.set_MemberView_Target(targets)
        if not targets:
            self.puller.pullCourses()

            targets = self.getTargets()
            self.user.set_MemberView_Target(targets)

            if not targets:
                self.user.op.done()
                return

        if self.user.force_post or self.isAvl():
            self.take()
        else:
            if not self.isStop():
                self.timingRun()
            else:
                self.getStop()

    def timingRun(self):
        self.user.status = Pool.TIMING_TAKE
        sec = delayer.timingRun(self.user, self.user.op.takeCourse, self.user.delay_range)
        self.user.set_MemberView_Timing(sec)

    def take(self):
        for i in self.getTargets():
            llogger.normal(self.user.account, '开始选课: [%s]' % i.__str__())
            res = self.postAdd(i)

            if res == '1':
                self.succeed(i)
                llogger.ok(self.user.account, '选课成功: [%s]' % i.__str__(), res)
            else:
                raise TakerBasicException(self.user, res, course=i)

    def stop(self):
        llogger.normal(self.user.account, '开始中止选课。')
        self.stop_flag = True
        if delayer.cancelTiming(self.user):
            self.getStop()

    def isStop(self):
        return self.stop_flag

    def getStop(self):
        self.stop_flag = False
        self.user.status = Pool.READY
        llogger.ok(self.user.account, '选课中止成功。')
        self.user.set_MemberView_Timing(-1)

    def postAdd(self, course):
        data = {
            # 'jxbdm': course.jxbdm,
            # 'jxbrs': course.jxbrs,
            # 'kcdm': course.kcdm,
            # 'kcflmc': course.kcflmc,
            'kcmc': course.kcmc,
            # 'kcptdm': course.kcptdm,
            'kcrwdm': course.kcrwdm,
            # 'kkxqdm': course.kkxqdm,
            # 'pkrs': course.pkrs,
            # 'rs1': course.rs1,
            # 'rs2': course.rs2,
            # 'rwdm': course.rwdm,
            # 'teaxm': course.teaxm,
            # 'wyfjdm': course.wyfjdm,
            # 'xbyqdm': course.xbyqdm,
            # 'xf': course.xf,
            # 'xmmc': course.xmmc,
            # 'zxs': course.zxs
        }
        raw, res = self.request(url=ADD_COURSE_URL, data=data, method='POST', branch_num=1, max_retry=-1)
        text = bytes.decode(raw) if isinstance(raw, bytes) else raw

        return text

    def postCancel(self, course):
        llogger.normal(self.user.account, '开始退选: [%s]' % course.__str__())

        data = {
            'jxbdm': course.jxbdm,
            'kcrwdm': course.kcrwdm,
            'kcmc': course.kcmc

        }

        raw, res = self.request(url=CANCEL_COURSE_URL, data=data, method='POST', branch_num=0, max_retry=3)
        text = bytes.decode(raw) if isinstance(raw, bytes) else raw
        try:
            if int(text) > 0:
                llogger.ok(self.user.account, '退选成功: [%s]' % course.__str__(), text)
                return True
            else:
                llogger.error(self.user.account, '退选失败: [%s]' % course.__str__(), text)
                return False
        except ValueError as e:
            raise TakerBasicException(self.user, text, e)

    def getTargets(self):
        targets = self.puller.optional[self.user.keys]
        tmp = targets[:]
        for i in tmp:
            if self.puller.selected.hasCourse(i):
                targets.remove(i)

        return targets

    def isAvl(self):

        raw, res = self.request(url=FOO_JS_URL, branch_num=1, max_retry=-1, method='GET')

        text = bytes.decode(raw) if isinstance(raw, bytes) else raw

        if KEYWORD_TAKE_FOO in text:
            return True
        else:
            if '请输入验证码' in text:
                self.user.op.login()
                return False
            elif '不是选课时间' in text:
                return False

            return

    def succeed(self, course):
        self.user.success_counter += 1
        if not self.puller.selected.hasCourse(course):
            self.puller.selected.append(course)
        if not self.getTargets():
            self.user.op.done()


def getItemsFromKey(key, iter_list):
    items = []
    for i in iter_list:
        if key in i.row:
            items.append(i)

    return items


class CoursePool(object):
    def __init__(self):
        self.infos = []
        self.total = 0

    def __getitem__(self, keys):

        keys = keys.split('|')
        key_and = []
        for i in keys:
            key_and.append(i.split(','))

        ret = []
        for i in key_and:
            matchs = self.infos
            for j in i:
                matchs = getItemsFromKey(j, matchs)

            ret.extend(matchs)

        return ret

    def extract(self, raw_json=None, rows=None):
        if raw_json:
            rows = json.loads(raw_json)  # courses list

        for i in rows:
            self.infos.append(CourseItem(i))
            self.total += 1

    def getAll(self):
        return self.infos

    def append(self, item):
        self.infos.append(item)
        self.total += 1

    def remove(self, object):
        self.infos.remove(object)
        self.total -= 1

    def hasCourse(self, course):
        for i in self.infos:
            if course.kcdm == i.kcdm:
                return True
        else:
            return False

    def __str__(self):
        info_list = []
        for i in self.infos:
            info_list.append(i.__str__())
        return '\n'.join(info_list)


    def pack(self):
        return json.dumps({'total': self.total, 'rows': self.infos})


class CourseItem(object):
    def __init__(self, row):
        # self.row = json.dumps()
        self.row = str(row)
        self.jxbdm = row.get('jxbdm')
        self.jxbrs = row.get('jxbrs')
        self.kcdm = row.get('kcdm')
        self.kcflmc = row.get('kcflmc')
        self.kcmc = row.get('kcmc')
        self.kcptdm = row.get('kcptdm')
        self.kcrwdm = row.get('kcrwdm')
        self.kkxqdm = row.get('kkxqdm')
        self.pkrs = row.get('pkrs')
        self.rs1 = row.get('rs1')
        self.rs2 = row.get('rs2')
        self.rwdm = row.get('rwdm')
        self.teaxm = row.get('teaxm')
        self.wyfjdm = row.get('wyfjdm')
        self.xbyqdm = row.get('xbyqdm')
        self.xf = row.get('xf')
        self.xmmc = row.get('xmmc')
        self.zxs = row.get('zxs')

        self.dgksdm = row.get('dgksdm')
        self.flfzmc = row.get('flfzmc')
        self.jcdm = row.get('jcdm')

        self.jxbmc = row.get('jxbmc')
        self.jxcdmc = row.get('jxcdmc')
        self.jxhjmc = row.get('jxhjmc')
        self.kxh = row.get('kxh')
        self.pkrq = row.get('pkrq')
        self.rownum_ = row.get('rownum_')

        self.sknrjj = row.get('sknrjj')
        self.teaxms = row.get('teaxms')
        self.xq = row.get('xq')
        self.zc = row.get('zc')




    def __str__(self):
        return '%s - %s' % (self.kcmc, self.teaxm if self.teaxm else self.teaxms)
