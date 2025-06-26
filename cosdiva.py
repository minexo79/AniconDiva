from flask import Flask
import configparser
from source.admin import admin_bp
from source.post import post_bp
from source.dba import *
import source.utils
import os

app = Flask(__name__)
config = configparser.ConfigParser()

def cosdiva_init():
    global app
    """
    初始化 CosDiva 應用。
    這個函數會在應用啟動時被調用，進行必要的初始化工作。
    """
    with open('config.ini', 'r', encoding='utf-8-sig') as f:
        config.read_file(f)

    source.utils.DB_PATH            = config.get('app', 'sql_file')
    source.utils.SECRET_KEY         = config.get('app', 'secret_key')
    source.utils.ADMIN_PSWD         = config.get('app', 'admin_password')
    source.utils.HASH_SALT          = config.get('security', 'hash_salt')
    source.utils.DBG_MODE           = config.getboolean('app', 'debug')
    source.utils.DISCORD_POSTED_URL = config.get('webhook', 'discord_posted_url', fallback=None)
    source.utils.DISCORD_VERIFY_URL = config.get('webhook', 'discord_verify_url', fallback=None)

    app.secret_key = source.utils.SECRET_KEY
    # --- 藍圖註冊 ---
    app.register_blueprint(post_bp)   # 一般功能
    app.register_blueprint(admin_bp)  # 管理員功能

    # 0. 檢查執行資料夾是否存在，若不存在則建立
    if not os.path.exists('apprun'):
        os.makedirs('apprun')
    source.utils.DB_PATH = os.path.join('apprun', source.utils.DB_PATH)

    # 1. 設定資料庫路徑和管理員密碼
    app.logger.info(f"> 設定資料庫路徑: {source.utils.DB_PATH}")
    app.logger.info(f"> 設定管理員密碼: {source.utils.ADMIN_PSWD}")
    app.logger.info(f"> 設定密碼鹽: {source.utils.HASH_SALT}")
    setup_config(source.utils.DB_PATH, source.utils.ADMIN_PSWD, source.utils.HASH_SALT)

    # 2. 資料庫相關初始化
    # check path "run" has exist?
    if not os.path.exists(source.utils.DB_PATH):
        app.logger.info(f"> 初始化資料庫 {source.utils.DB_PATH}...")

    init_db()

cosdiva_init()

if __name__ == '__main__':

    # 3. 啟動 Flask 應用
    app.run(debug=source.utils.DBG_MODE)