import os
import sys
import pytz
import ntplib
import platform
import traceback
import ctypes
import pandas as pd
from pathlib import Path
from ctypes import wintypes
from typing import List, Dict, Any, Tuple, Literal
from time import ctime
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN

class utils:
    @classmethod
    def make_DBURL(cls, user: str, password: str, host: str, port: str, database_name: str) -> str:
        """ 建立資料庫連接字串 """
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database_name}"
        return db_url