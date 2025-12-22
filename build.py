import PyInstaller.__main__
import os
import sys
import shutil
import subprocess
import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_executable():
    # Temizlik işlemleri
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("OTO-SERVIS.spec"):
        os.remove("OTO-SERVIS.spec")
    
    # Python installation paths
    python_path = sys.executable
    python_dir = os.path.dirname(python_path)
    
    # Check if we're in virtual environment
    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        # We're in virtual env, get the base Python installation
        base_python_dir = os.path.dirname(sys.base_prefix + "\\python.exe")
        print(f"Virtual environment detected")
        print(f"Virtual env Python: {python_dir}")
        print(f"Base Python: {base_python_dir}")
    else:
        base_python_dir = python_dir

    params = [
        'dashboard.py',
        '--name=OTO-SERVIS',
        '--onedir',
        '--windowed',
        '--icon=images.png',
        '--optimize=0',  # Disable optimization to prevent DLL loading issues
        '--noupx',
        '--noconfirm',
        '--clean',
        
        # Data files
        '--add-data=db_config.json;.',
        '--add-data=arial-unicode-ms.ttf;.',
        '--add-data=arial-unicode-ms-bold.ttf;.',
        '--add-data=classiccar.pdf;.',
        '--add-data=teklif.pdf;.',
        '--add-data=logo.png;.',
        '--add-data=dashboard.png;.',
        
        # Add Python DLLs explicitly
        f'--add-binary={python_dir}\\python312.dll;.',
        f'--add-binary={python_dir}\\python3.dll;.',
        
        # Essential hidden imports
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=PyQt5.QtPrintSupport',
        '--hidden-import=PyQt5.QtMultimedia',
        '--hidden-import=PyQt5.QtNetwork',
        '--hidden-import=qtawesome',
        '--hidden-import=sqlite3',
        '--hidden-import=_sqlite3',
        '--hidden-import=sip',
        '--hidden-import=PyQt5.sip',
        '--hidden-import=reportlab.pdfgen.canvas',
        '--hidden-import=reportlab.lib.pagesizes',
        '--hidden-import=reportlab.pdfbase.pdfmetrics',
        '--hidden-import=reportlab.pdfbase.ttfonts',
        '--hidden-import=reportlab.lib.utils',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=PyMuPDF',
        '--hidden-import=pkg_resources',
        
        # Collect necessary modules
        '--collect-submodules=qtawesome',
        '--collect-data=reportlab',
        '--collect-data=PIL',
        '--collect-data=PyQt5',
        
        # SADECE gereksiz 3rd-party libraries'i exclude edin
        '--exclude-module=tkinter',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        '--exclude-module=cv2',
        '--exclude-module=tensorflow',
        '--exclude-module=torch',
        '--exclude-module=sklearn',
        '--exclude-module=jupyter',
        '--exclude-module=IPython',
        '--exclude-module=notebook',
        '--exclude-module=sphinx',
        '--exclude-module=pytest',
    ]
    
    # Add DLLs from DLLs directory if they exist
    dlls_dir = os.path.join(python_dir, 'DLLs')
    if os.path.exists(dlls_dir):
        for dll_file in os.listdir(dlls_dir):
            if dll_file.endswith('.dll') and dll_file.startswith('sqlite'):
                params.append(f'--add-binary={os.path.join(dlls_dir, dll_file)};DLLs')
    
    # Check if base Python DLLs exist and add them
    base_dll_files = ['python312.dll', 'python3.dll', 'sqlite3.dll']
    for dll in base_dll_files:
        base_dll_path = os.path.join(base_python_dir, dll)
        if os.path.exists(base_dll_path):
            params.append(f'--add-binary={base_dll_path};.')

    # PyInstaller'ı çalıştır
    PyInstaller.__main__.run(params)

    print("Exe dosyası oluşturuldu: dist/OTO-SERVIS/OTO-SERVIS.exe")
    print("NOT: --onedir kullanıldığı için dosyalar dist/OTO-SERVIS/ klasöründe")
    print("Programı çalıştırmak için dist/OTO-SERVIS/OTO-SERVIS.exe dosyasını kullanın")

if __name__ == "__main__":
    create_executable()