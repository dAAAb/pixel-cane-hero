import PyInstaller.__main__
import os

# 獲取當前目錄
current_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(current_dir, 'assets')

# 確保 assets 目錄存在
if not os.path.exists(assets_dir):
    os.makedirs(assets_dir)

PyInstaller.__main__.run([
    'main.py',
    '--name=像素拐杖侠',
    '--onefile',
    '--windowed',
    f'--add-data={assets_dir}{os.pathsep}assets'
])
