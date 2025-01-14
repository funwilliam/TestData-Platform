from mongoengine import BooleanField, Document, EmbeddedDocument, EmbeddedDocumentField, IntField, MapField, StringField
from openapi_server.database.mongo_models.base_components import AbstractFormula
from openapi_server.database.mongo_models.inspection import Inspection

class Category(EmbeddedDocument):
    """
    嵌入文檔，用於存儲產品元數據、分類信息。

    Attributes:
        SeriesNumber (str): 產品系列。
        OutputQuantity (int): 輸出數量。
        ConverterType (str): 轉換類型。
        OutputRegulation (bool): 是否擁有輸出穩壓功能。
        RemoteControlType (str): 遠端控制類型。
        OutputTrim (bool): 是否擁有輸出微調功能。
        IoIsolation (str): Iinput/Output隔離電壓等級。
        InsulationSystemType (str): 絕緣系統類型。
        MountingType (str): 安裝類型。
        PackageType (str): 封裝類型。
        Applications (str): 主要應用領域。
    """
    SeriesNumber = StringField()
    OutputQuantity = IntField()
    ConverterType = StringField()
    OutputRegulation = BooleanField()
    RemoteControlType = StringField()
    OutputTrim = BooleanField()
    IoIsolation = StringField()
    InsulationSystemType = StringField()
    MountingType = StringField()
    PackageType = StringField()
    Applications = StringField()

class ProductModel(Document):
    """
    主文檔模型，用於存儲完整的產品數據，包括一般規格和質量測試規格。

    Attributes:
        ModelNumber (str): 唯一的產品型號，用於標識每個產品。
        Category (Category): 分類與性質總攬，包括幾種主要分類、應用領域標籤...等資料。
        Inspections (Dict[str, Inspection]): 品質檢查。
        Formulas (Dict[str, AbstractFormula]): 全域公式定義，其中每個鍵是公式名稱，對應的值是該公式的詳細內容。
    """
    ModelNumber = StringField(required=True, unique=True)
    Category = EmbeddedDocumentField(Category)
    Inspections = MapField(field=EmbeddedDocumentField(Inspection))
    Formulas = MapField(field=EmbeddedDocumentField(AbstractFormula))
    meta = {
        'collection': 'ProductModel'
    }