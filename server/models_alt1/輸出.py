from app.models.base import db
from datetime import datetime
from uuid import UUID


class 輸出(db.Model):
    __tablename__ = '輸出'

    輸出識別碼: UUID = db.Column(db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    產品型號識別碼: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('產品型號.產品型號識別碼'), nullable=False)
    多輸出編號: int = db.Column(db.Interger, nullable=False, server_default=1)
    腳位1識別碼: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('物件.物件識別碼'))
    腳位2識別碼: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('物件.物件識別碼'))
    額定電壓常數識別碼: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('常數.常數識別碼'))
    功能說明: str = db.Column(db.String)

    創建時間: datetime = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    更新時間: datetime = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    刪除時間: datetime = db.Column(db.DateTime(timezone=True))

    產品 = db.relationship('產品', back_populates='輸出', foreign_keys='[輸出.產品型號識別碼]')
    腳位1 = db.relationship('物件', back_populates='輸出', foreign_keys='[輸出.腳位1識別碼]')
    腳位2 = db.relationship('物件', back_populates='輸出', foreign_keys='[輸出.腳位2識別碼]')
    額定電壓常數 = db.relationship('常數', back_populates='輸出', foreign_keys='[常數.常數識別碼]')