from flask_sqlalchemy import SQLAlchemy

# 2025.7.31 Blackcat: Change Post Status To Int (With Operate ID)

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    superadmin = db.Column(db.Boolean, default=False, nullable=False)

class Tag(db.Model):
    __tablename__ = 'tag_dict'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(16), unique=True, nullable=False)
    pending_request = db.Column(db.Boolean, default=False, nullable=False)

class Operate(db.Model):
    __tablename__ = 'operate_dict'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(16), unique=True, nullable=False)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(16), nullable=False)
    content = db.Column(db.Text, nullable=False)
    ip = db.Column(db.String(64), nullable=False)
    user_agent = db.Column(db.String(255), nullable=False)
    tag = db.Column(db.Integer, db.ForeignKey('tag_dict.id'), nullable=False, default=1)
    status = db.Column(db.Integer, db.ForeignKey('operate_dict.id'), nullable=False, default=1)
    timestamp = db.Column(db.String(32), nullable=False)

class PostReview(db.Model):
    __tablename__ = 'post_reviews'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    decision = db.Column(db.Integer, db.ForeignKey('operate_dict.id'),nullable=False, default=1)
    timestamp = db.Column(db.String(32), nullable=False)