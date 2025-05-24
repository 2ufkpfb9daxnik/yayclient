from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
import yaylib
import threading
from datetime import datetime
import asyncio
import signal
import sys
import secrets
import webbrowser
from threading import Timer
from yaylib.errors import Required2FAError

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
posts_lock = threading.Lock()
yay_client = None

def open_browser():
    """ブラウザで自動的にアプリケーションを開く"""
    webbrowser.open('http://127.0.0.1:5000')

def signal_handler(sig, frame):
    """シグナルハンドラー"""
    print("\nアプリケーションを終了します...")
    sys.exit(0)

def get_client(allow_anonymous=True):
    """認証済みのクライアントを取得"""
    global yay_client
    if not yay_client and 'email' in session and 'password' in session:
        try:
            client = yaylib.Client()
            try:
                client.login(session['email'], session['password'])
                yay_client = client
            except Required2FAError:
                print("2FA required, using anonymous client for viewing")
                if not allow_anonymous:
                    raise
        except Exception as e:
            print(f"クライアント初期化エラー: {str(e)}")
            if not allow_anonymous:
                raise
    
    return yay_client if yay_client else (yaylib.Client() if allow_anonymous else None)

def fetch_posts(timeline_type='open'):
    """投稿を取得"""
    try:
        client = get_client(allow_anonymous=True)
        
        if timeline_type == 'following' and session.get('email'):
            timeline = client.get_following_timeline(number=30)
        else:
            timeline = client.get_timeline(number=30)
        
        return [{
            'text': post.text,
            'user': {
                'nickname': post.user.nickname
            },
            'likes_count': post.likes_count,
            'reposts_count': post.reposts_count,
            'in_reply_to_post_count': post.in_reply_to_post_count,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        } for post in timeline.posts]
    except Exception as e:
        print(f"投稿取得エラー: {str(e)}")
        return []

@app.route('/')
def index():
    """メインページを表示"""
    return render_template('index.html', email=session.get('email'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ログイン処理"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            global yay_client
            client = yaylib.Client()
            try:
                client.login(email, password)
            except Required2FAError:
                # 2FAエラーの場合でもログイン情報を保存
                pass
            
            session['email'] = email
            session['password'] = password
            yay_client = client
            
            return redirect(url_for('index'))
        except Exception as e:
            print(f"ログインエラー: {str(e)}")
            flash('ログインに失敗しました。メールアドレスとパスワードを確認してください。')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """ログアウト処理"""
    global yay_client
    session.clear()
    yay_client = None
    return redirect(url_for('index'))

@app.route('/posts')
def get_posts():
    """投稿を取得するAPI"""
    try:
        timeline_type = request.args.get('type', 'open')
        posts = fetch_posts(timeline_type)
        return jsonify(posts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/post', methods=['POST'])
def create_post():
    """新規投稿を作成"""
    if 'email' not in session:
        return jsonify({'error': 'ログインが必要です'}), 401
    
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': '投稿内容を入力してください'}), 400
        
        # 投稿専用のクライアントを作成
        post_client = yaylib.Client()
        try:
            post_client.login(session['email'], session['password'])
            post_client.create_post(text)
            return jsonify({'success': True})
        except Required2FAError:
            return jsonify({'error': '2段階認証が必要な場合は投稿できません'}), 403
            
    except Exception as e:
        print(f"投稿エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500

def run_app():
    """アプリケーションの実行"""
    signal.signal(signal.SIGINT, signal_handler)
    
    # 1秒後にブラウザを開く（サーバー起動を待つため）
    Timer(1.0, open_browser).start()
    
    # 開発サーバーを起動
    app.run(debug=False, threaded=True)

if __name__ == '__main__':
    run_app()