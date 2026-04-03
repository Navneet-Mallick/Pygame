# -*- mode: python ; coding: utf-8 -*-
import os
import ursina

# Locate ursina package directory to bundle its assets
ursina_path = os.path.dirname(ursina.__file__)

a = Analysis(
    ['cricket_3d_pro.py'],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(ursina_path, 'models'), 'ursina/models'),
        (os.path.join(ursina_path, 'textures'), 'ursina/textures'),
        (os.path.join(ursina_path, 'fonts'), 'ursina/fonts'),
        (os.path.join(ursina_path, 'shaders'), 'ursina/shaders'),
        (os.path.join(ursina_path, 'audio'), 'ursina/audio'),
    ],
    hiddenimports=[
        'ursina',
        'panda3d.core',
        'panda3d.direct',
        'direct.showbase.ShowBase',
        'direct.task',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LuminaCricket3D',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
