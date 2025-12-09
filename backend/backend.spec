# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for NSAanbiedingen backend."""

import sys
import os

# Configuration
# Use current working directory as base (PyInstaller runs from backend dir)
spec_dir = os.getcwd()
a = Analysis(
    [os.path.join(spec_dir, 'src', 'server.py')],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'weasyprint',
        'cairocffi',
        'cairosvg',
        'cssselect2',
        'tinycss2',
        'pydantic',
        'pydantic_core',
        '_pydantic_core',
    ],
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'django',
        'flask',
        'sqlalchemy',
        'psycopg2',
        'mysql',
        'pillow',  # Exclude PIL to keep size small
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window in production
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='backend',
)
