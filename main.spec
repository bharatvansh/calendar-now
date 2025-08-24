# -*- mode: python ; coding: utf-8 -*-


 a = Analysis(
    ['src\main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/icons/*.png', 'resources/icons'),
        ('resources/icons/*.ico', 'resources/icons'),
        ('resources/icons/*.svg', 'resources/icons'),
        ('resources/credentials/client_config.json', 'resources/credentials'),
        ('resources/', 'resources/'),
    ],
    hiddenimports=['ui.tray', 'ui.setup_wizard', 'ui.notifications', 'ui.task_display', 'calendar_api.client', 'calendar_api.events', 'auth.credentials', 'auth.oauth'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CalendarNow',
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
    icon='resources/icons/app_icon.ico',
)
