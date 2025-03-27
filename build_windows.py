import PyInstaller.__main__
import os

# 獲取當前目錄
current_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(current_dir, 'assets')

PyInstaller.__main__.run([
    'main.py',
    '--name=像素拐杖侠',
    '--onefile',
    '--windowed',
    '--add-data={}{}assets'.format(assets_dir, os.pathsep),
    '--icon=assets/pixel_ko.png',  # 如果有圖標的話
])
