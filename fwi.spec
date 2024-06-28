# -*- mode: python ; coding: utf-8 -*-
hidden_imports = [
    'dotenv',
    'numpy',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('fwi_gee', 'fwi_gee'),
        ('db', 'db'),
        ('dotenv', 'dotenv'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['config'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='fwi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["C:/Users/MKurziankou/Downloads/8725868_fire_icon.ico"],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='fire_weather_index',
)
