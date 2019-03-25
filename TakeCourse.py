import urllib.request
import urllib.parse
import json
from UrlOp import UrlOp
import math
import logging
import time, os

OPTIONAL_COURSE = 'http://jxfw.gdut.edu.cn/xsxklist!getDataList.action'
SELECTED = 'http://jxfw.gdut.edu.cn/xsxklist!getXzkcList.action'
FOO_JS = 'http://jxfw.gdut.edu.cn/xsxklist!xsmhxsxk.action'
TAKE = 'http://jxfw.gdut.edu.cn/xsxklist!getAdd.action'
TAKE_FOO_KEY = 'xsxklist!getAdd.action'





# OPTIONAL_COURSE = 'http://222.200.98.146/xsxklist!getDataList.action'
# SELECTED = 'http://222.200.98.146/xsxklist!getXzkcList.action'
# FOO_JS = 'http://222.200.98.146/xsxklist!xsmhxsxk.action'
# TAKE_FOO_KEY = 'xsxklist!getAdd.action'
# TAKE = 'http://222.200.98.146/xsxklist!getAdd.action'


PAGE_NUMBER = 150
MAX_RETRIES = 5
WAIT_TIME = 0.1

NO_RESPOND = 'no'
REQUEST_TIMEOUT = 'timeout'
RESPOND_SUCCESS = 'ok'

MAX_TAKE_RETRIES = 5

class TakeCourse:

    def __init__(self, op, keys):
        self.op = op
        self.keys = keys
        # self.opener = opener
        # self.cookiejar = cookiejar
        self.selected = Courses()
        self.optional = Courses()
        self.course_num = 0
        self.retries = 0
        self.relogin = False
        self.permission = False
        self.wait_retake = False
        # self.id = self.op.ip

    def get_optional_course(self, page):

        data = {
            'page': page,
            'rows': PAGE_NUMBER,
            'sort': 'kcrwdm',
            'order': 'asc'
        }
        raw, _ = self.op.request(OPTIONAL_COURSE, data, method='POST')

        try:
            res_json = json.loads(str(raw, encoding='utf-8'))
            return res_json['rows'], res_json['total']
        except:
            if '请输入验证码' in str(raw):
                self.relogin = True
                return None, None
            self.retries += 1
            if self.retries >= MAX_RETRIES:
                return None, None
            time.sleep(WAIT_TIME)
            return self.get_optional_course(page)
        finally:
            self.retries = 0

    def get_selected_course(self):
        self.selected = Courses()
        data = {
            'sort': 'kcrwdm',
            'order': 'asc'
        }
        raw, res = self.op.request(SELECTED, data, method='POST')
        # print(res.info()['Content-Type'])
        if not raw:
            return None
        try:
            res_json = json.loads(str(raw, encoding='utf-8'))
            return res_json
        except:
            if '请输入验证码' in str(raw, encoding='utf-8'):
                self.relogin = True
                return None
            self.retries += 1
            if self.retries >= MAX_RETRIES:
                return None
            time.sleep(WAIT_TIME)
            return self.get_selected_course()
        finally:
            self.retries = 0

    def take(self, course_info):
        logging.info('[%s] - taking "%s"' % (self.op.id, course_info.kcmc))
        data = {
            # 'jxbdm': course_info.jxbdm,
            # 'jxbrs': course_info.jxbrs,
            # 'kcdm': course_info.kcdm,
            # 'kcflmc': course_info.kcflmc,
            'kcmc': course_info.kcmc,
            # 'kcptdm': course_info.kcptdm,
            'kcrwdm': course_info.kcrwdm,
            # 'kkxqdm': course_info.kkxqdm,
            # 'pkrs': course_info.pkrs,
            # 'rs1': course_info.rs1,
            # 'rs2': course_info.rs2,
            # 'rwdm': course_info.rwdm,
            # 'teaxm': course_info.teaxm,
            # 'wyfjdm': course_info.wyfjdm,
            # 'xbyqdm': course_info.xbyqdm,
            # 'xf': course_info.xf,
            # 'xmmc': course_info.xmmc,
            # 'zxs': course_info.zxs
        }
        raw, res = self.op.request(TAKE, data, method='POST', branch=2)
        if not raw:
            return None
        try:
            text = str(raw, encoding='utf-8')

            if '1' == text:
                return True, '选课成功'
            elif '超出' in text:
                return False, text
            elif '选了' in text:
                return True, text
            elif '没有开设该课程' in text:
                return False, text
            elif '请输入验证码' in text:
                self.relogin = True
                return False, 'relogin'
            elif '不是选课时间' in text:
                return False, text
            else:
                return False, text

            # res_json = json.loads(str(raw, encoding='utf-8'))
            # return res_json
        except:
            if '找不到' in str(raw, encoding='utf-8'):
                return False, '找不到页面'
            self.retries += 1
            if self.retries >= MAX_RETRIES:
                return False, None
            time.sleep(WAIT_TIME)
            return self.take(course_info)
            # return None, str(raw, encoding='utf-8')
        finally:
            self.retries = 0

    def get_courses_data(self):
        self.selected = Courses()
        self.optional = Courses()
        _page = 1
        _count = 1
        while _count <= _page:
            raw_json, self.course_num = self.get_optional_course(_count)
            if raw_json is None:
                return False, NO_RESPOND
            _page = math.ceil(self.course_num / PAGE_NUMBER)
            if len(raw_json) == 0:
                break
            self.optional.append(raw_json)

            if self.course_num <= len(self.optional.infos):
                break
            _count += 1
        raw_json = self.get_selected_course()
        if raw_json is None:
            return False, NO_RESPOND
        self.selected.append(raw_json)

        return True, RESPOND_SUCCESS
    # def pre_run(self):
    #     self.get_courses_data()
    #     self.save_courses()

    def is_permission(self):
        raw, res = self.op.request(FOO_JS, branch=1)
        if not raw:
            return False
        text = str(raw, encoding='utf-8')
        # with open('log/%s.txt' % time.time(), 'w') as f:
        #     f.write(text)
        if '请输入验证码' in text:
            return False, 're-login'
        if TAKE_FOO_KEY in text:
            return True, 'ok'
        else:
            return False, 'not-allow'

    def run(self, force=False, safe=False):

        if os.path.exists('courses/%s.txt' % self.op.id) is False:
            logging.info('[%s] - (%s) - pulling courses...' % (self.op.id, self.op.proxy_info.real_ip))
            result, msg = self.get_courses_data()
            if result is True:
                self.save_courses()
            else:
                return False, msg
        else:
            if len(self.optional.infos) == 0:
                result, msg = self.load_courses()
                if result is False:
                    return False, msg
        if force is False:
            ret_msg, msg = self.is_permission()
            if msg == 're-login':
                self.relogin = True
                return False, msg
        else:
            ret_msg = True

        if ret_msg is False:
            logging.info('[%s] - (%s) - wait to re-take ...' % (self.op.id, self.op.proxy_info.real_ip))
            self.wait_retake = True
            return False, 'no-permission'

        logging.info('[%s] - (%s) - running take...' % (self.op.id, self.op.proxy_info.real_ip))
        target = self.optional[self.keys]
        # print(target)
        logging.info('[%s] - (%s) - taking course...' % (self.op.id, self.op.proxy_info.real_ip))
        # logging.info('[%s] - (%s) - taking course...' % (self.op.id, self.op.pool.proxy_op.origin.ip))
        # logging.info('[%s] - taking course ...' % (self.op.id))

        # target = self.optional[self.keys]
        # self.take(target)
        if not target:
            return False, 'no match target'

        success_flag = False
        while True:
            ret_result_msg = []
            for i in target:
                result, msg = self.take(i)
                ret_result_msg.append((result, msg))
                logging.info('[%s] - (%s) - take "%s" %s, msg: %s' % (self.op.id, self.op.proxy_info.real_ip,  i.xmmc, result, msg))
                if result is True:
                    if result is True:
                        success_flag = True
                else:
                    if '没有开设' in msg:
                        result1, msg1 = self.update_courses()
                        if result1 is True:
                            break
                        else:
                            break
                    elif '超出' in msg:
                        pass
                        # return False, ret_result_msg
                    elif '不是选课时间' in msg:
                        break
                    elif '找不到页面' in msg:
                        pass
                    elif 'relogin' in msg:
                        self.relogin = True
                        return False, ret_result_msg

            else:
                break
            continue

        if success_flag is True:
            return True, ret_result_msg
        else:
            return False, ret_result_msg

    def update_courses(self):
        if os.path.exists('courses/%s.txt' % self.op.id) is True:
            os.remove('courses/%s.txt' % self.op.id)
        result, msg = self.get_courses_data()
        if result is True:
            self.save_courses()
            return True, RESPOND_SUCCESS
        else:
            return False, msg

    def load_courses(self):

        self.optional = Courses()
        with open('courses/%s.txt' % self.op.id, 'r') as f:
            courses_row = f.read().replace('\'', '\"')
        try:
            self.optional.append(json.loads(courses_row))
            logging.info('[%s] - load courses done.' % self.op.id)
        except:
            return self.update_courses()

        return True, 'ok'

    def save_courses(self):
        # self.get_courses_data()
        if self.optional.rows != '':
            with open('courses/%s.txt' % self.op.id, 'w') as f:
                f.write(self.optional.rows)



class CourseInfo:
    def __init__(self, row):

        self.row = str(row)
        self.jxbdm = row['jxbdm']
        self.jxbrs = row['jxbrs']
        self.kcdm = row['kcdm']
        self.kcflmc = row['kcflmc']
        self.kcmc = row['kcmc']
        self.kcptdm = row['kcptdm']
        self.kcrwdm = row['kcrwdm']
        self.kkxqdm = row['kkxqdm']
        self.pkrs = row['pkrs']
        self.rs1 = row['rs1']
        self.rs2 = row['rs2']
        self.rwdm = row['rwdm']
        self.teaxm = row['teaxm']
        self.wyfjdm = row['wyfjdm']
        self.xbyqdm = row['xbyqdm']
        self.xf = row['xf']
        self.xmmc = row['xmmc']
        self.zxs = row['zxs']

    def __str__(self):
        return "{1:10}\t{2:{0}<20}\t{3:{0}<4}\t{4:{0}>3}/{5:{0}>3}".format(
            chr(12288), self.kcdm, self.kcmc[:20], self.teaxm[:4], self.jxbrs, self.pkrs)


class Courses:
    def __init__(self):
        self.rows = ''
        self.infos = []

    def __getitem__(self, keys):

        keys = keys.split('|')
        key_list = []
        for i in keys:
            key_list.append(i.split(','))

        ret = []
        for i in key_list:
            tmp = []
            for j in i:
                if j not in self.rows:
                    break
                else:
                    for k in self.infos:
                        if j in k.kcmc.lower() or j in k.teaxm.lower() or j in k.xmmc:
                            tmp.append(k)
            if len(i) > 1:
                for j in range(len(tmp) - 1):
                    if tmp[j] in tmp[j+1:]:
                        ret.append(tmp[j])
            else:
                ret.extend(tmp)

        return ret

    def append(self, rows):
        if self.rows != '':
            self.rows = '[' + self.rows[1:-1] + ', ' + str(rows)[1:-1] + ']'
        else:
            self.rows = '[' + str(rows)[1:-1] + ']'
        for i in rows:
            self.infos.append(CourseInfo(i))

    def __str__(self):
        info_list = []
        for i in self.infos:
            info_list.append(i.__str__())
        return '\n'.join(info_list)