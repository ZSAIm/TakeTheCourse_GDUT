# -*- coding: utf-8 -*-

import wx
from gui.listctrl.member_view import MemberView_ListCtrl
from gui.listctrl.logs import Logs_ListCtrl
import gui

class FrameMain(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u'GDUT教务系统助手', pos=wx.DefaultPosition, size=wx.Size(-1, -1), style=wx.DEFAULT_FRAME_STYLE|wx.FULL_REPAINT_ON_RESIZE|wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.Size(550, -1), wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

        self.sizer_global = wx.BoxSizer(wx.VERTICAL)
        self.sizer_global.SetMinSize(wx.Size(550, -1))

        self.listctrl_member = None
        self.init_MemberView_ListCtrl()

        self.listctrl_logs = None
        self.init_Logs_ListCtrl()

        self.SetSizer(self.sizer_global)
        self.Layout()

        self.status_bar = None
        self.init_StatusBar()

        self.sizer_global.Fit(self)

        self.menu_bar = FrameMain_MenuBar(0)
        self.SetMenuBar(self.menu_bar)

        self.Center(wx.BOTH)

    def init_StatusBar(self):
        self.status_bar = self.CreateStatusBar(10, wx.STB_SIZEGRIP, wx.ID_ANY)
        self.status_bar.SetStatusWidths([30, -1, 40, -1, 40, -1, 35, -1, 30, -6])
        self.status_bar.SetStatusText('Total', 0)
        self.status_bar.SetStatusText('Ready', 2)
        self.status_bar.SetStatusText('Taking', 4)
        self.status_bar.SetStatusText('Done', 6)
        self.status_bar.SetStatusText('', 8)

    def init_MemberView_ListCtrl(self):
        sizer_member = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u'MemberView'), wx.VERTICAL)
        self.listctrl_member = MemberView_ListCtrl(sizer_member.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition,
                                                        wx.Size(-1, 300),
                                                        wx.LC_SINGLE_SEL | wx.LC_REPORT | wx.HSCROLL | wx.VSCROLL)

        sizer_member.Add(self.listctrl_member, 0, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 5)

        self.sizer_global.Add(sizer_member, 0, wx.EXPAND, 5)

    def init_Logs_ListCtrl(self):
        sizer_logs = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Logs"), wx.VERTICAL)
        sizer_logs.SetMinSize(wx.Size(-1, 250))

        self.listctrl_logs = Logs_ListCtrl(sizer_logs.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                           wx.LC_REPORT | wx.FULL_REPAINT_ON_RESIZE)
        sizer_logs.Add(self.listctrl_logs, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 5)

        self.sizer_global.Add(sizer_logs, 0, wx.EXPAND, 5)



class FrameMain_MenuBar(wx.MenuBar):
    def __init__(self, *args):
        wx.MenuBar.__init__(self, *args)

        self.file = FrameMember_Menu_File()
        self.Append(self.file, u"File")

        self.edit = FrameMember_Menu_Edit()
        self.Append(self.edit, u'Edit')

        self.operation = FrameMember_Menu_Operation()
        self.Append(self.operation, u'Operation')

        self.help = FrameMember_Menu_Help()
        self.Append(self.help, u'Help')

    #     self.Bind(wx.EVT_MENU_OPEN, self.OnMenuOpen)
    #
    # def OnMenuOpen(self, event):
    #     listctrl_member_object = gui.frame_main.listctrl_member
    #     cur_selected = listctrl_member_object.GetFirstSelected()
    #     if cur_selected != -1:
    #         cur_item_status = listctrl_member_object.GetItem(cur_selected, 2).Text
    #         if cur_item_status == '选课中' or cur_item_status == '延时中':
    #             self.operation.login.Enable(False)
    #             self.operation.take.SetText('Stop')
    #         else:
    #             self.operation.login.Enable(True)
    #             self.operation.take.SetText('Take')


class FrameMember_Menu_File(wx.Menu):
    def __init__(self, *args):
        wx.Menu.__init__(self, *args)

        self.run = None
        self.save = None
        self.save_as = None

        self.import_ = None
        self.import_from_xlsx = None

        self.exit = None

        self.initItems()

    def initItems(self):
        self.run = wx.MenuItem(self, wx.ID_ANY, u"Run", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.run)

        self.AppendSeparator()

        self.save = wx.MenuItem(self, wx.ID_ANY, u"Save", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.save)
        self.save.Enable(False)

        self.save_as = wx.MenuItem(self, wx.ID_ANY, u"Save as", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.save_as)
        self.save_as.Enable(False)

        self.import_ = wx.Menu()
        self.import_from_xlsx = wx.MenuItem(self.import_, wx.ID_ANY, u"From xlsx", wx.EmptyString,
                                                 wx.ITEM_NORMAL)
        self.import_.Append(self.import_from_xlsx)
        self.AppendSubMenu(self.import_, u"Import")

        self.AppendSeparator()

        self.exit = wx.MenuItem(self, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.exit)



class FrameMember_Menu_Edit(wx.Menu):
    def __init__(self, *args):
        wx.Menu.__init__(self, *args)

        self.add = None
        self.delete = None
        self.delete_all = None

        self.initItems()

    def initItems(self):
        self.add = wx.MenuItem(self, wx.ID_ANY, u"Add", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.add)

        self.AppendSeparator()

        self.delete = wx.MenuItem(self, wx.ID_ANY, u"Delete", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.delete)

        self.delete_all = wx.MenuItem(self, wx.ID_ANY, u"Delete all", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.delete_all)
        self.delete_all.Enable(False)


class FrameMember_Menu_Operation(wx.Menu):
    def __init__(self, *args):
        wx.Menu.__init__(self, *args)

        self.login = None
        self.login_all = None

        self.take = None
        self.take_all = None

        self.verify = None
        self.verify_all = None

        self.initItems()



    def initItems(self):
        self.login = wx.MenuItem(self, wx.ID_ANY, u"&Login\tF3", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.login)

        self.login_all = wx.MenuItem(self, wx.ID_ANY, u"Login All", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.login_all)

        self.AppendSeparator()

        self.take = wx.MenuItem(self, wx.ID_ANY, u"&Take\tF4", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.take)

        self.take_all = wx.MenuItem(self, wx.ID_ANY, u"Take All", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.take_all)

        self.AppendSeparator()

        self.verify = wx.MenuItem(self, wx.ID_ANY, u"&Verify\tF5", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.verify)

        self.verify_all = wx.MenuItem(self, wx.ID_ANY, u"Verify All", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.verify_all)


class FrameMember_Menu_Help(wx.Menu):
    def __init__(self, *args):
        wx.Menu.__init__(self, *args)

        self.help = None
        self.about = None

        self.initItems()

    def initItems(self):
        self.help = wx.MenuItem(self, wx.ID_ANY, u"&Help", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.help)
        self.help.Enable(False)
        self.AppendSeparator()

        self.about = wx.MenuItem(self, wx.ID_ANY, u"&About", wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.about)

