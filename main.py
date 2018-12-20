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