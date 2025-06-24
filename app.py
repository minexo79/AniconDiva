from flask import Flask
import configparser
from source.admin import admin_bp
from source.post import post_bp
from source.dba import *
import os

# 讀取設定
config = configparser.ConfigParser()
config.read('config.ini')

SECRET_KEY = config.get('app', 'secret_key')
DB_PATH = 'posts.db'
ADMIN_PSWD = config.get('app', 'admin_password')
HASH_SALT = config.get('security', 'hash_salt')

app = Flask(__name__)
app.secret_key = SECRET_KEY

# --- 資料表初始化 ---
def hash_password(password):
    import hashlib
    salted = HASH_SALT + password
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()

def init_db():
    import sqlite3
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # 留言表
        c.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                ip TEXT NOT NULL,
                user_agent TEXT NOT NULL
            )
        ''')
        # 用戶表
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        # admin預設帳號
        c.execute('SELECT COUNT(*) FROM users WHERE username=?', ('admin',))
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (
                'admin', hash_password(ADMIN_PSWD)
            ))
        conn.commit()

# --- 藍圖註冊 ---
app.register_blueprint(post_bp)   # 一般功能
app.register_blueprint(admin_bp)  # 管理員功能

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
