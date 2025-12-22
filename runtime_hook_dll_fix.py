"""
Runtime hook for fixing DLL loading issues in PyInstaller
This hook ensures proper DLL search paths are set at runtime
"""
import os
import sys

# Add current directory to DLL search path
if hasattr(os, 'add_dll_directory'):
    # Python 3.8+
    try:
        current_dir = os.path.dirname(sys.executable)
        os.add_dll_directory(current_dir)
        
        # Also add DLLs subdirectory if it exists
        dlls_dir = os.path.join(current_dir, 'DLLs')
        if os.path.exists(dlls_dir):
            os.add_dll_directory(dlls_dir)
            
        print(f"DLL directories added: {current_dir}, {dlls_dir}")
    except Exception as e:
        print(f"Could not add DLL directories: {e}")

# Set DLL directory in PATH as fallback
current_dir = os.path.dirname(sys.executable)
if current_dir not in os.environ.get('PATH', ''):
    os.environ['PATH'] = current_dir + os.pathsep + os.environ.get('PATH', '')

# Set Qt plugin path to avoid plugin loading issues
qt_plugins_dir = os.path.join(current_dir, 'PyQt5', 'Qt', 'plugins')
if os.path.exists(qt_plugins_dir):
    os.environ['QT_PLUGIN_PATH'] = qt_plugins_dir
