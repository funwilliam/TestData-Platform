from app.models.base import db
from datetime import datetime, date
from uuid import UUID


class 產品型號(db.Model):
    __tablename__ = '產品型號'

    產品型號識別碼: UUID = db.Column(db.UUID(as_uuid=True), primary_key=True, server_default=db.text('gen_random_uuid()'))
    產品型號名稱: str = db.Column(db.String, nullable=False, unique=True)
    產品系列識別碼: UUID = db.Column(db.UUID(as_uuid=True), nullable=False) 

    輸入源類型: str = db.Column(db.String, nullable=False) # DC, AC
    穩壓類型: str = db.Column(db.String) # Regulated, Unregulated, null: 缺少資料
    封裝類型: str = db.Column(db.String) # SIP, SMD, DIP, Inch, Brick, Screw, Terminal, null: 缺少資料
    安裝類型: str = db.Column(db.String) # 'Board Mount-Surface Mount Device', 'Board Mount-Through Hole Device', 'Chassis & DIN-Rail Mount', null: 缺少資料
    IO絕緣類型: str = db.Column(db.String) # 1000VDC, 1500VDC, 1600VDC, 2000VAC, 2500VDC, 3000VAC, 3000VDC, 4000VAC, 4200VAC, 5000VAC, 5200VDC, 6000VDC, null: 缺少資料
    絕緣系統類型: str = db.Column(db.String) # Functional, Reinforced, null: 缺少資料
    輸出微調功能: bool = db.Column(db.Boolean) # True: 具備功能, False: 不具備功能, null: 缺少資料
    遠端控制功能: bool = db.Column(db.Boolean) # True: 具備功能, False: 不具備功能, null: 缺少資料
    
    負責人員工號: str = db.Column(db.String) # null: 缺少資料
    設計完成時間: date = db.Column(db.Date) # null: 缺少資料

    創建時間: datetime = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    更新時間: datetime = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    刪除時間: datetime = db.Column(db.DateTime(timezone=True))

    輸出清單 = db.relationship('輸出', back_populates='產品', foreign_keys='[輸出.產品型號識別碼]')
    常數清單 = db.relationship('常數', back_populates='產品系列', primaryjoin='常數.層級實例識別碼 == foreign(產品型號.產品型號識別碼)')
