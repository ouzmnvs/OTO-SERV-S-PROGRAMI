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

    # ReportLab font dosyasını proje dizinine kopyala
    reportlab_path = os.path.dirname(reportlab.__file__)
    fonts_path = os.path.join(reportlab_path, 'fonts')
    dejavu_path = os.path.join(fonts_path, 'DejaVuSans.ttf')
    
    # Font dosyasını proje dizinine kopyala
    if os.path.exists(dejavu_path):
        shutil.copy2(dejavu_path, 'DejaVuSans.ttf')
    else:
        print("Warning: DejaVuSans.ttf not found in ReportLab fonts directory")
        # Alternatif font dosyası oluştur
        with open('DejaVuSans.ttf', 'wb') as f:
            f.write(b'')  # Boş dosya oluştur

    # PyInstaller parametreleri
    params = [
        'dashboard.py',  # Ana program dosyası
        '--name=OTO-SERVIS',  # Exe dosyasının adı
        '--onefile',  # Tek bir exe dosyası oluştur
        '--windowed',  # Konsol penceresi gösterme
        '--icon=images.png',  # Program ikonu (eğer varsa)
        '--add-data=db_config.json;.',  # Yapılandırma dosyası
        '--add-data=DejaVuSans.ttf;.',  # Font dosyası
        '--add-data=classiccar.pdf;.',  # PDF şablon dosyası
        '--add-data=teklif.pdf;.',  
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