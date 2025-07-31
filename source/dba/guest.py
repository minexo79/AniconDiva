# guest.py
# 只處理 guest（投稿者）相關的資料庫操作
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from .model import Post

class GuestDBA:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def insert_post_guest(self, nickname, content, ip, user_agent, timestamp=None, tag=1, need_review=False):
        """新增一則投稿，預設狀態為 pending"""
        if timestamp is None:
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        post = Post(
            nickname=nickname,
            content=content,
            timestamp=timestamp,
            ip=ip,
            user_agent=user_agent,
            tag=tag,
            status=2 if not need_review else 1  # 1: pending, 2: accpeted
        )

        self.db.session.add(post)
        self.db.session.commit()
        return post.id

    def insert_post(self, nickname, content, ip, user_agent, timestamp=None, tag=1, status=1):
        """新增一則投稿 (匯入模式)"""

        post = Post(
            nickname=nickname,
            content=content,
            ip=ip,
            user_agent=user_agent,
            tag=tag,
            status=status,
            timestamp=timestamp
        )

        self.db.session.add(post)
        self.db.session.commit()
        return post.id