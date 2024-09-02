from app.models.base import db
from typing import Dict, Any
from datetime import datetime
from uuid import UUID


class 異動日誌(db.Model):
    __tablename__ = '異動日誌'

    異動日誌識別碼: UUID = db.Column('異動日誌識別碼', db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    異動資料來源表名: str = db.Column('異動資料來源表名', db.String)
    異動資料識別碼: UUID = db.Column('異動資料識別碼', db.UUID(as_uuid=True))
    異動操作人員工號: str = db.Column('異動操作人員工號', db.String, nullable=False)
    異動種類: str = db.Column('異動種類', db.String, nullable=False)
    異動原因: str = db.Column('異動原因', db.String)
    異動資料原始值: Dict[str, Any] = db.Column('異動資料原始值', db.JSONB)
    異動資料新值: Dict[str, Any] = db.Column('異動資料新值', db.JSONB)
    額外信息: Dict[str, Any] = db.Column('額外信息', db.JSONB)

    創建時間: datetime = db.Column('創建時間', db.DateTime(timezone=True), server_default=db.func.now())
    更新時間: datetime = db.Column('更新時間', db.DateTime(timezone=True), onupdate=db.func.now())
