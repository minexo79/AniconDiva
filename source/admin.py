# admin.py
from flask import current_app, Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from .utils.hash import hash_password
from .utils.default_dict import DefaultDict
import io
import csv
import math

# 2025.6.20 Blackcat: Modify Verified Approved and Rejected to reach admin / 2 threshold 
# 2025.6.28 Blackcat: Implement pagination for admin_verified to speed up loading
# 2025.6.29 Blackcat: Implement Verified Features
# 2025.7.23 Blackcat: Remove ConfigParser, use envload instead, Change dbaccess to SqlAlchemy
# 2025.7.25 Blackcar: Export CSV Changed to For Loop & Fix Pending Number Not Showing Issue
# 2025.7.31 Blackcat: Change Post Status To Int (With Operate ID)
# 2025.8.1 Blackcat: Add Admin User Management Features (Change Password), Add Logging (Using AvA For Header)

admin_bp = Blueprint('admin', __name__)

from functools import wraps
def login_required(func):
    """簡易管理員登入檢查（裝飾器）"""
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
    admin_dba = current_app.config.get('ADMIN_DBA')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        pw_hash = hash_password(password, admin_dba.hash_salt)
        user = admin_dba.get_user_by_name_pw(username, pw_hash)
        if user:
            session['admin'] = username
            current_app.logger.info('AvA => User %s logged in successfully', username)
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
    current_app.logger.info('AvA => User %s logged out', session.get('admin', 'Unknown'))
    session.pop('admin', None)
    return redirect(url_for('admin.login'))     # <-- 用 admin.login

@admin_bp.route('/admin_index')
@login_required
def admin_index():
    """管理後台首頁"""
    post_dba = current_app.config.get('POST_DBA')
    admin_name = session.get('admin', '未知管理員')
    # 待審核投稿數量
    pending_count = post_dba.get_posts_count(1)
    # 已審核通過投稿數量
    verified_count = post_dba.get_posts_count(2)
    # 已拒絕投稿數量
    rejected_count = post_dba.get_posts_count(3)
    # 已刪除投稿數量
    deleted_count = post_dba.get_posts_count(4)
    return render_template('admin_index.html',  admin_name=admin_name, 
                                                posted_count=pending_count, 
                                                verified_count=verified_count,
                                                rejected_count=rejected_count,
                                                deleted_count=deleted_count)

# --- 查看投稿內容 ---
@admin_bp.route('/view_post/<int:post_id>')
@login_required
def view_post(post_id):
    # 你如何取得 post 請自行根據 ORM/SQL 設計調整
    # 這裡假設回傳 (id, content, time, ip) tuple
    post_dba = current_app.config.get('POST_DBA')
    post = post_dba.get_posts_by_id(post_id)
    if not post:
        return admin_all_posts()
    
    _post = {
        'id': post[0].id,
        'nickname': post[0].nickname,
        'content': post[0].content,
        'timestamp': post[0].timestamp,
        'ip': post[0].ip,
        'user_agent': post[0].user_agent
    }

    return render_template('admin_view_post.html', post=_post)

# --- 管理員待審核投稿 ---
@admin_bp.route('/admin_pending')
@login_required
def admin_pending():
    """管理員待審核投稿列表（支援分頁）"""
    admin_dba = current_app.config.get('ADMIN_DBA')
    post_dba = current_app.config.get('POST_DBA')
    page = int(request.args.get('page', 1))
    per_page = 20
    # 直接呼叫 dba 封裝的分頁查詢
    posts = post_dba.get_posts_with_pagination(page, per_page, status=1)
    # 計算總數量
    total_count = post_dba.get_posts_count(1)

    # 計算每篇投稿的審核人數
    approved_review_counts = {post.id: admin_dba.get_post_review_count(post.id, 2) for post in posts}
    rejected_review_counts = {post.id: admin_dba.get_post_review_count(post.id, 3) for post in posts}

    # 計算總管理員數量與審核門檻
    total_admin = admin_dba.get_total_admin_count()
    # 審核門檻為總管理員數量的一半，至少1人
    threshold = max(1, total_admin // 2)
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
    return render_template('admin_pending.html', posts=posts, 
                           approved_review_counts=approved_review_counts, 
                           rejected_review_counts=rejected_review_counts,
                           threshold=threshold, 
                           pagination=pagination)

@admin_bp.route('/review_post/<int:post_id>', methods=['POST'])
@login_required
def review_post(post_id):
    """管理員審核投稿（通過/拒絕）"""
    admin_dba = current_app.config.get('ADMIN_DBA')
    post_dba = current_app.config.get('POST_DBA')
    decision = request.form.get('decision')  # 'approve' or 'reject'
    current_user = session['admin']
    row = admin_dba.get_user_by_name(current_user)
    admin_id = row.id if row else None
    if not admin_id:
        flash('找不到管理員資訊', 'danger')
        return redirect(url_for('admin.admin_pending'))
    # 若投稿已非 pending，禁止重複審核
    if post_dba.get_post_status(post_id) != 1:
        flash('此投稿已完成審核，無法重複操作', 'warning')
        return redirect(url_for('admin.admin_pending'))
    
    admin_dba.add_post_review(post_id, admin_id, decision)
    
    current_app.logger.info('AvA => User %s reviewed post %d with decision %s',    current_user, 
                                                                                    post_id, 
                                                                                    DefaultDict.OperateDict[int(decision)].label)

    # 計算已審核人數
    approved_review_count = admin_dba.get_post_review_count(post_id, 2)
    rejected_review_count = admin_dba.get_post_review_count(post_id, 3)

    total_admin = admin_dba.get_total_admin_count()
    threshold = max(1, total_admin // 2)

    # 達到人數門檻才通過
    if decision == '2':
        if approved_review_count < threshold:    
            flash(f'已審核，尚需 {threshold - approved_review_count} 人審核', 'info')
        else:
            admin_dba.update_post_status(post_id, 2)
            flash('投稿已通過審核', 'success')
    # 達到人數門檻才拒絕
    elif decision == '3':         
        if rejected_review_count < threshold:
            flash(f'已審核，尚需 {threshold - rejected_review_count} 人審核', 'info')
        else:
            admin_dba.update_post_status(post_id, 3)
            flash('投稿已被拒絕', 'danger')

    return redirect(url_for('admin.admin_pending'))

# --- 管理後台 - 全部投稿（含所有狀態） ---
@admin_bp.route('/admin_all_posts')
@login_required
def admin_all_posts():
    """管理後台全部投稿（可依狀態篩選）"""
    post_dba = current_app.config.get('POST_DBA')
    page = int(request.args.get('page', 1))
    per_page = 20
    status = request.args.get('status', 'all')
    # ALL: 顯示所有投稿
    # PENDING: 待審核
    # APPROVED: 已審核通過
    # REJECTED: 已拒絕
    posts = post_dba.get_posts_with_pagination(page, per_page, status)
    total_count = post_dba.get_posts_count(status)
    # 計算總頁數
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
    admin_dba = current_app.config.get('ADMIN_DBA')
    current_user = session['admin']
    row = admin_dba.get_user_by_name(current_user)
    current_user_id = row.id if row else None
    return render_template('admin_env.html', 
                           current_user_id=current_user_id,
                           debug_mode=current_app.config.get('DEBUG'),
                           discord_posted_url=current_app.config.get('DISCORD_POSTED_URL'),
                           discord_verified_url=current_app.config.get('DISCORD_VERIFY_URL'),
                           mysql_url=current_app.config.get('MYSQL_URL'),
                           mysql_port=current_app.config.get('MYSQL_PORT'),
                           mysql_user=current_app.config.get('MYSQL_USER'),
                           mysql_database=current_app.config.get('MYSQL_DATABASE'))

# --- 刪除投稿 ---
@admin_bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete(post_id):
    """管理員刪除投稿"""
    admin_dba = current_app.config.get('ADMIN_DBA')

    admin_dba.delete_post(post_id)                       # 標記為已刪除   
    admin_dba.update_post_status(post_id, 4)             # 標記為已刪除

    current_app.logger.info('AvA => User %s deleted post %d', session['admin'], post_id)

    return redirect(url_for('admin.admin_all_posts'))    # <-- 用 admin.admin_verified   

# --- 管理員用戶管理 ---
@admin_bp.route('/admin_users', methods=['GET', 'POST'])
@login_required
def admin_users():
    """管理員清單與添加"""
    admin_dba = current_app.config.get('ADMIN_DBA')
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        password2 = request.form.get('password2', '').strip()
        if not username or not password or not password2:
            flash('所有欄位都必填')
        elif password != password2:
            flash('密碼不一致')
        elif admin_dba.get_user_by_name(username):
            flash('帳號已存在')
        else:
            pw_hash = hash_password(password, admin_dba.hash_salt)
            admin_dba.insert_user(username, pw_hash)

            current_app.logger.info('AvA => New user %s added', username)

            flash('成功新增管理員')
        return redirect(url_for('admin.admin_users'))   # <-- 用 admin.admin_users
    # 取得所有管理員
    users = admin_dba.get_all_users()
    current_user = session['admin']
    row = admin_dba.get_user_by_name(current_user)
    is_superadmin = row.superadmin if row else None

    return render_template('admin_users.html',  users=users, 
                                                current_user=current_user, 
                                                is_superadmin=is_superadmin)

# --- 刪除管理員 ---
@admin_bp.route('/delete_admin/<int:user_id>', methods=['POST'])
@login_required
def delete_admin(user_id):
    """管理員列表中刪除（不能刪預設與自己）"""
    admin_dba = current_app.config.get('ADMIN_DBA')
    if user_id == 1:
        flash("系統預設管理員(編號1)不可刪除！", "warning")
        return redirect(url_for('admin.admin_users'))   # <-- 用 admin.admin_users
    row = admin_dba.get_username_by_id(user_id)
    if not row:
        flash("管理員不存在")
    elif row == session['admin']:
        flash("不能刪除自己！")
    else:
        admin_dba.delete_user_by_id(user_id)

        current_app.logger.info('AvA => Deleted admin user: %s', row)

        flash(f"已刪除管理員: {row}", "danger")
    return redirect(url_for('admin.admin_users'))      # <-- 用 admin.admin_users

# --- 更改密碼 --- 
@admin_bp.route('/change_password/<int:user_id>', methods=['POST'])
@login_required
def change_password(user_id):
    """管理員更改密碼"""
    admin_dba = current_app.config.get('ADMIN_DBA')

    password = request.form.get('password', '').strip()
    password2 = request.form.get('password2', '').strip()

    if not password or not password2:
        flash('密碼欄位不可為空', 'warning')
        return redirect(url_for('admin.admin_users'))  # <-- 用 admin.admin_users
    
    if password != password2:
        flash('兩次密碼輸入不一致', 'warning')
        return redirect(url_for('admin.admin_users'))
    
    pw_hash = hash_password(password, admin_dba.hash_salt)
    admin_dba.change_password(user_id, pw_hash)
    current_app.logger.info('AvA => Change password for user id %s', user_id)

    flash(f"已更改管理員密碼，請重新登入", "success")
    return redirect(url_for('admin.admin_users'))      # <-- 用 admin.admin_users




# --- 匯出投稿CSV ---
@admin_bp.route('/admin_export')
@login_required
def admin_export():
    """管理員匯出投稿(csv)"""
    post_dba = current_app.config.get('POST_DBA')
    rows = post_dba.get_all_posts()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Nickname", "Content", "IP", "User-Agent", "Tag", "Status", "Timestamp"])

    # 遍歷所有投稿資料，寫入CSV
    for row in rows:
        writer.writerow([row.id, row.nickname, row.content, row.ip, row.user_agent, row.tag, row.status, row.timestamp ])

    output.seek(0)
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))  # 加 BOM for Excel
    mem.seek(0)

    current_app.logger.info('AvA => Exported posts to CSV')

    return send_file(mem, mimetype='text/csv', as_attachment=True, download_name='posts_export.csv')

# --- 匯入投稿CSV ---
@admin_bp.route('/admin_import', methods=['GET', 'POST'])
@login_required
def admin_import():
    """管理員匯入投稿(csv)"""
    post_dba = current_app.config.get('POST_DBA')
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('請選擇要上傳的CSV檔案', 'warning')
            return redirect(url_for('admin.admin_env'))
        try:
            stream = io.StringIO(file.stream.read().decode('utf-8-sig'))
            reader = csv.reader(stream)
            header = next(reader, None)
            expected_header = ["ID", "Nickname", "Content", "IP", "User-Agent", "Tag", "Status", "Timestamp"]
            if header != expected_header:
                flash('CSV欄位格式錯誤，請使用正確的匯出格式', 'danger')
                return redirect(url_for('admin.admin_env'))
            imported = 0
            for row in reader:
                if not any(row):
                    continue
                try:
                    _, nickname, content, ip, user_agent, tag, status, timestamp = row
                    post_dba.insert_post(nickname, content, ip, user_agent, timestamp, tag, status)
                    imported += 1
                except Exception as e:
                    flash(f'匯入失敗: {e}', 'danger')
                    continue
                
            current_app.logger.info('AvA => Imported %d posts from CSV', imported)
            
            flash(f'成功匯入 {imported} 筆投稿', 'success')
            return redirect(url_for('admin.admin_env'))
        except Exception as e:
            flash(f'檔案處理失敗: {e}', 'danger')
            return redirect(url_for('admin.admin_env'))
    return render_template('admin_import.html')
