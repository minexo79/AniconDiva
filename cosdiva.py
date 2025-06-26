from flask import Flask
import configparser
from source.admin import admin_bp
from source.post import post_bp
from source.dba import *
import source.utils
import os

# 2025.6.26 Blackcat: Change to use environment variables instead of config.ini

app = Flask(__name__)
config = configparser.ConfigParser()

def cosdiva_init():
    global app
    """
    初始化 CosDiva 應用。
    這個函數會在應用啟動時被調用，進行必要的初始化工作。
    """
    # 0. 檢查執行資料夾是否存在，若不存在則建立
    if not os.path.exists('config'):
        os.makedirs('config')

    # 1. Config 讀取
    source.utils.DB_PATH            = os.environ.get("SQL_FILE", "posts.db")
    source.utils.SECRET_KEY         = os.environ.get("WEB_SECRET_KEY", "Your_Super_Secret_Key_123456")
    source.utils.ADMIN_PSWD         = os.environ.get("ADMIN_PASSWORD", "1234567890abcdef")
    source.utils.HASH_SALT          = os.environ.get("PASSWORD_HASH_SALT", "MyUltraHashSalt_XYZ")
    source.utils.DBG_MODE           = os.environ.get("DEBUG_MODE", False)
    source.utils.DISCORD_POSTED_URL = os.environ.get("DISCORD_POSTED_WEBHOOK", None)
    source.utils.DISCORD_VERIFY_URL = os.environ.get("DISCORD_VERIFIED_WEBHOOK", None)

    app.secret_key = source.utils.SECRET_KEY
    # --- 藍圖註冊 ---
    app.register_blueprint(post_bp)   # 一般功能
    app.register_blueprint(admin_bp)  # 管理員功能

    source.utils.DB_PATH = os.path.join('config', source.utils.DB_PATH)

    # 2. 設定資料庫路徑和管理員密碼
    app.logger.info(f"> 設定資料庫路徑: {source.utils.DB_PATH}")
    app.logger.info(f"> 設定管理員密碼: {source.utils.ADMIN_PSWD}")
    app.logger.info(f"> 設定密碼鹽: {source.utils.HASH_SALT}")
    setup_config(source.utils.DB_PATH, source.utils.ADMIN_PSWD, source.utils.HASH_SALT)

    # 3. 資料庫相關初始化
    # check path "run" has exist?
    if not os.path.exists(source.utils.DB_PATH):
        app.logger.info(f"> 初始化資料庫 {source.utils.DB_PATH}...")

    init_db()

cosdiva_init()

if __name__ == '__main__':
    # 4. 啟動 Flask 應用
    app.run(debug=source.utils.DBG_MODE)