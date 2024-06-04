from app.models.base import db
from datetime import datetime
from uuid import UUID


class 資料層級關係(db.Model):
    __tablename__ = '資料層級關係'

    關係識別碼: UUID = db.Column(db.UUID(as_uuid=True), primary_key=True,server_default=db.text('gen_random_uuid()'))
    父層級實例識別碼: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('層級實例.實例識別碼'))
    子層級實例識別碼: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('層級實例.實例識別碼'))
