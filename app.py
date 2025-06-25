from flask import Flask
import configparser
from source.admin import admin_bp
from source.post import post_bp
from source.dba import *
import os

def cosplaydiva_run():
    # 讀取設定
    config = configparser.ConfigParser()
    with open('config.ini', 'r', encoding='utf-8-sig') as f:
        config.read_file(f)

    WEB_CHN_NAME    = config.get('web', 'chinese_name')
    WEB_ENG_NAME    = config.get('web', 'english_name')
    DB_PATH         = config.get('app', 'sql_file')
    SECRET_KEY      = config.get('app', 'secret_key')
    ADMIN_PSWD      = config.get('app', 'admin_password')
    HASH_SALT       = config.get('security', 'hash_salt')
    DBG_MODE        = config.getboolean('app', 'debug')

    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    # --- 藍圖註冊 ---
    app.register_blueprint(post_bp)   # 一般功能
    app.register_blueprint(admin_bp)  # 管理員功能

    # 0. 檢查執行資料夾是否存在，若不存在則建立
    if not os.path.exists('apprun'):
        os.makedirs('apprun')
    DB_PATH = os.path.join('apprun', DB_PATH)

    # 1. 設定資料庫路徑和管理員密碼
    app.logger.info(f"> 設定資料庫路徑: {DB_PATH}")
    app.logger.info(f"> 設定管理員密碼: {ADMIN_PSWD}")
    app.logger.info(f"> 設定密碼鹽: {HASH_SALT}")
    setup_config(DB_PATH, ADMIN_PSWD, HASH_SALT)
    
    # 2. 資料庫相關初始化
    # check path "run" has exist?
    if not os.path.exists(DB_PATH):
        app.logger.info(f"> 初始化資料庫 {DB_PATH}...")
    init_db()

    # 3. 網頁服務啟用
    return app

if __name__ == '__main__':
    _app = cosplaydiva_run()
    _app.run(debug=True, host="127.0.0.1", port=5000)