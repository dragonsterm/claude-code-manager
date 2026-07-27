# -*- mode: python ; coding: utf-8 -*-
# onefile + windowed mode. UPX stays disabled: compressed PyInstaller payloads
# trigger more heuristic AV false positives.
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/icon.ico', 'assets')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'unittest', 'pydoc', 'pydoc_data', 'doctest', 'email', 'http',
        'xml', 'xmlrpc', 'sqlite3', 'pdb', 'bdb', 'ftplib', 'lib2to3',
        'multiprocessing', 'concurrent', 'asyncio', 'ssl', 'socket',
        'pickle', 'pytest', 'setuptools', 'distutils',
    ],
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ClaudeCodeManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon='assets/icon.ico',
    version='version_info.txt',
)
