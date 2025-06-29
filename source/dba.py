# dba.py
# ----- 所有與資料庫交互的function封裝 -----

import mysql.connector
from mysql.connector import pooling
from datetime import datetime
import threading

# 2025.6.28 Blackcat: Implement connection_pool to speed up loading

# MySQL 連線設定
DB_CONFIG = None
CONNECTION_POOL = None
_pool_lock = threading.Lock()

def setup_config(db_config: dict, admin_pswd: str, hash_salt: str):
    """在app一開始呼叫，統一帶入db資訊和密碼鹽，並初始化連接池"""
    global DB_CONFIG, ADMIN_PSWD, HASH_SALT, CONNECTION_POOL
    DB_CONFIG = db_config
    ADMIN_PSWD = admin_pswd
    HASH_SALT = hash_salt
    
    # 初始化連接池
    try:
        CONNECTION_POOL = pooling.MySQLConnectionPool(
            pool_name="mysql_pool",
            pool_size=20,  # 最大連接數
            pool_reset_session=True,
            **DB_CONFIG
        )
    except mysql.connector.Error as e:
        print(f"連接池初始化失敗: {e}")
        CONNECTION_POOL = None

def hash_password(password):
    """使用SHA-256加密密碼，並加上HASH_SALT"""
    import hashlib
    salted = HASH_SALT + password
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()

def get_conn():
    """獲取資料庫連接，優先使用連接池"""
    global CONNECTION_POOL
    if CONNECTION_POOL:
        try:
            return CONNECTION_POOL.get_connection()
        except mysql.connector.Error as e:
            print(f"從連接池獲取連接失敗: {e}")
            # 如果連接池失敗，回退到直接連接
            return mysql.connector.connect(**DB_CONFIG)
    else:
        return mysql.connector.connect(**DB_CONFIG)

def init_db():
    """初始化資料表，預設admin帳號"""
    with get_conn() as conn:
        c = conn.cursor()

        # 留言表
        c.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nickname VARCHAR(16) NOT NULL,
                content TEXT NOT NULL,
                timestamp VARCHAR(32) NOT NULL,
                ip VARCHAR(64) NOT NULL,
                user_agent VARCHAR(255) NOT NULL
            )
        ''')
        # 用戶表
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(16) NOT NULL UNIQUE,
                password VARCHAR(64) NOT NULL
            )
        ''')
        # admin預設帳號
        if ADMIN_PSWD is not None and HASH_SALT is not None:
            c.execute('SELECT COUNT(*) FROM users WHERE username=%s', ('admin',))
            if c.fetchone()[0] == 0:
                c.execute('INSERT INTO users (username, password) VALUES (%s,%s)',
                        ('admin', hash_password(ADMIN_PSWD)))
                
        conn.commit()


# --- 使用者管理相關 -----
def get_user_by_name_pw(username, pw_hash):
    """用帳號+密碼hash查詢用戶資料（for login）"""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=%s AND password=%s', (username, pw_hash))
        return c.fetchone()

def get_user_by_name(username):
    """用帳號查詢用戶"""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=%s', (username,))
        return c.fetchone()

def insert_user(username, pw_hash):
    """插入新用戶（管理員）"""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, pw_hash))
        conn.commit()

def get_all_users():
    """取得所有用戶（管理員）清單"""
    with get_conn() as conn:
        c = conn.cursor(dictionary=True)
        c.execute('SELECT id, username FROM users')
        return c.fetchall()

def delete_user_by_id(user_id):
    """刪除用戶（管理員）"""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM users WHERE id=%s', (user_id,))
        conn.commit()

def get_username_by_id(user_id):
    """用id查詢username"""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('SELECT username FROM users WHERE id=%s', (user_id,))
        return c.fetchone()

# --- 貼文管理相關 -----

def insert_post(nickname, content, ip, user_agent, timestamp: None) -> int:
    """新增一則投稿"""
    with get_conn() as conn:
        c = conn.cursor()
        if (timestamp is None):
            # 如果沒有提供時間戳，則使用當前時間
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('INSERT INTO posts (nickname, content, timestamp, ip, user_agent) VALUES (%s, %s, %s, %s, %s)',
                  (nickname, content, timestamp, ip, user_agent))
        conn.commit()
        new_id = c.lastrowid
        return new_id

def get_posts_by_id(post_id):
    """根據ID查詢單則投稿（回傳list of rows）"""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('SELECT id, nickname, content, timestamp, ip, user_agent FROM posts WHERE id=%s', (post_id,))
        return c.fetchall()

def get_posts_by_keyword(query):
    """根據關鍵字模糊查詢投稿"""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('SELECT id, nickname, content, timestamp, ip, user_agent FROM posts WHERE content LIKE %s ORDER BY id DESC', 
                  (f'%{query}%',))
        return c.fetchall()

def get_all_posts():
    """取得所有投稿（排序由新到舊）"""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('SELECT id, nickname, content, timestamp, ip, user_agent FROM posts ORDER BY id DESC')
        return c.fetchall()

def get_posts_with_pagination(page=1, per_page=10):
    """取得分頁投稿（排序由新到舊）"""
    offset = (page - 1) * per_page
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('SELECT id, nickname, content, timestamp, ip, user_agent FROM posts ORDER BY id DESC LIMIT %s OFFSET %s', 
                  (per_page, offset))
        return c.fetchall()

def get_posts_count():
    """取得投稿總數"""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM posts')
        return c.fetchone()[0]

def get_posts_by_keyword_with_pagination(query, page=1, per_page=10):
    """根據關鍵字模糊查詢投稿（分頁）"""
    offset = (page - 1) * per_page
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('SELECT id, nickname, content, timestamp, ip, user_agent FROM posts WHERE content LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s', 
                  (f'%{query}%', per_page, offset))
        return c.fetchall()

def get_posts_count_by_keyword(query):
    """取得符合關鍵字的投稿總數"""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM posts WHERE content LIKE %s', (f'%{query}%',))
        return c.fetchone()[0]

def delete_post(post_id):
    """刪除特定投稿"""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM posts WHERE id = %s', (post_id,))
        conn.commit()

def get_all_posts_csv():
    """取得所有投稿（for 匯出CSV）"""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('SELECT id, nickname, content, timestamp, ip, user_agent FROM posts')
        return c.fetchall()
