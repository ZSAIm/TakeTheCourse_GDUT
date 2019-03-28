
import wx
from gui.listctrl.basic_listctrl import BasicListCtrl

class Selected_ListCtrl(BasicListCtrl):
    def __init__(self, *args):
        wx.ListCtrl.__init__(self, *args)
        self.SetMinSize(wx.Size(500, 100))

        self.menu = None
        self.initMenu()
        self.initSelectedColumn()

    def initMenu(self):
        self.menu = Selected_Menu()

        self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)

    def OnContextMenu(self, event):
        self.PopupMenu(self.menu, event.GetPosition())

    def initSelectedColumn(self):
        self.ClearAll()
        self.AppendColumn('课程名称', format=wx.LIST_FORMAT_CENTER, width=130)
        self.AppendColumn('学分', format=wx.LIST_FORMAT_CENTER, width=45)
        self.AppendColumn('教师', format=wx.LIST_FORMAT_CENTER, width=55)
        self.AppendColumn('限选', format=wx.LIST_FORMAT_CENTER, width=45)
        self.AppendColumn('已选', format=wx.LIST_FORMAT_CENTER, width=45)
        self.AppendColumn('课程分类', format=wx.LIST_FORMAT_CENTER, width=100)



class Selected_Menu(wx.Menu):
    def __init__(self, *args):
        wx.Menu.__init__(self, *args)

        # self.view = None
        # self.configure = None
        # self.add = None
        self.delete = None

        self.initItems()

    def initItems(self):
        # self.view = wx.MenuItem(self, wx.ID_ANY, u'View', wx.EmptyString, wx.ITEM_NORMAL)
        # self.Append(self.view)
        #
        # self.configure = wx.MenuItem(self, wx.ID_ANY, u'Configure', wx.EmptyString, wx.ITEM_NORMAL)
        # self.Append(self.configure)
        #
        # self.AppendSeparator()
        #
        # self.add = wx.MenuItem(self, wx.ID_ANY, u'Add', wx.EmptyString, wx.ITEM_NORMAL)
        # self.Append(self.add)
        #
        # self.AppendSeparator()

        self.delete = wx.MenuItem(self, wx.ID_ANY, u'Delete', wx.EmptyString, wx.ITEM_NORMAL)
        self.Append(self.delete)
