from app.models.base import db
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class 層級屬性值(db.Model):
    __tablename__ = '層級屬性值'

    屬性關聯識別碼: UUID = db.Column(db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    屬性識別碼: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('層級屬性.屬性識別碼'))
    實例識別碼: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('層級實例.實例識別碼'))
    儲存文字: str = db.Column('儲存文字', db.String)
    儲存數值: Decimal = db.Column('儲存數值', db.Numeric(14, 7))
    數值特性: str = db.Column('數值特性', db.String)
    單位: str = db.Column('單位', db.String)