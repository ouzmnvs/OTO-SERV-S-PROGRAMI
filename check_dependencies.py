"""
Check for Microsoft Visual C++ Redistributables and other dependencies
This script helps diagnose DLL loading issues
"""
import os
import sys
import winreg
import subprocess

def check_vcredist():
    """Check for Microsoft Visual C++ Redistributables"""
    print("🔍 Microsoft Visual C++ Redistributables kontrolü...")
    
    # Registry paths for VC++ redistributables
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x86"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x86"),
    ]
    
    found_any = False
    
    for hkey, subkey in registry_paths:
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                version, _ = winreg.QueryValueEx(key, "Version")
                installed, _ = winreg.QueryValueEx(key, "Installed")
                
                if installed:
                    arch = "x64" if "x64" in subkey else "x86"
                    print(f"✅ VC++ Redistributable {arch} bulundu: Version {version}")
                    found_any = True
                    
        except (FileNotFoundError, OSError):
            continue
    
    if not found_any:
        print("❌ Microsoft Visual C++ Redistributables bulunamadı!")
        print("💡 Çözüm: Microsoft Visual C++ 2015-2022 Redistributable indirin:")
        print("   https://aka.ms/vs/17/release/vc_redist.x64.exe")
        return False
    
    return True

def check_system_dlls():
    """Check for critical system DLLs"""
    print("\n🔍 Sistem DLL'leri kontrolü...")
    
    system32_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32')
    critical_dlls = [
        'vcruntime140.dll',
        'msvcp140.dll',
        'ucrtbase.dll',
        'api-ms-win-crt-runtime-l1-1-0.dll',
        'kernel32.dll',
        'msvcrt.dll'
    ]
    
    missing_dlls = []
    
    for dll in critical_dlls:
        dll_path = os.path.join(system32_path, dll)
        if os.path.exists(dll_path):
            print(f"✅ {dll} bulundu")
        else:
            print(f"❌ {dll} bulunamadı")
            missing_dlls.append(dll)
    
    if missing_dlls:
        print(f"⚠️  Eksik sistem DLL'leri: {missing_dlls}")
        return False
    
    return True

def check_python_dlls():
    """Check for Python DLLs in current environment"""
    print("\n🔍 Python DLL'leri kontrolü...")
    
    python_dir = os.path.dirname(sys.executable)
    python_dlls = [
        'python312.dll',
        'python3.dll',
        'sqlite3.dll'
    ]
    
    found_dlls = []
    missing_dlls = []
    
    for dll in python_dlls:
        dll_path = os.path.join(python_dir, dll)
        if os.path.exists(dll_path):
            print(f"✅ {dll} bulundu: {dll_path}")
            found_dlls.append(dll)
        else:
            print(f"❌ {dll} bulunamadı: {dll_path}")
            missing_dlls.append(dll)
    
    # Check in base Python if we're in virtual env
    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        print("\n🔄 Virtual environment algılandı, base Python kontrol ediliyor...")
        base_python_dir = os.path.dirname(sys.base_prefix + "\\python.exe")
        
        for dll in missing_dlls[:]:
            base_dll_path = os.path.join(base_python_dir, dll)
            if os.path.exists(base_dll_path):
                print(f"✅ {dll} base Python'da bulundu: {base_dll_path}")
                found_dlls.append(dll)
                missing_dlls.remove(dll)
    
    # Check DLLs directory
    dlls_dir = os.path.join(python_dir, 'DLLs')
    if os.path.exists(dlls_dir):
        print(f"\n📁 DLLs dizini bulundu: {dlls_dir}")
        dll_files = [f for f in os.listdir(dlls_dir) if f.endswith('.dll')]
        print(f"   {len(dll_files)} DLL dosyası bulundu")
        
        sqlite_dlls = [f for f in dll_files if 'sqlite' in f.lower()]
        if sqlite_dlls:
            print(f"   SQLite DLL'leri: {sqlite_dlls}")
    
    return len(missing_dlls) == 0

def run_dependency_check():
    """Run dependency walker or similar tool if available"""
    print("\n🔍 Dependency Walker ile kontrol...")
    
    # Try to find dependency walker
    possible_paths = [
        r"C:\Program Files (x86)\Microsoft Visual Studio\*\*\Tools\depends.exe",
        r"C:\Program Files\Microsoft Visual Studio\*\*\Tools\depends.exe",
        "depends.exe"  # If in PATH
    ]
    
    print("💡 Dependency Walker manuel olarak çalıştırılabilir:")
    print("   1. depends.exe indirin: http://www.dependencywalker.com/")
    print("   2. OTO-SERVIS.exe dosyasını depends.exe ile açın")
    print("   3. Eksik DLL'leri görün")

def provide_solutions():
    """Provide solutions for common DLL issues"""
    print("\n" + "="*60)
    print("💡 DLL Yükleme Sorunları için Çözümler:")
    print("="*60)
    
    print("\n1. Microsoft Visual C++ Redistributables yükleyin:")
    print("   - x64: https://aka.ms/vs/17/release/vc_redist.x64.exe")
    print("   - x86: https://aka.ms/vs/17/release/vc_redist.x86.exe")
    
    print("\n2. PyInstaller'ı güncelleyin:")
    print("   pip install --upgrade pyinstaller")
    
    print("\n3. Virtual environment'ı yeniden oluşturun:")
    print("   - Mevcut env klasörünü silin")
    print("   - python -m venv env")
    print("   - env\\Scripts\\activate")
    print("   - pip install -r requirements.txt")
    
    print("\n4. Build sırasında şu seçenekleri deneyin:")
    print("   - --optimize=0 (optimizasyonu kapatın)")
    print("   - --debug=all (debug modunu açın)")
    print("   - --console (konsol modunu açın)")
    
    print("\n5. Manuel DLL kopyalama:")
    print("   - Python yükleme dizininden python312.dll'i kopyalayın")
    print("   - dist/OTO-SERVIS/ klasörüne yapıştırın")
    
    print("\n6. Alternative build yöntemleri:")
    print("   - cx_Freeze kullanın")
    print("   - Auto-py-to-exe GUI aracını deneyin")

def main():
    print("🔧 OTO-SERVIS DLL Tanı ve Çözüm Aracı")
    print("="*60)
    
    try:
        vcredist_ok = check_vcredist()
        system_dlls_ok = check_system_dlls()
        python_dlls_ok = check_python_dlls()
        
        print("\n" + "="*60)
        print("📊 ÖZET:")
        print("="*60)
        print(f"Visual C++ Redistributables: {'✅ OK' if vcredist_ok else '❌ EKSIK'}")
        print(f"Sistem DLL'leri: {'✅ OK' if system_dlls_ok else '❌ SORUNLU'}")
        print(f"Python DLL'leri: {'✅ OK' if python_dlls_ok else '❌ EKSIK'}")
        
        if not all([vcredist_ok, system_dlls_ok, python_dlls_ok]):
            print("\n⚠️  Sorunlar tespit edildi! Çözümler için aşağıya bakın.")
            provide_solutions()
        else:
            print("\n🎉 Tüm bağımlılıklar tamam! DLL sorunu başka bir nedenden kaynaklanıyor olabilir.")
            print("💡 build_improved.py ile debug build yapmayı deneyin.")
        
        run_dependency_check()
        
    except Exception as e:
        print(f"\n❌ Kontrol sırasında hata: {e}")
        provide_solutions()

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
