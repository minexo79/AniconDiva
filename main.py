from flask import Flask
import configparser
from source.admin import admin_bp
from source.post import post_bp
from source.dba import *
import source.utils
import envload
import os

# 2025.6.26 Blackcat: Change to use environment variables instead of config.ini

app = Flask(__name__)
config = configparser.ConfigParser()

def anicondiva_init():
    global app
    """
    初始化 AniconDiva。
    這個函數會在應用啟動時被調用，進行必要的初始化工作。
    """
    # 0. 檢查執行資料夾是否存在，若不存在則建立
    if not os.path.exists('config'):
        os.makedirs('config')

    # 1. Config 讀取
    envload.load_environment_variables()

    db_config = {
        'host': source.utils.MYSQL_URL,
        'port': source.utils.MYSQL_PORT,
        'user': source.utils.MYSQL_USER,
        'password': source.utils.MYSQL_PASSWORD,
        'database': source.utils.MYSQL_DATABASE,
        'charset': 'utf8mb4'
    }

    # --- 藍圖註冊 & Flask Scrcet Key 設定 ---
    app.secret_key = source.utils.SECRET_KEY
    app.register_blueprint(post_bp)   # 一般功能
    app.register_blueprint(admin_bp)  # 管理員功能

    # 2. 設定資料庫路徑和管理員密碼
    setup_config(db_config, source.utils.ADMIN_PSWD, source.utils.HASH_SALT)

    init_db()

anicondiva_init()

if __name__ == '__main__':
    # 3. 啟動 Flask 應用
    app.run(debug=source.utils.DBG_MODE)