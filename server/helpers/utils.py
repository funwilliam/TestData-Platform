import os
import re
import sys
# import pytz
# import ntplib
# import platform
# import traceback
# import ctypes
# import pandas as pd
from pathlib import Path
from pint import UnitRegistry, Quantity, Unit
# from ctypes import wintypes
from typing import List, Dict, Any, Tuple, Literal, Optional, Union
from time import ctime
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN

class utils:
    ureg = UnitRegistry()

    # @classmethod
    # def make_DBURL(cls, user: str, password: str, host: str, port: str, database_name: str) -> str:
    #     """ 建立資料庫連接字串 """
    #     db_url = f"postgresql://{user}:{password}@{host}:{port}/{database_name}"
    #     return db_url

    @classmethod
    def is_number(cls, s) -> bool:
        """ 
        檢查輸入是否符合python數字型別。
        支援類型: str | int | float | Decimal | Quantity | None
        注意: NaN, Infinity...等，屬於float型別的特殊數字，故回傳為真。
        """
        if s is None:
            return False
        
        if isinstance(s, (int, float, Decimal)):
            return True
        
        if isinstance(s, Quantity):
            return isinstance(s.magnitude, (int, float, Decimal)) and not isinstance(s.magnitude, bool)
        
        if isinstance(s, str):
            try:
                float(s)
                return True
            except (ValueError, TypeError):
                return False
        
        return False
    
    @classmethod
    def convert_to_quantity(cls, value: str | int | float | Decimal | Quantity, unit: Optional[Union[str, Unit]]) -> Quantity:
        """根據不同的輸入類型將值轉換為 Quantity，並使用可選的默認單位"""
        # 處理單位
        if not unit:
            unit = cls.ureg.dimensionless
        elif isinstance(unit, str):
            unit = cls.ureg.Unit(unit)

        # 處理數值
        if isinstance(value, Quantity):
            if unit.dimensionality != cls.ureg.dimensionless.dimensionality and not value.check(unit.dimensionality):
                print(unit.dimensionality, cls.ureg.dimensionless.dimensionality)
                raise ValueError(f"單位不一致: {value.units} 與 {unit} 不兼容")
            return value
        elif utils.is_number(value):
            return cls.ureg.Quantity(Decimal(value), unit)
        else:
            raise ValueError("不支持的數值類型")
        
class RangeExtractor:
    """
    A class to extract numerical ranges from strings.

    This class supports various input formats, handles extra spaces, and text prefixes.
    """

    # 定義各類型的正則表達式並預編譯
    number_pattern = r'[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?'
    number_validation_pattern = re.compile(r'^' + number_pattern + r'$', re.ASCII)
    symmetric_pattern = re.compile(r'(±|\{|\+-|\+/-)')
    range_separator_pattern = re.compile(r'[~～]')
    symmetric_match_pattern = re.compile(r'(±|\{|\+-|\+/-)(' + number_pattern + r')', re.ASCII)
    to_match_pattern = re.compile(r'(' + number_pattern + r')to(' + number_pattern + r')', re.IGNORECASE | re.ASCII)
    separator_match_pattern = re.compile(r'(' + number_pattern + r')[~～](' + number_pattern + r')', re.ASCII)
    separator_match_pattern_2 = re.compile(r'(' + number_pattern + r')[/](' + number_pattern + r')', re.ASCII)
    separator_match_pattern_3 = re.compile(r'(' + number_pattern + r')[-](' + number_pattern + r')', re.ASCII)

    @staticmethod
    def is_valid_number(num_str: str) -> bool:
        """
        Validates whether a given string is a valid number based on the pattern.

        Parameters:
            num_str (str): The input string representing a number.

        Returns:
            bool: True if the string is a valid number, False otherwise.

        Raises:
            None: This function does not raise any exceptions.
        """
        # 驗證是否為有效數字
        if not num_str:
            return False
        if not RangeExtractor.number_validation_pattern.match(num_str):
            return False
        try:
            Decimal(num_str)
            return True
        except Exception:
            return False

    @staticmethod
    def extract_range(value: str) -> Tuple[Decimal, Decimal]:
        """
        Extract a numerical range from a given string.

        This method supports various formats such as symmetric ranges, "from X to Y",
        "~" (tilde) separator ranges, and "/" separator ranges.
        It can also handle extra spaces and text prefixes.

        Supported Formats
        -----------------
        1. Symmetric ranges:
        - Symbols: "±", "{", "+-", "+/-"
        - Examples:
            - "±1.5" -> (-1.5, 1.5)
            - "{2e3" -> (-2000, 2000)
            - "+-0.5" -> (-0.5, 0.5)
            - "+/-5" -> (-5, 5)
        - Restrictions:
            - Only one symmetric symbol is allowed per input.
            - Cannot mix with other range formats (e.g., '~' separator).

        2. 'X to Y' format (with optional 'from' keyword):
        - Examples:
            - "from -100 to 500" -> (-100, 500)
            - "100 to 200" -> (100, 200)
        - Restrictions:
            - The word "from" is optional, but "to" is required.
            - Only valid numbers are accepted.

        3. Range with '~' or '～' separator:
        - Examples:
            - "1~2" -> (1, 2)
            - "-1.5e2~+1.5e2" -> (-150, 150)
        - Restrictions:
            - Only one '~' or '～' symbol is allowed to define the range.
            - No additional range symbols are allowed.
            - Number_1 should be smaller than Number_2.

        4. Range with '/' separator:
        - Examples:
            - "1/2" -> (1, 2)
            - "-1.5e2/+1.5e2" -> (-150, 150)
        - Restrictions:
            - Only one '/' symbol is allowed to define the range.
            - No additional range symbols are allowed.

        5. Range with '-' separator:
        - Examples:
            - "-2-+1" -> (-2, 1)
        - Restrictions:
            - Number_1 should be smaller than Number_2.
            - No additional range symbols are allowed.

        Handling Prefixes
        -----------------
        - Ranges can be extracted from strings with descriptive text before the range.
        - Example: "Temperature range: ±1.5" -> (-1.5, 1.5)

        Handling Extra Spaces
        ---------------------
        - The function ignores extra spaces in the input.
        - Example: " 50 to 100 " -> (50, 100)

        Parameters
        ----------
        value : str
            The input string representing the numerical range.

        Returns
        -------
        Tuple[Decimal, Decimal]
            A tuple containing the lower and upper bounds as Decimal objects.

        Raises
        ------
        ValueError
            If the input format is incorrect or contains invalid numerical values.

        Examples
        --------
        >>> extract_range("±1.5")
        (Decimal('-1.5'), Decimal('1.5'))

        >>> extract_range("from -100 to 500")
        (Decimal('-100'), Decimal('500'))

        >>> extract_range("1e2~2e2")
        (Decimal('100'), Decimal('200'))

        >>> extract_range("+/-5.5")
        (Decimal('-5.5'), Decimal('5.5'))
        """
        # 去除空格，處理可能的前綴文字
        value_clean = re.sub(r'\s+', '', value)

        # 檢查是否有多個對稱符號（±、{、+-、+/-），不允許多個同類符號
        symmetric_matches = RangeExtractor.symmetric_pattern.findall(value_clean)
        if len(symmetric_matches) > 1:
            raise ValueError(f"輸入 '{value}' 包含多個對稱符號，這是不允許的。")

        # 檢查是否有多個範圍分隔符號（~、～），不允許多個範圍符號
        range_separator_matches = RangeExtractor.range_separator_pattern.findall(value_clean)
        if len(range_separator_matches) > 1:
            raise ValueError(f"輸入 '{value}' 包含多個範圍分隔符號，這是不允許的。")

        # 檢查對稱符號和範圍分隔符號是否同時存在，這是不允許的
        if symmetric_matches and range_separator_matches:
            raise ValueError(f"輸入 '{value}' 同時包含對稱和範圍分隔符號，這是不允許的。")

        # 對稱範圍處理
        symmetric_match = RangeExtractor.symmetric_match_pattern.search(value_clean)
        if symmetric_match:
            num_str = symmetric_match.group(2)
            if not RangeExtractor.is_valid_number(num_str):
                raise ValueError(f"輸入 '{value}' 中包含無效的數字。")
            num = abs(Decimal(num_str))
            return -num, num

        # 檢查 'X to Y' 格式（允許 'from' 前綴）
        to_match = RangeExtractor.to_match_pattern.search(value_clean)
        if to_match:
            num_str1 = to_match.group(1)
            num_str2 = to_match.group(2)
            if not RangeExtractor.is_valid_number(num_str1) or not RangeExtractor.is_valid_number(num_str2):
                raise ValueError(f"輸入 '{value}' 中包含無效的數字。")
            lower = Decimal(num_str1)
            upper = Decimal(num_str2)
            if lower > upper:
                raise ValueError(f"下限 {lower} 大於上限 {upper}，這是不允許的。")
            # 檢查剩餘字元中是否還有多餘數字
            remaining = value_clean[:to_match.start()] + value_clean[to_match.end():]
            if re.search(RangeExtractor.number_pattern, remaining):
                raise ValueError(f"輸入 '{value}' 包含多餘的數字或無效的範圍格式。")
            return lower, upper

        # 檢查 '~' 有序分隔符格式
        separator_match = RangeExtractor.separator_match_pattern.search(value_clean)
        if separator_match:
            num_str1 = separator_match.group(1)
            num_str2 = separator_match.group(2)
            if not RangeExtractor.is_valid_number(num_str1) or not RangeExtractor.is_valid_number(num_str2):
                raise ValueError(f"輸入 '{value}' 中包含無效的數字。")
            lower = Decimal(num_str1)
            upper = Decimal(num_str2)
            if lower > upper:
                raise ValueError(f"下限 {lower} 大於上限 {upper}，這是不允許的。")
            # 檢查剩餘字元中是否還有多餘數字
            remaining = value_clean[:separator_match.start()] + value_clean[separator_match.end():]
            if re.search(RangeExtractor.number_pattern, remaining):
                raise ValueError(f"輸入 '{value}' 包含多餘的數字或無效的範圍格式。")
            return lower, upper

        # 檢查 '-' 有序分隔符格式(目前這段是髒code，需要重寫測試判定條件與註解)
        separator_match = RangeExtractor.separator_match_pattern_3.search(value_clean)
        if separator_match:
            num_str1 = separator_match.group(1)
            num_str2 = separator_match.group(2)
            if not RangeExtractor.is_valid_number(num_str1) or not RangeExtractor.is_valid_number(num_str2):
                raise ValueError(f"輸入 '{value}' 中包含無效的數字。")
            lower = Decimal(num_str1)
            upper = Decimal(num_str2)
            if lower > upper:
                raise ValueError(f"下限 {lower} 大於上限 {upper}，這是不允許的。")
            # 檢查剩餘字元中是否還有多餘數字
            remaining = value_clean[:separator_match.start()] + value_clean[separator_match.end():]
            if re.search(RangeExtractor.number_pattern, remaining):
                raise ValueError(f"輸入 '{value}' 包含多餘的數字或無效的範圍格式。")
            return lower, upper

        # 檢查 '/' 無序分隔符格式
        separator_match = RangeExtractor.separator_match_pattern_2.search(value_clean)
        if separator_match:
            num_str1 = separator_match.group(1)
            num_str2 = separator_match.group(2)
            if not RangeExtractor.is_valid_number(num_str1) or not RangeExtractor.is_valid_number(num_str2):
                raise ValueError(f"輸入 '{value}' 中包含無效的數字。")
            lower = Decimal(num_str1) if Decimal(num_str1) < Decimal(num_str2) else Decimal(num_str2)
            upper = Decimal(num_str2) if Decimal(num_str1) < Decimal(num_str2) else Decimal(num_str1)
            # 檢查剩餘字元中是否還有多餘數字
            remaining = value_clean[:separator_match.start()] + value_clean[separator_match.end():]
            if re.search(RangeExtractor.number_pattern, remaining):
                raise ValueError(f"輸入 '{value}' 包含多餘的數字或無效的範圍格式。")
            return lower, upper

        # 如果所有格式匹配都失敗，拋出錯誤
        raise ValueError(f"輸入 '{value}' 的格式不正確或包含無效的數字。")
    
    @staticmethod
    def extend_to_range(value: str, mode: Literal['from_opposite_number', 'from_origin'] = 'from_origin') -> Tuple[Decimal, Decimal]:
        """
        Generate a range of Decimal type lower and upper bounds based on the specified mode.

        Parameters
        ----------
        value : str
            The input numerical string to be converted to Decimal.
        mode : Literal [ 'from_opposite_number' , 'from_origin' ]
            The mode for generating the range. Defaults to 'from_opposite_number'.
            Options:
                - 'from_opposite_number': Generate a range from the opposite number to the value.
                - 'from_origin': Generate a range from zero to the value.

        Returns
        -------
        Tuple[Decimal, Decimal]
            A tuple representing the lower and upper bounds of the range.
        """
        num = Decimal(value)

        if mode == 'from_opposite_number':
            # Generate range from the opposite number of 'num' to 'num'
            lower = -num if num >= 0 else num
            upper = num if num >= 0 else -num
            return lower, upper

        elif mode == 'from_origin':
            # Generate range from zero to 'num'
            lower = Decimal('0') if num >= 0 else num
            upper = num if num >= 0 else Decimal('0')
            return lower, upper

        else:
            # Raise an error if the mode is invalid
            raise ValueError("Invalid mode. Please choose 'from_opposite_number' or 'from_origin'.")
