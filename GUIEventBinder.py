


import wx
import gui
import threading

_user_pool_ = None

def init(Pool):
    global _user_pool_
    _user_pool_ = Pool

    Main_MenuBar_File_Handler.bindEvent()
    Main_MenuBar_Edit_Handler.bindEvent()
    Main_MenuBar_Operation_Handler.bindEvent()
    Main_MenuBar_Help_Handler.bindEvent()
    Main_Member_Menu_Handler.bindEvent()
    Config_Button_Handler.bindEvent()
    Config_Choice_Handler.bindEvent()
    Config_TextCtrl_Handler.bindEvent()
    Config_ListCtrl_Selected_Handler.bindEvent()

def getUserOpFromTextCtrl():
    global _user_pool_
    account = gui.frame_configure.textctrl_account.GetLineText(0)
    userop = _user_pool_.getUserOp(account)
    return userop

def bind_main_menu_event(handler, source, attr_names):
    for i in attr_names:
        gui.frame_main.Bind(wx.EVT_MENU, getattr(handler, i), getattr(source, i))


# Frame Main MenuBar Handler

class Main_MenuBar_File_Handler:
    @staticmethod
    def bindEvent():
        events = ('run', 'save', 'save_as', 'import_from_xlsx', 'exit')
        bind_main_menu_event(Main_MenuBar_File_Handler, gui.frame_main.menu_bar.file, events)

    @staticmethod
    def run(event):
        _user_pool_.runTakeAll()

    @staticmethod
    def save(event):
        pass

    @staticmethod
    def save_as(event):
        pass

    @staticmethod
    def import_from_xlsx(event):
        dlg = wx.FileDialog(gui.frame_main, u"选择导入文件 *.xlsx", style=wx.FD_DEFAULT_STYLE)
        dlg.SetWildcard('*.xlsx')
        if dlg.ShowModal() == wx.ID_OK:
            path_name = dlg.GetPath()
            threading.Thread(target=_user_pool_.loadFromXlsx, args=(path_name,)).start()

        dlg.Destroy()

    @staticmethod
    def exit(event):
        exit()


class Main_MenuBar_Operation_Handler:
    @staticmethod
    def bindEvent():
        events = ('login', 'login_all', 'take', 'take_all', 'verify', 'verify_all')
        bind_main_menu_event(Main_MenuBar_Operation_Handler, gui.frame_main.menu_bar.operation, events)


    @staticmethod
    def login(event):
        Main_Member_Menu_Handler.login(event)

    @staticmethod
    def login_all(event):
        _user_pool_.runLoginAll()

    @staticmethod
    def take(event):
        Main_Member_Menu_Handler.take(event)

    @staticmethod
    def take_all(event):
        _user_pool_.runTakeAll()

    @staticmethod
    def verify(event):
        Main_Member_Menu_Handler.verify(event)

    @staticmethod
    def verify_all(event):
        _user_pool_.runVerifyAll()



class Main_MenuBar_Edit_Handler:
    @staticmethod
    def bindEvent():
        events = ('add', 'delete', 'delete_all')
        bind_main_menu_event(Main_MenuBar_Edit_Handler, gui.frame_main.menu_bar.edit, events)


    @staticmethod
    def add(event):
        gui.frame_configure.textctrl_account.Clear()
        gui.frame_configure.textctrl_password.Clear()
        gui.frame_configure.textctrl_keys.Clear()

        gui.frame_configure.textctrl_account.Enable(True)

        gui.frame_configure.Show(True)

    @staticmethod
    def delete(event):
        Main_Member_Menu_Handler.delete(event)

    @staticmethod
    def delete_all(event):
        pass




class Main_MenuBar_Help_Handler:
    @staticmethod
    def bindEvent():
        events = ('help', 'about')
        bind_main_menu_event(Main_MenuBar_Help_Handler, gui.frame_main.menu_bar.help, events)


    @staticmethod
    def help(event):
        pass

    @staticmethod
    def about(event):
        dlg = gui.About_Dialog(gui.frame_main)
        dlg.ShowModal()
        dlg.Destroy()

# Frame Main Member Menu Handler

class Main_Member_Menu_Handler:
    @staticmethod
    def bindEvent():
        events = ('view', 'configure', 'login', 'take', 'verify', 'delete')
        bind_main_menu_event(Main_Member_Menu_Handler, gui.frame_main.listctrl_member.menu, events)

    @staticmethod
    def view(event):
        gui.frame_configure.textctrl_account.Clear()
        gui.frame_configure.textctrl_password.Clear()
        gui.frame_configure.textctrl_keys.Clear()

        gui.frame_configure.textctrl_account.Enable(False)

        index = gui.frame_main.listctrl_member.GetFirstSelected()
        if index == -1:
            return
        item = _user_pool_.queue[index].user

        gui.frame_configure.textctrl_account.write(item.account)
        gui.frame_configure.textctrl_keys.write(item.keys)

        gui.frame_configure.Show(True)

    @staticmethod
    def login(event):
        index = gui.frame_main.listctrl_member.GetFirstSelected()

        userop = _user_pool_.queue[index]
        if index != -1:

            threading.Thread(target=userop.login, name='Menu_Login').start()



    @staticmethod
    def take(event):
        index = gui.frame_main.listctrl_member.GetFirstSelected()

        userop = _user_pool_.queue[index]
        if index != -1:
            menu_text = gui.frame_main.listctrl_member.menu.take.GetText()
            if 'Stop' in menu_text:
                threading.Thread(target=userop.taker.stop, name='Menu_Stop').start()
            elif 'Take' in menu_text:
                threading.Thread(target=userop.takeCourse, name='Menu_Take').start()



    @staticmethod
    def configure(event):
        Main_Member_Menu_Handler.view(event)

    @staticmethod
    def verify(event):
        index = gui.frame_main.listctrl_member.GetFirstSelected()

        userop = _user_pool_.queue[index]
        threading.Thread(target=userop.verify).start()


    @staticmethod
    def delete(event):
        gui.frame_configure.textctrl_account.Clear()
        gui.frame_configure.textctrl_password.Clear()
        gui.frame_configure.textctrl_keys.Clear()

        gui.frame_configure.textctrl_account.Enable(False)

        index = gui.frame_main.listctrl_member.GetFirstSelected()
        if index == -1:
            return
        _user_pool_.delete(index)


# Frame Configure Button Handler

def bind_config_button_event(handler, source, attr_names):
    for i in attr_names:
        gui.frame_configure.Bind(wx.EVT_BUTTON, getattr(handler, i), getattr(source, 'button_%s' % i))


class Config_Button_Handler:
    @staticmethod
    def bindEvent():
        events = ('login', 'load_course', 'load_usercourse', 'save_settings')
        bind_config_button_event(Config_Button_Handler, gui.frame_configure, events)

    @staticmethod
    def login(event):
        def after():
            gui.frame_configure.button_login.Enable(True)
            gui.frame_configure.textctrl_password.Clear()

        def add_or_delete(userop):
            if not userop.user.ready:
                _user_pool_.remove(userop)
            else:
                gui.frame_configure.textctrl_account.Enable(False)
            gui.frame_configure.textctrl_password.Clear()

        if not gui.frame_configure.textctrl_account.IsEnabled():
            gui.frame_configure.button_login.Enable(False)
            password = gui.frame_configure.textctrl_password.GetLineText(0)
            userop = getUserOpFromTextCtrl()

            if password:
                userop.user.password = password
            threading.Thread(target=userop.login).start()

            userop.join(exec_foo=after)
        else:
            account = gui.frame_configure.textctrl_account.GetLineText(0)
            password = gui.frame_configure.textctrl_password.GetLineText(0)
            keys = gui.frame_configure.textctrl_keys.GetLineText(0)

            userop = _user_pool_.add(account, password, keys)

            threading.Thread(target=userop.login).start()

            userop.join(exec_foo=add_or_delete, args=(userop,))

    @staticmethod
    def load_course(event):
        gui.frame_configure.button_load_course.Enable(False)
        userop = getUserOpFromTextCtrl()

        threading.Thread(target=userop.taker.puller.displayCourse).start()

        userop.join(gui.frame_configure.button_load_course.Enable, args=(True,))

    @staticmethod
    def load_usercourse(event):

        gui.frame_configure.button_load_usercourse.Enable(False)
        userop = getUserOpFromTextCtrl()

        threading.Thread(target=userop.taker.puller.displayUserCourse).start()

        userop.join(gui.frame_configure.button_load_usercourse.Enable, args=(True,))

    # @staticmethod
    # def export(event):
    #     pass

    @staticmethod
    def save_settings(event):
        dlg = wx.MessageDialog(gui.frame_configure, u'你确定要保存设置吗?',
                               u'提示', wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.YES:
            userop = getUserOpFromTextCtrl()
            userop.user.keys = gui.frame_configure.textctrl_keys.GetLineText(0)

            userop.user.force_post = gui.frame_configure.checkbox_force.GetValue()

            timer_refresh = gui.frame_configure.spinctrl_timer.GetValue()
            if userop.user.timer_refresh != timer_refresh:
                userop.user.timer_refresh = timer_refresh
                userop.cancelGetNotice()
                userop.timingGetNotice()

            userop.user.delay_range = [gui.frame_configure.spinctrl_start.GetValue(),
                                       gui.frame_configure.spinctrl_end.GetValue()]


# Frame Configure Choice Handler
class Config_Choice_Handler:
    @staticmethod
    def bindEvent():
        gui.frame_configure.Bind(wx.EVT_CHOICE, Config_Choice_Handler.season,
                                 gui.frame_configure.choice_season)

    @staticmethod
    def season(event):
        selected_index = gui.frame_configure.choice_season.GetCurrentSelection()

        userop = getUserOpFromTextCtrl()

        userop.taker.puller.season_code.setSeletedIndex(selected_index)


# Frame Configure Choice Handler
class Config_TextCtrl_Handler:
    @staticmethod
    def bindEvent():
        gui.frame_configure.Bind(wx.EVT_TEXT, Config_TextCtrl_Handler.keys,
                                 gui.frame_configure.textctrl_keys)

    @staticmethod
    def keys(event):
        if gui.frame_configure.listctrl_optional.style == 0:    # STYLE_OPTIONAL

            userop = getUserOpFromTextCtrl()
            if userop:
                userop.taker.puller.displayTarget()


def bind_config_menu_event(handler, source, attr_names):
    for i in attr_names:
        gui.frame_configure.Bind(wx.EVT_MENU, getattr(handler, i), getattr(source, i))


# Frame Configure Selected Handler
class Config_ListCtrl_Selected_Handler:
    @staticmethod
    def bindEvent():
        items = ('delete',)
        bind_config_menu_event(Config_ListCtrl_Selected_Handler, gui.frame_configure.listctrl_selected.menu, items)

    @staticmethod
    def delete(event):
        index = gui.frame_configure.listctrl_selected.GetFirstSelected()
        if index != -1:
            userop = getUserOpFromTextCtrl()
            course = userop.taker.puller.selected.index(index)
            dlg = wx.MessageDialog(gui.frame_configure, u'你确定要退选课程：[%s] ?' % course.__str__(),
                             u'提示', wx.YES_NO | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.YES:
                if userop.taker.postCancel():
                    wx.MessageDialog(gui.frame_configure, u'退选成功!', u'完成', wx.OK | wx.ICON_INFORMATION)
                else:
                    wx.MessageDialog(gui.frame_configure, u'退选失败，(详情请看主窗口的logs的ServerMsg)。', u'错误',
                                     wx.OK | wx.ICON_ERROR)

