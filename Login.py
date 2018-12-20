import urllib.request
import urllib.parse
import time

from io import BytesIO
import execjs
import json
import logging
import xlrd


CAPTCHA_URL = 'http://jxfw.gdut.edu.cn/yzm?d=%d'
POST_LOGIN = 'http://jxfw.gdut.edu.cn/new/login'
ENCRYPT_JS = 'http://jxfw.gdut.edu.cn/static/js/aes.js'

# CAPTCHA_URL = 'http://222.200.98.146/yzm?d=%d'
# POST_LOGIN = 'http://222.200.98.146/new/login'
# ENCRYPT_JS = 'http://222.200.98.146/static/js/aes.js'


# http://222.200.98.146/
MAX_RETRIES = 3
WAIT_TIME = 0.1

class UserData:
    def __init__(self):
        self.__data_list = []
        pass

    def load(self):
        self.__data_list = []
        filename = 'userdata.xlsx'
        book = xlrd.open_workbook(filename)
        sheet0 = book.sheet_by_index(0)
        table_head = sheet0.row_values(0)
        for i in range(1, sheet0.nrows):
            self.__data_list.append(sheet0.row_values(i))

    def get_userdata(self):
        ret = []
        for i in self.__data_list:
            tmp = []
            for j in i:
                if isinstance(j, float) is True:
                    # i0 = int(j)
                    tmp.append(str(int(j)))
                else:
                    tmp.append(str(j))

            ret.append(tmp)

        return ret


class Login:
    def __init__(self, op, account, password):
        self.account = account
        self.op = op
        self.password = password

    def run(self):
        # logging.info('[%s] - getting captcha image ...' % self.op.id)
        verifycode_fp = BytesIO()
        ret_img = self.get_verifycode_img()
        if ret_img is None:
            return None
        verifycode_fp.write(ret_img)
        verifycode = self.op.pool.crack_captcha.run(verifycode_fp)[0]
        pwd_encrypt = self.encrypt(self.password, verifycode)

        return self.post_login(self.account, pwd_encrypt, verifycode)

    def get_verifycode_img(self):
        raw, res = self.op.request(CAPTCHA_URL % (time.time() * 1000), method='GET', branch=2, independent=True)
        if raw is None:
            return None
        if 'image' not in res.info()['Content-Type']:
            self.op.proxy_invalid = True
            logging.error('[%s] - (%s) - IP Forbidden' % (self.op.id, self.op.proxy_info.real_ip))

            return None
            # raise ConnectionAbortedError

        return raw

    def post_login(self, account, pwd_encrypt, verifycode):
        data = {
            'account': account,
            'pwd': pwd_encrypt,
            'verifycode': verifycode
        }

        raw, _ = self.op.request(POST_LOGIN, data, method='POST', branch=0)
        if not raw:
            return None
        try:
            res_json = json.loads(str(raw, encoding='utf-8'))
            return res_json
        except:
            self.op.proxy_invalid = True
            return None
        finally:
            self.retries = 0



    def encrypt(self, psw, verifycode):
        global ctx
        return ctx.call('get_encrypt_pwd', psw, verifycode)


jscontext = ''
js_extension = """
function get_encrypt_pwd(password, verifycode){
    var key = CryptoJS.enc.Utf8.parse(verifycode+verifycode+verifycode+verifycode);
    var srcs = CryptoJS.enc.Utf8.parse(password);
    var encrypted = CryptoJS.AES.encrypt(srcs, key, {mode:CryptoJS.mode.ECB,padding: CryptoJS.pad.Pkcs7});
    password = encrypted.ciphertext.toString();
    return password		
}
"""

def update_encrypt_js():
    global jscontext
    res = urllib.request.urlopen(ENCRYPT_JS)
    jscontext = res.read()
    jscontext += js_extension



try:
    with open('aes.js', 'r') as f:
        jscontext = f.read()
    jscontext += js_extension

    ctx = execjs.compile(jscontext)
except:
    update_encrypt_js()
