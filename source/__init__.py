from flask import Flask
from .dba.init import db, AdminInitDB
from .dba.guest import GuestDBA
from .dba.admin import AdminDBA
from .dba.post import PostDBA
from .utils import envload
import os

# 2025.6.26 Blackcat: Change to use environment variables instead of config.ini
# 2025.7.23 Blackcat: Remove ConfigParser, use envload instead, Change dbAccess to SqlAlchemy
# 2025.7.25 Blackcat: Change To Factory Mode

project_root    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir    = os.path.join(project_root, 'templates')
static_dir      = os.path.join(project_root, 'static')

def anicondiva_init() -> Flask:
    """
    初始化 AniconDiva 環境設定。
    """
    # Get the parent directory (project root) for templates and static files
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    # 直接將環境變數寫入 app.config
    envload.load_environment_variables(app)

    app.secret_key = app.config['SECRET_KEY']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if app.config['DEBUG']:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(project_root, 'test.db')}"
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"mysql+pymysql://{app.config['MYSQL_USER']}:{app.config['MYSQL_PASSWORD']}@"
            f"{app.config['MYSQL_URL']}:{app.config['MYSQL_PORT']}/{app.config['MYSQL_DATABASE']}"
        )

    """
    初始化 AniconDiva 的資料庫。
    這個函數會在應用啟動時被調用，進行必要的資料庫初始化工作。
    """
    guest_dba   = GuestDBA()
    post_dba    = PostDBA()
    admin_dba   = AdminDBA(hash_salt=app.config['HASH_SALT'])
    admin_init  = AdminInitDB(admin_pswd=app.config['ADMIN_PSWD'], hash_salt=app.config['HASH_SALT'])
    
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