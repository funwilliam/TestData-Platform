import json
from pathlib import Path
from mongoengine import BooleanField, connect, Document, DynamicEmbeddedDocument, DynamicField, EmbeddedDocument, EmbeddedDocumentField, DecimalField, IntField, StringField, ListField, ValidationError

# Connect to MongoDB using the provided connection string.
connect(host='mongodb://localhost:27017/test_db')

# Define the ExactValue embedded document to store precise values with units.
class ExactValue(EmbeddedDocument):
    """
    嵌入文檔，用於存儲具有單位的精確值。

    Attributes:
        Value (Decimal): 精確數值。
        Unit (str): 數值的單位。
        SignalType (str, optional): 信號類型（例如 AC/DC）。
    """
    Value = DecimalField(required=True)
    Unit = StringField(required=True)
    SignalType = StringField()

# Define the Range embedded document to store a range of values.
class Range(EmbeddedDocument):
    """
    嵌入文檔，用於存儲數值範圍，包括上下限。

    Attributes:
        Lower (ExactValue, optional): 範圍的下限值。
        Upper (ExactValue, optional): 範圍的上限值。
    """
    Lower = EmbeddedDocumentField(ExactValue, null=True)
    Upper = EmbeddedDocumentField(ExactValue, null=True)

# Define the Instance embedded document to handle instances with exact values or ranges.
class Instance(DynamicEmbeddedDocument):
    """
    動態嵌入文檔，用於處理具有精確值或範圍的實例。

    Attributes:
        ExactValue (ExactValue, optional): 存儲單一精確值。
        Range (Range, optional): 存儲一個數值範圍。
    """
    ExactValue = EmbeddedDocumentField(ExactValue)
    Range = EmbeddedDocumentField(Range)

# Define the ProductTypeInstance embedded document to store product type-related information.
class ProductTypeInstance(EmbeddedDocument):
    """
    嵌入文檔，用於存儲產品類型相關的信息。

    Attributes:
        ConverterType (str): 轉換器類型。
        OutputRegulationType (str): 輸出調節類型。
        RemoteOnOff (bool): 遠端開關。
        OutputTrim (bool): 輸出修整功能。
        IoIsolation (str): IO隔離等級。
        InsulationSystemType (str): 絕緣系統類型。
        MountingType (str): 安裝類型。
        PackageType (str): 包裝類型。
        Applications (str): 應用領域。
    """
    ConverterType = StringField()
    OutputRegulationType = StringField()
    RemoteOnOff = BooleanField()
    OutputTrim = BooleanField()
    IoIsolation = StringField()
    InsulationSystemType = StringField()
    MountingType = StringField()
    PackageType = StringField()
    Applications = StringField()

# Define the ComponentInstance embedded document to store information about components.
class ComponentInstance(EmbeddedDocument):
    """
    嵌入文檔，用於存儲元件相關的信息。

    Attributes:
        ComponentType (str): 元件類型。
        Number (str): 元件編號。
        Statement (str, optional): 元件聲明或描述。
    """
    ComponentType = StringField(required=True)
    Number = StringField(required=True)
    Statement = StringField()

# Define the IOInstance embedded document to store information about input/output configurations.
class IOInstance(EmbeddedDocument):
    """
    嵌入文檔，用於存儲輸入/輸出配置相關的信息。

    Attributes:
        IOType (str): 輸入或輸出類型。
        Number (str): 輸入或輸出的編號。
        PinPair (list of str): 輸入或輸出的引腳對。

    Methods:
        clean(): 驗證 PinPair 的元素數量是否正確。
    """
    IOType = StringField(required=True)
    Number = StringField(required=True)
    PinPair = ListField(StringField())

    def clean(self):
        """
        驗證 PinPair 列表中的元素數量是否為 2。
        
        Raises:
            ValidationError: 如果 PinPair 的元素數量不是 2，則拋出異常。
        """
        if len(self.PinPair) != 2:
            raise ValidationError("PinPair must contain exactly 2 elements.")

# Define the GeneralSpecifications embedded document to store general product specifications.
class GeneralSpecifications(EmbeddedDocument):
    """
    嵌入文檔，用於存儲產品的一般規格。

    Attributes:
        ProductType (ProductTypeInstance): 產品類型信息。
        OutputQuantity (int): 輸出數量。
        Component (list of ComponentInstance): 元件的實例列表。
        IO (list of IOInstance): 輸入/輸出的實例列表。
        OperatingAmbientTemperature (list of Instance): 操作環境溫度的實例列表。
        InputVoltage (list of Instance): 輸入電壓的實例列表。
        OutputVoltage (list of Instance): 輸出電壓的實例列表。
        OutputCurrent (list of Instance): 輸出電流的實例列表。
        IsolationVoltage (list of Instance): 絕緣電壓的實例列表。
        IsolationResistance (list of Instance): 絕緣電阻的實例列表。
        IsolationCapacitance (list of Instance): 絕緣電容的實例列表。
    """
    ProductType = EmbeddedDocumentField(ProductTypeInstance)
    OutputQuantity = IntField()
    Component = ListField(EmbeddedDocumentField(ComponentInstance))
    IO = ListField(EmbeddedDocumentField(IOInstance))
    OperatingAmbientTemperature = ListField(EmbeddedDocumentField(Instance))
    InputVoltage = ListField(EmbeddedDocumentField(Instance))
    OutputVoltage = ListField(EmbeddedDocumentField(Instance))
    OutputCurrent = ListField(EmbeddedDocumentField(Instance))
    IsolationVoltage = ListField(EmbeddedDocumentField(Instance))
    IsolationResistance = ListField(EmbeddedDocumentField(Instance))
    IsolationCapacitance = ListField(EmbeddedDocumentField(Instance))

# Define the QualityTestSpecifications embedded document to store quality test specifications.
class QualityTestSpecifications(EmbeddedDocument):
    """
    嵌入文檔，用於存儲產品的質量測試規格。

    Attributes:
        InputCurrent (list of Instance): 輸入電流的實例列表。
        InputReflectedRippleCurrent (list of Instance): 反射紋波電流的實例列表。
        OutputVoltage (list of Instance): 輸出電壓的實例列表。
        OutputVoltageSettingAccuracy (list of Instance): 輸出電壓設置精度的實例列表。
        OutputVoltageBalance (list of Instance): 輸出電壓平衡的實例列表。
        LoadRegulation (list of Instance): 負載調整率的實例列表。
        LineRegulation (list of Instance): 線路調整率的實例列表。
        RippleAndNoise (list of Instance): 紋波與噪聲的實例列表。
        TransientRecoveryTime (list of Instance): 暫態恢復時間的實例列表。
        TransientResponseDeviation (list of Instance): 暫態響應偏差的實例列表。
        Overshoot (list of Instance): 過沖的實例列表。
        Efficiency (list of Instance): 效率的實例列表。
        ShortCircuitProtectionInputCurrent (list of Instance): 短路保護輸入電流的實例列表。
        OverloadProtection (list of Instance): 過載保護的實例列表。
        RemoteControlInputVoltage (list of Instance): 遠端控制輸入電壓的實例列表。
        RemoteControlInputCurrent (list of Instance): 遠端控制輸入電流的實例列表。
    """
    InputCurrent = ListField(EmbeddedDocumentField(Instance))
    InputReflectedRippleCurrent = ListField(EmbeddedDocumentField(Instance))
    OutputVoltage = ListField(EmbeddedDocumentField(Instance))
    OutputVoltageSettingAccuracy = ListField(EmbeddedDocumentField(Instance))
    OutputVoltageBalance = ListField(EmbeddedDocumentField(Instance))
    LoadRegulation = ListField(EmbeddedDocumentField(Instance))
    LineRegulation = ListField(EmbeddedDocumentField(Instance))
    RippleAndNoise = ListField(EmbeddedDocumentField(Instance))
    TransientRecoveryTime = ListField(EmbeddedDocumentField(Instance))
    TransientResponseDeviation = ListField(EmbeddedDocumentField(Instance))
    Overshoot = ListField(EmbeddedDocumentField(Instance))
    Efficiency = ListField(EmbeddedDocumentField(Instance))
    ShortCircuitProtectionInputCurrent = ListField(EmbeddedDocumentField(Instance))
    OverloadProtection = ListField(EmbeddedDocumentField(Instance))
    RemoteControlInputVoltage = ListField(EmbeddedDocumentField(Instance))
    RemoteControlInputCurrent = ListField(EmbeddedDocumentField(Instance))

# Define the main ProductModel document to store complete product data.
class ProductModel(Document):
    """
    主文檔模型，用於存儲完整的產品數據，包括一般規格和質量測試規格。

    Attributes:
        Model (str): 產品型號。
        GeneralSpecifications (GeneralSpecifications): 產品的一般規格。
        QualityTestSpecifications (QualityTestSpecifications): 產品的質量測試規格。
    """
    Model = StringField(required=True, unique=True)
    GeneralSpecifications = EmbeddedDocumentField(GeneralSpecifications)
    QualityTestSpecifications = EmbeddedDocumentField(QualityTestSpecifications)

# Insert data from a JSON file into the MongoDB database.
def insert_data_from_json(file_path):
    """
    從指定的 JSON 文件中讀取數據並將其插入到 MongoDB 數據庫中。

    Args:
        file_path (Path): JSON 文件的路徑。

    Raises:
        Exception: 如果文件讀取或數據解析過程中發生錯誤，將拋出異常。

    Side Effects:
        將讀取的數據作為新文檔保存到 MongoDB 數據庫中。
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Parse and create GeneralSpecifications from the JSON data
    general_specifications = GeneralSpecifications(
        ProductType=ProductTypeInstance(**data["GeneralSpecifications"]["ProductType"]),
        OutputQuantity=data["GeneralSpecifications"]["OutputQuantity"],
        Component=[ComponentInstance(**component) for component in data["GeneralSpecifications"]["Component"]["Instances"]],
        IO=[IOInstance(**io_data) for io_data in data["GeneralSpecifications"]["IO"]["Instances"]],
        OperatingAmbientTemperature=[Instance(**temp) for temp in data["GeneralSpecifications"]["OperatingAmbientTemperature"]["Instances"]],
        InputVoltage=[Instance(**volt) for volt in data["GeneralSpecifications"]["InputVoltage"]["Instances"]],
        OutputVoltage=[Instance(**volt) for volt in data["GeneralSpecifications"]["OutputVoltage"]["Instances"]],
        OutputCurrent=[Instance(**current) for current in data["GeneralSpecifications"]["OutputCurrent"]["Instances"]],
        IsolationVoltage=[Instance(**iso_volt) for iso_volt in data["GeneralSpecifications"]["IsolationVoltage"]["Instances"]],
        IsolationResistance=[Instance(**iso_res) for iso_res in data["GeneralSpecifications"]["IsolationResistance"]["Instances"]],
        IsolationCapacitance=[Instance(**iso_cap) for iso_cap in data["GeneralSpecifications"]["IsolationCapacitance"]["Instances"]],
    )

    # Parse and create QualityTestSpecifications from the JSON data
    quality_test_specifications = QualityTestSpecifications(
        InputCurrent=[Instance(**ic) for ic in data["QualityTestSpecifications"]["InputCurrent"]["Instances"]],
        InputReflectedRippleCurrent=[Instance(**irr) for irr in data["QualityTestSpecifications"]["InputReflectedRippleCurrent"]["Instances"]],
        OutputVoltage=[Instance(**ov) for ov in data["QualityTestSpecifications"]["OutputVoltage"]["Instances"]],
        OutputVoltageSettingAccuracy=[Instance(**ovsa) for ovsa in data["QualityTestSpecifications"]["OutputVoltageSettingAccuracy"]["Instances"]],
        OutputVoltageBalance=[Instance(**ovb) for ovb in data["QualityTestSpecifications"]["OutputVoltageBalance"]["Instances"]],
        LoadRegulation=[Instance(**lr) for lr in data["QualityTestSpecifications"]["LoadRegulation"]["Instances"]],
        LineRegulation=[Instance(**linr) for linr in data["QualityTestSpecifications"]["LineRegulation"]["Instances"]],
        RippleAndNoise=[Instance(**rn) for rn in data["QualityTestSpecifications"]["RippleAndNoise"]["Instances"]],
        TransientRecoveryTime=[Instance(**trt) for trt in data["QualityTestSpecifications"]["TransientRecoveryTime"]["Instances"]],
        TransientResponseDeviation=[Instance(**trd) for trd in data["QualityTestSpecifications"]["TransientResponseDeviation"]["Instances"]],
        Overshoot=[Instance(**os) for os in data["QualityTestSpecifications"]["Overshoot"]["Instances"]],
        Efficiency=[Instance(**eff) for eff in data["QualityTestSpecifications"]["Efficiency"]["Instances"]],
        ShortCircuitProtectionInputCurrent=[Instance(**scpic) for scpic in data["QualityTestSpecifications"]["ShortCircuitProtectionInputCurrent"]["Instances"]],
        OverloadProtection=[Instance(**op) for op in data["QualityTestSpecifications"]["OverloadProtection"]["Instances"]],
        RemoteControlInputVoltage=[Instance(**rciv) for rciv in data["QualityTestSpecifications"]["RemoteControlInputVoltage"]["Instances"]],
        RemoteControlInputCurrent=[Instance(**rcic) for rcic in data["QualityTestSpecifications"]["RemoteControlInputCurrent"]["Instances"]],
    )

    # Create a ProductModel instance and save it to the database
    product = ProductModel(
        Model=data["Model"],
        GeneralSpecifications=general_specifications,
        QualityTestSpecifications=quality_test_specifications
    )
    
    # Save the product data to the database
    product.save()
    print(f"Data for model {product.Model} saved successfully!")

if __name__ == "__main__":
    # Insert data from a JSON file into the MongoDB database
    insert_data_from_json(Path('server/models/data_structure_example.json'))
