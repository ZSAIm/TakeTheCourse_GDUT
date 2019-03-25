

import wx
from gui.listctrl.basic_listctrl import BasicListCtrl

class Logs_ListCtrl(BasicListCtrl):
    def __init__(self, *args):
        wx.ListCtrl.__init__(self, *args)

        self.initColumn()

    def initColumn(self):

        self.AppendColumn('Time', format=wx.LIST_FORMAT_CENTER, width=80)
        self.AppendColumn('Account', format=wx.LIST_FORMAT_CENTER, width=85)
        self.AppendColumn('SystemMsg', width=240, format=wx.LIST_FORMAT_LEFT)
        self.AppendColumn('ServerMsg', width=100, format=wx.LIST_FORMAT_LEFT)


    def Append(self, entry, fgcolor=None):
        BasicListCtrl.Append(self, entry, fgcolor)
        self.ScrollLines(5)


