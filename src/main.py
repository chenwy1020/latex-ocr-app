import sys
import os
import webview
from flask import Flask, render_template

# Determine base path: PyInstaller sets sys._MEIPASS for bundled apps
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
    src_dir = os.path.join(base_dir, 'src')
else:
    src_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(src_dir)
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

from src.api import Api

# Create Flask app with correct template and static folders
app = Flask(__name__,
            template_folder=os.path.join(src_dir, 'templates'),
            static_folder=os.path.join(src_dir, 'static'))

@app.route('/')
def index():
    return render_template('index.html')

def main():
    api = Api()
    webview.create_window('LaTeX OCR', app, js_api=api, width=1000, height=700)
    webview.start(debug=False)

if __name__ == '__main__':
    main()
