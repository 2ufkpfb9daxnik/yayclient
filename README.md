# YayClient

## インストール

```bash
git clone https://github.com/yourusername/yayclient.git
cd yayclient
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 実行

```bash
# 開発モード
python app.py

# exeファイル作成
python build.py
```

(dist/にビルド済みのものがあります)

## 操作方法

- `n`: 投稿フォームにフォーカス
- `Ctrl+Enter`: 投稿
- 更新間隔: 秒単位での調整可能
- タイムライン切り替え: オープン/フォロー中

## 開発

[yaylib](https://github.com/ekkx/yaylib)を使わせていただきました
