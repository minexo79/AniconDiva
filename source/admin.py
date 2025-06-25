# admin.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from .dba import *    # 如果你的檔案結構在 admin.py、dba.py 同一資料夾，否則直接 import dba
import hashlib
import configparser
import io
import csv

admin_bp = Blueprint('admin', __name__, url_prefix='')

# 設定（與app.py一致，或可改從app.config取得）
config = configparser.ConfigParser()
config.read('config.ini')
HASH_SALT = config.get('security', 'hash_salt')

def hash_password(password):
    """給密碼加鹽做sha256 hash（與主程式一致）"""
    salted = HASH_SALT + password
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()

def login_required(func):
    """簡易管理員登入檢查（裝飾器）"""
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin.login'))    # <-- 用 admin.login
        return func(*args, **kwargs)
    return wrapper

# --- 管理員登入 ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """管理後台登入頁與驗證"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        pw_hash = hash_password(password)
        user = get_user_by_name_pw(username, pw_hash)
        if user:
            session['admin'] = username
            return redirect(url_for('admin.admin_index'))  # <-- 用 admin.admin_index
        else:
            flash('登入失敗，請檢查帳號密碼')
        return render_template('login.html')
    return render_template('login.html')

# --- 管理員登出 ---
@admin_bp.route('/logout')
@login_required
def logout():
    """管理員登出"""
    session.pop('admin', None)
    return redirect(url_for('admin.login'))     # <-- 用 admin.login

# --- 管理後台主頁（顯示留言列表/查ID） ---
@admin_bp.route('/admin')
@login_required
def admin_index():
    """管理後台留言列表，可用id查詢"""
    post_id = request.args.get('id', '').strip()
    if post_id:
        posts = get_posts_by_id(post_id)
    else:
        posts = get_all_posts()
    return render_template('admin.html', posts=posts)

# --- 查看留言內容 ---
@admin_bp.route('/view_post/<int:post_id>')
@login_required
def view_post(post_id):
    # 你如何取得 post 請自行根據 ORM/SQL 設計調整
    # 這裡假設回傳 (id, content, time, ip) tuple
    post = get_posts_by_id(post_id)   # 你需要實作這個
    if not post:
        return admin_index()
    
    _post = {
        'id': post[0][0],
        'nickname': post[0][1],
        'content': post[0][2],
        'timestamp': post[0][3],
        'ip': post[0][4],
        'user_agent': post[0][5]
    }

    return render_template('admin_view_post.html', post=_post)


# --- 刪除留言 ---
@admin_bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete(post_id):
    """管理員刪除留言"""
    delete_post(post_id)
    return redirect(url_for('admin.admin_index'))    # <-- 用 admin.admin_index

# --- 匯出留言CSV ---
@admin_bp.route('/export')
@login_required
def export():
    """管理員匯出留言(csv)"""
    rows = get_all_posts_csv()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Content', 'Timestamp', 'IP', 'User-Agent'])
    writer.writerows(rows)
    output.seek(0)
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))  # 加 BOM for Excel
    mem.seek(0)
    return send_file(mem, mimetype='text/csv', as_attachment=True, download_name='posts_export.csv')

# --- 管理員用戶管理 ---
@admin_bp.route('/admin_users', methods=['GET', 'POST'])
@login_required
def admin_users():
    """管理員清單與添加"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        password2 = request.form.get('password2', '').strip()
        if not username or not password or not password2:
            flash('所有欄位都必填')
        elif password != password2:
            flash('密碼不一致')
        elif get_user_by_name(username):
            flash('帳號已存在')
        else:
            pw_hash = hash_password(password)
            insert_user(username, pw_hash)
            flash('成功新增管理員')
        return redirect(url_for('admin.admin_users'))   # <-- 用 admin.admin_users
    # 取得所有管理員
    users = get_all_users()
    current_user = session['admin']
    row = get_user_by_name(current_user)
    current_user_id = row[0] if row else None
    return render_template('admin_users.html', users=users, current_user=current_user, current_user_id=current_user_id)

# --- 刪除管理員 ---
@admin_bp.route('/delete_admin/<int:user_id>', methods=['POST'])
@login_required
def delete_admin(user_id):
    """管理員列表中刪除（不能刪預設與自己）"""
    if user_id == 1:
        flash("系統預設管理員(編號1)不可刪除！", "warning")
        return redirect(url_for('admin.admin_users'))   # <-- 用 admin.admin_users
    row = get_username_by_id(user_id)
    if not row:
        flash("管理員不存在")
    elif row[0] == session['admin']:
        flash("不能刪除自己！")
    else:
        delete_user_by_id(user_id)
        flash(f"已刪除管理員: {row[0]}", "danger")
    return redirect(url_for('admin.admin_users'))      # <-- 用 admin.admin_users
