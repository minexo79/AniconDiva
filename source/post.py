# post.py
from flask import Blueprint, render_template, request, redirect, url_for
from .dba import insert_post, get_posts_by_id, get_posts_by_keyword, get_all_posts

post_bp = Blueprint('post', __name__)

@post_bp.route('/', methods=['GET', 'POST'])
def index():
    """
    公開首頁投稿與查詢視圖。
    GET: 查詢（可依ID/id/全文關鍵字）
    POST: 新增投稿
    """
    post_id = request.args.get('id', '').strip()
    query = request.args.get('q', '')
    # 新增投稿
    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        content = request.form.get('content', '').strip()
        if content:
            insert_post(nickname, content, request.remote_addr, request.headers.get('User-Agent'))
        return redirect(url_for('post.index'))
    # 查詢邏輯
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
    return render_template('index.html', posts=posts, query=query)
