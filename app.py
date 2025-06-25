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



# --- 藍圖註冊 ---
app.register_blueprint(post_bp)   # 一般功能
app.register_blueprint(admin_bp)  # 管理員功能

if __name__ == '__main__':
    # 資料庫相關初始化
    setup_config(DB_PATH, ADMIN_PSWD, HASH_SALT)
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
