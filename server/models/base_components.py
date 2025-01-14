from mongoengine import EmbeddedDocument, StringField, DictField, DecimalField, GenericEmbeddedDocumentField, ListField, ValidationError, EmbeddedDocumentField

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