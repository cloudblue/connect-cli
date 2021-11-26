# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, copy_metadata

block_cipher = None


datas=[
    ('../connect/.data', 'connect/.data'),
]

datas += collect_data_files('cairocffi')
datas += collect_data_files('cairosvg')
datas += collect_data_files('connect.reports')
datas += collect_data_files('interrogatio')
datas += collect_data_files('pyphen')
datas += copy_metadata('connect-cli', recursive=True)

a = Analysis(
    ['../connect/cli/ccli.py'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'connect.cli.plugins.customer.commands',
        'connect.cli.plugins.product.commands',
        'connect.cli.plugins.report.commands',
        'connect.cli.plugins.play.commands',
        'connect.cli.plugins.project.commands',
        'cookiecutter.extensions',
        'jinja2_time',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
    name='ccli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
