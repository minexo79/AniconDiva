# admin.py
# 只處理 admin（管理員）相關的資料庫操作
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .model import Post, PostReview, User
from .init import db

class AdminDBA:
    def __init__(self, hash_salt):
        self.hash_salt = hash_salt

    def get_user_by_name_pw(self, username, pw_hash):
        """用帳號+密碼hash查詢用戶資料（for login）"""
        return User.query.filter_by(username=username, password=pw_hash).first()

    def get_user_by_name(self, username):
        """用帳號查詢用戶"""
        return User.query.filter_by(username=username).first()

    def insert_user(self, username, pw_hash):
        """插入新用戶（管理員）"""
        user = User(username=username, password=pw_hash)
        db.session.add(user)
        db.session.commit()

    def get_all_users(self):
        """取得所有用戶（管理員）清單"""
        return User.query.with_entities(User.id, User.username).all()

    def delete_user_by_id(self, user_id):
        """刪除用戶（管理員）"""
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

    def get_username_by_id(self, user_id):
        """用id查詢username"""
        user = User.query.get(user_id)
        return user.username if user else None

    def get_total_admin_count(self):
        """取得管理員總數"""
        return User.query.count()

    def add_post_review(self, post_id, admin_id, decision):
        """新增一筆投稿審核紀錄（同一管理員不可重複審核同一篇）"""
        review = PostReview(post_id=post_id, admin_id=admin_id, decision=decision)
        db.session.add(review)
        db.session.commit()

    def get_post_review_count(self, post_id, decision):
        """取得某投稿已審核人數"""
        return PostReview.query.filter_by(post_id=post_id, decision=decision).count()

    def update_post_status(self, post_id, status):
        """更新投稿狀態（pending/approved/rejected）"""
        post = Post.query.get(post_id)
        if post:
            post.status = status
            db.session.commit()

    def delete_post(self, post_id):
        """刪除投稿"""
        post = Post.query.get(post_id)
        if post:
            db.session.delete(post)
            db.session.commit()