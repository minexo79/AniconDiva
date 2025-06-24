# dba.py
# ----- 所有與資料庫交互的function封裝 -----

import sqlite3
from datetime import datetime

DB_PATH = 'posts.db'

def init_db(db_name: str):
    """指定DB位置"""
    global DB_PATH
    DB_PATH = db_name

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

def insert_post(content, ip, user_agent):
    """新增一則投稿"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('INSERT INTO posts (content, timestamp, ip, user_agent) VALUES (?, ?, ?, ?)',
                  (content, timestamp, ip, user_agent))
        conn.commit()

def get_posts_by_id(post_id):
    """根據ID查詢單則投稿（回傳list of rows）"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, content, timestamp, ip, user_agent FROM posts WHERE id=?', (post_id,))
        return c.fetchall()

def get_posts_by_keyword(query):
    """根據關鍵字模糊查詢投稿"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, content, timestamp, ip, user_agent FROM posts WHERE content LIKE ? ORDER BY id DESC', 
                  (f'%{query}%',))
        return c.fetchall()

def get_all_posts():
    """取得所有投稿（排序由新到舊）"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, content, timestamp, ip, user_agent FROM posts ORDER BY id DESC')
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
        c.execute('SELECT id, content, timestamp, ip, user_agent FROM posts')
        return c.fetchall()
