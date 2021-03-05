# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['../cnctcli/ccli.py'],
             pathex=['/workspaces/product-sync'],
             binaries=[],
             datas=[
                ('../resources/theme_files','interrogatio/themes/theme_files'),
                ('../cnctcli/reports/connect-reports', 'cnctcli/commands'),
                ('../cnctcli/reports/connect-reports','cnctcli/reports/connect-reports'),
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
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
          console=True )
