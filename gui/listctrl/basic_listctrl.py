

import wx

ODD_BGCOLOR = wx.Colour(240, 240, 240, 255)
EVEN_BGCOLOR = wx.Colour(255, 255, 255, 255)

class BasicListCtrl(wx.ListCtrl):
    def Append(self, entry, fgcolor=None):
        wx.ListCtrl.Append(self, entry)
        item_count = self.GetItemCount()
        if not item_count % 2:
            self.SetItemBackgroundColour(item_count - 1, ODD_BGCOLOR)

        if fgcolor:
            self.SetItemTextColour(item_count-1, wx.Colour(fgcolor))

        # self.ScrollList(0, 10)
        # self.ScrollLines(1)

    def DeleteItem(self, item):
        wx.ListCtrl.DeleteItem(self, item)
        item_count = self.GetItemCount()
        odd = True if item % 2 else False

        for i in range(item_count - item):

            self.SetItemBackgroundColour(i + item, ODD_BGCOLOR if odd else EVEN_BGCOLOR)

            odd = not odd




