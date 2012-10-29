import wx

class FollowPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self._list = None
    def add_packet(self, pkg):
        pass

if __name__ == '__main__':
    app = wx.App()
    frame = wx.Frame(None)
    panel = FollowPanel(frame)
    panel.Show()
    app.MainLoop()
