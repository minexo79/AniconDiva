from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(16), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.String(32), nullable=False)
    ip = db.Column(db.String(64), nullable=False)
    user_agent = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(16), nullable=False, default='pending')

class PostReview(db.Model):
    __tablename__ = 'post_reviews'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, nullable=False)
    admin_id = db.Column(db.Integer, nullable=False)
    decision = db.Column(db.String(16), nullable=False)
