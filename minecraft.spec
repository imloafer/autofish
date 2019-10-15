# -*- mode: python -*-

block_cipher = None
added_files = [('C:/Users\Jerry/PycharmProjects/jiangyang_learn_python/*.qm', '.')]

a = Analysis(['main.py'],
             pathex=['C:\\Users\Jerry\\PycharmProjects\\jiangyang_learn_python'],
             binaries=[],
             datas=added_files,
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
          [],
          exclude_binaries=True,
          name='AutoFish for Minecraft',
          version='file_version_info.txt',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='AutoFish for Minecraft')
