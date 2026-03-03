"""Build script: creates a standalone .exe launcher for LaTeX OCR.
Uses PyInstaller with minimal bundling - only the app code and resources.
PyTorch/pix2tex will be loaded from the system Python environment at runtime.
"""
import subprocess
import sys
import os

def build():
    """Build a lightweight exe that bootstraps the app."""
    # Create a small launcher that sets up paths and runs main
    launcher_code = '''
import sys
import os
import subprocess
import shutil

def show_error(msg):
    """Show error message box on Windows."""
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, "LaTeX OCR - Error", 0x10)
    except Exception:
        print(msg)

def find_python():
    """Find system Python executable (not the frozen exe)."""
    # If not frozen, just use sys.executable
    if not getattr(sys, 'frozen', False):
        return sys.executable
    
    # When frozen, find system python via PATH
    python = shutil.which('python')
    if python:
        return python
    python = shutil.which('python3')
    if python:
        return python
    
    # Check common Windows Python locations
    for base in [os.environ.get('LOCALAPPDATA', ''), os.environ.get('PROGRAMFILES', ''),
                 'C:\\\\Python312', 'C:\\\\Python311', 'C:\\\\Python310',
                 os.path.expanduser('~\\\\anaconda3'),
                 os.path.expanduser('~\\\\miniconda3'),
                 'D:\\\\ProgramData\\\\anaconda3']:
        for name in ['python.exe', 'Scripts\\\\python.exe']:
            p = os.path.join(base, name)
            if os.path.isfile(p):
                return p
    return None

def main():
    # Get the directory where the exe is located
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    src_dir = os.path.join(app_dir, 'src')
    main_py = os.path.join(src_dir, 'main.py')
    
    if not os.path.exists(main_py):
        # Try parent directory
        app_dir = os.path.dirname(app_dir)
        main_py = os.path.join(app_dir, 'src', 'main.py')
    
    if not os.path.exists(main_py):
        show_error("Cannot find src/main.py.\\nPlease place LaTeX-OCR.exe in the project root directory.")
        sys.exit(1)
    
    python = find_python()
    if not python:
        show_error("Cannot find Python installation.\\nPlease install Python 3.10+ and add it to PATH.")
        sys.exit(1)
    
    # Launch the app using system Python
    os.chdir(app_dir)
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    result = subprocess.run([python, main_py], cwd=app_dir)
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()
'''
    
    launcher_path = os.path.join(os.path.dirname(__file__), '_launcher.py')
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_code)
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--noconsole',
        '--name', 'LaTeX-OCR',
        '--noconfirm',
        '--clean',
        # Exclude everything heavy - this is just a launcher
        '--exclude-module', 'torch',
        '--exclude-module', 'torchvision',
        '--exclude-module', 'pix2tex',
        '--exclude-module', 'numpy',
        '--exclude-module', 'PIL',
        '--exclude-module', 'flask',
        '--exclude-module', 'webview',
        '--exclude-module', 'PyQt5',
        '--exclude-module', 'PyQt6',
        '--exclude-module', 'PySide6',
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'scipy',
        '--exclude-module', 'pandas',
        '--exclude-module', 'sklearn',
        '--exclude-module', 'sphinx',
        '--exclude-module', 'IPython',
        '--exclude-module', 'jupyter',
        launcher_path,
    ]
    
    print("Building LaTeX-OCR.exe launcher...")
    result = subprocess.run(cmd)
    
    # Clean up temp file
    os.remove(launcher_path)
    
    if result.returncode == 0:
        exe_path = os.path.join('dist', 'LaTeX-OCR.exe')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / 1024 / 1024
            print(f"\nBuild successful!")
            print(f"  Output: {os.path.abspath(exe_path)}")
            print(f"  Size: {size_mb:.1f} MB")
            print(f"\nTo use: copy LaTeX-OCR.exe to the project root and double-click.")
        else:
            print("Build completed but exe not found!")
    else:
        print(f"Build failed with code {result.returncode}")

if __name__ == '__main__':
    build()
