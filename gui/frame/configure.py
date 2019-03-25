

import wx
from gui.listctrl.optional import Optional_ListCtrl
from gui.listctrl.selected import Selected_ListCtrl

class FrameConfigure(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Configure", pos=wx.DefaultPosition,
                           size=wx.Size(680, 600), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        self.sizer_global = wx.BoxSizer(wx.HORIZONTAL)

        self.sizer_left = wx.BoxSizer(wx.VERTICAL)

        self.listctrl_optional = None
        self.listctrl_selected = None

        self.button_load_course = None
        self.button_load_usercourse = None
        self.button_export = None
        self.button_login = None
        self.button_save_settings = None

        self.choice_season = None

        self.init_LeftPanel()

        self.sizer_right = wx.BoxSizer(wx.VERTICAL)
        self.textctrl_account = None
        self.textctrl_password = None
        self.textctrl_keys = None

        self.checkbox_force = None
        self.spinctrl_start = None
        self.spinctrl_end = None

        self.spinctrl_timer = None

        self.init_RightPanel()

        self.SetSizer(self.sizer_global)
        self.Layout()
        self.Center(wx.BOTH)



    def init_Optional_ListCtrl(self):
        sizer_optional = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"可选课程/目标课程/个人课表"), wx.HORIZONTAL)
        sizer_optional.SetMinSize(wx.Size(500, -1))

        self.listctrl_optional = Optional_ListCtrl(sizer_optional.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition,
                                                   wx.Size(-1, -1), wx.LC_REPORT)

        sizer_optional.Add(self.listctrl_optional, 1, wx.ALL, 5)

        self.sizer_left.Add(sizer_optional, 1, wx.EXPAND, 5)

    def init_Seleted_ListCtrl(self):
        sizer_selected = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"已选课程"), wx.HORIZONTAL)
        sizer_selected.SetMinSize(wx.Size(500, 100))

        self.listctrl_selected = Selected_ListCtrl(sizer_selected.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition,
                                                   wx.Size(-1, 100), wx.LC_REPORT)

        sizer_selected.Add(self.listctrl_selected, 1, wx.ALL, 5)

        self.sizer_left.Add(sizer_selected, 0, wx.EXPAND, 5)


    def init_ControlPanel(self):
        sizer_control_pannel = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u'操作面板'), wx.HORIZONTAL)

        self.button_load_course = wx.Button(sizer_control_pannel.GetStaticBox(), wx.ID_ANY, u"加载选课课程",
                                                   wx.DefaultPosition, wx.DefaultSize, 0)

        self.button_load_usercourse = wx.Button(sizer_control_pannel.GetStaticBox(), wx.ID_ANY, u"加载个人课表",
                                                   wx.DefaultPosition, wx.DefaultSize, 0)

        self.button_export = wx.Button(sizer_control_pannel.GetStaticBox(), wx.ID_ANY, u"导出课表",
                                       wx.DefaultPosition, wx.DefaultSize, 0)

        self.choice_season = wx.Choice(sizer_control_pannel.GetStaticBox(), wx.ID_ANY,
                                       wx.DefaultPosition, wx.DefaultSize, [], 0)
        self.choice_season.SetSelection(0)

        sizer_control_pannel.Add(self.button_load_course, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer_control_pannel.Add(self.button_load_usercourse, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer_control_pannel.Add(self.button_export, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer_control_pannel.Add(self.choice_season, 0,  wx.ALIGN_CENTER | wx.ALL, 5)

        self.sizer_left.Add(sizer_control_pannel, 0, wx.EXPAND, 5)

    def init_LeftPanel(self):
        self.init_Optional_ListCtrl()
        self.init_Seleted_ListCtrl()
        self.init_ControlPanel()

        self.sizer_global.Add(self.sizer_left, 1, wx.EXPAND, 5)

    def init_RightPanel(self):

        sizer_settings = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"设置"), wx.VERTICAL)
        sizer_userinfo = wx.StaticBoxSizer(wx.StaticBox(sizer_settings.GetStaticBox(), wx.ID_ANY, u"用户信息"), wx.VERTICAL)

        sizer_fg = wx.FlexGridSizer(0, 2, 0, 0)
        sizer_fg.SetFlexibleDirection(wx.BOTH)
        sizer_fg.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        text_account = wx.StaticText(sizer_userinfo.GetStaticBox(), wx.ID_ANY, u'账号', wx.DefaultPosition, wx.DefaultSize, 0)
        text_password = wx.StaticText(sizer_userinfo.GetStaticBox(), wx.ID_ANY, u'密码', wx.DefaultPosition, wx.DefaultSize, 0)
        text_ep = wx.StaticText(sizer_userinfo.GetStaticBox(), wx.ID_ANY, u'', wx.DefaultPosition, wx.DefaultSize, 0)

        text_account.Wrap(-1)
        text_password.Wrap(-1)

        self.textctrl_account = wx.TextCtrl(sizer_userinfo.GetStaticBox(), wx.ID_ANY, u'', wx.DefaultPosition,
                                       wx.DefaultSize, 0)
        self.textctrl_account.Enable(False)

        self.textctrl_password = wx.TextCtrl(sizer_userinfo.GetStaticBox(), wx.ID_ANY, u'', wx.DefaultPosition,
                                       wx.DefaultSize, wx.TE_PASSWORD)

        self.button_login = wx.Button(sizer_userinfo.GetStaticBox(), wx.ID_ANY, u"登录", wx.DefaultPosition,
                                                       wx.Size(100, -1), 0)

        # =====================================================
        sizer_fg.Add(text_account, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer_fg.Add(self.textctrl_account, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        sizer_fg.Add(text_password, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer_fg.Add(self.textctrl_password, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        sizer_fg.Add(text_ep, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer_fg.Add(self.button_login, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        # =====================================================
        sizer_userinfo.Add(sizer_fg, 0, wx.EXPAND, 5)

        sizer_settings.Add(sizer_userinfo, 0, wx.EXPAND, 5)

        # =====================================================
        sizer_course = wx.StaticBoxSizer(wx.StaticBox(sizer_settings.GetStaticBox(), wx.ID_ANY, u"选课设置"), wx.VERTICAL)

        sizer_course_filter = wx.StaticBoxSizer(wx.StaticBox(sizer_course.GetStaticBox(), wx.ID_ANY, u"课程过滤器"), wx.HORIZONTAL)

        text_keys = wx.StaticText(sizer_course_filter.GetStaticBox(), wx.ID_ANY, u'Keys', wx.DefaultPosition, wx.DefaultSize, 0)
        text_keys.Wrap(-1)
        self.textctrl_keys = wx.TextCtrl(sizer_course_filter.GetStaticBox(), wx.ID_ANY, u'', wx.DefaultPosition,
                                       wx.DefaultSize, 0)
        self.textctrl_keys.SetToolTip(u"过滤器规则：（优先级从左到右）\n(1) ,  :与操作\n(2) |  :或操作\n例如： 羽毛球,李三|乒乓球,张四")

        # =====================================================
        sizer_course_filter.Add(text_keys, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer_course_filter.Add(self.textctrl_keys, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # =====================================================

        self.checkbox_force = wx.CheckBox(sizer_course.GetStaticBox(), wx.ID_ANY, u"强制提交",
                                          wx.DefaultPosition, wx.DefaultSize, 0)

        # =====================================================

        sizer_post_range = wx.StaticBoxSizer(wx.StaticBox(sizer_course.GetStaticBox(), wx.ID_ANY, u"提交间隔"), wx.HORIZONTAL)
        self.spinctrl_start = wx.SpinCtrl(sizer_post_range.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                          wx.Size(60, -1), wx.SP_ARROW_KEYS, 0, 10, 1)
        self.spinctrl_end = wx.SpinCtrl(sizer_post_range.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                        wx.Size(60, -1), wx.SP_ARROW_KEYS, 0, 10, 3)

        text_line = wx.StaticText(sizer_post_range.GetStaticBox(), wx.ID_ANY, u'-', wx.DefaultPosition, wx.DefaultSize, 0)
        text_sec = wx.StaticText(sizer_post_range.GetStaticBox(), wx.ID_ANY, u'sec', wx.DefaultPosition, wx.DefaultSize, 0)

        # =====================================================
        sizer_post_range.Add(self.spinctrl_start, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer_post_range.Add(text_line, 0, wx.ALIGN_CENTER | wx.ALL, 0)
        sizer_post_range.Add(self.spinctrl_end, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer_post_range.Add(text_sec, 0, wx.ALIGN_CENTER | wx.ALL, 0)
        # =====================================================
        sizer_timer = wx.BoxSizer( wx.HORIZONTAL )
        text_timer = wx.StaticText(sizer_course.GetStaticBox(), wx.ID_ANY, u"定时刷新", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        text_timer.Wrap(-1)

        self.spinctrl_timer = wx.SpinCtrl(sizer_course.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                       wx.Size(60, -1), wx.SP_ARROW_KEYS, 0, 300, 200)

        text_sec1 = wx.StaticText(sizer_course.GetStaticBox(), wx.ID_ANY, u"sec", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        text_sec1.Wrap(-1)


        # =====================================================
        sizer_timer.Add(text_timer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer_timer.Add(self.spinctrl_timer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer_timer.Add(text_sec1, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # =====================================================

        self.button_save_settings = wx.Button(sizer_course.GetStaticBox(), wx.ID_ANY, u"保存设置", wx.DefaultPosition, wx.DefaultSize, 0)

        # =====================================================
        sizer_course.Add(self.checkbox_force, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer_course.Add(sizer_course_filter, 1, wx.EXPAND, 5)
        sizer_course.Add(sizer_post_range, 1, wx.EXPAND, 5)

        sizer_course.Add(sizer_timer, 0, wx.EXPAND, 5)
        sizer_course.Add(self.button_save_settings, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        sizer_settings.Add(sizer_course, 0, wx.EXPAND, 5)

        self.sizer_right.Add(sizer_settings, 0, wx.EXPAND, 5)

        self.sizer_global.Add(self.sizer_right, 0, wx.EXPAND, 5)

