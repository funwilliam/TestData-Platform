import sympy as sp
from decimal import Decimal
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Type
from pint import UnitRegistry, Quantity, Unit
from server.helpers.utils import utils

ureg = utils.ureg



""" 數值類型 """
# class 基本數值類型(ABC):
#     def __init__(self, value: Union[List, Quantity]) -> None:
#         super().__init__()


class 單一值:
    def __init__(self, value: str | int | float | Decimal | Quantity, unit: Optional[Union[str, Unit]] = None):
        self.value = self._convert_to_quantity(value, unit)

    def _convert_to_quantity(self, value: str | int | float | Decimal | Quantity, unit: Optional[Union[str, Unit]]) -> Quantity:
        """根據不同的輸入類型將值轉換為 Quantity，並使用可選的默認單位"""
        return utils.convert_to_quantity(value, unit)

    def evaluate(self) -> Quantity:
        return self.value

    def to(self, unit: str) -> Quantity:
        """將當前值轉換為指定單位"""
        return self.value.to(unit)

    def __repr__(self) -> str:
        return f"{self.value}"


class 範圍值:
    def __init__(
            self,
            lower: Optional[Union[int, float, str, Quantity]] = None,
            upper: Optional[Union[int, float, str, Quantity]] = None,
            unit: Optional[Union[str, Unit]] = None
        ):
        self.lower = self._convert_to_quantity(lower, unit) if lower is not None else None
        self.upper = self._convert_to_quantity(upper, unit) if upper is not None else None

    def _convert_to_quantity(self, value: str | int | float | Decimal | Quantity, unit: Optional[Union[str, Unit]]) -> Quantity:
        """根據不同的輸入類型將值轉換為 Quantity，並使用可選的默認單位"""
        return utils.convert_to_quantity(value, unit)
        
    def evaluate(self) -> Dict[str, Optional[Quantity]]:
        return {"lower": self.lower, "upper": self.upper}

    def __repr__(self):
        return f"範圍值(lower={self.lower}, upper={self.upper})"


class 公式值:
    def __init__(self, formula: str):
        self.formula = sp.sympify(formula)

    def evaluate(self, context: Dict[str, Union[int, float, Quantity]]) -> Quantity:
        variables = {sp.Symbol(k): (v.magnitude if isinstance(v, Quantity) else v) for k, v in context.items()}
        result = self.formula.subs(variables)
        if isinstance(result, sp.Basic):
            result = float(result)
        # 這裡假設公式返回的結果應該與 context 中的某個變量的單位一致
        sample_unit = next((v for v in context.values() if isinstance(v, Quantity)), None)
        if sample_unit is not None:
            return result * sample_unit.units
        else:
            raise ValueError("公式計算結果無法確定單位")

    def __repr__(self):
        return f"公式值(formula={self.formula})"


""" 零件 """
class 產品零件:
    def __init__(self):
        pass


class Pin(產品零件):
    def __init__(self):
        super().__init__()


class Case(產品零件):
    def __init__(self):
        super().__init__()


""" 概念 """
# class 基本概念(ABC):
#     def __init__(self, conception_type: str) -> None:
#         super().__init__()
#         self.conception_type = conception_type


class 輸入:
    def __init__(self, parent: object, pins: List[Optional['Pin']]):
        if pins and len(pins) == 2:
            self.pins = pins
        else:
            self.pins = []


class 輸出:
    def __init__(self, parent: object, pins: List[Optional['Pin']]):
        if pins:
            self.set_output_object_pins(pins)
        else:
            self.pins = []
    
    def set_output_object_pins(self, pins: List[Pin]):
        """
        設定輸出物件的 pins。\n
        如果 pins 的列表不符合要求，則拋出異常。
        """
        if pins and len(pins) == 2 and isinstance(pins[0], Pin) and isinstance(pins[1], Pin):
            self.pins = pins
        else:
            raise ValueError("參數 pins 必須是包含兩個 Pin 物件的列表")


class 保護:
    def __init__(self, parent: object):
        pass


class 絕緣:
    def __init__(self, parent: object, groups: List[List[Optional['產品零件']]]):
        if groups and len(groups) == 2 and len(groups[0]) > 0 and len(groups[1]) > 0:
            self.groups = groups
        else:
            self.groups = []


class 遠端控制:
    def __init__(self, parent: object, pin: Optional['Pin']):
        self.pin = pin


""" 標準數據結構 """
class 基本物件(ABC):
    def __init__(self, value: Union['單一值', '範圍值', '公式值'], value_label: Union[List[str], str]):
        super().__init__()
        self.value = value
        self.value_label = value_label

    def matches_label(self, label: Union[List[str], str]) -> bool:
        """
        匹配物件的標籤是否與給定的標籤相符。
        """
        if isinstance(self.value_label, list) and isinstance(label, list):
            return all(item in self.value_label for item in label)
        return self.value_label == label


class 電壓(基本物件):
    def __init__(self, value: int | float | Decimal | str | Quantity, value_label: Union[List[str], str]):
        value = 單一值(value, ureg.volt)
        super().__init__(value, value_label)


class 電流(基本物件):
    def __init__(self, value: int | float | Decimal | str | Quantity, value_label: Union[List[str], str]):
        value = 單一值(value, ureg.ampere)
        super().__init__(value, value_label)


class 功率(基本物件):
    def __init__(self, value: int | float | Decimal | str | Quantity, value_label: Union[List[str], str]):
        value = 單一值(value, ureg.watt)
        super().__init__(value, value_label)


class 電阻(基本物件):
    def __init__(self, value: int | float | Decimal | str | Quantity, value_label: Union[List[str], str]):
        value = 單一值(value, ureg.ohm)
        super().__init__(value, value_label)


class 電容(基本物件):
    def __init__(self, value: int | float | Decimal | str | Quantity, value_label: Union[List[str], str]):
        value = 單一值(value, ureg.farad)
        super().__init__(value, value_label)


class 溫度(基本物件):
    def __init__(self, value: int | float | Decimal | str | Quantity, value_label: Union[List[str], str]):
        value = 單一值(value, ureg.degC)
        super().__init__(value, value_label)

    @classmethod
    def NTP(cls):
        return 溫度(
            value= Decimal('25'),
            value_label=['nominal', '常溫']
        )


class 濕度(基本物件):
    def __init__(self, value: int | float | Decimal | str | Quantity, value_label: Union[List[str], str]):
        value = 單一值(value, ureg.percent)
        super().__init__(value, value_label)


class 輸入電壓(電壓):
    def __init__(self, value: int | float | Decimal | str | Quantity, value_label: Union[List[str], str], input: 輸入):
        super().__init__(value, value_label)
        self.input = input


class 輸入電流(電流):
    def __init__(self, value: int | float | Decimal | str | Quantity, value_label: Union[List[str], str], input: 輸入):
        super().__init__(value, value_label)
        self.input = input


class 輸入功率(功率):
    def __init__(self, value: int | float | Decimal | str | Quantity, value_label: Union[List[str], str], input: 輸入):
        super().__init__(value, value_label)
        self.input = input


class 輸出電壓(電壓):
    def __init__(self, value: int | float | Decimal | str | Quantity, value_label: Union[List[str], str], output: 輸出):
        super().__init__(value, value_label)
        self.output = output


class 輸出電流(電流):
    def __init__(self, value: int | float | Decimal | str | Quantity, value_label: Union[List[str], str], output: 輸出):
        super().__init__(value, value_label)
        self.output = output


class 輸出功率(功率):
    def __init__(self, value: int | float | Decimal | str | Quantity, value_label: Union[List[str], str], output: 輸出):
        super().__init__(value, value_label)
        self.output = output


""" 條件 """
class 條件:
    def __init__(self, condition_type: Type, value_label: Optional[str], value: Optional[Union['單一值', '範圍值', '公式值']]):
        self.condition_type = condition_type
        self.value_label = value_label

    def matches(self, other_conditions: List['條件']) -> bool:
        """
        匹配條件是否與給定的條件列表中的某一項相符。
        """
        for condition in other_conditions:
            if self.condition_type == condition.condition_type and self.value_label == condition.value_label:
                return True
        return False