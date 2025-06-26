# post.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from .dba import insert_post, get_posts_by_id, get_posts_by_keyword, get_all_posts
from .webhook import send_to_discord_webhook
import source.utils

# 2025.6.26 Blackcat: Use HTTP_X_FORWARDED_FOR To get real IP address if use proxy
post_bp = Blueprint('post', __name__)
@post_bp.route('/view_post', methods=['GET', 'POST'])
def view_post():
    post_id = request.args.get('id', '').strip()
    query = request.args.get('q', '')
    posts = []

    # GET 查詢流程
    if post_id:
        rows = get_posts_by_id(post_id)
    elif query:
        rows = get_posts_by_keyword(query)
    else:
        rows = get_all_posts()
    posts = [
        {'id': row[0], 'content': row[2], 'timestamp': row[3], 'ip': row[4], 'user_agent': row[5]}
        for row in rows
    ]
    return render_template('view_post.html', posts=posts, query=query)

@post_bp.route('/create_post', methods=['GET', 'POST'])
def create_post():
    posts = []
    # 新增投稿
    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        content = request.form.get('content', '').strip()
        # 取得 IP 地址，若有使用代理則取 HTTP_X_FORWARDED_FOR，否則取 remote_addr
        ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

        # 前端有擋住必填欄位，可以略過 null
        if content:
            # 假設 insert_post 回傳新 id！
            post_new_id = insert_post(nickname, content, ip_addr, request.headers.get('User-Agent'), None)
            # 新增完直接取得所有資料，或只取得剛剛那筆也可以
            posts = get_all_posts()  # 可依需求選擇
            posts = [
                {'id': row[0], 'content': row[2], 'timestamp': row[3], 'ip': row[4], 'user_agent': row[5]}
                for row in posts
            ]

            # 如果有設定 Discord Webhook，則發送通知
            if source.utils.DISCORD_POSTED_URL:
                result = send_to_discord_webhook(source.utils.DISCORD_POSTED_URL, 
                                                    post_new_id, 
                                                    nickname, 
                                                    content, 
                                                    ip_addr, 
                                                    request.headers.get('User-Agent'), 
                                                    posts[0]['timestamp'])
                
                current_app.logger.info(f"Discord Webhook 發送結果: {result.status_code} - {result.text}")

            # 改用redirect 來避免重複提交
            flash("投稿成功，您的匿名ID是：" + str(post_new_id), 'new_id')
            return redirect(url_for('post.create_post'))

    return render_template('create_post.html')

@post_bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')