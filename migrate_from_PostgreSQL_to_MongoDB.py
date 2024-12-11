import re
import psycopg2
import mongoengine
from decimal import Decimal, ROUND_HALF_UP
from psycopg2.extras import RealDictCursor
from mongoengine.errors import ValidationError, NotUniqueError
from server.helpers.utils import RangeExtractor, utils
from server.models.spec import *

# Connect to MongoDB using the provided connection string.
mongoengine.connect(host='mongodb://localhost:27017/testdataplatform-db')

# 連接到 PostgreSQL 資料庫
conn = psycopg2.connect(
    dbname="pg-productspec-db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)

# 建立使用 RealDictCursor 的游標
cursor = conn.cursor(cursor_factory=RealDictCursor)

# 查詢接腳資料
query = """
SELECT
    "外觀尺寸編號",
    "接腳編號",
    "接腳功能",
    "直徑_mm"
FROM public."接腳說明"
ORDER BY "外觀尺寸編號" ASC, "接腳編號" ASC
"""
cursor.execute(query)
pin_record_rows = cursor.fetchall()

# 查詢主要規格資料
query = """
WITH AvailableModels AS (
    -- 取得 "型號" 與 "產品規格" 表中有交集的型號
    SELECT mo."型號", mo."轉換類型", mo."系列"
    FROM "型號" mo
    INNER JOIN "產品規格" ps ON mo."型號" = ps."主型號"
)
SELECT 
    am."型號",  -- 只選擇 AvailableModels 的 "型號"
    am."轉換類型",  -- 加入 "轉換類型"
    am."系列",  -- 加入 "系列"
    ps.*,  -- 取得 "產品規格" 表中的所有欄位
    pt."STEP", 
    pt."操作溫度範圍 2", 
    pt."電阻值", 
    pt."電容值", 
    pt."輸出電壓調整範圍最大 2", 
    pt."輸出電壓調整範圍最小 2", 
    pt."輸出調整電壓電阻值 2", 
    pt."測試用電阻負載KEY 1", 
    pt."測試用電阻負載KEY 2", 
    pt."Start up time", 
    pt."過溫度保護範圍", 
    pt."開機點最高值", 
    pt."關機點最高值", 
    pt."負載1", 
    pt."負載2", 
    pt."負載3", 
    pt."負載4", 
    pt."負載1輸入電壓", 
    pt."負載2輸入電壓", 
    pt."負載3輸入電壓", 
    pt."負載4輸入電壓", 
    pt."操作溫度2", 
    pt."操作溫度3", 
    pt."操作溫度4", 
    pt."交換頻率範圍值", 
    pt."操作溫度5", 
    pt."負載5輸入電壓", 
    pt."負載5", 
    pt."操作溫度單位1", 
    pt."操作溫度單位2", 
    pt."操作溫度單位3", 
    pt."備註五", 
    pt."3",  
    u.*    -- 取得 "單位" 表中的所有欄位
FROM 
    AvailableModels am
LEFT JOIN 
    "產品規格" ps ON am."型號" = ps."主型號"
LEFT JOIN 
    "包裝管標籤" pt ON am."型號" = pt."型號"
LEFT JOIN 
    "單位" u ON am."型號" = u."型號"
ORDER BY 
    am."型號";
"""
cursor.execute(query)
main_record_rows = cursor.fetchall()

cursor.close()
conn.close()

pin_info_dict = {}
for record in pin_record_rows:
    外觀尺寸編號 = record.get('外觀尺寸編號')
    接腳編號 = record.get('接腳編號')
    接腳功能 = record.get('接腳功能')
    直徑_mm = record.get('直徑_mm')
    
    if 外觀尺寸編號 not in pin_info_dict:
        pin_info_dict[外觀尺寸編號] = []
    
    pin_info_dict[外觀尺寸編號].append({
        "接腳編號": 接腳編號,
        "接腳功能": 接腳功能,
        "直徑_mm": 直徑_mm
    })

products = []
for record in main_record_rows:
    # if record.get('主型號') != 'MJWI10-48D05':
    #     continue
    try:
        # [Category]
        SeriesNumber = record.get('系列')
        # 輸出組數
        OutputQuantity = int(bool(record.get('額定輸出1'))) + int(bool(record.get('額定輸出3')))
        # 轉換類型
        ConverterType = record.get('轉換類型', 'DC->DC')
        # 擁有輸出穩壓功能
        OutputRegulation = None # 因無判斷方法，初始化僅先佔位
        # 遠端控制類型
        RemoteControlType = 'UNDEFINED'
        if record.get('遠端開 / 關控制 '):
            if record.get('遠端開 / 關控制 ').lower().strip() == 'Enable High'.lower().strip():
                RemoteControlType = 'Enable High'
            if record.get('遠端開 / 關控制 ').lower().strip() == 'Enable Low'.lower().strip():
                RemoteControlType = 'Enable Low'
        # 擁有輸出微調功能
        OutputTrim = bool(record.get('輸出調整電壓範圍最大值') or record.get('輸出調整電壓範圍最小值'))
        # Iinput/Output隔離電壓等級
        IoIsolation = None # 因無判斷方法，初始化僅先佔位
        # 絕緣系統類型
        InsulationSystemType = None # 因無判斷方法，初始化僅先佔位
        # 安裝類型
        MountingType = None # 因無判斷方法，初始化僅先佔位
        # 封裝類型
        PackageType = None # 因無判斷方法，初始化僅先佔位
        # 主要應用領域
        Applications = None # 因無判斷方法，初始化僅先佔位

        # [InspectionParameters]
        # 零件
        GS_Component = {key: [] for key in ["Case", "Pin"]}
        GS_Component["Case"].append(
            ComponentInstance(
                Number='1',
                Statement=None
            )
        )
        appearance_category = record.get('外觀尺寸編')
        for pin in pin_info_dict.get(appearance_category, []):
            GS_Component["Pin"].append(
                ComponentInstance(
                    Number=pin.get('接腳編號'),
                    Statement=pin.get('接腳功能')
                )
            )
        # 輸入輸出
        GS_InputOutput = {key: [] for key in ["Input", "Output"]}
        GS_InputOutput["Input"].append(
            IOInstance(
                Number="1",
                PinPair=None # 因無判斷方法，初始化暫不填值
            )
        )
        for i in range(OutputQuantity):
            GS_InputOutput["Output"].append(
                IOInstance(
                    Number=str(i + 1),
                    PinPair=None # 因無判斷方法，初始化暫不填值
                )
            )
        # 環境溫度的實例
        GS_AmbientTemperature=[]
        if record.get('操作溫度範圍'):
            try:
                lower, upper = RangeExtractor.extract_range(record.get('操作溫度範圍'))
                GS_AmbientTemperature = [
                    Instance(
                        ValueLabel=["低溫", "MinimumTemperature"],
                        ExactValue={
                            "Value": lower,
                            "Unit": "degC",
                            "SignalType": None
                        }
                    ),
                    Instance(
                        ValueLabel=["常溫", "RoomTemperature"],
                        ExactValue={
                            "Value": 25,
                            "Unit": "degC",
                            "SignalType": None
                        }
                    ),
                    Instance(
                        ValueLabel=["高溫", "MaximumTemperature"],
                        ExactValue={
                            "Value": upper,
                            "Unit": "degC",
                            "SignalType": None
                        }
                    )
                ]
            except:
                # 從 record 中取得 '主型號'，並打印錯誤訊息，提示 RangeExtractor.extract_range() 無法套用在 record 中的 "操作溫度範圍" 字串數據上
                print(f'{record.get("主型號")}: Fail to execute RangeExtractor.extract_range() on input string: record["操作溫度範圍"]="{record.get('操作溫度範圍')}"')
                continue
        # 輸入電壓MAP
        input_voltage_map = {}
        # 輸入電壓的實例
        GS_InputVoltage = []
        # 輸入電壓-最大值
        if record.get('輸入電壓最'):
            input_voltage_map[Decimal(record.get('輸入電壓最'))] = 'HighLine'
            GS_InputVoltage.append(
                Instance(
                    ValueLabel=["最高值", "上限", "HighLine"],
                    ExactValue={
                        "Value": Decimal(record.get('輸入電壓最')),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
                )
            )
        # 輸入電壓-中間值
        if record.get('輸入電壓中'):
            input_voltage_map[Decimal(record.get('輸入電壓中'))] = 'NominalLine'
            GS_InputVoltage.append(
                Instance(
                    ValueLabel=["中心值", "標準", "NominalLine"],
                    ExactValue={
                        "Value": Decimal(record.get('輸入電壓中')),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
                )
            )
        # 輸入電壓-最小值
        if record.get('輸入電壓2'):
            input_voltage_map[Decimal(record.get('輸入電壓2'))] = 'LowLine'
            GS_InputVoltage.append(
                Instance(
                    ValueLabel=["最低值", "下限", "LowLine"],
                    ExactValue={
                        "Value": Decimal(record.get('輸入電壓2')),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
                )
            )
        # 輸出電壓的實例
        GS_OutputVoltage = []
        # 輸出電壓-額定值-輸出1
        if record.get('額定輸出1'):
            GS_OutputVoltage.append(
                Instance(
                    OutputNumber="1",
                    ExactValue={
                        "Value": Decimal(record.get('額定輸出1')),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
                )
            )
        # 輸出電壓-額定值-輸出2
        if record.get('額定輸出3'):
            GS_OutputVoltage.append(
                Instance(
                    OutputNumber="2",
                    ExactValue={
                        "Value": Decimal(record.get('額定輸出3')),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
                )
            )
        # 輸出電流MAP
        output_current_map = {}
        # 輸出電流的實例
        GS_OutputCurrent = []
        # 輸出電流-滿載-輸出1
        if record.get('額定輸出2'):
            GS_OutputCurrent.append(
                Instance(
                    OutputNumber="1",
                    ValueLabel=["Nominal", "MaximumLoad", "滿載"],
                    ExactValue={
                        "Value": record.get('額定輸出2'),
                        "Unit": "milliampere",
                        "SignalType": None
                    }
                )
            )
        # 輸出電流-滿載-輸出2
        if record.get('額定輸出4'):
            GS_OutputCurrent.append(
                Instance(
                    OutputNumber="2",
                    ValueLabel=["Nominal", "MaximumLoad", "滿載"],
                    ExactValue={
                        "Value": record.get('額定輸出4'),
                        "Unit": "milliampere",
                        "SignalType": None
                    }
                )
            )
        # 輸出電流-輕載-輸出1
        if record.get('測試用輕載'):
            GS_OutputCurrent.append(
                Instance(
                    OutputNumber="1",
                    ValueLabel=["Light", "MinimumLoad", "輕載"],
                    ExactValue={
                        "Value": record.get('測試用輕載'),
                        "Unit": "milliampere",
                        "SignalType": None
                    }
                )
            )
        # 輸出電流-輕載-輸出2
        if record.get('測試用輕2'):
            GS_OutputCurrent.append(
                Instance(
                    OutputNumber="1",
                    ValueLabel=["Light", "MinimumLoad", "輕載"],
                    ExactValue={
                        "Value": record.get('測試用輕2'),
                        "Unit": "milliampere",
                        "SignalType": None
                    }
                )
            )
        # 輸出電流-空載
        for i in range(OutputQuantity):
            GS_OutputCurrent.append(
                Instance(
                    OutputNumber=str(i + 1),
                    ValueLabel=["NoLoad", "空載"],
                    ExactValue={
                        "Value": 0,
                        "Unit": "milliampere",
                        "SignalType": None
                    }
                )
            )
        # 輸出電流-滿載值
        if record.get('額定輸出2') or record.get('額定輸出4'):
            total_output_current = abs(record.get('額定輸出2', 0) or 0) + abs(record.get('額定輸出4', 0) or 0)
            output_current_map[Decimal(total_output_current)] = 'MaximumLoad'
        # 輸出電流-輕載值
        if record.get('測試用輕載') or record.get('測試用輕2'):
            output_current = abs(record.get('測試用輕載', 0) or 0) + abs(record.get('測試用輕2', 0) or 0)
            output_current_map[Decimal(output_current)] = 'MinimumLoad'
        # 輸出電流-空載值
        output_current_map[Decimal(0)]='NoLoad'
        # 輸出功率總和-額定值
        GS_OutputPower = []
        if (
            (record.get('額定輸出1') and record.get('額定輸出2')) or
            (record.get('額定輸出3') and record.get('額定輸出4')) or
            (record.get('額定輸出5') and record.get('額定輸出6')) or
            (record.get('額定輸出7') and record.get('額定輸出8')) or
            record.get('額定輸出功')
        ):
            output_power = Decimal(0)
            if record.get('額定輸出1') and record.get('額定輸出2'):
                output_1_power = Decimal(record.get('額定輸出1')) * Decimal(record.get('額定輸出2'))
                if output_1_power >= 0:
                    output_power += output_1_power
                else:
                    raise ValueError(f'"{record.get("主型號")}"."額定輸出功率總和"."輸出1的功率不能為負值"。實際值(電壓*電流): "{record.get('額定輸出1')} * {record.get('額定輸出2')} = {output_1_power}"')
            if record.get('額定輸出3') and record.get('額定輸出4'):
                output_2_power = Decimal(record.get('額定輸出3')) * Decimal(record.get('額定輸出4'))
                if output_2_power >= 0:
                    output_power += output_2_power
                else:
                    raise ValueError(f'"{record.get("主型號")}"."額定輸出功率總和"."輸出2的功率不能為負值"。實際值(電壓*電流): "{record.get('額定輸出3')} * {record.get('額定輸出4')} = {output_2_power}"')
            if record.get('額定輸出5') and record.get('額定輸出6'):
                output_3_power = Decimal(record.get('額定輸出5')) * Decimal(record.get('額定輸出6'))
                if output_3_power >= 0:
                    output_power += output_3_power
                else:
                    raise ValueError(f'"{record.get("主型號")}"."額定輸出功率總和"."輸出3的功率不能為負值"。實際值(電壓*電流): "{record.get('額定輸出5')} * {record.get('額定輸出6')} = {output_3_power}"')
            output_power /= 1000
            if record.get('額定輸出7'):
                output_power += Decimal(record.get('額定輸出7'))
            if record.get('額定輸出8'):
                output_power += Decimal(record.get('額定輸出8'))
            if record.get('額定輸出功'):
                output_power += Decimal(record.get('額定輸出功'))
            GS_OutputPower = [
                Instance(
                    ValueLabel=["NominalOutputPower", "MaximumOutputPower"],
                    ExactValue={
                        "Value": output_power.quantize(Decimal('0.001'), ROUND_HALF_UP),
                        "Unit": "watt",
                        "SignalType": None
                    }
                )
            ]
        # 測試用電阻負載
        GS_ResistiveLoad = []
        if (
            (record.get('額定輸出1') and record.get('額定輸出2')) or
            (record.get('額定輸出3') and record.get('額定輸出4'))
        ):
            output_1_abstract_pair = None
            output_2_abstract_pair = None
            simplified_test_abstract_pair = None
            if OutputQuantity == 1:
                output_1_abstract_pair = ['+vout', '-vout']
            elif OutputQuantity == 2:
                output_1_abstract_pair = ['+vout', 'common']
                output_2_abstract_pair = ['common', '-vout']
                simplified_test_abstract_pair = ['+vout', '-vout']
            if record.get('額定輸出1') and record.get('額定輸出2'):
                output_voltage_obj = FormulaVariable(
                    Type="#/Inspections/default/Parameters/OutputVoltage",
                    Condition={
                        "OutputNumber": "1",
                        "ValueLabel": "Nominal",
                    },
                    GetValue="ExactValue",
                )
                output_current_obj = FormulaVariable(
                    Type="#/Inspections/default/Parameters/OutputCurrent",
                    Condition={
                        "OutputNumber": "1",
                        "ValueLabel": "Nominal",
                    },
                    GetValue="ExactValue",
                )
                formula = LocalFormula(
                    Expression="output_voltage/output_current",
                    Variables={
                        "output_voltage": output_voltage_obj,
                        "output_current": output_current_obj,
                    }
                )
                GS_ResistiveLoad.append(
                    LoadInstance(
                        AbstractPair=output_1_abstract_pair,
                        ExactValue={
                            "Formula": formula,
                            "Unit": "CALCULATE_RESULT",
                            "SignalType": None
                        }
                    )
                )
            if record.get('額定輸出3') and record.get('額定輸出4'):
                output_voltage_obj = FormulaVariable(
                    Type="#/Inspections/default/Parameters/OutputVoltage",
                    Condition={
                        "OutputNumber": "2",
                        "ValueLabel": "Nominal",
                    },
                    GetValue="ExactValue",
                )
                output_current_obj = FormulaVariable(
                    Type="#/Inspections/default/Parameters/OutputCurrent",
                    Condition={
                        "OutputNumber": "2",
                        "ValueLabel": "Nominal",
                    },
                    GetValue="ExactValue",
                )
                formula = LocalFormula(
                    Expression="output_voltage/output_current",
                    Variables={
                        "output_voltage": output_voltage_obj,
                        "output_current": output_current_obj,
                    }
                )
                GS_ResistiveLoad.append(
                    LoadInstance(
                        AbstractPair=output_2_abstract_pair,
                        ExactValue={
                            "Formula": formula,
                            "Unit": "CALCULATE_RESULT",
                            "SignalType": None
                        }
                    )
                )
            if record.get('額定輸出1') and record.get('額定輸出2') and record.get('額定輸出3') and record.get('額定輸出4'):
                output_voltage_obj_1 = FormulaVariable(
                    Type="#/Inspections/default/Parameters/OutputVoltage",
                    Condition={
                        "OutputNumber": "1",
                        "ValueLabel": "Nominal",
                    },
                    GetValue="ExactValue",
                )
                output_voltage_obj_2 = FormulaVariable(
                    Type="#/Inspections/default/Parameters/OutputVoltage",
                    Condition={
                        "OutputNumber": "2",
                        "ValueLabel": "Nominal",
                    },
                    GetValue="ExactValue",
                )
                output_current_obj_1 = FormulaVariable(
                    Type="#/Inspections/default/Parameters/OutputCurrent",
                    Condition={
                        "OutputNumber": "1",
                        "ValueLabel": "Nominal",
                    },
                    GetValue="ExactValue",
                )
                output_current_obj_2 = FormulaVariable(
                    Type="#/Inspections/default/Parameters/OutputCurrent",
                    Condition={
                        "OutputNumber": "2",
                        "ValueLabel": "Nominal",
                    },
                    GetValue="ExactValue",
                )
                formula = LocalFormula(
                    Expression="output_voltage_1/output_current_1+output_voltage_2/output_current_2",
                    Variables={
                        "output_voltage_1": output_voltage_obj_1,
                        "output_voltage_2": output_voltage_obj_2,
                        "output_current_1": output_current_obj_1,
                        "output_current_2": output_current_obj_2,
                    }
                )
                GS_ResistiveLoad.append(
                    LoadInstance(
                        AbstractPair=simplified_test_abstract_pair,
                        ExactValue={
                            "Formula": formula,
                            "Unit": "CALCULATE_RESULT",
                            "SignalType": None
                        }
                    )
                )
        # 測試用電容負載
        GS_CapacitiveLoad = []
        if record.get('測試用電容負載[1]'):
            GS_CapacitiveLoad.append(
                LoadInstance(
                    AbstractPair=['+vout', '-vout'],
                    ExactValue={
                        "Value": Decimal(record.get('測試用電容負載[1]')),
                        "Unit": "microfarad",
                        "SignalType": None
                    }
                )
            )
        if record.get('測試用電容負載[2]'):
            GS_CapacitiveLoad.append(
                LoadInstance(
                    AbstractPair=['+vout', 'common'],
                    ExactValue={
                        "Value": Decimal(record.get('測試用電容負載[2]')),
                        "Unit": "microfarad",
                        "SignalType": None
                    }
                )
            )
        if record.get('測試用電容負載[3]'):
            GS_CapacitiveLoad.append(
                LoadInstance(
                    AbstractPair=['common', '-vout'],
                    ExactValue={
                        "Value": Decimal(record.get('測試用電容負載[3]')),
                        "Unit": "microfarad",
                        "SignalType": None
                    }
                )
            )
        # 啟動臨界電壓
        GS_StartupThresholdVoltage = []
        if record.get('開機點最高值'):
            GS_StartupThresholdVoltage = [
                Instance(
                    ExactValue={
                        "Value": Decimal(record.get('開機點最高值')),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
                )
            ]
        # 欠壓關機電壓
        GS_UndervoltageShutdownVoltage = []
        if record.get('關機點最高值'):
            GS_UndervoltageShutdownVoltage = [
                Instance(
                    ExactValue={
                        "Value": Decimal(record.get('關機點最高值')),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
                )
            ]
        # 絕緣電壓的實例
        IsolationVoltage = []
        # 絕緣電壓-輸入/輸出
        if record.get('輸入對輸5'):
            duration = None
            value_unit = None
            signal_type = None

            if record.get('輸入對輸出絕緣電壓測試值') == 'VDC':
                value_unit = 'volt'
                signal_type = 'DC'
            elif record.get('輸入對輸出絕緣電壓測試值') == 'VAC':
                value_unit = 'volt'
                signal_type = 'AC'
            else:
                value_unit = None # 缺值，無預設值
                signal_type = None # 缺值，無預設值
                raise ValueError(f'"{record.get("主型號")}"."絕緣電壓(輸入/輸出)"單位缺值或不合規定。實際值: "{record.get('輸入對輸出絕緣電壓測試值')}"，可接受值: "VDC" or "VAC"')

            if record.get('成品測試秒數'):
                duration = re.search(r'\d+\.?\d*', record.get('成品測試秒數', ''))[0]
            else:
                duration = 1 # 缺值，填入預設值
                raise ValueError(f'"{record.get("主型號")}"."絕緣電壓(輸入/輸出)"測試時長欄位缺值。實際值: "{record.get('成品測試秒數')}"，可接受值: 包含數字的字串')

            IsolationVoltage.append(
                Instance(
                    Duration={
                        "Value": float(duration),
                        "Unit": "second",
                    },
                    ComponentsGroup1="AllInputPins",
                    ComponentsGroup2="AllOutputPins",
                    ExactValue={
                        "Value": record.get('輸入對輸5'),
                        "Unit": value_unit,
                        "SignalType": signal_type
                    }
                )
            )
        # 絕緣電壓-輸入/Case
        if record.get('輸入對CASE'):
            duration = None
            value_unit = None
            signal_type = None

            if record.get('輸入對CASE絕緣電壓測試值') == 'VDC':
                value_unit = 'volt'
                signal_type = 'DC'
            elif record.get('輸入對CASE絕緣電壓測試值') == 'VAC':
                value_unit = 'volt'
                signal_type = 'AC'
            else:
                value_unit = None # 缺值，無預設值
                signal_type = None # 缺值，無預設值
                raise ValueError(f'"{record.get("主型號")}"."絕緣電壓(輸入/Case)"單位缺值或不合規定。實際值: "{record.get('輸入對輸出絕緣電壓測試值')}"，可接受值: "VDC" or "VAC"')

            if record.get('輸入對CASE測試秒數'):
                duration = re.search(r'\d+\.?\d*', record.get('輸入對CASE測試秒數', ''))[0]
            else:
                # duration = 1 # 缺值，填入預設值
                raise ValueError(f'"{record.get("主型號")}"."絕緣電壓(輸入/Case)"測試時長欄位缺值。實際值: "{record.get('輸入對CASE測試秒數')}"，可接受值: 包含數字的字串')

            IsolationVoltage.append(
                Instance(
                    Duration={
                        "Value": float(duration),
                        "Unit": "second",
                    },
                    ComponentsGroup1="AllInputPins",
                    ComponentsGroup2="Case",
                    ExactValue={
                        "Value": record.get('輸入對CASE'),
                        "Unit": value_unit,
                        "SignalType": signal_type
                    }
                )
            )
        # 絕緣電壓-輸出/Case
        if record.get('輸出對CASE'):
            duration = None
            value_unit = None
            signal_type = None

            if record.get('輸出對CASE絕緣電壓測試值') == 'VDC':
                value_unit = 'volt'
                signal_type = 'DC'
            elif record.get('輸出對CASE絕緣電壓測試值') == 'VAC':
                value_unit = 'volt'
                signal_type = 'AC'
            else:
                value_unit = None # 缺值，無預設值
                signal_type = None # 缺值，無預設值
                raise ValueError(f'"{record.get("主型號")}"."絕緣電壓(輸出/Case)"單位缺值或不合規定。實際值: "{record.get('輸入對輸出絕緣電壓測試值')}"，可接受值: "VDC" or "VAC"')

            if record.get('輸出對CASE測試秒數'):
                duration = re.search(r'\d+\.?\d*', record.get('輸出對CASE測試秒數', ''))[0]
            else:
                duration = 1 # 缺值，填入預設值
                raise ValueError(f'"{record.get("主型號")}"."絕緣電壓(輸出/Case)"測試時長欄位缺值。實際值: "{record.get('輸出對CASE測試秒數')}"，可接受值: 包含數字的字串')

            IsolationVoltage.append(
                Instance(
                    Duration={
                        "Value": float(duration),
                        "Unit": "second",
                    },
                    ComponentsGroup1="AllOutputPins",
                    ComponentsGroup2="Case",
                    ExactValue={
                        "Value": record.get('輸出對CASE'),
                        "Unit": value_unit,
                        "SignalType": signal_type
                    }
                )
            )
        # 絕緣電阻
        IsolationResistance = []
        if record.get('輸入對輸2'):
            unit = None
            if record.get('輸入對輸出絕緣電阻(MIN)') == 'GΩ' or record.get('輸入對輸出絕緣電阻(MIN)') == 'G[':
                unit = 'gigaohm'
            elif record.get('輸入對輸出絕緣電阻(MIN)') == 'MΩ' or record.get('輸入對輸出絕緣電阻(MIN)') == 'M[':
                unit = 'megaohm'
            else:
                unit = None # 缺值，無預設值
                raise ValueError(f'"{record.get("主型號")}"."絕緣電阻"單位缺值或不合規定。實際值: "{record.get('輸入對輸出絕緣電阻(MIN)')}"，可接受值: "GΩ" or "MΩ"')
                
            IsolationResistance = [
                Instance(
                    ComponentsGroup1="AllInputPins",
                    ComponentsGroup2="AllOutputPins",
                    ExactValue={
                        "Value": record.get('輸入對輸2'),
                        "Unit": unit,
                        "SignalType": None
                    }
                )
            ]
        # 絕緣電容
        IsolationCapacitance = []
        if record.get('輸入對輸4'):
            IsolationCapacitance = [
                Instance(
                    ComponentsGroup1="AllInputPins",
                    ComponentsGroup2="AllOutputPins",
                    ExactValue={
                        "Value": record.get('輸入對輸4'),
                        "Unit": "picofarad",
                        "SignalType": None
                    }
                )
            ]
        # 輸出電壓調整電阻值
        OutputVoltageTrimResistance = []
        if record.get('輸出調整電壓電阻值'):
            unit = None
            if record.get('輸出調整電壓電阻值(單位)'):
                if 'k' in record.get('輸出調整電壓電阻值(單位)'):
                    unit = 'kiloohm'
                elif 'K' in record.get('輸出調整電壓電阻值(單位)'):
                    unit = 'kiloohm'
                elif 'M' in record.get('輸出調整電壓電阻值(單位)'):
                    unit = 'megaohm'
                elif 'm' in record.get('輸出調整電壓電阻值(單位)'):
                    unit = 'milliohm'
                else:
                    unit = 'ohm' # 預設值
            else:
                unit = 'ohm' # 預設值
            OutputVoltageTrimResistance = [
                Instance(
                    ExactValue={
                        "Value": Decimal(record.get('輸出調整電壓電阻值')),
                        "Unit": unit,
                        "SignalType": None
                    }
                )
            ]
        # 交換頻率
        SwitchingFrequency = []
        if record.get('交換頻率最'):
            SwitchingFrequency.append(
                Instance(
                    ValueLabel=['Minimum'],
                    ExactValue={
                        "Value": record.get('交換頻率最'),
                        "Unit": "hertz",
                        "SignalType": None
                    }
                )
            )
        if record.get('交換頻率2'):
            SwitchingFrequency.append(
                Instance(
                    ValueLabel=['Maximum'],
                    ExactValue={
                        "Value": record.get('交換頻率2'),
                        "Unit": "hertz",
                        "SignalType": None
                    }
                )
            )

        # [InspectionAttributes]
        # 輸入電流的實例
        QT_InputCurrent = []
        # 輸入電流-(@遠端控制狀態=工作 AND @輸入電壓=中間值 AND @輸出電流=滿載)
        if record.get('效率最低值') and record.get('輸入電壓中') and GS_OutputPower:
            efficiency_mini = Decimal(record.get('效率最低值'))
            input_voltage = Decimal(record.get('輸入電壓中'))
            output_power = Decimal(GS_OutputPower[0].ExactValue.Value)
            output_power_obj = FormulaVariable(
                Type="#/Inspections/default/Parameters/OutputPower",
                Condition={ "ValueLabel": "NominalOutputPower" },
                GetValue="ExactValue",
            )
            efficiency_mini_obj = FormulaVariable(
                Type="#/Inspections/default/Attributes/Efficiency",
                Condition={
                    "InputVoltage": "NominalLine",
                    "OutputCurrent": "MaximumLoad",
                },
                GetValue="Lower",
            )
            input_voltage_obj = FormulaVariable(
                Type="#/Inspections/default/Parameters/InputVoltage",
                Condition={ "ValueLabel": "NominalLine" },
                GetValue="ExactValue",
            )
            formula = LocalFormula(
                Expression = "output_power/efficiency_mini/input_voltage",
                Variables = {
                    "output_power": output_power_obj,
                    "efficiency_mini": efficiency_mini_obj,
                    "input_voltage": input_voltage_obj,
                }
            )
            QT_InputCurrent.append(
                Instance(
                    RemoteControlMode="working",
                    InputVoltage="NominalLine",
                    OutputCurrent="MaximumLoad",
                    Range={
                        "Lower": None,
                        "Upper": {
                            # "Value": (100000 * output_power / efficiency_mini / input_voltage).quantize(Decimal('0.1'), ROUND_HALF_UP),
                            "Formula": formula,
                            "Unit": "CALCULATE_RESULT",
                            "SignalType": None
                        }
                    }
                )
            )
        # 輸入電流-(@遠端控制狀態=工作 AND @輸入電壓=指定值 AND @輸出電流=指定值)
        if record.get('負載電流最大值-規格') and record.get('負載電流最大值') and record.get('輸入電流@'):
            input_voltage_label = input_voltage_map.get(Decimal(record.get('輸入電流@')))
            output_current_label = output_current_map.get(1000 * Decimal(record.get('負載電流最大值-規格')))
            if input_voltage_label and output_current_label:
                QT_InputCurrent.append(
                    Instance(
                        RemoteControlMode="working",
                        InputVoltage=input_voltage_label,
                        OutputCurrent=output_current_label,
                        Range={
                            "Lower": None,
                            "Upper": {
                                "Value": Decimal(record.get('負載電流最大值')),
                                "Unit": "milliampere",
                                "SignalType": None
                            }
                        }
                    )
                )
            else:
                input_voltage_value_label = ""
                output_current_value_label = ""
                if record.get('輸入電流@') and not input_voltage_label:
                    all_value_labels = [label for instance in GS_InputVoltage for label in instance.ValueLabel]
                    counter = 0
                    while counter < 100:
                        counter += 1
                        if f"InputVoltageSpecialCase_{counter}" not in all_value_labels:
                            input_voltage_value_label = f"InputVoltageSpecialCase_{counter}"
                            break
                if record.get('負載電流最大值-規格') and not output_current_label and OutputQuantity == 1:
                    all_value_labels = [label for instance in GS_OutputCurrent for label in instance.ValueLabel if instance.OutputNumber=="1"]
                    counter = 0
                    while counter < 100:
                        counter += 1
                        if f"OutputCurrentSpecialCase_{counter}" not in all_value_labels:
                            output_current_value_label = f"OutputCurrentSpecialCase_{counter}"
                            break
                # print(f'"{record.get("主型號")}"."電器測試規格"."輸入"."輸入電流"(self-defined load / Vin)數據在遷移時被遺棄: InputVoltage={record.get('輸入電流@')}, OutputCurrent={record.get('負載電流最大值-規格')}')
                if (input_voltage_label or input_voltage_value_label) and (output_current_label or output_current_value_label):
                    if input_voltage_value_label:
                        GS_InputVoltage.append(
                            Instance(
                                ValueLabel=[input_voltage_value_label],
                                ExactValue={
                                    "Value": Decimal(record.get('輸入電流@')),
                                    "Unit": "volt",
                                    "SignalType": "DC"
                                }
                            )
                        )
                        input_voltage_map[Decimal(record.get('輸入電流@'))] = input_voltage_value_label
                    if output_current_value_label:
                        GS_OutputCurrent.append(
                            Instance(
                                OutputNumber="1",
                                ValueLabel=[output_current_value_label],
                                ExactValue={
                                    "Value": Decimal(record.get('負載電流最大值-規格')),
                                    "Unit": "ampere",
                                    "SignalType": None
                                }
                            )
                        )
                        output_current_map[1000 * Decimal(record.get('負載電流最大值-規格'))] = output_current_value_label
                    QT_InputCurrent.append(
                        Instance(
                            RemoteControlMode="working",
                            InputVoltage=input_voltage_label or input_voltage_value_label,
                            OutputCurrent=output_current_label or output_current_value_label,
                            Range={
                                "Lower": None,
                                "Upper": {
                                    "Value": Decimal(record.get('負載電流最大值')),
                                    "Unit": "milliampere",
                                    "SignalType": None
                                }
                            }
                        )
                    )
                else:
                    print(f'"{record.get("主型號")}"."電器測試規格"."輸入"."輸入電流"(self-defined load / Vin)數據在遷移時被遺棄: InputVoltage={record.get('輸入電流@')}, OutputCurrent={record.get('負載電流最大值-規格')}')
        # 輸入電流-(@遠端控制狀態=工作 AND @輸入電壓=中間值 AND @輸出電流=空載)
        if record.get('空載輸入2'):
            QT_InputCurrent.append(
                Instance(
                    RemoteControlMode="working",
                    InputVoltage="NominalLine",
                    OutputCurrent="NoLoad",
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": Decimal(record.get('空載輸入2')),
                            "Unit": "milliampere",
                            "SignalType": None
                        }
                    }
                )
            )
        # 輸入電流-(@遠端控制狀態=待機 AND @輸入電壓=中間值 AND @輸出電流=空載)
        if record.get('待機輸入2'):
            # 取得待機輸入電流最大值的單位
            unit1 = utils.ureg.parse_expression(record.get('待機輸入電流最大值')).units
            
            # 解析待機輸入2，取得數值和單位
            expression = utils.ureg.Quantity(record.get('待機輸入2'))
            value = Decimal(expression.magnitude)  # 取得數值
            unit2 = expression.units  # 取得單位

            # 判斷單位是否匹配或只有一個單位存在
            if (unit1 == unit2 != utils.ureg.dimensionless) or ((unit1 == utils.ureg.dimensionless) ^ (unit2 == utils.ureg.dimensionless)):
                unit = str(unit1) if unit1 != utils.ureg.dimensionless else str(unit2)
            elif unit1 == unit2 == utils.ureg.dimensionless:
                unit = str(utils.ureg.parse_expression('mA').units)
            else:
                raise ValueError(f"'{record.get('主型號')}'輸入電流-(@遠端控制狀態=待機 AND @輸入電壓=中間值 AND @輸出電流=空載) 的單位重複定義且不相同: unit1={unit1}, unit2={unit2}")

            QT_InputCurrent.append(
                Instance(
                    RemoteControlMode="standby",
                    InputVoltage="NominalLine",
                    OutputCurrent="NoLoad",
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": value,
                            "Unit": unit,
                            "SignalType": "DC"
                        }
                    }
                )
            )
        # 反射輸入漣波電流-(@輸入電壓=中間值 AND @輸出電流=滿載)
        InputReflectedRippleCurrent = []
        if record.get('反射輸入2'):
            InputReflectedRippleCurrent = [
                Instance(
                    InputVoltage="NominalLine",
                    OutputCurrent= "MaximumLoad",
                    Range= {
                        "Lower": None,
                        "Upper": {
                            "Value": Decimal(record.get('反射輸入2')),
                            "Unit": "milliampere",
                            "SignalType": "P-P"
                        }
                    }
                )
            ]
        # 輸出電壓的實例
        QT_OutputVoltage = []
        # 輸出電壓-輸出1-(@輸入電壓=中間值 AND @輸出電流=空載)
        if record.get('空載輸出電壓最大值[1]'):
            QT_OutputVoltage.append(
                Instance(
                    OutputNumber="1",
                    InputVoltage="NominalLine",
                    OutputCurrent="NoLoad",
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": record.get('空載輸出電壓最大值[1]'),
                            "Unit": "volt",
                            "SignalType": "DC"
                        }
                    }
                )
            )
        # 輸出電壓-輸出2-(@輸入電壓=中間值 AND @輸出電流=空載)
        if record.get('空載輸出電壓最大值[2]'):
            QT_OutputVoltage.append(
                Instance(
                    OutputNumber="2",
                    InputVoltage="NominalLine",
                    OutputCurrent="NoLoad",
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": record.get('空載輸出電壓最大值[2]'),
                            "Unit": "volt",
                            "SignalType": "DC"
                        }
                    }
                )
            )
        # 輸出電壓準確度的實例
        OutputVoltageAccuracy = []
        # 輸出電壓準確度-特殊加測條件
        if record.get('標註2'):
            """本處定義了輸出電壓準確度特殊加測條件，具體內容寫在備註"""
            if '備註一' in record.get('標註2'):
                record.get('備註一')
            elif '備註二' in record.get('標註2'):
                record.get('備註二')
        # 輸出電壓準確度-輸出1-(@輸入電壓=中間值 AND @輸出電流=滿載)
        if record.get('輸出電壓3'):
            try:
                Lower, Upper = RangeExtractor.extract_range(record.get('輸出電壓3'))
            except Exception as e:
                Lower, Upper = RangeExtractor.extend_to_range(record.get('輸出電壓3'))
                # print(f"[Warning] {record.get('主型號')}[輸出電壓準確度-輸出1]={record.get('輸出電壓3')}，判定為'{Lower}~{Upper}'")
            finally:
                OutputVoltageAccuracy.append(
                    Instance(
                        OutputNumber="1",
                        InputVoltage="NominalLine",
                        OutputCurrent="MaximumLoad",
                        Range={
                            "Lower": {
                                "Value": Lower,
                                "Unit": "percent",
                                "SignalType": None
                            },
                            "Upper": {
                                "Value": Upper,
                                "Unit": "percent",
                                "SignalType": None
                            }
                        }
                    )
                )
        # 輸出電壓準確度-輸出2-(@輸入電壓=中間值 AND @輸出電流=滿載)
        if record.get('輸出電壓5'):
            try:
                Lower, Upper = RangeExtractor.extract_range(record.get('輸出電壓5'))
            except Exception as e:
                Lower, Upper = RangeExtractor.extend_to_range(record.get('輸出電壓5'))
                # print(f"[Warning] {record.get('主型號')}[輸出電壓準確度-輸出2]={record.get('輸出電壓5')}，判定為'{Lower}~{Upper}'")
            finally:
                OutputVoltageAccuracy.append(
                    Instance(
                        OutputNumber="2",
                        InputVoltage="NominalLine",
                        OutputCurrent="MaximumLoad",
                        Range={
                            "Lower": {
                                "Value": Lower,
                                "Unit": "percent",
                                "SignalType": None
                            },
                            "Upper": {
                                "Value": Upper,
                                "Unit": "percent",
                                "SignalType": None
                            }
                        }
                    )
                )
        # 輸出電壓平衡率的實例
        OutputVoltageBalance = []
        # 輸出電壓平衡率-(@輸入電壓=中間值 AND @輸出電流=滿載)
        if record.get('輸出電壓2'):
            try:
                Lower, Upper = RangeExtractor.extract_range(record.get('輸出電壓2'))
            except Exception as e:
                Lower, Upper = RangeExtractor.extend_to_range(record.get('輸出電壓2'))
                # print(f"[Warning] {record.get('主型號')}[輸出電壓平衡率]={record.get('輸出電壓2')}，判定為'{Lower}~{Upper}'")
            finally:
                OutputVoltageBalance.append(
                    Instance(
                        InputVoltage="NominalLine",
                        OutputCurrent="MaximumLoad",
                        Range={
                            "Lower": {
                                "Value": Lower,
                                "Unit": "percent",
                                "SignalType": None
                            },
                            "Upper": {
                                "Value": Upper,
                                "Unit": "percent",
                                "SignalType": None
                            }
                        }
                    )
                )
        # 負載調整率的實例
        LoadRegulation = []
        # 負載調整率-輸出1-(@輸入電壓=中間值 AND @輸出電流=滿載)
        if record.get('負載調整率'):
            try:
                Lower, Upper = RangeExtractor.extract_range(record.get('負載調整率'))
            except Exception as e:
                Lower, Upper = RangeExtractor.extend_to_range(record.get('負載調整率'))
                # print(f"[Warning] {record.get('主型號')}[負載調整率-輸出1]={record.get('負載調整率')}，判定為'{Lower}~{Upper}'")
            finally:
                LoadRegulation.append(
                    Instance(
                        OutputNumber="1",
                        InputVoltage="NominalLine",
                        OutputCurrent="MaximumLoad",
                        Range={
                            "Lower": {
                                "Value": Lower,
                                "Unit": "percent",
                                "SignalType": None
                            },
                            "Upper": {
                                "Value": Upper,
                                "Unit": "percent",
                                "SignalType": None
                            }
                        }
                    )
                )
        # 負載調整率-輸出2-(@輸入電壓=中間值 AND @輸出電流=滿載)
        if record.get('負載調整4'):
            try:
                Lower, Upper = RangeExtractor.extract_range(record.get('負載調整4'))
            except Exception as e:
                Lower, Upper = RangeExtractor.extend_to_range(record.get('負載調整4'))
                # print(f"[Warning] {record.get('主型號')}[負載調整率-輸出2]={record.get('負載調整4')}，判定為'{Lower}~{Upper}'")
            finally:
                LoadRegulation.append(
                    Instance(
                        OutputNumber="2",
                        InputVoltage="NominalLine",
                        OutputCurrent="MaximumLoad",
                        Range={
                            "Lower": {
                                "Value": Lower,
                                "Unit": "percent",
                                "SignalType": None
                            },
                            "Upper": {
                                "Value": Upper,
                                "Unit": "percent",
                                "SignalType": None
                            }
                        }
                    )
                )
        # 線調整率的實例
        LineRegulation = []
        # 線調整率-輸出1-(@輸入電壓=中間值 AND @輸出電流=滿載)
        if record.get('線調整率最'):
            try:
                Lower, Upper = RangeExtractor.extract_range(record.get('線調整率最'))
            except Exception as e:
                Lower, Upper = RangeExtractor.extend_to_range(record.get('線調整率最'))
                # print(f"[Warning] {record.get('主型號')}[線調整率-輸出1]={record.get('線調整率最')}，判定為'{Lower}~{Upper}'")
            finally:
                LineRegulation.append(
                    Instance(
                        OutputNumber="1",
                        InputVoltage="NominalLine",
                        OutputCurrent="MaximumLoad",
                        Range={
                            "Lower": {
                                "Value": Lower,
                                "Unit": "percent",
                                "SignalType": None
                            },
                            "Upper": {
                                "Value": Upper,
                                "Unit": "percent",
                                "SignalType": None
                            }
                        }
                    )
                )
        # 線調整率-輸出2-(@輸入電壓=中間值 AND @輸出電流=滿載)
        if record.get('線調整率3'):
            try:
                Lower, Upper = RangeExtractor.extract_range(record.get('線調整率3'))
            except Exception as e:
                Lower, Upper = RangeExtractor.extend_to_range(record.get('線調整率3'))
                # print(f"[Warning] {record.get('主型號')}[線調整率-輸出2]={record.get('線調整率3')}，判定為'{Lower}~{Upper}'")
            finally:
                LineRegulation.append(
                    Instance(
                        OutputNumber="2",
                        InputVoltage="NominalLine",
                        OutputCurrent="MaximumLoad",
                        Range={
                            "Lower": {
                                "Value": Lower,
                                "Unit": "percent",
                                "SignalType": None
                            },
                            "Upper": {
                                "Value": Upper,
                                "Unit": "percent",
                                "SignalType": None
                            }
                        }
                    )
                )
        # 漣波及雜訊的實例
        RippleAndNoise = []
        # 漣波及雜訊-附註
        if record.get('附註'):
            pass
        # 漣波及雜訊峰峰最大值-輸出1-(@輸入電壓=中間值 AND @輸出電流=滿載)
        if record.get('漣波及雜2'):
            RippleAndNoise.append(
                Instance(
                    OutputNumber="1",
                    InputVoltage="NominalLine",
                    OutputCurrent="MaximumLoad",
                    ValueLabel=["PeakToPeakMaximum"],
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": record.get('漣波及雜2'),
                            "Unit": "millivolt",
                            "SignalType": "P-P"
                        }
                    }
                )
            )
        # 漣波及雜訊峰峰最大值-輸出2-(@輸入電壓=中間值 AND @輸出電流=滿載)
        if record.get('漣波及雜6'):
            RippleAndNoise.append(
                Instance(
                    OutputNumber="2",
                    InputVoltage="NominalLine",
                    OutputCurrent="MaximumLoad",
                    ValueLabel=["PeakToPeakMaximum"],
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": record.get('漣波及雜6'),
                            "Unit": "millivolt",
                            "SignalType": "P-P"
                        }
                    }
                )
            )
        # 漣波及雜訊峰峰極限值-輸出1-(@輸入電壓=中間值 AND @輸出電流=滿載)
        if record.get('漣波及雜3'):
            RippleAndNoise.append(
                Instance(
                    OutputNumber="1",
                    InputVoltage="NominalLine",
                    OutputCurrent="MaximumLoad",
                    ValueLabel=["PeakToPeakExtreme"],
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": record.get('漣波及雜3'),
                            "Unit": "millivolt",
                            "SignalType": "P-P"
                        }
                    }
                )
            )
        # 漣波及雜訊峰峰極限值-輸出2-(@輸入電壓=中間值 AND @輸出電流=滿載)
        if record.get('漣波及雜7'):
            RippleAndNoise.append(
                Instance(
                    OutputNumber="2",
                    InputVoltage="NominalLine",
                    OutputCurrent="MaximumLoad",
                    ValueLabel=["PeakToPeakExtreme"],
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": record.get('漣波及雜7'),
                            "Unit": "millivolt",
                            "SignalType": "P-P"
                        }
                    }
                )
            )
        # 漣波及雜訊方均根最大值-輸出1-(@輸入電壓=中間值 AND @輸出電流=滿載)
        if record.get('漣波及雜4'):
            RippleAndNoise.append(
                Instance(
                    OutputNumber="1",
                    InputVoltage="NominalLine",
                    OutputCurrent="MaximumLoad",
                    ValueLabel=["QuadraticMeanMaximum"],
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": record.get('漣波及雜4'),
                            "Unit": "millivolt",
                            "SignalType": "rms"
                        }
                    }
                )
            )
        # 漣波及雜訊方均根最大值-輸出2-(@輸入電壓=中間值 AND @輸出電流=滿載)
        if record.get('漣波及雜8'):
            RippleAndNoise.append(
                Instance(
                    OutputNumber="2",
                    InputVoltage="NominalLine",
                    OutputCurrent="MaximumLoad",
                    ValueLabel=["QuadraticMeanMaximum"],
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": record.get('漣波及雜8'),
                            "Unit": "millivolt",
                            "SignalType": "rms"
                        }
                    }
                )
            )
        # 暫態變動測試條件說明
        TransientLoadChange=record.get('暫態輸出電')
        # 暫態回復時間
        TransientRecoveryTime = []
        if record.get('暫態回復時'):
            TransientRecoveryTime = [
                Instance(
                    LoadChange=TransientLoadChange,
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": record.get('暫態回復時'),
                            "Unit": "microsecond",
                            "SignalType": None
                        }
                    }
                )
            ]
        # 暫態變動率
        TransientResponseDeviation = []
        if record.get('暫態變動2'):
            try:
                Lower, Upper = RangeExtractor.extract_range(record.get('暫態變動2'))
            except Exception as e:
                Lower, Upper = RangeExtractor.extend_to_range(record.get('暫態變動2'))
                # print(f"[Warning] {record.get('主型號')}[暫態變動率]={record.get('暫態變動2')}，判定為'{Lower}~{Upper}'")
            finally:
                TransientResponseDeviation = [
                    Instance(
                        LoadChange=TransientLoadChange,
                        Range={
                            "Lower": {
                                "Value": Lower,
                                "Unit": "percent",
                                "SignalType": None
                            },
                            "Upper": {
                                "Value": Upper,
                                "Unit": "percent",
                                "SignalType": None
                            }
                        }
                    )
                ]
        # 啟動過衝率的實例
        Overshoot = []
        # 啟動過衝率-輸出1
        if record.get('OVERSHOOT'):
            Overshoot.append(
                Instance(
                    OutputNumber="1",
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": record.get('OVERSHOOT'),
                            "Unit": "percent",
                            "SignalType": None
                        }
                    }
                )
            )
        # 啟動過衝率-輸出2
        if record.get('OVERSHOOT'):
            Overshoot.append(
                Instance(
                    OutputNumber="2",
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": record.get('OVERSHOOT'),
                            "Unit": "percent",
                            "SignalType": None
                        }
                    }
                )
            )
        # 效率-(@輸入電壓=中間值 AND @輸出電流=滿載)
        Efficiency = []
        if record.get('效率最低值'):
            Efficiency = [
                Instance(
                    InputVoltage="NominalLine",
                    OutputCurrent="MaximumLoad",
                    Range={
                        "Lower": {
                            "Value": record.get('效率最低值'),
                            "Unit": "percent",
                            "SignalType": None
                        },
                        "Upper": None
                    }
                )
            ]
        # 短路操作頻率
        ShortCircuitProtectionFrequency = []
        if record.get('短路操作頻率最大值'):
            ShortCircuitProtectionFrequency = [
                Instance(
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": record.get('短路操作頻率最大值'),
                            "Unit": "hertz",
                            "SignalType": None
                        }
                    }
                )
            ]
        # 短路輸入功率
        ShortCircuitProtectionInputPower = []
        if record.get('短路輸入功'):
            ShortCircuitProtectionInputPower = [
                Instance(
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": Decimal(record.get('短路輸入功')),
                            "Unit": "milliwatt",
                            "SignalType": None
                        }
                    }
                )
            ]
        # 短路輸入電流
        ShortCircuitProtectionInputCurrent = []
        if record.get('短路輸入功') and record.get('輸入電壓中') and record.get('@Vin'):
            # sc_input_current = Decimal(Decimal(record.get('短路輸入功')) / Decimal(record.get('輸入電壓中'))).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            input_voltage = input_voltage_map.get(Decimal(record.get('@Vin')))
            short_circuit_input_power_obj = FormulaVariable(
                Type="#/Inspections/default/Attributes/ShortCircuitProtectionInputPower",
                Condition={},
                GetValue="Upper",
            )
            input_voltage_obj = FormulaVariable(
                Type="#/Inspections/default/Parameters/InputVoltage",
                Condition={ "ValueLabel": "NominalLine" },
                GetValue="ExactValue",
            )
            formula = LocalFormula(
                Expression = "short_circuit_input_power/input_voltage",
                Variables = {
                    "short_circuit_input_power": short_circuit_input_power_obj,
                    "input_voltage": input_voltage_obj,
                }
            )
            ShortCircuitProtectionInputCurrent = [
                Instance(
                    InputVoltage=input_voltage,
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Formula": formula,
                            "Unit": "CALCULATE_RESULT",
                            "SignalType": None
                        }
                    }
                )
            ]
        # 過負載電流保護
        OverloadCurrentProtection = []
        if (record.get('過負載電流保護最小值') or record.get('過負載電流保護最大值')) and record.get('過負載電流@Vin'):
            input_voltage = input_voltage_map.get(Decimal(record.get('過負載電流@Vin')))
            Lower = {
                "Value": record.get('過負載電流保護最小值'),
                "Unit": "percent",
                "SignalType": None
            } if record.get('過負載電流保護最小值') else None
            Upper = {
                "Value": record.get('過負載電流保護最大值'),
                "Unit": "percent",
                "SignalType": None
            } if record.get('過負載電流保護最大值') else None
            OverloadCurrentProtection = [
                Instance(
                    InputVoltage=input_voltage,
                    Range={
                        "Lower": Lower,
                        "Upper": Upper
                    }
                )
            ]
        # 遠端控制電壓的實例
        RemoteControlInputVoltage = []
        # 遠端控制電壓-工作狀態
        if (record.get('遠端控制電壓最小值-ON') or record.get('遠端控制電壓最大值-ON')):
            Lower = {
                "Value": Decimal(record.get('遠端控制電壓最小值-ON')),
                "Unit": "volt",
                "SignalType": "DC"
            } if record.get('遠端控制電壓最小值-ON') else None
            Upper = {
                "Value": Decimal(record.get('遠端控制電壓最大值-ON')),
                "Unit": "volt",
                "SignalType": "DC"
            } if record.get('遠端控制電壓最大值-ON') else None
            RemoteControlInputVoltage.append(
                Instance(
                    RemoteControlMode="working",
                    Range={
                        "Lower": Lower,
                        "Upper": Upper
                    }
                )
            )
        # 遠端控制電壓-待機狀態
        if (record.get('遠端控制電壓最小值-OFF') or record.get('遠端控制電壓最大值-OFF')):
            Lower = {
                "Value": Decimal(record.get('遠端控制電壓最小值-OFF')),
                "Unit": "volt",
                "SignalType": "DC"
            } if record.get('遠端控制電壓最小值-OFF') else None
            Upper = {
                "Value": Decimal(record.get('遠端控制電壓最大值-OFF')),
                "Unit": "volt",
                "SignalType": "DC"
            } if record.get('遠端控制電壓最大值-OFF') else None
            RemoteControlInputVoltage.append(
                Instance(
                    RemoteControlMode="standby",
                    Range={
                        "Lower": Lower,
                        "Upper": Upper
                    }
                )
            )
        # 遠端控制電流的實例
        RemoteControlInputCurrent = []
        # 遠端控制電流-工作狀態
        if (record.get('控制輸入電流最小值-ON') or record.get('控制輸入電流最大值-ON')):
            column1_value = None
            column2_value = None
            lower_value = None
            upper_value = None
            column1_unit = None
            column2_unit = None
            lower_unit = None
            upper_unit = None
            if record.get('控制輸入電流最小值-ON'):
                column1_unit1 = utils.ureg.parse_expression(record.get('控制-工作狀態1')).units
                column1_expression = utils.ureg.Quantity(record.get('控制輸入電流最小值-ON'))
                column1_value = Decimal(column1_expression.magnitude)
                column1_unit2 = column1_expression.units
                if (column1_unit1 == column1_unit2 != utils.ureg.dimensionless) or ((column1_unit1 == utils.ureg.dimensionless) ^ (column1_unit2 == utils.ureg.dimensionless)):
                    column1_unit = str(column1_unit1) if column1_unit1 != utils.ureg.dimensionless else str(column1_unit2)
                elif column1_unit1 == column1_unit2 == utils.ureg.dimensionless:
                    raise ValueError(f"'{record.get('主型號')}'遠端控制電流-工作狀態最小值 未定義單位")
                else:
                    raise ValueError(f"'{record.get('主型號')}'遠端控制電流-工作狀態最小值 的單位重複定義且不相同。 unit1={column1_unit1}, unit2={column1_unit2}")
            if record.get('控制輸入電流最大值-ON'):
                column2_unit1 = utils.ureg.parse_expression(record.get('控制-工作狀態2')).units
                column2_expression = utils.ureg.Quantity(record.get('控制輸入電流最大值-ON'))
                column2_value = Decimal(column2_expression.magnitude)
                column2_unit2 = column2_expression.units
                if (column2_unit1 == column2_unit2 != utils.ureg.dimensionless) or ((column2_unit1 == utils.ureg.dimensionless) ^ (column2_unit2 == utils.ureg.dimensionless)):
                    column2_unit = str(column2_unit1) if column2_unit1 != utils.ureg.dimensionless else str(column2_unit2)
                elif column2_unit1 == column2_unit2 == utils.ureg.dimensionless:
                    raise ValueError(f"'{record.get('主型號')}'遠端控制電流-工作狀態最大值 未定義單位")
                else:
                    raise ValueError(f"'{record.get('主型號')}'遠端控制電流-工作狀態最大值 的單位重複定義且不相同。 unit1={column2_unit1}, unit2={column2_unit2}")
            if (column1_value or 0) < (column2_value or 0):
                lower_value = column1_value
                lower_unit = column1_unit
                upper_value = column2_value
                upper_unit = column2_unit
            else:
                lower_value = column2_value
                lower_unit = column2_unit
                upper_value = column1_value
                upper_unit = column1_unit
            Lower = {
                "Value": Decimal(lower_value),
                "Unit": lower_unit,
                "SignalType": None
            } if lower_value else None
            Upper = {
                "Value": Decimal(upper_value),
                "Unit": upper_unit,
                "SignalType": None
            } if upper_value else None
            RemoteControlInputCurrent.append(
                Instance(
                    RemoteControlMode="working",
                    Range={
                        "Lower": Lower,
                        "Upper": Upper
                    }
                )
            )
        # 遠端控制電流-待機狀態
        if (record.get('控制輸入電流最小值-OFF') or record.get('控制輸入電流最大值-OFF')):
            column1_value = None
            column2_value = None
            lower_value = None
            upper_value = None
            column1_unit = None
            column2_unit = None
            lower_unit = None
            upper_unit = None
            if record.get('控制輸入電流最小值-OFF'):
                column1_unit1 = utils.ureg.parse_expression(record.get('控制-待機狀態1')).units
                column1_expression = utils.ureg.Quantity(record.get('控制輸入電流最小值-OFF'))
                column1_value = Decimal(column1_expression.magnitude)
                column1_unit2 = column1_expression.units
                if (column1_unit1 == column1_unit2 != utils.ureg.dimensionless) or ((column1_unit1 == utils.ureg.dimensionless) ^ (column1_unit2 == utils.ureg.dimensionless)):
                    column1_unit = str(column1_unit1) if column1_unit1 != utils.ureg.dimensionless else str(column1_unit2)
                elif column1_unit1 == column1_unit2 == utils.ureg.dimensionless:
                    raise ValueError(f"'{record.get('主型號')}'遠端控制電流-待機狀態最小值 未定義單位")
                else:
                    raise ValueError(f"'{record.get('主型號')}'遠端控制電流-待機狀態最小值 的單位重複定義且不相同。 unit1={column1_unit1}, unit2={column1_unit2}")
            if record.get('控制輸入電流最大值-OFF'):
                column2_unit1 = utils.ureg.parse_expression(record.get('控制-待機狀態2')).units
                column2_expression = utils.ureg.Quantity(record.get('控制輸入電流最大值-OFF'))
                column2_value = Decimal(column2_expression.magnitude)
                column2_unit2 = column2_expression.units
                if (column2_unit1 == column2_unit2 != utils.ureg.dimensionless) or ((column2_unit1 == utils.ureg.dimensionless) ^ (column2_unit2 == utils.ureg.dimensionless)):
                    column2_unit = str(column2_unit1) if column2_unit1 != utils.ureg.dimensionless else str(column2_unit2)
                elif column2_unit1 == column2_unit2 == utils.ureg.dimensionless:
                    raise ValueError(f"'{record.get('主型號')}'遠端控制電流-待機狀態最大值 未定義單位")
                else:
                    raise ValueError(f"'{record.get('主型號')}'遠端控制電流-待機狀態最大值 的單位重複定義且不相同。 unit1={column2_unit1}, unit2={column2_unit2}")
            if (column1_value or 0) < (column2_value or 0):
                lower_value = column1_value
                lower_unit = column1_unit
                upper_value = column2_value
                upper_unit = column2_unit
            else:
                lower_value = column2_value
                lower_unit = column2_unit
                upper_value = column1_value
                upper_unit = column1_unit
            Lower = {
                "Value": Decimal(lower_value),
                "Unit": lower_unit,
                "SignalType": None
            } if lower_value else None
            Upper = {
                "Value": Decimal(upper_value),
                "Unit": upper_unit,
                "SignalType": None
            } if upper_value else None
            RemoteControlInputCurrent.append(
                Instance(
                    RemoteControlMode="standby",
                    Range={
                        "Lower": Lower,
                        "Upper": Upper
                    }
                )
            )
        # 輸出電壓調整範圍的實例
        OutputVoltageTrimRange = []
        # 輸出電壓調整範圍最大值
        if record.get('輸出調整電壓範圍最大值'):
            try:
                prehandle_str = re.sub(r"[^0-9\.\+\-/{to~]", "", record.get('輸出調整電壓範圍最大值'))
                l, u = RangeExtractor.extract_range(prehandle_str)
                Lower = {
                    "Value": l,
                    "Unit": "volt",
                    "SignalType": "DC"
                }
                Upper = {
                    "Value": u,
                    "Unit": "volt",
                    "SignalType": "DC"
                }
            except Exception as e:
                Lower = None
                if record.get('輸出調整電壓範圍最小值'):
                    Lower = {
                        "Value": Decimal(record.get('輸出調整電壓範圍最小值')),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
                Upper = {
                    "Value": Decimal(record.get('輸出調整電壓範圍最大值')),
                    "Unit": "volt",
                    "SignalType": "DC"
                }
            finally:
                OutputVoltageTrimRange.append(
                    Instance(
                        ValueLabel=["WithTrimResistor"],
                        Range={
                            "Lower": Lower,
                            "Upper": Upper
                        }
                    )
                )
        # 輸出電壓調整範圍最小值
        if record.get('輸出調整電壓範圍最小值'):
            try:
                prehandle_str = re.sub(r"[^0-9\.\+\-/{to~]", "", record.get('輸出調整電壓範圍最小值'))
                l, u = RangeExtractor.extract_range(prehandle_str)
                Lower = {
                    "Value": l,
                    "Unit": "volt",
                    "SignalType": "DC"
                }
                Upper = {
                    "Value": u,
                    "Unit": "volt",
                    "SignalType": "DC"
                }
            except Exception as e:
                Lower = {
                    "Value": Decimal(record.get('輸出調整電壓範圍最小值')),
                    "Unit": "volt",
                    "SignalType": "DC"
                }
                Upper = None
                if record.get('輸出調整電壓範圍最大值'):
                    Upper = {
                        "Value": Decimal(record.get('輸出調整電壓範圍最大值')),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
            finally:
                OutputVoltageTrimRange.append(
                    Instance(
                        ValueLabel=["WithoutTrimResistor"],
                        Range={
                            "Lower": Lower,
                            "Upper": Upper
                        }
                    )
                )


        # 產品元數據、分類信息
        product_categories = Category(
            SeriesNumber=SeriesNumber,
            OutputQuantity=OutputQuantity,
            ConverterType=ConverterType,
            OutputRegulation=OutputRegulation,
            RemoteControlType=RemoteControlType,
            OutputTrim=OutputTrim,
            IoIsolation=IoIsolation,
            InsulationSystemType=InsulationSystemType,
            MountingType=MountingType,
            PackageType=PackageType,
            Applications=Applications
        )

        inspection_parameters = InspectionParameters(
            Component=GS_Component,
            IO=GS_InputOutput,
            AmbientTemperature=GS_AmbientTemperature,
            InputVoltage=GS_InputVoltage,
            OutputVoltage=GS_OutputVoltage,
            OutputCurrent=GS_OutputCurrent,
            OutputPower=GS_OutputPower,
            ResistiveLoad=GS_ResistiveLoad,
            CapacitiveLoad=GS_CapacitiveLoad,
            StartupThresholdVoltage=GS_StartupThresholdVoltage,
            UndervoltageShutdownVoltage=GS_UndervoltageShutdownVoltage,
            IsolationVoltage=IsolationVoltage,
            IsolationResistance=IsolationResistance,
            IsolationCapacitance=IsolationCapacitance,
            OutputVoltageTrimResistance=OutputVoltageTrimResistance,
            SwitchingFrequency=SwitchingFrequency
        )

        inspection_attributes = InspectionAttributes(
            InputCurrent=QT_InputCurrent,
            InputReflectedRippleCurrent=InputReflectedRippleCurrent,
            OutputVoltage=QT_OutputVoltage,
            OutputVoltageAccuracy=OutputVoltageAccuracy,
            OutputVoltageBalance=OutputVoltageBalance,
            LoadRegulation=LoadRegulation,
            LineRegulation=LineRegulation,
            RippleAndNoise=RippleAndNoise,
            TransientRecoveryTime=TransientRecoveryTime,
            TransientResponseDeviation=TransientResponseDeviation,
            Overshoot=Overshoot,
            Efficiency=Efficiency,
            ShortCircuitProtectionFrequency=ShortCircuitProtectionFrequency,
            ShortCircuitProtectionInputPower=ShortCircuitProtectionInputPower,
            ShortCircuitProtectionInputCurrent=ShortCircuitProtectionInputCurrent,
            OverloadCurrentProtection=OverloadCurrentProtection,
            RemoteControlInputVoltage=RemoteControlInputVoltage,
            RemoteControlInputCurrent=RemoteControlInputCurrent,
            OutputVoltageTrimRange=OutputVoltageTrimRange
        )

        inspections = {
            "default": Inspection(
                Parameters=inspection_parameters,
                Attributes=inspection_attributes,
            )
        }

        formulas = {
            
        }

        product = ProductModel(
            ModelNumber=record.get('主型號'),
            Category=product_categories,
            Inspections=inspections,
            Formulas=formulas,
        )

        # Validate the product instance
        try:
            product.validate()
            products.append(product)
        except ValidationError as e:
            print(f"{product.Model} 格式驗證報錯跳過 : {e}")
            continue
    except ValueError as e:
        print(f'遺棄{record.get('主型號')}整筆資料。報錯原因: {e}')
        continue

if products:
    successful_case = 0
    failed_case = 0
    failed_records = []

    for product in products:
        try:
            # 單個插入產品數據，捕捉可能的錯誤
            product.save()
            successful_case += 1  # 成功插入一條數據

        except NotUniqueError as e:
            # 捕捉重複鍵的錯誤，記錄失敗的產品
            # print(f"Duplicate data error for product {product}: {e}")
            failed_case += 1
            failed_records.append(f"Duplicate data issue for product {product}: {e}")

        except ValidationError as e:
            # 捕捉驗證失敗的錯誤，記錄失敗的產品
            # print(f"Validation error for product {product}: {e}")
            failed_case += 1
            failed_records.append(f"Validation issue for product {product}: {e}")

        except Exception as e:
            # 捕捉其他可能的錯誤，記錄失敗的產品
            # print(f"An unknown error occurred for product {product}: {e}")
            failed_case += 1
            failed_records.append(f"Unknown issue for product {product}: {e}")
            print(e)
            input('按任意鍵繼續')

    # 如果有失敗的插入，提示用戶具體錯誤
    # if failed_case > 0:
    #     print(f"{failed_case} model(s) were dropped due to errors.")
    #     for record in failed_records:
    #         print(record)

    # 確保打印成功和失敗的總數
    print(f"Summary: {successful_case} models saved successfully, {len(main_record_rows) - successful_case} models failed ({len(main_record_rows) - successful_case - failed_case} dropped)")
else:
    print("No valid products to save.")
    