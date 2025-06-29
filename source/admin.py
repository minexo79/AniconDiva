# admin.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from .dba import *    # 如果你的檔案結構在 admin.py、dba.py 同一資料夾，否則直接 import dba
import hashlib
import source.utils
import configparser
import io
import csv
import math

# 2025.6.28 Blackcat: Implement pagination for admin_verified to speed up loading

admin_bp = Blueprint('admin', __name__, url_prefix='')

def hash_password(password):
    """給密碼加鹽做sha256 hash（與主程式一致）"""
    salted = source.utils.HASH_SALT + password
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

@admin_bp.route('/admin_index')
@login_required
def admin_index():
    """管理後台首頁"""
    admin_name = session.get('admin', '未知管理員')
    # 已審核通過投稿數量
    verified_count = get_posts_count_by_status('approved')
    # 待審核投稿數量
    pending_count = get_posts_count_by_status('pending')
    # 已拒絕投稿數量
    rejected_count = get_posts_count_by_status('rejected')
    return render_template('admin_index.html',  admin_name=admin_name, 
                                                posted_count=pending_count, 
                                                verified_count=verified_count,
                                                rejected_count=rejected_count)

# --- 管理後台 - 已發布投稿（顯示投稿列表/查ID） ---
@admin_bp.route('/admin_verified')
@login_required
def admin_verified():
    """管理後台已發布投稿列表，只顯示已審核通過"""
    post_id = request.args.get('id', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 20  # 管理員頁面顯示更多內容
    pagination = None
    
    if post_id:
        posts = [row for row in get_posts_by_id(post_id) if get_post_status(row[0]) == 'approved']
    else:
        # 只顯示已審核通過
        all_rows = get_posts_with_pagination(page, per_page)
        posts = [row for row in all_rows if get_post_status(row[0]) == 'approved']
        total_count = get_posts_count_by_status('approved')
        import math
        total_pages = math.ceil(total_count / per_page)
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total_count,
            'pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_num': page - 1 if page > 1 else None,
            'next_num': page + 1 if page < total_pages else None
        }
    
    return render_template('admin_verified.html', posts=posts, pagination=pagination)

# --- 查看投稿內容 ---
@admin_bp.route('/view_post/<int:post_id>')
@login_required
def view_post(post_id):
    # 你如何取得 post 請自行根據 ORM/SQL 設計調整
    # 這裡假設回傳 (id, content, time, ip) tuple
    post = get_posts_by_id(post_id)   # 你需要實作這個
    if not post:
        return admin_verified()
    
    _post = {
        'id': post[0][0],
        'nickname': post[0][1],
        'content': post[0][2],
        'timestamp': post[0][3],
        'ip': post[0][4],
        'user_agent': post[0][5]
    }

    return render_template('admin_view_post.html', post=_post)

# --- 管理員待審核投稿 ---
@admin_bp.route('/admin_pending')
@login_required
def admin_pending():
    """管理員待審核投稿列表（支援分頁）"""
    page = int(request.args.get('page', 1))
    per_page = 20
    # 直接呼叫 dba 封裝的分頁查詢
    posts = get_pending_posts_with_pagination(page, per_page)
    # 計算總數量
    total_count = get_pending_posts_count()
    # 計算每篇投稿的審核人數
    review_counts = {post[0]: get_post_review_count(post[0]) for post in posts}
    # 計算總管理員數量與審核門檻
    total_admin = get_total_admin_count()
    # 審核門檻為總管理員數量的一半，至少1人
    threshold = max(1, total_admin // 2)
    import math
    total_pages = math.ceil(total_count / per_page)
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_count,
        'pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page < total_pages else None
    }
    return render_template('admin_pending.html', posts=posts, review_counts=review_counts, threshold=threshold, pagination=pagination)

@admin_bp.route('/review_post/<int:post_id>', methods=['POST'])
@login_required
def review_post(post_id):
    """管理員審核投稿（通過/拒絕）"""
    decision = request.form.get('decision')  # 'approve' or 'reject'
    current_user = session['admin']
    row = get_user_by_name(current_user)
    admin_id = row[0] if row else None
    if not admin_id:
        flash('找不到管理員資訊', 'danger')
        return redirect(url_for('admin.admin_pending'))
    # 若投稿已非 pending，禁止重複審核
    if get_post_status(post_id) != 'pending':
        flash('此投稿已完成審核，無法重複操作', 'warning')
        return redirect(url_for('admin.admin_pending'))
    add_post_review(post_id, admin_id, decision)
    # 計算已審核人數
    review_count = get_post_review_count(post_id)
    total_admin = get_total_admin_count()
    threshold = max(1, total_admin // 2)
    if decision == 'approve' and review_count >= threshold:
        update_post_status(post_id, 'approved')
        flash('投稿已通過審核', 'success')
    elif decision == 'reject':
        update_post_status(post_id, 'rejected')
        flash('投稿已被拒絕', 'danger')
    else:
        flash(f'已審核，尚需 {threshold - review_count} 人審核', 'info')
    return redirect(url_for('admin.admin_pending'))

# --- 管理後台 - 全部投稿（含所有狀態） ---
@admin_bp.route('/admin_all_posts')
@login_required
def admin_all_posts():
    """管理後台全部投稿（可依狀態篩選）"""
    page = int(request.args.get('page', 1))
    per_page = 20
    status = request.args.get('status', 'all')
    # ALL: 顯示所有投稿
    # PENDING: 待審核
    # APPROVED: 已審核通過
    # REJECTED: 已拒絕
    if status == 'all':
        posts = get_posts_with_pagination(page, per_page)
        total_count = get_posts_count()
    else:
        posts = get_posts_with_pagination(page, per_page)
        # 篩選狀態
        posts = [post for post in posts if post[6] == status]
        total_count = get_posts_count_by_status(status)
    total_pages = math.ceil(total_count / per_page)
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_count,
        'pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page < total_pages else None
    }
    return render_template('admin_all_posts.html', posts=posts, pagination=pagination, status=status)

# --- 系統一覽 ---
@admin_bp.route('/admin_env')
@login_required
def admin_env():
    """管理後台系統一覽，當ID為1的管理員可見"""
    # 取得當言管理員ID
    current_user = session['admin']
    row = get_user_by_name(current_user)
    current_user_id = row[0] if row else None

    return render_template('admin_env.html', 
                           current_user_id=current_user_id,
                           debug_mode=source.utils.DBG_MODE,
                           discord_posted_url=source.utils.DISCORD_POSTED_URL,
                           discord_verified_url=source.utils.DISCORD_VERIFY_URL,
                           mysql_url=source.utils.MYSQL_URL,
                           mysql_port=source.utils.MYSQL_PORT,
                           mysql_user=source.utils.MYSQL_USER,
                           mysql_database=source.utils.MYSQL_DATABASE)

# --- 刪除投稿 ---
@admin_bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete(post_id):
    """管理員刪除投稿"""
    delete_post(post_id)
    return redirect(url_for('admin.admin_verified'))    # <-- 用 admin.admin_verified   

# --- 匯出投稿CSV ---
@admin_bp.route('/admin_export')
@login_required
def admin_export():
    """管理員匯出投稿(csv)"""
    rows = get_all_posts_csv()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Nickname' ,'Content', 'Timestamp', 'IP', 'User-Agent', 'Status'])
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

# --- 匯入投稿CSV ---
@admin_bp.route('/admin_import', methods=['GET', 'POST'])
@login_required
def admin_import():
    """管理員匯入投稿(csv)"""
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('請選擇要上傳的CSV檔案', 'warning')
            return redirect(url_for('admin.admin_env'))
        try:
            stream = io.StringIO(file.stream.read().decode('utf-8-sig'))
            reader = csv.reader(stream)
            header = next(reader, None)
            expected_header = ['ID', 'Nickname', 'Content', 'Timestamp', 'IP', 'User-Agent', 'Status']
            if header != expected_header:
                flash('CSV欄位格式錯誤，請使用正確的匯出格式', 'danger')
                return redirect(url_for('admin.admin_env'))
            imported = 0
            for row in reader:
                if not any(row):
                    continue
                try:
                    _, nickname, content, timestamp, ip, user_agent, status = row
                    if status not in ['pending', 'approved', 'rejected']:
                        status = 'pending'
                    import_post_row(nickname, content, timestamp, ip, user_agent, status)
                    imported += 1
                except Exception as e:
                    flash(f'匯入失敗: {e}', 'danger')
                    continue
            flash(f'成功匯入 {imported} 筆投稿', 'success')
            return redirect(url_for('admin.admin_env'))
        except Exception as e:
            flash(f'檔案處理失敗: {e}', 'danger')
            return redirect(url_for('admin.admin_env'))
    return render_template('admin_import.html')
