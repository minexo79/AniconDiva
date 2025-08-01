from flask import Flask
from .dba.init import InitDB
from .dba.guest import GuestDBA
from .dba.admin import AdminDBA
from .dba.post import PostDBA
from .dba.model import db
from .utils import envload
from .utils.default_dict import DefaultDict 
from .utils.log import log_init
import os

# 2025.6.26 Blackcat: Change to use environment variables instead of config.ini
# 2025.7.23 Blackcat: Remove ConfigParser, use envload instead, Change dbAccess to SqlAlchemy
# 2025.7.25 Blackcat: Change To Factory Mode
# 2025.7.31 Blackcat: Change Post Status To Int (With Operate ID)
# 2025.8.1 Blackcat: Add Logging (Using AvA For Header), Fix DEBUG Mode Issue For Init

project_root    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir    = os.path.join(project_root, 'templates')
static_dir      = os.path.join(project_root, 'static')

def anicondiva_init() -> Flask:
    """
    初始化 AniconDiva 環境設定。
    """
    log_init()  # 初始化日誌系統
    
    # Get the parent directory (project root) for templates and static files
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    # 將環境變數寫入 app.config
    envload.load_environment_variables(app)
    app.logger.info('AvA => Environment Variables Loaded.')
    app.secret_key = app.config['SECRET_KEY']
    app.logger.info('AvA => Debug Mode: %s', app.config['DEBUG'])

    if app.config['DEBUG'] == 'True':   # 2025.8.1 Blackcat: 要用字串，不可用Bool
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(project_root, 'test.db')}"
        app.logger.info('AvA => Using SQLite for Database.')
    else:
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"mysql+pymysql://{app.config['MYSQL_USER']}:{app.config['MYSQL_PASSWORD']}@"
            f"{app.config['MYSQL_URL']}:{app.config['MYSQL_PORT']}/{app.config['MYSQL_DATABASE']}"
        )
        app.logger.info('AvA => Using MySQL for Database.')

    """
    初始化 AniconDiva 的資料庫。
    這個函數會在應用啟動時被調用，進行必要的資料庫初始化工作。
    """
    post_dba    = PostDBA()
    guest_dba   = GuestDBA(db)
    admin_dba   = AdminDBA(hash_salt=app.config['HASH_SALT'], db=db)
    admin_init  = InitDB(db=db, admin_pswd=app.config['ADMIN_PSWD'], hash_salt=app.config['HASH_SALT'], default_dict=DefaultDict())

    app.config['GUEST_DBA'] = guest_dba
    app.config['ADMIN_DBA'] = admin_dba
    app.config['POST_DBA']  = post_dba

    """
    設定 AniconDiva 的 Flask 應用。
    """
    # 藍圖註冊 & Flask Secret Key 設定
    from source.post import post_bp
    from source.admin import admin_bp

    app.register_blueprint(post_bp)   # 一般功能
    app.register_blueprint(admin_bp)  # 管理員功能

    with app.app_context():
        db.init_app(app)
        admin_init.init_db()    # 初始化管理員預設帳號

    return app