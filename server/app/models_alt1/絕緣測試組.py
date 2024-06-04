from app.models.base import db
from datetime import datetime
from uuid import UUID


物件群1 = db.Table(
    '物件群1',
    db.Column('絕緣測試組識別碼', db.UUID(as_uuid=True), db.ForeignKey('絕緣測試組.絕緣測試組識別碼')),
    db.Column('物件識別碼', db.UUID(as_uuid=True), db.ForeignKey('物件.物件識別碼'))
    )

物件群2 = db.Table(
    '物件群2',
    db.Column('絕緣測試組識別碼', db.UUID(as_uuid=True), db.ForeignKey('絕緣測試組.絕緣測試組識別碼')),
    db.Column('物件識別碼', db.UUID(as_uuid=True), db.ForeignKey('物件.物件識別碼'))
    )


class 絕緣測試組(db.Model):
    __tablename__ = '絕緣測試組'

    絕緣測試組識別碼: UUID = db.Column('絕緣測試組識別碼', db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    產品識別碼: UUID = db.Column('產品識別碼', db.UUID(as_uuid=True), db.ForeignKey('產品.產品識別碼'), nullable=False)
    種類分類: str = db.Column('種類分類', db.String, nullable=False)
    物件群1 = db.relationship('物件', secondary=物件群1)
    物件群2 = db.relationship('物件', secondary=物件群2)
    測試持續時長常數識別碼: UUID = db.Column('測試持續時長常數識別碼', db.UUID(as_uuid=True), db.ForeignKey('常數.常數識別碼'))
    功能說明: str = db.Column('功能說明', db.String)
    

    創建時間: datetime = db.Column('創建時間', db.DateTime(timezone=True), server_default=db.func.now())
    更新時間: datetime = db.Column('更新時間', db.DateTime(timezone=True), onupdate=db.func.now())
    刪除時間: datetime = db.Column('刪除時間', db.DateTime(timezone=True))
