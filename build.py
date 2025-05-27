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

    # PyInstaller parametreleri
    params = [
        'dashboard.py',  # Ana program dosyası
        '--name=OTO-SERVIS',  # Exe dosyasının adı
        '--onefile',  # Tek bir exe dosyası oluştur
        '--windowed',  # Konsol penceresi gösterme
        '--icon=images.png',  # Program ikonu
        '--add-data=db_config.json;.',  # Yapılandırma dosyası
        '--add-data=arial-unicode-ms.ttf;.',
        '--add-data=arial-unicode-ms-bold.ttf;.',  # Arial Unicode MS font dosyası
        '--add-data=classiccar.pdf;.',  # PDF şablon dosyası
        '--add-data=teklif.pdf;.',  # Teklif PDF şablonu
        '--add-data=logo.png;.',  # Logo dosyası
        '--add-data=dashboard.png;.',  # Logo dosyası
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=qtawesome',
        '--hidden-import=sqlite3',
        '--hidden-import=reportlab',
        '--hidden-import=reportlab.pdfbase',
        '--hidden-import=reportlab.pdfbase.ttfonts',
        '--hidden-import=reportlab.lib.fonts',
        '--hidden-import=reportlab.lib.utils',
        '--hidden-import=PyMuPDF',
        '--hidden-import=locale',
        '--hidden-import=datetime',
        '--hidden-import=json',
        '--hidden-import=io',
        '--collect-all=reportlab',
        '--collect-all=PyMuPDF',
        '--exclude-module=pydoc',
        '--clean',  # Önceki build dosyalarını temizle
        '--noconfirm',  # Onay istemeden üzerine yaz
    ]

    # PyInstaller'ı çalıştır
    PyInstaller.__main__.run(params)

    print("Exe dosyası oluşturuldu: dist/OTO-SERVIS.exe")

if __name__ == "__main__":
    create_executable() 