
import wx
from gui.listctrl.basic_listctrl import BasicListCtrl

STYLE_OPTIONAL = 0
STYLE_USER_COURSE = 1

class Optional_ListCtrl(BasicListCtrl):
    def __init__(self, *args):
        wx.ListCtrl.__init__(self, *args)
        self.SetMinSize(wx.Size(500, 400))

        # self.menu = None
        # self.initMenu()
        # self.initUserCourseColumn()
        self.initOptionColumn()

        self.style = STYLE_OPTIONAL

    def initOptionColumn(self):
        self.style = STYLE_OPTIONAL
        self.ClearAll()
        self.AppendColumn('课程名称', format=wx.LIST_FORMAT_CENTER, width=130)
        self.AppendColumn('学分', format=wx.LIST_FORMAT_CENTER, width=45)
        self.AppendColumn('教师', format=wx.LIST_FORMAT_CENTER, width=55)
        self.AppendColumn('限选', format=wx.LIST_FORMAT_CENTER, width=45)
        self.AppendColumn('已选', format=wx.LIST_FORMAT_CENTER, width=45)
        self.AppendColumn('课程分类', format=wx.LIST_FORMAT_CENTER, width=100)


    def initUserCourseColumn(self):
        self.style = STYLE_USER_COURSE
        self.ClearAll()
        self.AppendColumn('课程名称', format=wx.LIST_FORMAT_CENTER, width=100)
        self.AppendColumn('班级名称', format=wx.LIST_FORMAT_CENTER, width=60)
        self.AppendColumn('人数', format=wx.LIST_FORMAT_CENTER, width=40)
        self.AppendColumn('教师', format=wx.LIST_FORMAT_CENTER, width=60)
        self.AppendColumn('周次', format=wx.LIST_FORMAT_CENTER, width=38)
        self.AppendColumn('星期', format=wx.LIST_FORMAT_CENTER, width=38)
        self.AppendColumn('节次', format=wx.LIST_FORMAT_CENTER, width=60)
        self.AppendColumn('上课地点', format=wx.LIST_FORMAT_CENTER, width=70)
        self.AppendColumn('排课日期', format=wx.LIST_FORMAT_CENTER, width=80)
        self.AppendColumn('课序', format=wx.LIST_FORMAT_CENTER, width=38)
        self.AppendColumn('类型', format=wx.LIST_FORMAT_CENTER, width=60)
        self.AppendColumn('授课内容简介', format=wx.LIST_FORMAT_LEFT, width=200)


    # def initMenu(self):
    #     self.menu = Optional_Menu()
    #
    #     self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)

#     def OnContextMenu(self, event):
#         self.PopupMenu(self.menu, event.GetPosition())
#
#
# class Optional_Menu(wx.Menu):
#     def __init__(self, *args):
#         wx.Menu.__init__(self, *args)
#
#         self.view = None
#         self.add = None
#         self.delete = None
#
#         self.initItems()
#
#     def initItems(self):
#         self.view = wx.MenuItem(self, wx.ID_ANY, u'View', wx.EmptyString, wx.ITEM_NORMAL)
#         self.Append(self.view)
#
#         self.AppendSeparator()
#
#         self.add = wx.MenuItem(self, wx.ID_ANY, u'Add', wx.EmptyString, wx.ITEM_NORMAL)
#         self.Append(self.add)
#
#         # self.AppendSeparator()
#
#         self.delete = wx.MenuItem(self, wx.ID_ANY, u'Delete', wx.EmptyString, wx.ITEM_NORMAL)
#         self.Append(self.delete)
#
