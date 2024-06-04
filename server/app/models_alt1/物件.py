from app.models.base import db
from datetime import datetime
from uuid import UUID

class 物件表(db.Model):
    __tablename__ = '物件表'

    物件表識別碼: UUID = db.Column(db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    父資料層級名稱: str = db.Column(db.String, db.ForeignKey('資料層級.資料層級名稱'), nullable=False) # 系列, 型號
    父層級實例識別碼: UUID = db.Column(db.UUID(as_uuid=True), nullable=False)
    
    創建時間: datetime = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    更新時間: datetime = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    刪除時間: datetime = db.Column(db.DateTime(timezone=True))


class 物件(db.Model):
    __tablename__ = '物件'

    物件識別碼: UUID = db.Column(db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    物件表識別碼: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('物件表.物件表識別碼'), nullable=False)
    物件種類: str = db.Column(db.String, nullable=False)
    同類物件識別編號: str = db.Column(db.String, server_default='1')
    關聯料號: str = db.Column(db.String)
    功能說明: str = db.Column(db.String)

    創建時間: datetime = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    更新時間: datetime = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    刪除時間: datetime = db.Column(db.DateTime(timezone=True))
