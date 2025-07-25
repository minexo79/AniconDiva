
# init.py
# 管理員初始化資料表與預設帳號
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .model import User, Post, PostReview, db
from ..utils.hash import hash_password

class AdminInitDB:
    def __init__(self, admin_pswd, hash_salt):
        self.admin_pswd = admin_pswd
        self.hash_salt  = hash_salt

    def init_db(self):
        db.create_all()
        # 建立預設 admin 帳號
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', 
                              password=hash_password(self.admin_pswd, self.hash_salt))
            
            db.session.add(admin_user)
            db.session.commit()
