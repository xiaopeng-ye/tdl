# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main_gui.pyw'],
             pathex=['E:\\Xiao\\OneDrive - Universidad Politécnica de Madrid\\Ingeniería informática\\Procesadores de lenguajes\\Práctica\\js-pdl\\src'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += [("config/descendente_tabular.csv","./config/descendente_tabular.csv","DATA"),
           ("config/lexico_tabla.csv","./config/lexico_tabla.csv","DATA"),
           ("config/producciones.txt","./config/producciones.txt","DATA")]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='main_gui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon="../pdl.ico")
