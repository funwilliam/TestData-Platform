from app.models.base import db
from datetime import datetime
from uuid import UUID


class 文件(db.Model):
    __tablename__ = '文件'

    文件識別碼: UUID = db.Column('文件識別碼', db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    產品識別碼: UUID = db.Column('產品識別碼', db.UUID(as_uuid=True), db.ForeignKey('產品.產品識別碼'), nullable=False)
    文件發行版本: str = db.Column('文件發行版本', db.String, server_default='0')
    文件類型: str = db.Column('文件類型', db.String, nullable=False)
    核准人員工號: str = db.Column('核准人員工號', db.String)
    審核人員工號: str = db.Column('審核人員工號', db.String)
    設計人員工號: str = db.Column('設計人員工號', db.String)
    審核通過時間: datetime = db.Column('審核通過時間', db.DateTime(timezone=True))

    創建時間: datetime = db.Column('創建時間', db.DateTime(timezone=True), server_default=db.func.now())
    更新時間: datetime = db.Column('更新時間', db.DateTime(timezone=True), onupdate=db.func.now())
    刪除時間: datetime = db.Column('刪除時間', db.DateTime(timezone=True))
