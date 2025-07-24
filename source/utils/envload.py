import os
from . import config
from dotenv import load_dotenv

def load_environment_variables():   
    # check .env file exists
    if os.path.exists('.env'):
        load_dotenv()

    config.SECRET_KEY         = os.environ.get("WEB_SECRET_KEY", "Your_Super_Secret_Key_123456")
    config.ADMIN_PSWD         = os.environ.get("ADMIN_PASSWORD", "123456789abcdef")
    config.HASH_SALT          = os.environ.get("PASSWORD_HASH_SALT", "MyUltraHashSalt_XYZ")
    config.DBG_MODE           = os.environ.get("DEBUG_MODE", True)
    config.DISCORD_POSTED_URL = os.environ.get("DISCORD_POSTED_WEBHOOK", None)
    config.DISCORD_VERIFY_URL = os.environ.get("DISCORD_VERIFIED_WEBHOOK", None)
    config.MYSQL_URL          = os.environ.get("MYSQL_URL", None)
    config.MYSQL_PORT         = os.environ.get("MYSQL_PORT", None)
    config.MYSQL_USER         = os.environ.get("MYSQL_USER", None)
    config.MYSQL_PASSWORD     = os.environ.get("MYSQL_PASSWORD", None)
    config.MYSQL_DATABASE     = os.environ.get("MYSQL_DATABASE", None)