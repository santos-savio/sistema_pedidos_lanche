# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # Adiciona os binários diretamente aqui
    a.zipfiles,   # Adiciona os arquivos zip diretamente aqui
    a.datas,      # Adiciona os dados diretamente aqui
    name='Aventulanches',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon='aventureiros.ico',
    version='version.txt',
    onefile=True,  # Garante que tudo será empacotado em um único .exe
)
