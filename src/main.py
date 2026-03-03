import sys
import os
import webview
from flask import Flask, render_template

# Add the project root to sys.path to allow imports from src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.api import Api

# Create Flask app with correct template and static folders
app = Flask(__name__,
            template_folder=os.path.join(current_dir, 'templates'),
            static_folder=os.path.join(current_dir, 'static'))

@app.route('/')
def index():
    return render_template('index.html')

def main():
    api = Api()
    webview.create_window('LaTeX OCR', app, js_api=api, width=1000, height=700)
    webview.start(debug=True)

if __name__ == '__main__':
    main()
