
import tensorflow as tf
from captcha import inference
from PIL import Image
import numpy as np

IMG_HEIGHT = 60
IMG_WIDTH = 140

INPUT_NODE = IMG_HEIGHT * IMG_WIDTH

MODEL_PATH_NAME = 'model/model.ckpt'

CAPTCHA_CHARS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'k', 'm', 'n', 'p', 'q', 's', 'u', 'w', 'x',
             'y', '2', '3', '4', '5', '6', '7', '8']

CAPTCHA_CHARS_NUM = len(CAPTCHA_CHARS)
CAPTCHA_LEN = 4

OUTPUT_NODE = CAPTCHA_LEN * CAPTCHA_CHARS_NUM


INPUT_SHAPE = [-1, IMG_HEIGHT, IMG_WIDTH, 1]
OUTPUT_SHAPE = [-1, CAPTCHA_LEN, CAPTCHA_CHARS_NUM]


__Killer__ = None

def init():
    global __Killer__
    if not __Killer__:
        __Killer__ = CaptchaKiller()
        __Killer__.loadModel()
    return __Killer__


def get(f):
    return __Killer__.run(f)[0]


class CaptchaKiller(object):
    def __init__(self):
        tf.reset_default_graph()
        self.session = None
        self.input_holder = None
        self.output_node = None

        self.cur_imgsrc = None

    def run(self, f):
        self.__loadImg__(f)
        self.__imgProcess__()

        reshape_img = np.reshape(self.cur_imgsrc, INPUT_SHAPE)
        predict = self.session.run(self.output_node, feed_dict={self.input_holder: reshape_img})

        res = []
        for i in predict:
            res.append(onehot_to_chars(i))

        return res


    def loadModel(self):
        with tf.device('/cpu:0'):
            self.input_holder = tf.placeholder(tf.float32, [None, IMG_HEIGHT, IMG_WIDTH, 1])
            _output = inference.inference(self.input_holder, False)

            self.output_node = tf.reshape(_output, OUTPUT_SHAPE)

            saver = tf.train.Saver()

        self.session = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))

        saver.restore(self.session, MODEL_PATH_NAME)

    def __loadImg__(self, f):
        self.cur_imgsrc = Image.open(f)

    def __imgProcess__(self):
        imgsrc = self.cur_imgsrc.convert('L')

        imgpx = imgsrc.load()

        for i in range(0, imgsrc.height):
            for j in range(0, imgsrc.width):

                if imgpx[j, i] > 120:
                    imgpx[j, i] = 255
                else:
                    imgpx[j, i] = 0
        for i in range(2):
            for y in range(0, imgsrc.height):
                for x in range(0, imgsrc.width):
                    if imgpx[x, y] == 0:
                        if x - 1 < 0 or y - 1 < 0 or x + 1 >= imgsrc.width or y + 1 >= imgsrc.height:
                            imgpx[x, y] = 255
                            continue
                        count = 0
                        if imgpx[x + 1, y] == 255:
                            count += 1
                        if imgpx[x - 1, y] == 255:
                            count += 1
                        if imgpx[x, y + 1] == 255:
                            count += 1
                        if imgpx[x, y - 1] == 255:
                            count += 1
                        if count >= 3:
                            imgpx[x, y] = 255

        self.cur_imgsrc = imgsrc



def onehot_to_chars(onehot):
    _chars = ''
    for m in np.argmax(onehot, axis=1):
        _chars += CAPTCHA_CHARS[m]
    return _chars