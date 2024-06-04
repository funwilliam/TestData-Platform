from app.models.base import db
from typing import Dict, Any
from datetime import datetime
from uuid import UUID

class 規格(db.Model):
    __tablename__ = '規格'

    規格細項識別碼: UUID = db.Column(db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    產品型號名稱: str = db.Column(db.String, db.ForeignKey('產品型號.產品型號名稱', ondelete="cascade", onupdate='CASCADE'), nullable=False)
    規格定義: Dict[str, Any] = db.Column(db.Jsonb, nullable=False)

    創建時間: datetime = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    更新時間: datetime = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    刪除時間: datetime = db.Column(db.DateTime(timezone=True))
