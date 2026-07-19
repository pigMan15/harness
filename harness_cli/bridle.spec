# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Bridle single-file executable."""

import sys
from pathlib import Path

a = Analysis(
    ['src/harness_cli/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/harness_cli/templates', 'templates'),
    ],
    hiddenimports=[
        'textual',
        'rich',
        'rich.console',
        'rich.panel',
        'rich.progress',
        'rich.table',
        'rich.text',
        'yaml',
        'jsonschema',
        'jsonschema.validators',
        'textual.app',
        'textual.binding',
        'textual.containers',
        'textual.widgets',
        'textual.screen',
        'textual.css',
        'markdown_it',
        'mdit_py_plugins',
        'linkify_it',
        'uc_micro',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='bridle',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
