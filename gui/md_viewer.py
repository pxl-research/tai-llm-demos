import markdown
import wx
import wx.html2 as webview


class MarkdownViewer(wx.Dialog):
    def __init__(self, parent, id, title):
        screensize = wx.GetDisplaySize()
        width = int(screensize.Width / 3)
        height = int(screensize.Height / 2)

        wx.Dialog.__init__(self, parent, id, title,
                           size=(width, height))

        self.SetIcon(wx.Icon('../assets/icons/chat.png', wx.BITMAP_TYPE_PNG))

        # ui elements
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.wv = webview.WebView.New(self, size=(200, 200))
        self.wv.SetPage('<h1>Hello World</h1>', 'www.none.be')

        btn_2 = wx.Button(self, 2, label='&Click me', size=(110, -1))

        # binding handlers

        self.Bind(wx.EVT_BUTTON, self.onRandomMove, id=2)

        # layout
        sizer.Add(self.wv, proportion=1, flag=wx.EXPAND)
        sizer.Add(btn_2, flag=wx.EXPAND)

        self.SetSizer(sizer)
        v_pos = int(screensize.Height / 4)
        self.SetPosition((0, v_pos))

        self.ShowModal()
        self.Destroy()

    def onRandomMove(self, event):
        md_file = open(f"../README.md", "r")
        md_content = md_file.read()
        md_file.close()
        html = markdown.markdown(md_content)

        # header = '<head><style>body {background-color: darkgray; color: white;}</style></head>'
        header_file = open(f"./header.html", "r")
        header_content = header_file.read()
        header_file.close()

        print(header_content)
        print(html)

        full_page = header_content + '<body class="markdown-body"> ' + html + '</body>'

        self.wv.SetPage(full_page, 'www.markdown.be')


# main code
app = wx.App(0)
MarkdownViewer(None, -1, 'Markdown Viewer')
app.MainLoop()

# https://github.com/wxWidgets/Phoenix/blob/master/demo/HTML2_WebView.py
