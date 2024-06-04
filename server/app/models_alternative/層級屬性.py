from app.models.base import db
from datetime import datetime
from uuid import UUID


class 層級屬性(db.Model):
    __tablename__ = '層級屬性'

    屬性識別碼: UUID = db.Column(db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    屬性名稱: str = db.Column(db.String, nullable=False)
    種類分類: str = db.Column('常數分類', db.String, nullable=False)
    數值分類: str = db.Column('數值分類', db.String)
    數據類型: str = db.Column(db.String, nullable=False)
    數值量級: str = db.Column(db.String)