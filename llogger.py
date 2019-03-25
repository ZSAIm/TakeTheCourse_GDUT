

import time, threading
import gui
import json


OK = 0
ERROR = 1
WARNING = 2
NORMAL = 3

append_lock = threading.Lock()

logs_msg = []

def get_ctime():
    return '%s.%03d' % (time.strftime('%H:%M:%S', time.localtime()), int(time.time() % 1 * 1000))


def ok(*entry):
    global append_lock, OK
    with append_lock:
        msg = (get_ctime(), *entry)
        logs_msg.append((OK, *msg))
        gui.frame_main.listctrl_logs.Append(msg, (0, 0, 255, 255))


def error(*entry):
    global append_lock, ERROR
    with append_lock:
        msg = (get_ctime(), *entry)
        logs_msg.append((ERROR, *msg))
        gui.frame_main.listctrl_logs.Append(msg, (255, 0, 0, 255))


def normal(*entry):
    global append_lock, NORMAL
    with append_lock:
        msg = (get_ctime(), *entry)
        logs_msg.append((NORMAL, *msg))
        gui.frame_main.listctrl_logs.Append(msg)


def warning(*entry):
    global append_lock, WARNING
    with append_lock:
        msg = (get_ctime(), *entry)
        logs_msg.append((WARNING, *msg))
        gui.frame_main.listctrl_logs.Append(msg, (0, 128, 0, 255))


def export(file):
    global logs_msg

    with open(file, 'w') as f:
        f.write(json.dumps(logs_msg))

