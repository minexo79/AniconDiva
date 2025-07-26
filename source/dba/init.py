
# init.py
# 管理員初始化資料表與預設帳號
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .model import User, Post, PostReview, db, Tag, Operate
from ..utils.default_dict import DefaultDict
from ..utils.hash import hash_password

class InitDB:
    def __init__(self, db: SQLAlchemy, admin_pswd: str, hash_salt: str, default_dict: DefaultDict):
        self.db = db
        self.admin_pswd = admin_pswd
        self.hash_salt  = hash_salt
        self.default_dict = default_dict

    def init_admin(self):
        '''建立預設 admin 帳號'''
        admin_user = self.db.session.query(User).filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', 
                              password=hash_password(self.admin_pswd, self.hash_salt),
                              superadmin=True)

            self.db.session.add(admin_user)
            self.db.session.commit()

    def init_operate(self):
        '''
        建立預設 Operate<br>
        '''
        if not Operate.query.first():
            for op in DefaultDict.OperateDict:
                operate = Operate(label=DefaultDict.OperateDict[op].label)
                self.db.session.add(operate)
            self.db.session.commit()


    def init_tag(self):
        '''
        建立預設 Tag<br>
        '''
        if not Tag.query.first():
            for tag in DefaultDict.TagDict:
                tag_entry = Tag(label=DefaultDict.TagDict[tag].label,
                                pending_request=DefaultDict.TagDict[tag].pending_request)
                self.db.session.add(tag_entry)
            self.db.session.commit()

    def init_db(self):
        self.db.create_all()
        self.init_admin()
        self.init_operate()
        self.init_tag()