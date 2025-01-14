from mongoengine import BooleanField, connect, DictField, Document, DynamicEmbeddedDocument, DynamicField, DecimalField, EmbeddedDocument, EmbeddedDocumentField, GenericEmbeddedDocumentField, IntField, MapField, StringField, ListField, ValidationError


class FormulaVariable(EmbeddedDocument):
    """
    嵌入文檔，用於存儲單個變量的信息。

    Attributes:
        Type (str): 含路徑的變量類型（例如 "InputVoltage"）。
        Condition (dict): 變量的條件描述，例如 {"Value": "NominalLine"}。
        GetValue (str): 指定如何獲取變量的值，取值為 'ExactValue', 'Upper', 'Lower'。
    """
    Type = StringField(required=True)
    Condition = DictField()
    GetValue = StringField(choices=['ExactValue', 'Upper', 'Lower'], required=True)

class LocalFormula(EmbeddedDocument):
    """
    嵌入文檔，用於存儲本地定義的公式信息。

    Attributes:
        Expression (str): 公式表達式。
        Variables (dict): 公式中涉及的變量映射，鍵是變量名，值是 FormulaVariable 物件。
        Description (str, optional): 對公式的描述或註釋。
    """
    Expression = StringField(required=True)
    Variables = DictField(field=EmbeddedDocumentField(FormulaVariable))
    Description = StringField()

class ReferenceFormula(EmbeddedDocument):
    """
    嵌入文檔，用於描述引用全局公式的具體信息。

    Attributes:
        FormulaID (str): 引用的公式的唯一標識符（在 ProductModel 中的公式）。
        ParameterMappings (dict): 將產品數據中的屬性映射到公式中的變量。
    """
    FormulaID = StringField(required=True)
    ParameterMappings = DictField(field=StringField())

class ExactValue(EmbeddedDocument):
    """
    嵌入文檔，用於存儲具有單位的精確值。

    Attributes:
        Value (Decimal, optional): 精確數值。
        Formula (ReferenceFormula or LocalFormula, optional): 用於計算的公式引用或本地定義的公式。
        Unit (str): 數值的單位。
        SignalType (str, optional): 信號類型（例如 AC/DC/P-P）。
    """
    Value = DecimalField(precision=4)
    Formula = GenericEmbeddedDocumentField(choices=[ReferenceFormula, LocalFormula])
    Unit = StringField(required=True)
    SignalType = StringField()

    def clean(self):
        if self.Value is not None and self.Formula is not None:
            raise ValidationError("Only one of 'Value' or 'Formula' should be defined.")
        if self.Value is None and self.Formula is None:
            raise ValidationError("One of 'Value' or 'Formula' must be defined.")

class Range(EmbeddedDocument):
    """
    嵌入文檔，用於存儲數值範圍，包括上下限。

    Attributes:
        Lower (ExactValue, optional): 範圍的下限值。
        Upper (ExactValue, optional): 範圍的上限值。
    """
    Lower = EmbeddedDocumentField(ExactValue, null=True)
    Upper = EmbeddedDocumentField(ExactValue, null=True)

class Instance(DynamicEmbeddedDocument):
    """
    動態嵌入文檔，用於處理具有精確值或範圍的實例。

    Attributes:
        ExactValue (ExactValue, optional): 存儲單一精確值。
        Range (Range, optional): 存儲一個數值範圍。
    """
    ExactValue = EmbeddedDocumentField(ExactValue)
    Range = EmbeddedDocumentField(Range)

class ComponentInstance(EmbeddedDocument):
    """
    嵌入文檔，用於存儲元件相關的信息。

    Attributes:
        Number (str): 元件編號。
        Statement (str, optional): 元件聲明或描述。
    """
    Number = StringField(required=True)
    Statement = StringField()

class IOInstance(EmbeddedDocument):
    """
    嵌入文檔，用於存儲輸入/輸出配置相關的信息。

    Attributes:
        Number (str): 輸入或輸出的編號。
        PinPair (list of str): 輸入或輸出的引腳對。

    Methods:
        clean(): 驗證 PinPair 的元素數量是否正確。
    """
    Number = StringField(required=True)
    PinPair = ListField(StringField())

    def clean(self):
        """
        驗證 PinPair 列表中的元素數量是否為 2。

        Raises:
            ValidationError: 如果 PinPair 的元素數量不是 2，則拋出異常。
        """
        if self.PinPair and len(self.PinPair) != 2:
            raise ValidationError("PinPair must contain exactly 2 elements.")

class LoadInstance(EmbeddedDocument):
    """
    嵌入文檔，用於存儲測試用負載相關的信息。

    Attributes:
        AbstractPair (list of str): 引腳對(抽象)，例如: [+vout, -vout]。
        ExactValue (ExactValue): 負載物的值。

    Methods:
        clean(): 驗證 AbstractPair 的元素數量是否正確。
    """
    AbstractPair = ListField(StringField(), null=True)
    ExactValue = EmbeddedDocumentField(ExactValue, null=True)

    def clean(self):
        """
        驗證 AbstractPair 列表中的元素數量是否為 2。

        Raises:
            ValidationError: 如果 AbstractPair 的元素數量不是 2，則拋出異常。
        """
        if self.AbstractPair and len(self.AbstractPair) != 2:
            raise ValidationError("AbstractPair must contain exactly 2 elements.")

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

class InspectionParameters(EmbeddedDocument):
    """
    嵌入文檔，用於存儲測試時可能使用到的參數清單。

    Attributes:
        Component (Dict[str, List[ComponentInstance]]): 元件的分類與實例列表。
        IO (Dict[str, List[IOInstance]]): 輸入的實例列表。
        AmbientTemperature (list of Instance): 操作環境溫度的實例列表。
        InputVoltage (list of Instance): 輸入電壓的實例列表。
        OutputVoltage (list of Instance): 輸出電壓的實例列表。
        OutputCurrent (list of Instance): 輸出電流的實例列表。
        OutputPower (list of Instance): 輸出功率的實例列表。
        ResistiveLoad (list of LoadInstance): 電阻負載的實例列表。
        CapacitiveLoad (list of LoadInstance): 電容負載的實例列表。
        StartUpThresholdVoltage (list of Instance): 啟動臨界電壓的實例列表。
        UndervoltageShutdownVoltage (list of Instance): 欠壓關斷電壓的實例列表。
        OutputVoltageTrimResistance (list of Instance): 輸出電壓調整電阻的實例列表。
        IsolationVoltage (list of Instance): 絕緣電壓測試值的實例列表。
    """
    Component = MapField(field=ListField(EmbeddedDocumentField(ComponentInstance)))
    IO = MapField(field=ListField(EmbeddedDocumentField(IOInstance)))
    AmbientTemperature = ListField(EmbeddedDocumentField(Instance))
    InputVoltage = ListField(EmbeddedDocumentField(Instance))
    OutputVoltage = ListField(EmbeddedDocumentField(Instance))
    OutputCurrent = ListField(EmbeddedDocumentField(Instance))
    OutputPower = ListField(EmbeddedDocumentField(Instance))
    ResistiveLoad = ListField(EmbeddedDocumentField(LoadInstance))
    CapacitiveLoad = ListField(EmbeddedDocumentField(LoadInstance))
    StartupThresholdVoltage = ListField(EmbeddedDocumentField(Instance))
    UndervoltageShutdownVoltage = ListField(EmbeddedDocumentField(Instance))
    OutputVoltageTrimResistance = ListField(EmbeddedDocumentField(Instance))
    IsolationVoltage = ListField(EmbeddedDocumentField(Instance))

class InspectionAttributes(EmbeddedDocument):
    """
    嵌入文檔，用於存儲產品的品質檢查合格規範。

    Attributes:
        InputCurrent (list of Instance): 輸入電流的實例列表。
        ReflectedInputRippleCurrent (list of Instance): 反射輸入漣波電流的實例列表。
        OutputVoltage (list of Instance): 輸出電壓的實例列表。
        OutputVoltageAccuracy (list of Instance): 輸出電壓精度的實例列表。
        OutputVoltageBalance (list of Instance): 輸出電壓平衡的實例列表。
        LoadRegulation (list of Instance): 負載調整率的實例列表。
        LineRegulation (list of Instance): 線路調整率的實例列表。
        RippleAndNoise (list of Instance): 紋波與噪聲的實例列表。
        TransientRecoveryTime (list of Instance): 暫態恢復時間的實例列表。
        TransientResponseDeviation (list of Instance): 暫態響應偏差的實例列表。
        Overshoot (list of Instance): 過沖的實例列表。
        Efficiency (list of Instance): 效率的實例列表。
        ShortCircuitProtectionFrequency (list of Instance): 短路保護操作頻率的實例列表。
        ShortCircuitProtectionInputPower (list of Instance): 短路保護輸入功率的實例列表。
        ShortCircuitProtectionInputCurrent (list of Instance): 短路保護輸入電流的實例列表。
        OverloadCurrentProtection (list of Instance): 過載保護的實例列表。
        RemoteControlInputVoltage (list of Instance): 遠端控制輸入電壓的實例列表。
        RemoteControlInputCurrent (list of Instance): 遠端控制輸入電流的實例列表。
        OutputVoltageTrimRange (list of Instance): 輸出電壓調整範圍的實例列表。
        InsulationResistance (list of Instance): 絕緣電阻的實例列表。
        InsulationCapacitance (list of Instance): 絕緣電容的實例列表。
        SwitchingFrequency (list of Instance): 交換頻率的實例列表。
    """
    InputCurrent = ListField(EmbeddedDocumentField(Instance))
    ReflectedInputRippleCurrent = ListField(EmbeddedDocumentField(Instance))
    OutputVoltage = ListField(EmbeddedDocumentField(Instance))
    OutputVoltageAccuracy = ListField(EmbeddedDocumentField(Instance))
    OutputVoltageBalance = ListField(EmbeddedDocumentField(Instance))
    LoadRegulation = ListField(EmbeddedDocumentField(Instance))
    LineRegulation = ListField(EmbeddedDocumentField(Instance))
    RippleAndNoise = ListField(EmbeddedDocumentField(Instance))
    TransientRecoveryTime = ListField(EmbeddedDocumentField(Instance))
    TransientResponseDeviation = ListField(EmbeddedDocumentField(Instance))
    Overshoot = ListField(EmbeddedDocumentField(Instance))
    Efficiency = ListField(EmbeddedDocumentField(Instance))
    ShortCircuitProtectionFrequency = ListField(EmbeddedDocumentField(Instance))
    ShortCircuitProtectionInputPower = ListField(EmbeddedDocumentField(Instance))
    ShortCircuitProtectionInputCurrent = ListField(EmbeddedDocumentField(Instance))
    OverloadCurrentProtection = ListField(EmbeddedDocumentField(Instance))
    RemoteControlInputVoltage = ListField(EmbeddedDocumentField(Instance))
    RemoteControlInputCurrent = ListField(EmbeddedDocumentField(Instance))
    OutputVoltageTrimRange = ListField(EmbeddedDocumentField(Instance))
    InsulationResistance = ListField(EmbeddedDocumentField(Instance))
    InsulationCapacitance = ListField(EmbeddedDocumentField(Instance))
    SwitchingFrequency = ListField(EmbeddedDocumentField(Instance))

class Inspection(EmbeddedDocument):
    """
    嵌入文檔，用於儲存品質檢查相關資料。

    Attributes:
        Parameters (InspectionParameters): 產品的一般規格，例如輸入電壓、輸出電壓等基本電氣參數。
        Attributes (InspectionAttributes): 產品的品質測試屬性，例如品質測試條件、合格範圍等。
    """
    Parameters = EmbeddedDocumentField(InspectionParameters)
    Attributes = EmbeddedDocumentField(InspectionAttributes)

class AbstractFormula(EmbeddedDocument):
    """
    嵌入文檔，用於存儲公式信息。

    Attributes:
        Expression (str): 公式表達式。
        Variables (list): 公式中涉及的變量名稱列表。
        Description (str, optional): 對公式的描述或註釋。
    """
    Expression = StringField(required=True)
    Variables = ListField(field=StringField())
    Description = StringField()

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
