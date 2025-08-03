import os
from dotenv import load_dotenv

def load_environment_variables(app):
    # check .env file exists
    if os.path.exists('.env'):
        load_dotenv()

    app.config['SECRET_KEY']           = os.environ.get("WEB_SECRET_KEY", "Your_Super_Secret_Key_123456")
    app.config['ADMIN_PSWD']           = os.environ.get("ADMIN_PASSWORD", "123456789abcdef")
    app.config['HASH_SALT']            = os.environ.get("PASSWORD_HASH_SALT", "MyUltraHashSalt_XYZ")
    app.config['DEBUG']                = os.environ.get("DEBUG_MODE", 'True')
    app.config['DISCORD_POSTED_URL']   = os.environ.get("DISCORD_POSTED_WEBHOOK", None)
    app.config['DISCORD_VERIFY_URL']   = os.environ.get("DISCORD_VERIFIED_WEBHOOK", None)
    app.config['MYSQL_URL']            = os.environ.get("MYSQL_URL", None)
    app.config['MYSQL_PORT']           = os.environ.get("MYSQL_PORT", None)
    app.config['MYSQL_USER']           = os.environ.get("MYSQL_USER", None)
    app.config['MYSQL_PASSWORD']       = os.environ.get("MYSQL_PASSWORD", None)
    app.config['MYSQL_DATABASE']       = os.environ.get("MYSQL_DATABASE", None)

def build_sql_uri(app):
    if app.config['DEBUG'] == 'True':
        return f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.db')}"
    else:
        return (
            f"mysql+pymysql://{app.config['MYSQL_USER']}:{app.config['MYSQL_PASSWORD']}@"
            f"{app.config['MYSQL_URL']}:{app.config['MYSQL_PORT']}/{app.config['MYSQL_DATABASE']}"
        )