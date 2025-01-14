import os
import ctypes
from ctypes import wintypes
from pathlib import Path
import mongoengine
import pandas as pd
from typing import Dict, Literal, List
from decimal import Decimal
from datetime import datetime
from server.models.base_components import ExactValue
# from server.models.save import CheckSpec, InspectionRecord, MeasuredResultEntry, SubTest, SubTestData
from server.models.save import InspectionRecord, InspectionAttachment, InspectionAttachmentDetails, MeasuredResultEntry, SubTest, SubTestData
from mongoengine.errors import ValidationError, NotUniqueError

def select_items(select_mode: Literal['folder', 'file', 'multi-files'], buffer_size: int = 8192) -> List[str]:
    """
    Opens a Windows dialog to select files or folders.

    Args:
        select_mode (str): The mode of selection. Options: [ 'folder' , 'file' , 'multi-files' ]
        buffer_size (int): The size of the buffer for storing file or folder paths. Defaults to 8192.

    Returns:
        List[str]: A list of selected items (files or folders). Returns an empty list if canceled or an error occurs.

    Raises:
        ValueError: If the select_mode is invalid.
    """
    # 定義 BROWSEINFO 結構體，用於文件夾選擇對話框
    class BROWSEINFO(ctypes.Structure):
        _fields_ = [
            ("hwndOwner", wintypes.HWND),               # 父視窗的句柄，None 表示無父視窗
            ("pidlRoot", wintypes.LPCVOID),             # 根目錄的 PIDL
            ("pszDisplayName", wintypes.LPWSTR),        # 用於接收文件夾名稱的緩衝區
            ("lpszTitle", wintypes.LPCWSTR),            # 對話框標題
            ("ulFlags", wintypes.UINT),                 # 對話框標誌
            ("lpfn", wintypes.LPVOID),                  # 鉤子函數的指標
            ("lParam", wintypes.LPARAM),                # 自定義數據
            ("iImage", wintypes.INT),                   # 文件夾圖標的索引
        ]
    
    # 定義 OPENFILENAME 結構體，用於文件選擇對話框
    class OPENFILENAME(ctypes.Structure):
        _fields_ = [
            ("lStructSize", wintypes.DWORD),            # 結構體的大小（以字節為單位）
            ("hwndOwner", wintypes.HWND),               # 父視窗的句柄，None 表示無父視窗
            ("hInstance", wintypes.HINSTANCE),          # 應用程序實例句柄，通常為 None
            ("lpstrFilter", wintypes.LPCWSTR),          # 文件過濾器字串，用於指定可選的文件類型
            ("lpstrCustomFilter", wintypes.LPWSTR),     # 自定義過濾器
            ("nMaxCustFilter", wintypes.DWORD),         # 自定義過濾器的大小
            ("nFilterIndex", wintypes.DWORD),           # 當前選中的過濾器索引
            ("lpstrFile", wintypes.LPWSTR),             # 文件名緩衝區的指標，用於接收用戶選中的文件路徑
            ("nMaxFile", wintypes.DWORD),               # 文件名緩衝區的大小
            ("lpstrFileTitle", wintypes.LPWSTR),        # 文件名的緩衝區指標（不含路徑）
            ("nMaxFileTitle", wintypes.DWORD),          # 文件名緩衝區的大小
            ("lpstrInitialDir", wintypes.LPCWSTR),      # 初始化對話框的目錄
            ("lpstrTitle", wintypes.LPCWSTR),           # 對話框的標題
            ("Flags", wintypes.DWORD),                  # 對話框的選項標誌
            ("nFileOffset", wintypes.WORD),             # 文件名相對於完整路徑的偏移量
            ("nFileExtension", wintypes.WORD),          # 文件擴展名在路徑中的偏移量
            ("lpstrDefExt", wintypes.LPCWSTR),          # 預設的文件擴展名
            ("lCustData", wintypes.LPARAM),             # 用戶數據，用於自定義回調
            ("lpfnHook", wintypes.LPVOID),              # 鉤子函數的指標
            ("lpTemplateName", wintypes.LPCWSTR),       # 模板名稱，用於自定義對話框界面
            ("pvReserved", wintypes.LPVOID),            # 保留字段，應設為 None
            ("dwReserved", wintypes.DWORD),             # 保留字段，應設為 0
            ("FlagsEx", wintypes.DWORD),                # 擴展標誌
        ]

    # 常量定義
    FOS_PICKFOLDERS = 0x00000020        # 文件夾選擇模式
    OFN_ALLOWMULTISELECT = 0x00000200   # 允許多選
    OFN_EXPLORER = 0x00080000           # 使用新樣式
    OFN_FILEMUSTEXIST = 0x00000008      # 文件必須存在

    # 創建緩衝區，用於接收文件或文件夾路徑
    buffer = ctypes.create_unicode_buffer(buffer_size)

    # 選擇模式: 文件夾
    if select_mode == 'folder':
        shell32 = ctypes.windll.shell32
        ole32 = ctypes.windll.ole32

        # 初始化 COM 庫
        ole32.CoInitialize(None)

        # 定義相關函數
        SHBrowseForFolder = shell32.SHBrowseForFolderW
        SHBrowseForFolder.restype = ctypes.c_void_p  # 設置返回值類型
        SHGetPathFromIDList = shell32.SHGetPathFromIDListW
        CoTaskMemFree = ole32.CoTaskMemFree

        # 初始化 BROWSEINFO 結構體
        bi = BROWSEINFO()
        bi.hwndOwner = None
        bi.pidlRoot = None
        bi.pszDisplayName = ctypes.cast(ctypes.addressof(buffer), wintypes.LPWSTR)
        bi.lpszTitle = "選擇資料夾"
        bi.ulFlags = FOS_PICKFOLDERS
        bi.lpfn = None
        bi.lParam = 0

        # 打開文件夾選擇對話框
        pidl = SHBrowseForFolder(ctypes.byref(bi))
        # 如果選擇成功，解析路徑
        if pidl:
            pidl_ptr = ctypes.cast(pidl, wintypes.LPCVOID)
            SHGetPathFromIDList(pidl_ptr, buffer)
            result = buffer[:].split("\0")
            # 釋放內存
            CoTaskMemFree(pidl_ptr)
            # 釋放 COM 庫
            ole32.CoUninitialize()
            return [result[0]]
        else:
            # 如果取消，釋放 COM 庫
            ole32.CoUninitialize()
            return []
    else:
        # 使用 comdlg32.dll（提供文件選擇對話框的功能）
        comdlg32 = ctypes.windll.comdlg32

        GetOpenFileName = comdlg32.GetOpenFileNameW
        CommDlgExtendedError = comdlg32.CommDlgExtendedError

        # 定義文件過濾器（篩選出可選的文件類型）
        filter_text = "所有檔案\0*.*\0CSV 檔案\0*.csv\0文字檔案\0*.txt\0\0"

        # 初始化 OPENFILENAME 結構體
        ofn = OPENFILENAME()
        # 設置結構體大小
        ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
        # 無父視窗
        ofn.hwndOwner = None
        # 文件過濾器
        ofn.lpstrFilter = filter_text
        # 指定文件緩衝區
        ofn.lpstrFile = ctypes.cast(ctypes.addressof(buffer), wintypes.LPWSTR)
        # 設定緩衝區大小
        ofn.nMaxFile = buffer_size

        # 選擇模式: 文件
        if select_mode == 'file':
            # 對話框標題
            ofn.lpstrTitle = "選擇檔案"
            # 設置標誌
            ofn.Flags = OFN_EXPLORER | OFN_FILEMUSTEXIST
        # 選擇模式: 複數文件
        elif select_mode == 'multi-files':
            # 對話框標題
            ofn.lpstrTitle = "選擇檔案(可複選)"
            # 設置標誌
            ofn.Flags = OFN_EXPLORER | OFN_FILEMUSTEXIST | OFN_ALLOWMULTISELECT
        else:
            raise ValueError("Invalid select_mode value. Must be 'folder', 'file', or 'multi-files'.")

        # 呼叫文件選擇對話框
        flag = GetOpenFileName(ctypes.byref(ofn))
        # 如果用戶選擇文件
        if flag:
            files = []
            # 獲取緩衝區內容
            # result = buffer[:].split("\0")
            result = [item for item in buffer[:].split("\0") if item]
            # 如果選擇多個文件
            if len(result) > 1:
                # 第一個項目是資料夾路徑
                folder = result[0]
                # 拼接路徑
                files = [os.path.join(folder, f) for f in result[1:] if f]
            # 如果僅選擇一個文件
            else:
                files = [result[0]]
            # 返回文件路徑清單
            return files
        # 如果用戶取消或發生錯誤
        else:
            # 如果取消或發生錯誤，處理錯誤碼
            error_code = CommDlgExtendedError()
            if error_code == 0:
                print("Dialog canceled.")
            else:
                print(f"Error occurred. CommDlgExtendedError code: {error_code}")
            return []


def read_csv(file_path, encoding="big5") -> Dict[Literal['mo_number', 'model_number', 'records'], str | List]:
    """
    讀取具有不固定描述說明列的 CSV 文件，找到欄位名稱行，並使用 pandas 讀取資料。
    
    Attributes:
        file_path (str): CSV 文件的路徑
        encoding (str): 文件的編碼，預設為 big5
    Return:
        Dict
    """
    header_identifier = "編號(No.)"
    model_number_identifier = "測試型號:"
    mo_number_identifier = "工單號碼:"

    # 打開文件進行掃描
    with open(file_path, 'r', encoding=encoding) as file:
        lines = file.readlines()
    
    # 找到欄位名稱所在的行號
    mo_number = None
    inspection_stage = None
    model_number = None
    header_line_index = None
    for index, line in enumerate(lines):
        if mo_number_identifier in line:
            mo_number = line.split(',')[1].split('-')[0].replace('\n','')
            inspection_stage = 'SemiProduct' if '半成品' in line.split(',')[1] else 'FinalProduct' if '成品' in line.split(',')[1] else None
        if model_number_identifier in line:
            model_number = line.split(',')[1].replace('\n','')
        if header_identifier in line:
            header_line_index = index
    
    if header_line_index is None:
        raise ValueError(f"找不到包含欄位名稱 '{header_identifier}' 的行，請檢查文件內容。")
    
    # 使用 pandas 讀取，跳過欄位名稱之前的行
    data = pd.read_csv(file_path, skiprows=header_line_index, encoding=encoding)

    # 將 DataFrame 轉換為 list[dict]
    records = data.to_dict(orient="records")

    return {
        'mo_number': mo_number,
        'inspection_stage': inspection_stage,
        'model_number': model_number,
        'records': records,
    }


measured_result_column_mapping = {
    "滿載輸入電流(mA)(FL)": {"DataType": "InputCurrent", "RemoteControlMode": "Working", "OutputCurrent": "MaximumLoad", "InputVoltage": "LowLine", "Unit": "milliampere", "SignalType": None},
    "滿載輸入電流(mA)(FN)": {"DataType": "InputCurrent", "RemoteControlMode": "Working", "OutputCurrent": "MaximumLoad", "InputVoltage": "NominalLine", "Unit": "milliampere", "SignalType": None},
    "滿載輸入電流(mA)(FH)": {"DataType": "InputCurrent", "RemoteControlMode": "Working", "OutputCurrent": "MaximumLoad", "InputVoltage": "HighLine", "Unit": "milliampere", "SignalType": None},
    "空載輸入電流(mA)(NL)": {"DataType": "InputCurrent", "RemoteControlMode": "Working", "OutputCurrent": "NoLoad", "InputVoltage": "LowLine", "Unit": "milliampere", "SignalType": None},
    "空載輸入電流(mA)(NN)": {"DataType": "InputCurrent", "RemoteControlMode": "Working", "OutputCurrent": "NoLoad", "InputVoltage": "NominalLine", "Unit": "milliampere", "SignalType": None},
    "空載輸入電流(mA)(NH)": {"DataType": "InputCurrent", "RemoteControlMode": "Working", "OutputCurrent": "NoLoad", "InputVoltage": "HighLine", "Unit": "milliampere", "SignalType": None},
    "輸出電壓(FL)(+)": {"DataType": "OutputVoltage", "OutputNumber": "1", "OutputCurrent": "MaximumLoad", "InputVoltage": "LowLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(FL)(-)": {"DataType": "OutputVoltage", "OutputNumber": "2", "OutputCurrent": "MaximumLoad", "InputVoltage": "LowLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(FN)(+)": {"DataType": "OutputVoltage", "OutputNumber": "1", "OutputCurrent": "MaximumLoad", "InputVoltage": "NominalLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(FN)(-)": {"DataType": "OutputVoltage", "OutputNumber": "2", "OutputCurrent": "MaximumLoad", "InputVoltage": "NominalLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(FH)(+)": {"DataType": "OutputVoltage", "OutputNumber": "1", "OutputCurrent": "MaximumLoad", "InputVoltage": "HighLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(FH)(-)": {"DataType": "OutputVoltage", "OutputNumber": "2", "OutputCurrent": "MaximumLoad", "InputVoltage": "HighLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(LL)(+)": {"DataType": "OutputVoltage", "OutputNumber": "1", "OutputCurrent": "MinimumLoad", "InputVoltage": "LowLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(LL)(-)": {"DataType": "OutputVoltage", "OutputNumber": "2", "OutputCurrent": "MinimumLoad", "InputVoltage": "LowLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(LN)(+)": {"DataType": "OutputVoltage", "OutputNumber": "1", "OutputCurrent": "MinimumLoad", "InputVoltage": "NominalLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(LN)(-)": {"DataType": "OutputVoltage", "OutputNumber": "2", "OutputCurrent": "MinimumLoad", "InputVoltage": "NominalLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(LH)(+)": {"DataType": "OutputVoltage", "OutputNumber": "1", "OutputCurrent": "MinimumLoad", "InputVoltage": "HighLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(LH)(-)": {"DataType": "OutputVoltage", "OutputNumber": "2", "OutputCurrent": "MinimumLoad", "InputVoltage": "HighLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(NL)(+)": {"DataType": "OutputVoltage", "OutputNumber": "1", "OutputCurrent": "NoLoad", "InputVoltage": "LowLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(NL)(-)": {"DataType": "OutputVoltage", "OutputNumber": "2", "OutputCurrent": "NoLoad", "InputVoltage": "LowLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(NN)(+)": {"DataType": "OutputVoltage", "OutputNumber": "1", "OutputCurrent": "NoLoad", "InputVoltage": "NominalLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(NN)(-)": {"DataType": "OutputVoltage", "OutputNumber": "2", "OutputCurrent": "NoLoad", "InputVoltage": "NominalLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(NH)(+)": {"DataType": "OutputVoltage", "OutputNumber": "1", "OutputCurrent": "NoLoad", "InputVoltage": "HighLine", "Unit": "volt", "SignalType": "DC"},
    "輸出電壓(NH)(-)": {"DataType": "OutputVoltage", "OutputNumber": "2", "OutputCurrent": "NoLoad", "InputVoltage": "HighLine", "Unit": "volt", "SignalType": "DC"},
    "絕緣電容(pF)": {"DataType": "InsulationCapacitance", "ComponentsGroup1": "AllInputPins", "ComponentsGroup2": "AllOutputPins", "Unit": "picofarad", "SignalType": None},
    "漏電流(uA)": {"DataType": "LeakageCurrent", "Unit": "microampere", "SignalType": None},
    "漣波雜訊(mV/VP-P)(FL)(+)": {"DataType": "RippleAndNoise", "OutputNumber": "1", "OutputCurrent": "MaximumLoad", "InputVoltage": "LowLine", "ValueLabel": "PeakToPeakMaximum", "Unit": "millivolt", "SignalType": "P-P"},
    "漣波雜訊(mV/VP-P)(FL)(-)": {"DataType": "RippleAndNoise", "OutputNumber": "2", "OutputCurrent": "MaximumLoad", "InputVoltage": "LowLine", "ValueLabel": "PeakToPeakMaximum", "Unit": "millivolt", "SignalType": "P-P"},
    "漣波雜訊(mV/VP-P)(FN)(+)": {"DataType": "RippleAndNoise", "OutputNumber": "1", "OutputCurrent": "MaximumLoad", "InputVoltage": "NominalLine", "ValueLabel": "PeakToPeakMaximum", "Unit": "millivolt", "SignalType": "P-P"},
    "漣波雜訊(mV/VP-P)(FN)(-)": {"DataType": "RippleAndNoise", "OutputNumber": "2", "OutputCurrent": "MaximumLoad", "InputVoltage": "NominalLine", "ValueLabel": "PeakToPeakMaximum", "Unit": "millivolt", "SignalType": "P-P"},
    "漣波雜訊(mV/VP-P)(FH)(+)": {"DataType": "RippleAndNoise", "OutputNumber": "1", "OutputCurrent": "MaximumLoad", "InputVoltage": "HighLine", "ValueLabel": "PeakToPeakMaximum", "Unit": "millivolt", "SignalType": "P-P"},
    "漣波雜訊(mV/VP-P)(FH)(-)": {"DataType": "RippleAndNoise", "OutputNumber": "2", "OutputCurrent": "MaximumLoad", "InputVoltage": "HighLine", "ValueLabel": "PeakToPeakMaximum", "Unit": "millivolt", "SignalType": "P-P"},
    "漣波雜訊(mV/VP-P)(LN)(+)": {"DataType": "RippleAndNoise", "OutputNumber": "1", "OutputCurrent": "MinimumLoad", "InputVoltage": "NominalLine", "ValueLabel": "PeakToPeakMaximum", "Unit": "millivolt", "SignalType": "P-P"},
    "漣波雜訊(mV/VP-P)(LN)(-)": {"DataType": "RippleAndNoise", "OutputNumber": "2", "OutputCurrent": "MinimumLoad", "InputVoltage": "NominalLine", "ValueLabel": "PeakToPeakMaximum", "Unit": "millivolt", "SignalType": "P-P"},
    "震盪頻率(KHz)FL": {"DataType": "SwitchingFrequency", "OutputCurrent":"MaximumLoad", "InputVoltage":"LowLine", "Unit": "kilohertz", "SignalType": None},
    "震盪頻率(KHz)FN": {"DataType": "SwitchingFrequency", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "kilohertz", "SignalType": None},
    "震盪頻率(KHz)FH": {"DataType": "SwitchingFrequency", "OutputCurrent":"MaximumLoad", "InputVoltage":"HighLine", "Unit": "kilohertz", "SignalType": None},
    "短路電流(mA)FL": {"DataType": "ShortCircuitProtectionInputCurrent", "OutputCurrent":"MaximumLoad", "InputVoltage":"LowLine", "Unit": "milliampere", "SignalType": None},
    "短路電流(mA)FN": {"DataType": "ShortCircuitProtectionInputCurrent", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "milliampere", "SignalType": None},
    "短路電流(mA)FH": {"DataType": "ShortCircuitProtectionInputCurrent", "OutputCurrent":"MaximumLoad", "InputVoltage":"HighLine", "Unit": "milliampere", "SignalType": None},
    "反射輸入漣波(mA/P-P)FL": {"DataType": "ReflectedInputRippleCurrent", "OutputCurrent":"MaximumLoad", "InputVoltage":"LowLine", "Unit": "milliampere", "SignalType": "P-P"},
    "反射輸入漣波(mA/P-P)FN": {"DataType": "ReflectedInputRippleCurrent", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "milliampere", "SignalType": "P-P"},
    "反射輸入漣波(mA/P-P)FH": {"DataType": "ReflectedInputRippleCurrent", "OutputCurrent":"MaximumLoad", "InputVoltage":"HighLine", "Unit": "milliampere", "SignalType": "P-P"},
    "FL暫態(uS)(+)": {"DataType": "TransientRecoveryTime", "OutputNumber": "1", "OutputCurrent":"MaximumLoad", "InputVoltage":"LowLine", "Unit": "microsecond ", "SignalType": None},
    "FL暫態(uS)(-)": {"DataType": "TransientRecoveryTime", "OutputNumber": "2", "OutputCurrent":"MaximumLoad", "InputVoltage":"LowLine", "Unit": "microsecond ", "SignalType": None},
    "FN暫態(uS)(+)": {"DataType": "TransientRecoveryTime", "OutputNumber": "1", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "microsecond ", "SignalType": None},
    "FN暫態(uS)(-)": {"DataType": "TransientRecoveryTime", "OutputNumber": "2", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "microsecond ", "SignalType": None},
    "FH暫態(uS)(+)": {"DataType": "TransientRecoveryTime", "OutputNumber": "1", "OutputCurrent":"MaximumLoad", "InputVoltage":"HighLine", "Unit": "microsecond ", "SignalType": None},
    "FH暫態(uS)(-)": {"DataType": "TransientRecoveryTime", "OutputNumber": "2", "OutputCurrent":"MaximumLoad", "InputVoltage":"HighLine", "Unit": "microsecond ", "SignalType": None},
    "FL暫態(%)(+)": {"DataType": "TransientResponseDeviation", "OutputNumber": "1", "OutputCurrent":"MaximumLoad", "InputVoltage":"LowLine", "Unit": "percent", "SignalType": None},
    "FL暫態(%)(-)": {"DataType": "TransientResponseDeviation", "OutputNumber": "2", "OutputCurrent":"MaximumLoad", "InputVoltage":"LowLine", "Unit": "percent", "SignalType": None},
    "FN暫態(%)(+)": {"DataType": "TransientResponseDeviation", "OutputNumber": "1", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "percent", "SignalType": None},
    "FN暫態(%)(-)": {"DataType": "TransientResponseDeviation", "OutputNumber": "2", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "percent", "SignalType": None},
    "FH暫態(%)(+)": {"DataType": "TransientResponseDeviation", "OutputNumber": "1", "OutputCurrent":"MaximumLoad", "InputVoltage":"HighLine", "Unit": "percent", "SignalType": None},
    "FH暫態(%)(-)": {"DataType": "TransientResponseDeviation", "OutputNumber": "2", "OutputCurrent":"MaximumLoad", "InputVoltage":"HighLine", "Unit": "percent", "SignalType": None},
    "效率(%)FL": {"DataType": "Efficiency", "OutputCurrent":"MaximumLoad", "InputVoltage":"LowLine", "Unit": "percent", "SignalType": None},
    "效率(%)FN": {"DataType": "Efficiency", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "percent", "SignalType": None},
    "效率(%)FH": {"DataType": "Efficiency", "OutputCurrent":"MaximumLoad", "InputVoltage":"HighLine", "Unit": "percent", "SignalType": None},
    "線調整率(%)(FN)(+)": {"DataType": "LineRegulation", "OutputNumber": "1", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "percent", "SignalType": None},
    "線調整率(%)(FN)(-)": {"DataType": "LineRegulation", "OutputNumber": "2", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "percent", "SignalType": None},
    "負載調整率(%)(FN)(+)": {"DataType": "LoadRegulation", "OutputNumber": "1", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "percent", "SignalType": None},
    "負載調整率(%)(FN)(-)": {"DataType": "LoadRegulation", "OutputNumber": "2", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "percent", "SignalType": None},
    "電壓平衡率(%)(FN)": {"DataType": "OutputVoltageBalance", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "percent", "SignalType": None},
    "電壓準確率(%)(FN)(+)": {"DataType": "OutputVoltageAccuracy", "OutputNumber": "1", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "percent", "SignalType": None},
    "電壓準確率(%)(FN)(-)": {"DataType": "OutputVoltageAccuracy", "OutputNumber": "2", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine", "Unit": "percent", "SignalType": None},
    "過電流保護(%)(FL)": {"DataType": "OverloadCurrentProtection", "InputVoltage":"LowLine", "Unit": "percent", "SignalType": None},
    "過電流保護(%)(FN)": {"DataType": "OverloadCurrentProtection", "InputVoltage":"NominalLine", "Unit": "percent", "SignalType": None},
    "過電流保護(%)(FH)": {"DataType": "OverloadCurrentProtection", "InputVoltage":"HighLine", "Unit": "percent", "SignalType": None},
    "Trim(Up)": {"DataType": "OutputVoltageTrimRange", "OutputNumber": "1", "Unit": "volt", "SignalType": "DC"},
    "Trim(Dn)": {"DataType": "OutputVoltageTrimRange", "OutputNumber": "1", "Unit": "volt", "SignalType": "DC"},
    "最小開機電壓(V)": {"DataType": "StartupThresholdVoltage", "Unit": "volt", "SignalType": "DC"},
    "最大關機電壓(V)": {"DataType": "UndervoltageShutdownVoltage", "Unit": "volt", "SignalType": "DC"},
    "遠端控制最大待機電壓/電流值(N)(V)": {"DataType": "RemoteControlInputVoltage", "RemoteControlMode": "Standby", "Unit": "volt", "SignalType": "DC"},
    "遠端控制最大待機電壓/電流值(N)(mA)": {"DataType": "RemoteControlInputCurrent", "RemoteControlMode": "Standby", "Unit": "milliampere", "SignalType": None},
    "OverShoot(%)(+V)(L)": {"DataType": "Overshoot", "OutputNumber": "1", "InputVoltage":"LowLine", "Unit": "percent", "SignalType": None},
    "OverShoot(%)(-V)(L)": {"DataType": "Overshoot", "OutputNumber": "2", "InputVoltage":"LowLine", "Unit": "percent", "SignalType": None},
    "OverShoot(%)(+V)(N)": {"DataType": "Overshoot", "OutputNumber": "1", "InputVoltage":"NominalLine", "Unit": "percent", "SignalType": None},
    "OverShoot(%)(-V)(N)": {"DataType": "Overshoot", "OutputNumber": "2", "InputVoltage":"NominalLine", "Unit": "percent", "SignalType": None},
    "OverShoot(%)(+V)(H)": {"DataType": "Overshoot", "OutputNumber": "1", "InputVoltage":"HighLine", "Unit": "percent", "SignalType": None},
    "OverShoot(%)(-V)(H)": {"DataType": "Overshoot", "OutputNumber": "2", "InputVoltage":"HighLine", "Unit": "percent", "SignalType": None},
    "遠端控制最小工作電壓/電流值(N)(V)": {"DataType": "RemoteControlInputVoltage", "RemoteControlMode": "Working", "Unit": "volt", "SignalType": "DC"},
    "遠端控制最小工作電壓/電流值(N)(mA)": {"DataType": "RemoteControlInputCurrent", "RemoteControlMode": "Working", "Unit": "milliampere", "SignalType": None},
    "短路操作頻率最大值(L)(hz)": {"DataType": "ShortCircuitProtectionFrequency", "InputVoltage":"LowLine", "Unit": "hertz", "SignalType": None},
    "短路操作頻率最大值(N)(hz)": {"DataType": "ShortCircuitProtectionFrequency", "InputVoltage":"NominalLine", "Unit": "hertz", "SignalType": None},
    "短路操作頻率最大值(H)(hz)": {"DataType": "ShortCircuitProtectionFrequency", "InputVoltage":"HighLine", "Unit": "hertz", "SignalType": None},
    "待機最大電流(RMT=0)(N)(mA)": {"DataType": "InputCurrent", "RemoteControlMode": "Standby", "OutputCurrent": "NoLoad", "InputVoltage": "NominalLine", "Unit": "milliampere", "SignalType": "DC"},
}
sub_test_mapping = {
    "Remote ON": {"TestType": "RemoteControlTest"},
    "Remote OFF": {"TestType": "RemoteControlTest"},
    "I.R.": {"TestType": "InsulationResistanceTest"},
    "HI-POT": {"TestType": "HighPotentialTest"},
    "FL開機測試(R+C)": {"TestType": "StartupTest", "ElectricalLoadType": "ResistorLoad+CapacitorLoad", "OutputCurrent":"MaximumLoad", "InputVoltage":"LowLine"},
    "FL開機測試(R)": {"TestType": "StartupTest", "ElectricalLoadType": "ResistorLoad", "OutputCurrent":"MaximumLoad", "InputVoltage":"LowLine"},
    "FL開機測試(E)": {"TestType": "StartupTest", "ElectricalLoadType": "ElectronicLoad", "OutputCurrent":"MaximumLoad", "InputVoltage":"LowLine"},
    "FL開機測試(E+C)": {"TestType": "StartupTest", "ElectricalLoadType": "ElectronicLoad+CapacitorLoad", "OutputCurrent":"MaximumLoad", "InputVoltage":"LowLine"},
    "FN開機測試(R+C)": {"TestType": "StartupTest", "ElectricalLoadType": "ResistorLoad+CapacitorLoad", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine"},
    "FN開機測試(R)": {"TestType": "StartupTest", "ElectricalLoadType": "ResistorLoad", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine"},
    "FN開機測試(E)": {"TestType": "StartupTest", "ElectricalLoadType": "ElectronicLoad", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine"},
    "FN開機測試(E+C)": {"TestType": "StartupTest", "ElectricalLoadType": "ElectronicLoad+CapacitorLoad", "OutputCurrent":"MaximumLoad", "InputVoltage":"NominalLine"},
    "FH開機測試(R+C)": {"TestType": "StartupTest", "ElectricalLoadType": "ResistorLoad+CapacitorLoad", "OutputCurrent":"MaximumLoad", "InputVoltage":"HighLine"},
    "FH開機測試(R)": {"TestType": "StartupTest", "ElectricalLoadType": "ResistorLoad", "OutputCurrent":"MaximumLoad", "InputVoltage":"HighLine"},
    "FH開機測試(E)": {"TestType": "StartupTest", "ElectricalLoadType": "ElectronicLoad", "OutputCurrent":"MaximumLoad", "InputVoltage":"HighLine"},
    "FH開機測試(E+C)": {"TestType": "StartupTest", "ElectricalLoadType": "ElectronicLoad+CapacitorLoad", "OutputCurrent":"MaximumLoad", "InputVoltage":"HighLine"},
    "LL開機測試(R+C)": {"TestType": "StartupTest", "ElectricalLoadType": "ResistorLoad+CapacitorLoad", "OutputCurrent":"MinimumLoad", "InputVoltage":"LowLine"},
    "LL開機測試(R)": {"TestType": "StartupTest", "ElectricalLoadType": "ResistorLoad", "OutputCurrent":"MinimumLoad", "InputVoltage":"LowLine"},
    "LL開機測試(E)": {"TestType": "StartupTest", "ElectricalLoadType": "ElectronicLoad", "OutputCurrent":"MinimumLoad", "InputVoltage":"LowLine"},
    "LL開機測試(E+C)": {"TestType": "StartupTest", "ElectricalLoadType": "ElectronicLoad+CapacitorLoad", "OutputCurrent":"MinimumLoad", "InputVoltage":"LowLine"},
    "LN開機測試(R+C)": {"TestType": "StartupTest", "ElectricalLoadType": "ResistorLoad+CapacitorLoad", "OutputCurrent":"MinimumLoad", "InputVoltage":"NominalLine"},
    "LN開機測試(R)": {"TestType": "StartupTest", "ElectricalLoadType": "ResistorLoad", "OutputCurrent":"MinimumLoad", "InputVoltage":"NominalLine"},
    "LN開機測試(E)": {"TestType": "StartupTest", "ElectricalLoadType": "ElectronicLoad", "OutputCurrent":"MinimumLoad", "InputVoltage":"NominalLine"},
    "LN開機測試(E+C)": {"TestType": "StartupTest", "ElectricalLoadType": "ElectronicLoad+CapacitorLoad", "OutputCurrent":"MinimumLoad", "InputVoltage":"NominalLine"},
    "LH開機測試(R+C)": {"TestType": "StartupTest", "ElectricalLoadType": "ResistorLoad+CapacitorLoad", "OutputCurrent":"MinimumLoad", "InputVoltage":"HighLine"},
    "LH開機測試(R)": {"TestType": "StartupTest", "ElectricalLoadType": "ResistorLoad", "OutputCurrent":"MinimumLoad", "InputVoltage":"HighLine"},
    "LH開機測試(E)": {"TestType": "StartupTest", "ElectricalLoadType": "ElectronicLoad", "OutputCurrent":"MinimumLoad", "InputVoltage":"HighLine"},
    "LH開機測試(E+C)": {"TestType": "StartupTest", "ElectricalLoadType": "ElectronicLoad+CapacitorLoad", "OutputCurrent":"MinimumLoad", "InputVoltage":"HighLine"},
    # "輕載失控(LL)": LightLoadStabilityTest
    # "輕載失控(LN)": 
    # "輕載失控(LH)": 
    # "輕載加到滿載(L)": 
    # "輕載加到滿載(N)": 
    # "輕載加到滿載(H)": 
    # "電阻切換負載(L)": 
    # "電阻切換負載(N)": 
    # "電阻切換負載(H)": 
    # "R+C切換負載(L)": 
    # "R+C切換負載(N)": 
    # "R+C切換負載(H)": 
    # "E+C切換負載(L)": 
    # "E+C切換負載(N)": 
    # "E+C切換負載(H)": 
    # "電子開機測試": StartupTest, ElectronicLoad,
    # "電子關機測試": ShutdownTest, ElectronicLoad,
}
其他欄位 = {
    "R4'V監控電壓": None,
    "P3'V38**之P3電壓": None,
    "P7'V38**之P7電壓": None,
    "VDS責任週期(FL)": "DutyCycle",
    "VDS責任週期(FN)": None,
    "VDS責任週期(FH)": None,
    "VGS(FL)": "閘極源極電壓",
    "VGS(FH)": None,
    "VDS(FN)": "汲極源極電壓",
    "VDS(FH)": None,
    "ULVO(N)": ["UnderVoltageLockout","欠壓鎖定"],
}
pictures = {
    "Image:RippleFreq(FL)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'RippleFrequency', 'OutputCurrent': 'MaximumLoad', 'InputVoltage': 'LowLine'},
    "Image:RippleFreq(FN)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'RippleAndNoise', 'OutputCurrent': 'MaximumLoad', 'InputVoltage': 'NominalLine'},
    "Image:RippleFreq(FH)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'RippleAndNoise', 'OutputCurrent': 'MaximumLoad', 'InputVoltage': 'NominalLine'},
    "Image:RippleFreq(LN)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'RippleAndNoise', 'OutputCurrent': 'MinimumLoad', 'InputVoltage': 'NominalLine'},
    # "Image:IiRef(FL)": 
    # "Image:IiRef(FN)": 
    # "Image:IiRef(FH)": 
    # "Image:VoDYNA(FL)": 
    # "Image:VoDYNA(FN)": 
    # "Image:VoDYNA(FH)": 
    # "Image:VGS(FL)": 
    # "Image:VGS(FH)": 
    # "Image:VDS(FN)": 
    # "Image:VDS(FH)": 
    # "Image:DutyCycle(FL)": 
    # "Image:DutyCycle(FN)": 
    # "Image:DutyCycle(FH)": 
    "Image:OverShoot(FL)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'OverShoot', 'OutputCurrent': 'MaximumLoad', 'InputVoltage': 'LowLine'},
    "Image:OverShoot(FN)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'OverShoot', 'OutputCurrent': 'MaximumLoad', 'InputVoltage': 'NominalLine'},
    "Image:OverShoot(FH)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'OverShoot', 'OutputCurrent': 'MaximumLoad', 'InputVoltage': 'HighLine'},
    "Image:VoShortFreqMax(L)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'ShortCircuitProtectionFrequency', 'OutputCurrent': None, 'InputVoltage': 'LowLine'},
    "Image:VoShortFreqMax(N)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'ShortCircuitProtectionFrequency', 'OutputCurrent': None, 'InputVoltage': 'NominalLine'},
    "Image:VoShortFreqMax(H)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'ShortCircuitProtectionFrequency', 'OutputCurrent': None, 'InputVoltage': 'HighLine'},
    # "Image:OverShoot(ViL)": 
    # "Image:OverShoot(ViN)": 
    # "Image:OverShoot(ViH)": 
    "Image:Rmt_On/Off(L)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'RemoteControl_ON_OFF', 'OutputCurrent': None, 'InputVoltage': 'LowLine'},
    "Image:Rmt_On/Off(N)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'RemoteControl_ON_OFF', 'OutputCurrent': None, 'InputVoltage': 'NominalLine'},
    "Image:Rmt_On/Off(H)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'RemoteControl_ON_OFF', 'OutputCurrent': None, 'InputVoltage': 'HighLine'},
    "Image:Freq(FL)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'SwitchingFrequency', 'OutputCurrent': 'MaximumLoad', 'InputVoltage': 'LowLine'},
    "Image:Freq(FN)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'SwitchingFrequency', 'OutputCurrent': 'MaximumLoad', 'InputVoltage': 'NominalLine'},
    "Image:Freq(FH)": {'AttachmentType': 'OscilloscopeImage', 'MeasuredTarget': 'SwitchingFrequency', 'OutputCurrent': 'MaximumLoad', 'InputVoltage': 'HighLine'},
}

if __name__ == '__main__':
    # Connect to MongoDB using the provided connection string.
    mongoengine.connect(host='mongodb://localhost:27017/testdataplatform-db')

    inspection_records: List[InspectionRecord] = []
    SubTests: List[SubTest] = []
    MeasuredResultTable: List[MeasuredResultEntry] = []
    AmbientTemperature: ExactValue = None
    FinishAt: datetime = None
    Attachments: List[InspectionAttachment] = []

    file_path_list = select_items(select_mode='multi-files')

    for full_file_path in file_path_list:
        try:
            data = read_csv(Path(full_file_path))
        except:
            print(f'無法讀取路徑: {full_file_path}')
            continue

        for row in data['records']:
            MeasuredResultTable = []
            Attachments = []
            for column_name in measured_result_column_mapping:
                value = row[column_name]
                if not value:
                    continue
                if isinstance(value, str) and value != '824999999999999000000000000000000000000.00%' and value != '-824999999999999000000000000000000000000.00%':
                    if value.endswith('%'):
                        if measured_result_column_mapping[column_name]['Unit'] == '%' or measured_result_column_mapping[column_name]['Unit'] == 'percent':
                            value = Decimal(value.replace('%', ''))
                        else:
                            raise ValueError(f'DataType={measured_result_column_mapping[column_name]['DataType']}, Value={value} has % but Unit={measured_result_column_mapping[column_name]['Unit']} does not use %')
                if isinstance(value, (float, Decimal)) and -1e38 < value < 1e38:
                    value = Decimal(value)
                else:
                    continue
                try:
                    measured_result_entry = MeasuredResultEntry(
                        DataType=measured_result_column_mapping[column_name]['DataType'],
                        ExactValue=ExactValue(
                            Value=value,
                            Unit=measured_result_column_mapping[column_name]['Unit'],
                            SignalType=measured_result_column_mapping[column_name]['SignalType'],
                        ),
                        CheckSpec=None,
                    )
                except:
                    print(column_name, value)
                for key in measured_result_column_mapping[column_name]:
                    if key not in ['DataType', 'Unit', 'SignalType']:
                        measured_result_entry[key] = measured_result_column_mapping[column_name][key]
                MeasuredResultTable.append(measured_result_entry)
            for column_name in sub_test_mapping:
                value = row[column_name]
                if value is None:
                    continue
                if isinstance(value, str):
                    if value.strip().lower() in ['passed', 'pass', 'true', 'ok']:
                        value = True
                    elif value.strip().lower() in ['failed', 'fail', 'false', 'ng']:
                        value = False
                    else:
                        raise ValueError(f'TestType={sub_test_mapping[column_name]['TestType']}, Value={value} not in passed/failed, pass/fail, true/false, ok/ng')
                elif not isinstance(value, bool):
                    continue

                parameters = []
                for key in sub_test_mapping[column_name]:
                    if key != 'TestType':
                        parameters.append(SubTestData(DataName=key, TextValue=sub_test_mapping[column_name][key]))
                test = SubTest(
                    TestType=sub_test_mapping[column_name]['TestType'],
                    Parameters=parameters,
                    IsPassed=value,
                )
                SubTests.append(test)

            for column_name in pictures:
                value = row[column_name]
                if value is None or not isinstance(value, str):
                    continue

                Attachments.append(
                    InspectionAttachment(
                        AttachmentType=pictures[column_name]['AttachmentType'],
                        FilePath=value,
                        Description='',
                        Details=InspectionAttachmentDetails(
                            MeasuredTarget=pictures[column_name]['MeasuredTarget'],
                            OutputCurrent=pictures[column_name]['OutputCurrent'],
                            InputVoltage=pictures[column_name]['InputVoltage'],
                        ),
                    )
                )

            if isinstance(row['溫度(攝氏)'], (str, float)):
                AmbientTemperature = ExactValue(
                    Value=Decimal(row['溫度(攝氏)']),
                    Unit='degC',
                )

            if isinstance(row['測試時間'], str):
                try:
                    FinishAt = datetime.strptime(row['測試時間'], '%Y/%m/%d %H:%M:%S')
                except ValueError:
                    FinishAt = datetime.strptime(row['測試時間'], '%Y/%m/%d %H:%M')
            elif isinstance(row['測試時間'], datetime):
                FinishAt = row['測試時間']
            
            inspection_record = InspectionRecord(
                ModelNumber=data['model_number'],
                ManufacturingOrderNumber=data['mo_number'],
                InspectionStage=data['inspection_stage'],
                TestMethod='Automated',
                EquipmentIds=[],
                InspectorIds=[],
                FinishAt=FinishAt,
                AmbientTemperature=AmbientTemperature,
                RelativeHumidity=None,
                AtmosphericPressure=None,
                SubTests=SubTests,
                MeasuredResultTable=MeasuredResultTable,
                Attachments=Attachments,
                Notes=None,
            )

            # Validate the product instance
            try:
                inspection_record.save()
            except ValidationError as e:
                print(f"{inspection_record.ModelNumber} 格式驗證報錯跳過 : {e}")
                continue

        # for item in MeasuredResultTable:
        #     print(item.to_json())
        # for item in SubTests:
        #     print(item.to_json())
