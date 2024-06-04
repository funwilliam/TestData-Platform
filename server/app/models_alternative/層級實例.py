from app.models.base import db
from datetime import datetime
from uuid import UUID


class 層級實例(db.Model):
    __tablename__ = '層級實例'

    實例識別碼: UUID = db.Column(db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    層級名稱 = db.Column(db.String, db.ForeignKey('資料層級.層級名稱'))
    實例名稱 = db.Column(db.String, nullable=False)