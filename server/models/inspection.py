from mongoengine import EmbeddedDocument, EmbeddedDocumentField, ListField, MapField
from server.models.instance_models import ComponentInstance, Instance, IOInstance, LoadInstance

class InspectionParameters(EmbeddedDocument):
    """
    嵌入文檔，用於存儲測試時可能使用到的參數清單。

    Attributes:
        Component (Dict[str, List[ComponentInstance]]): 元件的分類與實例列表。
        IO (Dict[str, List[IOInstance]]): 輸入輸出的實例列表。
        AmbientTemperature (list of Instance): 操作環境溫度的實例列表。
        InputVoltage (list of Instance): 輸入電壓的實例列表。
        OutputVoltage (list of Instance): 輸出電壓的實例列表。
        OutputCurrent (list of Instance): 輸出電流的實例列表。
        OutputPower (list of Instance): 輸出功率的實例列表。
        ResistiveLoad (list of LoadInstance): 電阻負載的實例列表。
        CapacitiveLoad (list of LoadInstance): 電容負載的實例列表。
        StartupThresholdVoltage (list of Instance): 啟動臨界電壓的實例列表。
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
        OutputVoltageAccuracy (list of Instance): 輸出電壓準確率的實例列表。
        OutputVoltageBalance (list of Instance): 輸出電壓平衡率的實例列表。
        LoadRegulation (list of Instance): 負載調整率的實例列表。
        LineRegulation (list of Instance): 線性調整率的實例列表。
        RippleAndNoise (list of Instance): 漣波與雜訊的實例列表。
        TransientRecoveryTime (list of Instance): 暫態恢復時間的實例列表。
        TransientResponseDeviation (list of Instance): 暫態響應偏差的實例列表。
        Overshoot (list of Instance): 過沖的實例列表。
        Efficiency (list of Instance): 效率的實例列表。
        ShortCircuitProtectionFrequency (list of Instance): 短路保護操作頻率的實例列表。
        ShortCircuitProtectionInputPower (list of Instance): 短路保護輸入功率的實例列表。
        ShortCircuitProtectionInputCurrent (list of Instance): 短路保護輸入電流的實例列表。
        OverloadCurrentProtection (list of Instance): 過負載電流保護的實例列表。
        RemoteControlInputVoltage (list of Instance): 遠端控制輸入電壓的實例列表。
        RemoteControlInputCurrent (list of Instance): 遠端控制輸入電流的實例列表。
        OutputVoltageTrimRange (list of Instance): 輸出電壓調整範圍的實例列表。
        InsulationResistance (list of Instance): 絕緣電阻的實例列表。
        InsulationCapacitance (list of Instance): 絕緣電容的實例列表。
        SwitchingFrequency (list of Instance): 切換頻率的實例列表。
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