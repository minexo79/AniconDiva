# post.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .dba import insert_post, get_posts_by_id, get_posts_by_keyword, get_all_posts

post_bp = Blueprint('post', __name__)

@post_bp.route('/', methods=['GET', 'POST'])
def index():
    post_id = request.args.get('id', '').strip()
    query = request.args.get('q', '')
    posts = []
    new_id = None

    # 新增投稿
    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        content = request.form.get('content', '').strip()
        # 前端有擋住必填欄位，可以略過 null
        if content:
            # 假設 insert_post 回傳新 id！
            post_new_id = insert_post(nickname, content, request.remote_addr, request.headers.get('User-Agent'))
            # 新增完直接取得所有資料，或只取得剛剛那筆也可以
            posts = get_all_posts()  # 可依需求選擇
            posts = [
                {'id': row[0], 'content': row[2], 'timestamp': row[3], 'ip': row[4], 'user_agent': row[5]}
                for row in posts
            ]

            # 改用redirect 來避免重複提交
            flash("投稿成功，您的匿名ID是：" + str(post_new_id), 'new_id')
            return redirect(url_for('post.index'))
    
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
    return render_template('index.html', posts=posts, query=query, new_id=None)
