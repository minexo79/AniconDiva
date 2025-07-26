# post.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from . import social
import math

# 2025.6.29 Blackcat: Fix IP Display Issue
# 2025.6.28 Blackcat: Implement pagination for view_post to speed up loading
# 2025.6.26 Blackcat: Use HTTP_X_FORWARDED_FOR To get real IP address if use proxy
# 2025.7.23 Blackcat: Change id & q request.args.get to content & Change dbaccess to SqlAlchemy
# 2025.7.25 Blackcat: Get Only One Post by ID in create_post To Improve Performance
# 2025.7.26 Blackcat: Using Social Mode Instead webhook

post_bp = Blueprint('post', __name__)

@post_bp.route('/view_post', methods=['GET', 'POST'])
def view_post():
    post_dba = current_app.config.get('POST_DBA')
    page = int(request.args.get('page', 1))
    per_page = 10  # 統一每頁顯示10筆
    posts = []
    pagination = None

    query = request.args.get('query', '').strip()
    # GET 查詢流程
    if query:
        if query.isdigit():
            # 查詢特定ID的投稿（僅顯示已審核通過）
            rows = post_dba.get_posts_by_id(query)
            posts = [
                {'id': row.id, 'content': row.content, 'timestamp': row.timestamp, 'ip': row.ip, 'user_agent': row.user_agent}
                for row in rows
                if post_dba.get_post_status(row.id) == 'approved'
            ]
            total_count = len(posts)
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
            # 只顯示當前分頁內容
            start = (page - 1) * per_page
            end = start + per_page
            posts = posts[start:end]
        else:
            # 關鍵字搜尋（分頁，僅顯示已審核通過）
            rows = post_dba.get_posts_by_keyword_with_pagination(query, page, per_page, 'approved')
            total_count = rows.__len__()
            posts = [
                {'id': row.id, 'content': row.content, 'timestamp': row.timestamp, 'ip': row.ip, 'user_agent': row.user_agent}
                for row in rows
            ]
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
    else:
        # 顯示所有投稿（分頁，僅顯示已審核通過）
        rows = post_dba.get_posts_with_pagination(page, per_page, 'approved')
        total_count = post_dba.get_posts_count('approved')
        posts = [
            {'id': row.id, 'content': row.content, 'timestamp': row.timestamp, 'ip': row.ip, 'user_agent': row.user_agent}
            for row in rows
        ]
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

    return render_template('view_post.html', posts=posts, query=query, pagination=pagination)


@post_bp.route('/rules', methods=['GET'])
def rules():
    # 顯示規則頁面
    return render_template('rules.html')

@post_bp.route('/create_post', methods=['GET', 'POST'])
def create_post():
    guest_dba = current_app.config.get('GUEST_DBA')
    post_dba = current_app.config.get('POST_DBA')
    posts = []
    # 新增投稿
    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        content = request.form.get('content', '').strip()
        # 取得 IP 地址，若有使用代理則取 HTTP_X_FORWARDED_FOR，否則取 remote_addr
        ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

        if (str(ip_addr).__contains__(":") == True):
            # 如果帶有Port，取第一個冒號前的部分
            ip_addr = ip_addr.split(':')[0]

        # 前端有擋住必填欄位，可以略過 null
        if content:
            # 假設 insert_post 回傳新 id！
            post_new_id = guest_dba.insert_post(nickname, content, ip_addr, request.headers.get('User-Agent'), None)
            # 取得剛剛那筆投稿
            posts = post_dba.get_posts_by_id(post_new_id)  # 可依需求選擇
            # 透過 social module 發送社群貼文
            result = social.send(social.social_mode.PendingPost,
                                    anon_id=str(post_new_id),
                                    nickname=nickname,
                                    content=content,
                                    ip=ip_addr,
                                    user_agent=request.headers.get('User-Agent'),
                                    post_time=posts[0].timestamp)
            
            # current_app.logger.info(f"發送結果: {result.status_code} - {result.text}")

            # 改用redirect 來避免重複提交
            flash("投稿成功，您的匿名ID是：" + str(post_new_id), 'new_id')
            return redirect(url_for('post.create_post'))

    return render_template('create_post.html')

@post_bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')