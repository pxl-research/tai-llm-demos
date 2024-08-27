import os.path
import threading

import wx
import wx.html2 as webview

from fn_llm_or import OpenLLM
from fn_utils import markdown_to_html, get_abs_path


class PixieLite(wx.Frame):
    ID_BTN_PROMPT = 2
    BASE_URL = 'https://www.pxl.be/'

    llm = None
    completion = None

    def __init__(self, parent, id, title):
        self.html_header = None
        screen_size = wx.GetDisplaySize()
        w_width = int(screen_size.Width / 2)
        w_height = int(screen_size.Height / 2)
        wx.Frame.__init__(self, parent, id, title, size=(w_width, w_height))

        icon_path = get_abs_path('assets/chat.png')
        if os.path.exists(icon_path):
            self.SetIcon(wx.Icon(icon_path, wx.BITMAP_TYPE_PNG))

        # ui elements
        self.wv_markdown = webview.WebView.New(self)
        self.wv_markdown.SetPage(html='', baseUrl=PixieLite.BASE_URL)

        self.tx_prompt = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.tx_prompt.SetToolTip('Voer hier je prompt in')
        self.btn_send = wx.Button(self, id=PixieLite.ID_BTN_PROMPT, label='&Send')

        # binding handlers
        self.Bind(event=wx.EVT_BUTTON, handler=self.on_button_pressed, id=PixieLite.ID_BTN_PROMPT)
        self.tx_prompt.Bind(event=wx.EVT_KEY_UP, handler=self.on_key_down)

        # layout
        bs_horizontal = wx.BoxSizer(wx.HORIZONTAL)
        bs_horizontal.Add(self.tx_prompt, proportion=1, flag=wx.EXPAND)
        bs_horizontal.Add(self.btn_send, flag=wx.EXPAND)

        bs_vertical = wx.BoxSizer(wx.VERTICAL)
        bs_vertical.Add(self.wv_markdown, proportion=1, flag=wx.EXPAND)
        bs_vertical.Add(bs_horizontal, flag=wx.EXPAND)

        self.SetSizer(bs_vertical)

        # load some default content into webview
        try:
            f_name = get_abs_path("assets/README.md")
            md_file = open(f_name, "r")
            md_content = md_file.read()
            md_file.close()
            html_content = markdown_to_html(md_content)
            full_html = self.add_header(html_content)
            self.wv_markdown.SetPage(html=full_html, baseUrl=PixieLite.BASE_URL)
        except FileNotFoundError as fnfe:
            print(fnfe)

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
        if len(prompt) < 1:
            return

        self.completion = self.get_llm().complete(prompt)  # call the LLM
        threading.Thread(target=self.live_update, daemon=True).start()

    def live_update(self):
        if self.completion is None:
            return
        for part in self.completion:
            wx.CallAfter(self.update_webview, part)

        self.completion.close()
        self.completion = None

        # render complete message
        self.wv_markdown.RunScript("window.scrollTo(0, document.body.scrollHeight);")

    def update_webview(self, new_content):
        html_history = self.get_history_as_html()

        content_html = markdown_to_html(new_content)
        if content_html not in html_history:
            html_history = f'{html_history}\n<div class="bubble assistant">\n{content_html}\n</div>\n'

        full_page = self.add_header(html_history)
        self.wv_markdown.SetPage(html=full_page, baseUrl=PixieLite.BASE_URL)

    def get_html_header(self):
        if self.html_header is None:  # lazy loading
            f_name = get_abs_path("assets/header.html")
            header_file = open(f_name, "r")
            header_content = header_file.read()
            header_file.close()
            self.html_header = header_content
        return self.html_header

    def get_llm(self):
        if self.llm is None:  # lazy loading
            self.llm = OpenLLM()
        return self.llm

    def add_header(self, html_content):
        header_content = self.get_html_header()
        full_page = header_content + '<body class="markdown-body"> ' + html_content + '</body>'
        return full_page

    def get_history_as_html(self):
        history = self.get_llm().get_history()
        html_history = ''
        for message in history:
            content_html = markdown_to_html(message['content'])
            html_history = f'{html_history}\n<div class="bubble {message['role']}">\n{content_html}\n</div>\n'
        return html_history


# main code
app = wx.App()
PixieLite(parent=None, id=0, title='Pixie Lite')
app.MainLoop()

# https://github.com/wxWidgets/Phoenix/blob/master/demo/HTML2_WebView.py
