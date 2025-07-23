from flask import Flask
from source.dba.init import db, AdminInitDB
from source.dba.guest import GuestDBA
from source.dba.admin import AdminDBA
from source.dba.post import PostDBA
import source.utils
import envload

# 2025.6.26 Blackcat: Change to use environment variables instead of config.ini
# 2025.7.23 Blackcat: Remove ConfigParser, use envload instead, Change dbAccess to SqlAlchemy

app = Flask(__name__)
admin_init = None

def anicondiva_init():
    """
    初始化 AniconDiva 環境設定。
    """
    # Config 讀取
    envload.load_environment_variables()

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{source.utils.MYSQL_USER}:{source.utils.MYSQL_PASSWORD}@{source.utils.MYSQL_URL}:{source.utils.MYSQL_PORT}/{source.utils.MYSQL_DATABASE}'
    app.secret_key = source.utils.SECRET_KEY

def anicondiva_db_init():
    """
    初始化 AniconDiva 的資料庫。
    這個函數會在應用啟動時被調用，進行必要的資料庫初始化工作。
    """
    global admin_init

    guest_dba   = GuestDBA()
    post_dba    = PostDBA()
    admin_dba   = AdminDBA(hash_salt=source.utils.HASH_SALT)
    admin_init  = AdminInitDB(admin_pswd=source.utils.ADMIN_PSWD, 
                             hash_salt=source.utils.HASH_SALT)
    
    app.config['GUEST_DBA'] = guest_dba
    app.config['ADMIN_DBA'] = admin_dba
    app.config['POST_DBA'] = post_dba

def anicondiva_app_init():
    """
    設定 AniconDiva 的 Flask 應用。
    """
    global app
    # 藍圖註冊 & Flask Secret Key 設定
    from source.post import post_bp
    from source.admin import admin_bp

    app.register_blueprint(post_bp)   # 一般功能
    app.register_blueprint(admin_bp)  # 管理員功能

    with app.app_context():
        db.init_app(app)
        admin_init.init_db()    # 初始化管理員預設帳號

anicondiva_init()
anicondiva_db_init()
anicondiva_app_init()

if __name__ == '__main__':
    # 5. 啟動 Flask 應用
    app.run(debug=source.utils.DBG_MODE)