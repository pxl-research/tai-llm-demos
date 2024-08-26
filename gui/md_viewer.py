import threading

import markdown
import wx
import wx.html2 as webview

from gui.fn_llm_or import OpenLLM


class MarkdownViewer(wx.Frame):
    ID_BTN_PROMPT = 2
    BASE_URL = 'https://www.pxl.be/'

    llm = OpenLLM()
    completion = None

    def __init__(self, parent, id, title):
        self.html_header = None
        screen_size = wx.GetDisplaySize()
        w_width = int(screen_size.Width / 2)
        w_height = int(screen_size.Height / 2)
        wx.Frame.__init__(self, parent, id, title, size=(w_width, w_height))

        self.SetIcon(wx.Icon('../assets/icons/chat.png', wx.BITMAP_TYPE_PNG))

        # ui elements
        self.wv_markdown = webview.WebView.New(self)
        self.wv_markdown.SetPage(html='', baseUrl=MarkdownViewer.BASE_URL)

        self.tx_prompt = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.btn_send = wx.Button(self, id=MarkdownViewer.ID_BTN_PROMPT, label='&Send')

        # binding handlers
        self.Bind(event=wx.EVT_BUTTON, handler=self.on_button_pressed, id=MarkdownViewer.ID_BTN_PROMPT)
        self.tx_prompt.Bind(event=wx.EVT_KEY_UP, handler=self.on_key_down)

        # layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.wv_markdown, proportion=1, flag=wx.EXPAND)
        sizer.Add(self.tx_prompt, flag=wx.EXPAND)
        sizer.Add(self.btn_send, flag=wx.EXPAND)
        self.SetSizer(sizer)

        # load some default content into webview
        md_file = open(f"./README.md", "r")
        md_content = md_file.read()
        md_file.close()
        html = self.markdown_to_html(md_content)
        self.wv_markdown.SetPage(html=html, baseUrl=MarkdownViewer.BASE_URL)

        self.Center()
        self.Show()

    def on_button_pressed(self, event):
        self.process_prompt()

    def on_key_down(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN and event.ControlDown():
            self.process_prompt()
            event.Skip()
        else:
            event.Skip()

    def process_prompt(self):
        prompt = self.tx_prompt.GetValue()
        self.tx_prompt.Clear()
        print(prompt)

        self.completion = self.llm.complete(prompt)
        threading.Thread(target=self.live_update, daemon=True).start()

    def live_update(self):
        if self.completion is None:
            return
        for part in self.completion:
            wx.CallAfter(self.update_webview, part)

    def update_webview(self, md_content):
        print(md_content)
        html = self.markdown_to_html(md_content)
        self.wv_markdown.SetPage(html=html, baseUrl=MarkdownViewer.BASE_URL)

    def get_html_header(self):
        if self.html_header is None:  # lazy loading
            header_file = open(f"./header.html", "r")
            header_content = header_file.read()
            header_file.close()
            self.html_header = header_content
        return self.html_header

    def markdown_to_html(self, md_content):
        html = markdown.markdown(md_content)
        header_content = self.get_html_header()
        full_page = header_content + '<body class="markdown-body"> ' + html + '</body>'
        return full_page


# main code
app = wx.App(0)
MarkdownViewer(None, -1, 'Markdown Viewer')
app.MainLoop()

# https://github.com/wxWidgets/Phoenix/blob/master/demo/HTML2_WebView.py
