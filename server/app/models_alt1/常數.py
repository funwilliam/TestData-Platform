from app.models.base import db
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class 有效數據(db.Model):
    __tablename__ = '有效數據'

    有效數據識別碼: UUID = db.Column(db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    父資料層級名稱: str = db.Column(db.String, db.ForeignKey('資料層級.資料層級名稱'))
    父層級實例識別碼: UUID = db.Column(db.UUID(as_uuid=True), nullable=False)
    同類數據識別編號: str = db.Column(db.String)
    種類分類: str = db.Column(db.String, nullable=False)
    數據名稱: str = db.Column(db.String)
    數據: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('數據單元.數據單元識別碼'), nullable=False)


class 數據單元(db.Model):
    __tablename__ = '數據單元'

    數據單元識別碼: UUID = db.Column(db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    數據類型: str = db.Column(db.String, nullable=False) # 數值範圍, 單一數值, 文字
    

class 常數(db.Model):
    __tablename__ = '常數'

    常數識別碼: UUID = db.Column(db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    數據識別碼: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('數據.數據識別碼'), nullable=False)
    
    儲存文字: str = db.Column(db.String)
    儲存數值: Decimal = db.Column(db.Numeric(16, 4))
    數值特性: str = db.Column(db.String)
    單位: str = db.Column(db.String)

    創建時間: datetime = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    更新時間: datetime = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    刪除時間: datetime = db.Column(db.DateTime(timezone=True))


class 成立條件(db.Model):
    __tablename__ = '成立條件'

    條件識別碼: UUID = db.Column(db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    有效數據識別碼: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('有效數據.有效數據識別碼'), nullable=False)
    條件名稱: str = db.Column(db.String)
    條件數據: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('數據單元.數據單元識別碼'), nullable=False)