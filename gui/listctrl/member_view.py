
import wx
from gui.listctrl.basic_listctrl import BasicListCtrl
import gui

# MENU_STYLE_ALL = 0
MENU_STYLE_DIS_LOGIN = 1
MENU_STYLE_TAKE_TO_STOP = 2




class MemberView_ListCtrl(BasicListCtrl):
    def __init__(self, *args):
        wx.ListCtrl.__init__(self, *args)
        self.SetMinSize(wx.Size(-1, 300))

        self.menu = None
        self.initMenu()
        self.initColumn()

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.updateMenuText, self)

    def initColumn(self):

        self.AppendColumn('', format=wx.LIST_FORMAT_CENTER, width=20)
        self.AppendColumn('Account', format=wx.LIST_FORMAT_CENTER, width=85)
        self.AppendColumn('Status', width=70, format=wx.LIST_FORMAT_CENTER)

        self.AppendColumn('Online', width=50, format=wx.LIST_FORMAT_CENTER)
        self.AppendColumn('Target', width=50, format=wx.LIST_FORMAT_CENTER)
        self.AppendColumn('Delay', width=58, format=wx.LIST_FORMAT_CENTER)

        self.AppendColumn('LastUpdateTime', width=166, format=wx.LIST_FORMAT_CENTER)

        # self.AppendColumn('Now', width=100, format=wx.LIST_FORMAT_CENTER)

    def Append(self, entry, fgcolor=None):
        BasicListCtrl.Append(self, (self.GetItemCount()+1, *entry), fgcolor)

    def initMenu(self):
        self.menu = MemberView_Menu()
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)

    def updateMenuText(self, event=None):
        cur_selected = self.GetFirstSelected()
        if cur_selected != -1:
            cur_item_status = self.GetItem(cur_selected, 2).Text
            if cur_item_status == '选课中' or cur_item_status == '延时中':
                self.menu.login.Enable(False)
                self.menu.take.SetText('Stop')
                self.menu.take.Enable(True)

                gui.frame_main.menu_bar.operation.login.Enable(False)
                gui.frame_main.menu_bar.operation.take.SetText('&Stop\tF4')
                gui.frame_main.menu_bar.operation.take.Enable(True)
            elif cur_item_status == '完成':
                self.menu.login.Enable(True)
                self.menu.take.SetText('Take')
                self.menu.take.Enable(False)

                gui.frame_main.menu_bar.operation.login.Enable(True)
                gui.frame_main.menu_bar.operation.take.SetText('&Take\tF4')
                gui.frame_main.menu_bar.operation.take.Enable(False)
            else:
                self.menu.login.Enable(True)
                self.menu.take.SetText('Take')
                self.menu.take.Enable(True)

                gui.frame_main.menu_bar.operation.login.Enable(True)
                gui.frame_main.menu_bar.operation.take.SetText('&Take\tF4')
                gui.frame_main.menu_bar.operation.take.Enable(True)


    def OnContextMenu(self, event):
        self.updateMenuText(event)

        self.PopupMenu(self.menu, event.GetPosition())



class MemberView_Menu(wx.Menu):
    def __init__(self, *args):
        wx.Menu.__init__(self, *args)

        self.view = None
        self.configure = None
        self.login = None
        self.take = None
        # self.add = None
        self.verify = None
        self.delete = None

        self.initItems()


    def initItems(self):
        self.view = wx.MenuItem(self, wx.ID_ANY, u'View', wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.view)

        self.configure = wx.MenuItem(self, wx.ID_ANY, u'Configure', wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.configure)

        self.AppendSeparator()

        self.login = wx.MenuItem(self, wx.ID_ANY, u'Login', wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.login)

        self.take = wx.MenuItem(self, wx.ID_ANY, u'Take', wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.take)

        self.AppendSeparator()

        self.verify = wx.MenuItem(self, wx.ID_ANY, u'Verify', wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.verify)

        self.AppendSeparator()

        self.delete = wx.MenuItem(self, wx.ID_ANY, u'Delete', wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.delete)


