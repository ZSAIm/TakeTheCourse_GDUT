
from core import encryptor
from handler import Pool
import gui
import time
from random import randint
import threading
import llogger

def get_cdatetime():
    return time.asctime(time.localtime())

class UserData(object):
    def __init__(self, account, password, keys, op):
        self.op = op
        self.account = account
        self.password = password

        self.post_data = {'account': self.account,
                          'pwd': None,
                          'verifycode': None}

        self.verifycode = None

        self.keys = keys

        self.status = None

        self.ready = False

        self.target_num = 0

        self.success_counter = 0

        self.delay_range = [1, 3]   # sec

        self.timer_refresh = 200

        self.force_post = False

        self.timing_thread = None

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)
        if key == 'verifycode' and self.verifycode is not None:
            pwd = encryptor.aes_cipher(self.verifycode*4, self.password)
            self.post_data.update({'pwd': pwd, 'verifycode': self.verifycode})
        elif key == 'status':
            if self.status:
                self.set_MemberView_Item()

    def setVerifyCode(self, verifycode):
        self.verifycode = verifycode

    def getPostData(self):
        return self.post_data

    def isReady(self):
        return self.ready

    def set_MemberView_Timing(self, sec):

        index = self.op.parent.getUserIndex(self)
        if sec == -1:
            gui.frame_main.listctrl_member.SetItem(index, 5, u'○')

        else:
            gui.frame_main.listctrl_member.SetItem(index, 5, str(int(sec*1000.0)))

            llogger.normal(self.account, '[%d ms]后尝试下一次选课。')



    def set_MemberView_Target(self, target):
        index = self.op.parent.getUserIndex(self)
        gui.frame_main.listctrl_member.SetItem(index, 4, str(len(target)))


    def set_MemberView_Item(self):
        cur_status = self.op.getStatus()
        index = self.op.parent.getUserIndex(self)
        gui.frame_main.listctrl_member.SetItem(index, 2, Pool.status2str(cur_status))
        if cur_status == Pool.UNREADY or cur_status == Pool.FAILURE:
            gui.frame_main.listctrl_member.SetItem(index, 3,  u'×')
        elif cur_status == Pool.LOGINNING:
            gui.frame_main.listctrl_member.SetItem(index, 3, u'○')
        else:
            gui.frame_main.listctrl_member.SetItem(index, 3, u'√')

        if cur_status == Pool.READY:
            gui.frame_main.listctrl_member.SetItem(index, 6, get_cdatetime())

        if cur_status == Pool.UNREADY or cur_status == Pool.READY:
            gui.frame_main.listctrl_member.SetItem(index, 4, u'○')

        gui.frame_main.listctrl_member.updateMenuText()

        if cur_status == Pool.DONE:
            gui.frame_main.listctrl_member.SetItem(index, 5, u'○')