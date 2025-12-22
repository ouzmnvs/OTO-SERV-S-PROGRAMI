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

    params = [
        'dashboard.py',
        '--name=OTO-SERVIS',
        '--onedir',
        '--windowed',
        '--icon=images.png',
        '--optimize=2',
        '--noupx',
        
        # Data files
        '--add-data=db_config.json;.',
        '--add-data=arial-unicode-ms.ttf;.',
        '--add-data=arial-unicode-ms-bold.ttf;.',
        '--add-data=classiccar.pdf;.',
        '--add-data=teklif.pdf;.',
        '--add-data=logo.png;.',
        '--add-data=dashboard.png;.',
        
        # Essential hidden imports
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=PyQt5.QtPrintSupport',
        '--hidden-import=PyQt5.QtMultimedia',
        '--hidden-import=PyQt5.QtNetwork',
        '--hidden-import=qtawesome',
        '--hidden-import=sqlite3',
        '--hidden-import=reportlab.pdfgen.canvas',
        '--hidden-import=reportlab.lib.pagesizes',
        '--hidden-import=reportlab.pdfbase.pdfmetrics',
        '--hidden-import=reportlab.pdfbase.ttfonts',
        '--hidden-import=reportlab.lib.utils',  # EKLENDI
        '--hidden-import=PIL',  # EKLENDI
        '--hidden-import=PIL.Image',  # EKLENDI
        '--hidden-import=PyMuPDF',
        '--hidden-import=pkg_resources',
        
        # Collect necessary modules
        '--collect-submodules=qtawesome',
        '--collect-data=reportlab',
        '--collect-data=PIL',  # EKLENDI
        
        # SADECE gereksiz 3rd-party libraries'i exclude edin
        '--exclude-module=tkinter',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        # '--exclude-module=PIL',  # BU SATIRI SİLDİM - Reportlab için gerekli
        '--exclude-module=cv2',
        '--exclude-module=tensorflow',
        '--exclude-module=torch',
        '--exclude-module=sklearn',
        '--exclude-module=jupyter',
        '--exclude-module=IPython',
        '--exclude-module=notebook',
        '--exclude-module=sphinx',
        '--exclude-module=pytest',
        
        '--clean',
        '--noconfirm',
    ]

    # PyInstaller'ı çalıştır
    PyInstaller.__main__.run(params)

    print("Exe dosyası oluşturuldu: dist/OTO-SERVIS/OTO-SERVIS.exe")
    print("NOT: --onedir kullanıldığı için dosyalar dist/OTO-SERVIS/ klasöründe")
    print("Programı çalıştırmak için dist/OTO-SERVIS/OTO-SERVIS.exe dosyasını kullanın")

if __name__ == "__main__":
    create_executable()