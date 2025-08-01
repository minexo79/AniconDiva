# admin.py
# 只處理 admin（管理員）相關的資料庫操作
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from .model import Post, PostReview, User

# 2025.7.31 Blackcat: Change Post Status To Int (With Operate ID)

class AdminDBA:
    def __init__(self, hash_salt, db: SQLAlchemy):
        self.hash_salt = hash_salt
        self.db = db

    def get_user_by_name_pw(self, username, pw_hash):
        """用帳號+密碼hash查詢用戶資料（for login）"""
        return self.db.session.query(User).filter_by(username=username, password=pw_hash).first()

    def get_user_by_name(self, username):
        """用帳號查詢用戶"""
        return self.db.session.query(User).filter_by(username=username).first()

    def insert_user(self, username, pw_hash):
        """插入新用戶（管理員）"""
        user = User(username=username, password=pw_hash)
        self.db.session.add(user)
        self.db.session.commit()

    def change_password(self, user_id, new_password):
        """更改用戶（管理員）密碼"""
        user = self.db.session.query(User).get(user_id)
        if user:
            user.password = new_password
            self.db.session.commit()

    def get_all_users(self):
        """取得所有用戶（管理員）清單"""
        return self.db.session.query(User).with_entities(User.id, User.username).order_by(User.id.desc()).all()

    def delete_user_by_id(self, user_id):
        """刪除用戶（管理員）"""
        user = self.db.session.query(User).get(user_id)
        if user:
            self.db.session.delete(user)
            self.db.session.commit()

    def get_username_by_id(self, user_id):
        """用id查詢username"""
        user = self.db.session.query(User).get(user_id)
        return user.username if user else None

    def get_total_admin_count(self):
        """取得管理員總數"""
        return self.db.session.query(User).count()

    def add_post_review(self, post_id, admin_id, decision):
        """新增一筆投稿審核紀錄（同一管理員不可重複審核同一篇）"""
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        review = PostReview(post_id=post_id, admin_id=admin_id, decision=decision, timestamp=timestamp)
        self.db.session.add(review)
        self.db.session.commit()

    def get_post_review_count(self, post_id, decision):
        """取得某投稿已審核人數"""
        return self.db.session.query(PostReview).filter_by(post_id=post_id, decision=decision).count()

    def update_post_status(self, post_id, status):
        """更新投稿狀態（pending/approved/rejected/deleted）"""
        post = self.db.session.query(Post).get(post_id)
        if post:
            post.status = int(status)
            self.db.session.commit()

    def delete_post(self, post_id):
        """刪除投稿"""
        post = Post.query.get(post_id)
        if post:
            post.status = 4  # 標記為已刪除
            self.db.session.commit()