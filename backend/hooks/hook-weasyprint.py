"""PyInstaller hook for WeasyPrint to bundle GTK3 dependencies."""

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

# Collect WeasyPrint data files
datas = collect_data_files('weasyprint')

# Collect dynamic libraries for GTK3 and Cairo
binaries = collect_dynamic_libs('cairocffi') or []
binaries += collect_dynamic_libs('cairosvg') or []

# On Windows, we need to ensure GTK3 libraries are included
# On macOS/Linux, system libraries are typically available
import sys
if sys.platform == 'win32':
    # Try to collect GTK3 libraries from common locations
    try:
        from PyInstaller.utils.hooks import get_module_file_attribute
        import os

        # Common GTK3 installation paths on Windows
        gtk_paths = [
            os.path.expandvars(r'C:\Program Files\GTK3-Runtime\bin'),
            os.path.expandvars(r'C:\Program Files (x86)\GTK3-Runtime\bin'),
            os.path.expandvars(r'%LOCALAPPDATA%\GTK3-Runtime\bin'),
        ]

        for gtk_path in gtk_paths:
            if os.path.exists(gtk_path):
                for dll_file in os.listdir(gtk_path):
                    if dll_file.endswith('.dll'):
                        binaries.append((os.path.join(gtk_path, dll_file), '.'))
                break
    except Exception:
        # If automatic collection fails, manual bundling will be required
        pass

# Hidden imports for WeasyPrint and dependencies
hiddenimports = [
    'weasyprint',
    'cairocffi',
    'cairosvg',
    'cssselect2',
    'tinycss2',
    'cffi',
    'PIL',
    'font_loader',
]

# Collect all submodules
hiddenimports.extend(collect_submodules('weasyprint'))
hiddenimports.extend(collect_submodules('cairocffi'))
