import os
import sys

import markdown


def get_abs_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_path, relative_path)
    print(full_path)
    return full_path


def markdown_to_html(md_content):
    html = markdown.markdown(md_content, extensions=['fenced_code', 'codehilite'])
    return html
