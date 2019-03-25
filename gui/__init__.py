

import wx
import gui.frame.main
import gui.frame.configure
from gui.frame.about import About_Dialog

frame_main = None
frame_configure = None

app = None



def init():
    global frame_main, frame_configure, app
    app = wx.App(False)
    frame_main = gui.frame.main.FrameMain(None)
    frame_configure = gui.frame.configure.FrameConfigure(frame_main)

    frame_main.Show(True)


def MainLoop():
    global app
    app.MainLoop()