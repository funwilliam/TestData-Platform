import os
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