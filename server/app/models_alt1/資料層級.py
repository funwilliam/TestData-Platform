from app.models.base import db
from datetime import datetime
from uuid import UUID

class 資料層級(db.Model):
    __tablename__ = '資料層級'

    資料層級名稱: str = db.Column(db.String, primary_key=True)
    上級層級名稱: str = db.Column(db.String, db.ForeignKey('資料層級.資料層級名稱'))

    創建時間: datetime = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    更新時間: datetime = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    刪除時間: datetime = db.Column(db.DateTime(timezone=True))

    上級層級 = db.relationship('資料層級', remote_side=[資料層級名稱], backref='下級層級')