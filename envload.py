import os
import source.utils
from dotenv import load_dotenv

def load_environment_variables():   
    # check .env file exists
    if os.path.exists('.env'):
        load_dotenv()
    
    source.utils.SECRET_KEY         = os.environ.get("WEB_SECRET_KEY", "Your_Super_Secret_Key_123456")
    source.utils.ADMIN_PSWD         = os.environ.get("ADMIN_PASSWORD", "123456789abcdef")
    source.utils.HASH_SALT          = os.environ.get("PASSWORD_HASH_SALT", "MyUltraHashSalt_XYZ")
    source.utils.DBG_MODE           = os.environ.get("DEBUG_MODE", True)
    source.utils.DISCORD_POSTED_URL = os.environ.get("DISCORD_POSTED_WEBHOOK", None)
    source.utils.DISCORD_VERIFY_URL = os.environ.get("DISCORD_VERIFIED_WEBHOOK", None)
    source.utils.MYSQL_URL          = os.environ.get("MYSQL_URL", None)
    source.utils.MYSQL_PORT         = os.environ.get("MYSQL_PORT", None)
    source.utils.MYSQL_USER         = os.environ.get("MYSQL_USER", None)
    source.utils.MYSQL_PASSWORD     = os.environ.get("MYSQL_PASSWORD", None)
    source.utils.MYSQL_DATABASE     = os.environ.get("MYSQL_DATABASE", None)