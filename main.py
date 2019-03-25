<<<<<<< HEAD


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

=======
import time
import logging
import PoolOp
import cProfile
import Login

# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

logging.basicConfig(level=logging.DEBUG,
                    filename='log/all/log-%s.log' % time.strftime('[%Y-%m-%d]', time.localtime()),
                    format='%(asctime)s - %(levelname)s: %(message)s'
                    )

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def main():
    logging.info('initialize runing ...')
    pool = PoolOp.PoolOp()
    pool.proxy_op.collect()
    pool.proxy_op.save()
    # pool.init_proxy()
    # pool.proxy_op.load()
    #
    #
    logging.info('initialize done.')
    user_op = Login.UserData()
    user_op.load()
    user = user_op.get_userdata()
    for i in user:
        pool.build_member(i[0], i[1], i[2])

    pool.batch_run()
    while True:
        if pool.isEnd() is True:
            break
        time.sleep(1)

    pool.batch_verify()



if __name__ == '__main__':
    main()
>>>>>>> origin/master
