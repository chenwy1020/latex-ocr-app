import sys
import os
import webview

# Add the project root to sys.path to allow imports from src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.api import Api

def main():
    api = Api()
    # We assume index.html will be in the src directory or project root.
    # Using absolute path to src/index.html if it exists, otherwise relative 'index.html'
    index_path = os.path.join(current_dir, 'index.html')
    url = index_path if os.path.exists(index_path) else 'index.html'
    
    webview.create_window('LaTeX OCR', url=url, js_api=api)
    webview.start(debug=True)

if __name__ == '__main__':
    main()
