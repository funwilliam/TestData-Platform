from app.models.base import db
from datetime import datetime
from uuid import UUID


class 常數多態映射(db.Model):
    __tablename__ = '常數多態映射'

    常數識別碼: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('常數.常數識別碼'), primary_key=True)
    層級實例識別碼: UUID = db.Column(db.UUID(as_uuid=True), db.ForeignKey('產品.產品識別碼'), primary_key=True)
    數據類型: str = db.Column(db.String, nullable=False)