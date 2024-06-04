from app.models.base import db
from datetime import datetime
from uuid import UUID


class 產品系列(db.Model):
    __tablename__ = '產品系列'

    產品系列識別碼: UUID = db.Column(db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    產品系列名稱: str = db.Column(db.String)

    創建時間: datetime = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    更新時間: datetime = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    刪除時間: datetime = db.Column(db.DateTime(timezone=True))

    常數清單 = db.relationship('常數', back_populates='產品系列', primaryjoin='常數.層級實例識別碼 == foreign(產品系列.產品系列識別碼)')
