"""
Improved build script for OTO-SERVIS that handles DLL loading issues
Uses a custom spec file with better DLL handling
"""
import PyInstaller.__main__
import os
import sys
import shutil
import subprocess

def create_executable_with_spec():
    """Build using the improved spec file"""
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Verify spec file exists
    spec_file = "OTO-SERVIS-IMPROVED.spec"
    if not os.path.exists(spec_file):
        print(f"Error: {spec_file} not found!")
        return False
    
    # Verify runtime hook exists
    runtime_hook = "runtime_hook_dll_fix.py"
    if not os.path.exists(runtime_hook):
        print(f"Error: {runtime_hook} not found!")
        return False
    
    # Build with spec file
    try:
        PyInstaller.__main__.run([
            spec_file,
            '--clean',
            '--noconfirm'
        ])
        
        exe_path = "dist/OTO-SERVIS/OTO-SERVIS.exe"
        if os.path.exists(exe_path):
            print("✅ Exe dosyası başarıyla oluşturuldu!")
            print(f"📁 Konum: {os.path.abspath(exe_path)}")
            print("📋 Programı çalıştırmak için dist/OTO-SERVIS/OTO-SERVIS.exe dosyasını kullanın")
            return True
        else:
            print("❌ Exe dosyası oluşturulamadı!")
            return False
            
    except Exception as e:
        print(f"❌ Build hatası: {e}")
        return False

def check_python_environment():
    """Check Python environment and DLL availability"""
    print("🔍 Python environment kontrolü...")
    print(f"Python sürümü: {sys.version}")
    print(f"Python yolu: {sys.executable}")
    
    python_dir = os.path.dirname(sys.executable)
    print(f"Python dizini: {python_dir}")
    
    # Check critical DLLs
    critical_dlls = ['python312.dll', 'python3.dll']
    missing_dlls = []
    
    for dll in critical_dlls:
        dll_path = os.path.join(python_dir, dll)
        if os.path.exists(dll_path):
            print(f"✅ {dll} bulundu: {dll_path}")
        else:
            print(f"❌ {dll} bulunamadı: {dll_path}")
            missing_dlls.append(dll)
    
    # Check if we're in virtual environment
    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        print("🔄 Virtual environment algılandı")
        base_python_dir = os.path.dirname(sys.base_prefix + "\\python.exe")
        print(f"Base Python dizini: {base_python_dir}")
        
        # Check base Python DLLs
        for dll in missing_dlls[:]:
            base_dll_path = os.path.join(base_python_dir, dll)
            if os.path.exists(base_dll_path):
                print(f"✅ {dll} base Python'da bulundu: {base_dll_path}")
                missing_dlls.remove(dll)
    
    if missing_dlls:
        print(f"⚠️  Eksik DLL'ler: {missing_dlls}")
        print("Bu DLL'ler build sırasında otomatik olarak aranacak.")
    
    return len(missing_dlls) == 0

def create_debug_build():
    """Create a debug build to help diagnose DLL issues"""
    print("🔧 Debug build oluşturuluyor...")
    
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    params = [
        'dashboard.py',
        '--name=OTO-SERVIS-DEBUG',
        '--onedir',
        '--console',  # Enable console for debugging
        '--icon=images.png',
        '--debug=all',  # Enable all debug options
        '--optimize=0',
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
        
        # Essential imports only
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=sqlite3',
        '--hidden-import=_sqlite3',
        
        # Runtime hook
        '--runtime-hook=runtime_hook_dll_fix.py',
    ]
    
    try:
        PyInstaller.__main__.run(params)
        
        exe_path = "dist/OTO-SERVIS-DEBUG/OTO-SERVIS-DEBUG.exe"
        if os.path.exists(exe_path):
            print("✅ Debug exe dosyası oluşturuldu!")
            print(f"📁 Konum: {os.path.abspath(exe_path)}")
            print("🐛 Bu sürümü çalıştırarak detaylı hata mesajlarını görebilirsiniz.")
            return True
        else:
            print("❌ Debug exe dosyası oluşturulamadı!")
            return False
            
    except Exception as e:
        print(f"❌ Debug build hatası: {e}")
        return False

if __name__ == "__main__":
    print("🚀 OTO-SERVIS Build Süreci Başlıyor...")
    print("=" * 50)
    
    # Check environment first
    env_ok = check_python_environment()
    print("=" * 50)
    
    print("Hangi build türünü istiyorsunuz?")
    print("1. Normal build (önerilen)")
    print("2. Debug build (sorun giderme için)")
    print("3. Her ikisi de")
    
    try:
        choice = input("Seçiminiz (1-3): ").strip()
        
        if choice == "1":
            success = create_executable_with_spec()
        elif choice == "2":
            success = create_debug_build()
        elif choice == "3":
            print("Debug build oluşturuluyor...")
            debug_success = create_debug_build()
            print("\nNormal build oluşturuluyor...")
            normal_success = create_executable_with_spec()
            success = debug_success or normal_success
        else:
            print("Geçersiz seçim! Normal build yapılıyor...")
            success = create_executable_with_spec()
            
        if success:
            print("\n🎉 Build tamamlandı!")
        else:
            print("\n❌ Build başarısız!")
            print("Debug build'i deneyerek sorunları teşhis edebilirsiniz.")
            
    except KeyboardInterrupt:
        print("\n❌ Build iptal edildi!")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
