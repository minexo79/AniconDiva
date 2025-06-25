# dba.py
# ----- 所有與資料庫交互的function封裝 -----

import sqlite3
from datetime import datetime

DB_PATH = 'posts.db'

def setup_config(db_path: str, admin_pswd: str, hash_salt: str):
    """在app一開始呼叫，統一帶入db資訊和密碼鹽"""
    global DB_PATH, ADMIN_PSWD, HASH_SALT
    DB_PATH = db_path
    ADMIN_PSWD = admin_pswd
    HASH_SALT = hash_salt

def hash_password(password):
    """使用SHA-256加密密碼，並加上HASH_SALT"""
    import hashlib
    salted = HASH_SALT + password
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()

def init_db():
    """初始化資料表，預設admin帳號"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # 留言表
        c.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                ip TEXT NOT NULL,
                user_agent TEXT NOT NULL
            )
        ''')
        # 用戶表
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        # admin預設帳號
        if ADMIN_PSWD is not None and HASH_SALT is not None:
            c.execute('SELECT COUNT(*) FROM users WHERE username=?', ('admin',))
            if c.fetchone()[0] == 0:
                c.execute('INSERT INTO users (username, password) VALUES (?,?)',
                        ('admin', hash_password(ADMIN_PSWD)))
        conn.commit()


# --- 使用者管理相關 -----
def get_user_by_name_pw(username, pw_hash):
    """用帳號+密碼hash查詢用戶資料（for login）"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=? AND password=?', (username, pw_hash))
        return c.fetchone()

def get_user_by_name(username):
    """用帳號查詢用戶"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=?', (username,))
        return c.fetchone()

def insert_user(username, pw_hash):
    """插入新用戶（管理員）"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, pw_hash))
        conn.commit()

def get_all_users():
    """取得所有用戶（管理員）清單"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT id, username FROM users')
        return c.fetchall()

def delete_user_by_id(user_id):
    """刪除用戶（管理員）"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM users WHERE id=?', (user_id,))
        conn.commit()

def get_username_by_id(user_id):
    """用id查詢username"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT username FROM users WHERE id=?', (user_id,))
        return c.fetchone()

# --- 貼文管理相關 -----

def insert_post(nickname, content, ip, user_agent):
    """新增一則投稿"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('INSERT INTO posts (nickname, content, timestamp, ip, user_agent) VALUES (?, ?, ?, ?, ?)',
                  (nickname, content, timestamp, ip, user_agent))
        conn.commit()

def get_posts_by_id(post_id):
    """根據ID查詢單則投稿（回傳list of rows）"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, nickname, content, timestamp, ip, user_agent FROM posts WHERE id=?', (post_id,))
        return c.fetchall()

def get_posts_by_keyword(query):
    """根據關鍵字模糊查詢投稿"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, nickname, content, timestamp, ip, user_agent FROM posts WHERE content LIKE ? ORDER BY id DESC', 
                  (f'%{query}%',))
        return c.fetchall()

def get_all_posts():
    """取得所有投稿（排序由新到舊）"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, nickname, content, timestamp, ip, user_agent FROM posts ORDER BY id DESC')
        return c.fetchall()

def delete_post(post_id):
    """刪除特定投稿"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()

def get_all_posts_csv():
    """取得所有投稿（for 匯出CSV）"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, nickname, content, timestamp, ip, user_agent FROM posts')
        return c.fetchall()
