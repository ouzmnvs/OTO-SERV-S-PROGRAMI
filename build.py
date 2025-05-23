import PyInstaller.__main__
import os
import shutil

def build_exe():
    # Önce eski build klasörünü temizle
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # PyInstaller parametreleri
    params = [
        'dashboard.py',  # Ana script
        '--name=OTO-SERVIS',  # Exe adı
        '--onefile',  # Tek exe dosyası
        '--windowed',  # Konsol penceresi gösterme
        '--icon=images.png',  # İkon dosyasını image.png olarak güncelle
        '--add-data=db_config.json;.',  # Yapılandırma dosyası
        '--hidden-import=PyQt5',
        '--hidden-import=qtawesome',
        '--hidden-import=sqlite3',
        '--clean',  # Temiz build
        '--noconfirm',  # Onay istemeden üzerine yaz
    ]
    
    # PyInstaller'ı çalıştır
    PyInstaller.__main__.run(params)
    
    print("Build tamamlandı! Exe dosyası 'dist' klasöründe.")

if __name__ == "__main__":
    build_exe() 