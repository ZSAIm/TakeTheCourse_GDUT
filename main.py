# -*- coding: utf-8 -*-

# author: ZSAIm
# github: https://github.com/ZSAIm/TakeTheCourse_GDUT
# 				programming by python3.5


import threading
import llogger
import time
import sys
import os
import gui
from handler.Pool import UserPool
import captcha.killer
import GUIEventBinder

pool = None


def init_model():
    llogger.normal('NULL', '开始加载验证码识别模型。')
    try:
        captcha.killer.init()
    except:
        llogger.error('NULL', '识别模型加载失败。')
    else:
        llogger.ok('NULL', '识别模型加载成功。')

def init_dir():
    if not os.path.exists('logs') or os.path.isfile('logs'):
        os.mkdir('logs')
    if not os.path.exists('cookies') or os.path.isfile('cookies'):
        os.mkdir('cookies')

def __main__():
    global pool
    init_dir()
    init_model()
    pool = UserPool()
    GUIEventBinder.init(pool)


def main():
    threading.Thread(target=__main__).start()


if __name__ == '__main__':
    gui.init()
    main()
    gui.MainLoop()

    llogger.export('logs/%s.log' % time.asctime(time.localtime()).replace(':', '-'))
    pool.exit()
    sys.exit()

