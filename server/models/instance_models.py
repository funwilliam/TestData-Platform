from mongoengine import EmbeddedDocument, EmbeddedDocumentField, DynamicEmbeddedDocument, ListField, StringField, ValidationError
from server.models.base_components import ExactValue, Range

class Instance(DynamicEmbeddedDocument):
    """
    動態嵌入文檔，用於處理具有精確值或範圍的實例。

    Attributes:
        ExactValue (ExactValue, optional): 存儲單一精確值。
        Range (Range, optional): 存儲一個數值範圍。
    """
    ExactValue = EmbeddedDocumentField(ExactValue)
    Range = EmbeddedDocumentField(Range)

class IOInstance(EmbeddedDocument):
    """
    嵌入文檔，用於存儲輸入/輸出配置相關的信息。

    Attributes:
        Number (str): 輸入或輸出的編號。
        PinPair (list of str): 輸入或輸出的引腳對。
    """
    Number = StringField(required=True)
    PinPair = ListField(StringField())

    def clean(self):
        if self.PinPair and len(self.PinPair) != 2:
            raise ValidationError("PinPair must contain exactly 2 elements.")

class LoadInstance(EmbeddedDocument):
    """
    嵌入文檔，用於存儲測試用負載相關的信息。

    Attributes:
        AbstractPair (list of str): 引腳對(抽象)。
        ExactValue (ExactValue): 負載物的值。
    """
    AbstractPair = ListField(StringField(), null=True)
    ExactValue = EmbeddedDocumentField(ExactValue, null=True)

    def clean(self):
        if self.AbstractPair and len(self.AbstractPair) != 2:
            raise ValidationError("AbstractPair must contain exactly 2 elements.")

class ComponentInstance(EmbeddedDocument):
    """
    嵌入文檔，用於存儲元件相關的信息。

    Attributes:
        Number (str): 元件編號。
        Statement (str, optional): 元件聲明或描述。
    """
    Number = StringField(required=True)
    Statement = StringField()