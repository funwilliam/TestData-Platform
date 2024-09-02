from app.models.base import db
from datetime import datetime
from uuid import UUID

class 資料層級(db.Model):
    __tablename__ = '資料層級'

    資料層級名稱: str = db.Column('資料層級名稱', db.String, primary_key=True)
    上級層級名稱: int = db.Column('上級層級名稱', db.String, db.ForeignKey('資料層級.資料層級名稱'))