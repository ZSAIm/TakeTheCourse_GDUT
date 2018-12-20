import tensorflow as tf
from PIL import Image
import inference
import numpy as np


INPUT_NODE = 60*140
OUTPUT_NODE = 4*24
IMAGE_HEIGHT = 60
IMAGE_WIDTH = 140
CAPTCHA_LEN = 4
CHARS_LEN = 24
# THRESHOLE = 120

MODEL_PATH_NAME = 'models/model.ckpt'
CHARS_SET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'k', 'm', 'n', 'p', 'q', 's', 'u', 'w', 'x',
             'y', '2', '3', '4', '5', '6', '7', '8']

class CrackCaptcha:
    def __init__(self):
        tf.reset_default_graph()
        self.Sess, self.Input, self.Output = load_tf_model()

    def run(self, fp):
        imgsrc = load_image(fp)
        preprocess(imgsrc)
        imgsrc = np.reshape(imgsrc, [-1, IMAGE_HEIGHT, IMAGE_WIDTH, 1])
        predict = self.Sess.run(self.Output, feed_dict={self.Input: imgsrc})
        res = []
        for i in predict:
            res.append(onehot_to_chars(i))
        return res

    def __del__(self):
        # print('session close')
        self.Sess.close()

def load_image(fp):
    imgsrc = Image.open(fp).convert('L')
    return imgsrc

def preprocess(imgsrc):
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



def onehot_to_chars(onehot):
    _chars = ''
    for m in np.argmax(onehot, axis=1):
        _chars += CHARS_SET[m]
    return _chars

def load_tf_model():
    with tf.device('/cpu:0'):
        _input = tf.placeholder(tf.float32, [None, IMAGE_HEIGHT, IMAGE_WIDTH, 1])
        _output = inference.inference(_input, False)

        _output = tf.reshape(_output, [-1, CAPTCHA_LEN, CHARS_LEN])
        saver = tf.train.Saver()
    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
    saver.restore(sess, MODEL_PATH_NAME)

    return sess, _input, _output





# tf.reset_default_graph()
# Sess, Input, Output = load_tf_model()
