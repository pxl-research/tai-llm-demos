import markdown
import wx
import wx.html2 as webview


class MarkdownViewer(wx.Frame):
    def __init__(self, parent, id, title):
        self.html_header = None
        screen_size = wx.GetDisplaySize()
        w_width = int(screen_size.Width / 2)
        w_height = int(screen_size.Height / 2)
        wx.Frame.__init__(self, parent, id, title, size=(w_width, w_height))

        self.SetIcon(wx.Icon('../assets/icons/chat.png', wx.BITMAP_TYPE_PNG))

        # ui elements
        self.wv_markdown = webview.WebView.New(self)
        self.wv_markdown.SetPage('<h1>Hello World</h1>', 'www.none.be')

        self.tx_prompt = wx.TextCtrl(self)
        self.btn_send = wx.Button(self, 2, label='&Send')

        # binding handlers
        self.Bind(wx.EVT_BUTTON, self.onButtonPressed, id=2)

        # layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.wv_markdown, proportion=1, flag=wx.EXPAND)
        sizer.Add(self.tx_prompt, flag=wx.EXPAND)
        sizer.Add(self.btn_send, flag=wx.EXPAND)
        self.SetSizer(sizer)

        self.Center()
        self.Show()

    def onButtonPressed(self, event):
        md_file = open(f"../README.md", "r")
        md_content = md_file.read()
        md_file.close()

        html = self.markdown_to_html(md_content)
        self.wv_markdown.SetPage(html, 'www.markdown.be')

    def get_html_header(self):
        if self.html_header is None:  # lazy loading
            header_file = open(f"./header.html", "r")
            header_content = header_file.read()
            header_file.close()
            self.html_header = header_content
        return self.html_header

    def markdown_to_html(self, md_content):
        prompt = self.tx_prompt.GetValue()
        print(prompt)
        self.tx_prompt.Clear()

        html = markdown.markdown(md_content)
        header_content = self.get_html_header()
        full_page = header_content + '<body class="markdown-body"> ' + html + '</body>'
        return full_page


# main code
app = wx.App(0)
MarkdownViewer(None, -1, 'Markdown Viewer')
app.MainLoop()

# https://github.com/wxWidgets/Phoenix/blob/master/demo/HTML2_WebView.py
