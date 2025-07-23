# guest.py
# 只處理 guest（投稿者）相關的資料庫操作
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from .model import Post
from .init import db

class GuestDBA:
    def insert_post(self, nickname, content, ip, user_agent, timestamp=None):
        """新增一則投稿，預設狀態為 pending"""
        if timestamp is None:
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        post = Post(
            nickname=nickname,
            content=content,
            timestamp=timestamp,
            ip=ip,
            user_agent=user_agent,
            status='pending'
        )
        
        db.session.add(post)
        db.session.commit()
        return post.id