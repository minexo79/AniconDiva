# post.py
# 處理所有投稿相關的資料庫"查詢"操作
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from .model import Post

class PostDBA:
    def get_posts_by_id(self, post_id):
        """根據ID查詢單則投稿（回傳list of rows）"""
        return Post.query.filter_by(id=post_id).all()

    def get_posts_by_keyword(self, query):
        """根據關鍵字模糊查詢投稿"""
        return Post.query.filter(Post.content.like(f'%{query}%')).order_by(Post.id.desc()).all()

    def get_all_posts(self):
        """取得所有投稿（排序由新到舊）"""
        return Post.query.order_by(Post.id.desc()).all()

    def get_posts_with_pagination(self, page=1, per_page=10, status='approved'):
        """取得分頁的投稿（可設定狀態，排序由新到舊）"""
        if (status == 'all'):
            return Post.query.order_by(Post.id.desc()).paginate(page=page, per_page=per_page, error_out=False).items
        else:
            return Post.query.filter_by(status=status).order_by(Post.id.desc()).paginate(page=page, per_page=per_page, error_out=False).items

    def get_posts_by_keyword_with_pagination(self, query, page=1, per_page=10, status='approved'):
        """根據關鍵字模糊查詢投稿（分頁，可設定狀態）"""
        if (status == 'all'):
            return Post.query.filter(Post.content.like(f'%{query}%')).order_by(Post.id.desc()).paginate(page=page, per_page=per_page, error_out=False).items
        else:
            return Post.query.filter(Post.status==status, (Post.content.like(f'%{query}%') | Post.nickname.like(f'%{query}%'))).order_by(Post.id.desc()).paginate(page=page, per_page=per_page, error_out=False).items

    def get_post_status(self, post_id):
        """取得單一投稿狀態（pending/approved/rejected）"""
        post = Post.query.filter_by(id=post_id).first()
        return post.status if post else None

    def get_posts_count(self, status='approved'):
        """取得投稿總數（可設定狀態）"""
        if (status == 'all'):
            return Post.query.count()
        else:
            return Post.query.filter_by(status=status).count()