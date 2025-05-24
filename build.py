import PyInstaller.__main__
import os
import shutil

# 既存のbuildとdistフォルダを削除
for folder in ['build', 'dist']:
    if os.path.exists(folder):
        shutil.rmtree(folder)

# アプリケーションをビルド
PyInstaller.__main__.run([
    'app.py',
    '--onefile',  # 単一の実行ファイルを作成
    '--add-data', 'templates;templates',  # テンプレートフォルダを含める
    '--add-data', 'static;static',  # 静的ファイルを含める
    '--name', 'YayClient',  # 出力ファイル名
    '--icon', 'NONE',  # アイコンなし
    '--noconsole',  # コンソールウィンドウを表示しない
])

print("ビルドが完了しました。dist/YayClient.exeが生成されました。")