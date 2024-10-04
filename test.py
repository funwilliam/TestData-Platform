import re
import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
from server.helpers.utils import RangeExtractor
from server.models.spec import ProductModel, GeneralSpecifications, QualityTestSpecifications, ProductMetaInstance, ComponentInstance, IOInstance, Instance


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
    SELECT mo."型號"
    FROM "型號" mo
    INNER JOIN "產品規格" ps ON mo."型號" = ps."主型號"
)
SELECT 
    am."型號",  -- 只選擇 AvailableModels 的 "型號"
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


for record in main_record_rows:
    # [ProductMeta]
    # 輸出組數
    OutputQuantity = int(record.get('額定輸出1', '0') or 0) + int(record.get('額定輸出3', '0') or 0)
    # 轉換類型
    ConverterType = 'DC->DC'
    # 擁有輸出穩壓功能
    OutputRegulation = None # 因無判斷方法，初始化暫不填值
    # 遠端控制類型
    RemoteOnOffType = None
    if record.get('遠端開 / 關控制 '):
        if record.get('遠端開 / 關控制 ').lower().strip() == 'Enable High'.lower().strip():
            RemoteOnOffType = 'Enable High'
        if record.get('遠端開 / 關控制 ').lower().strip() == 'Enable Low'.lower().strip():
            RemoteOnOffType = 'Enable Low'
    # 擁有輸出微調功能
    OutputTrim = bool(record.get('輸出調整電壓範圍最大值') or record.get('輸出調整電壓範圍最小值'))
    # Iinput/Output隔離電壓等級
    IoIsolation = None # 因無判斷方法，初始化暫不填值
    # 絕緣系統類型
    InsulationSystemType = None # 因無判斷方法，初始化暫不填值
    # 安裝類型
    MountingType = None # 因無判斷方法，初始化暫不填值
    # 封裝類型
    PackageType = None # 因無判斷方法，初始化暫不填值
    # 主要應用領域
    Applications = None # 因無判斷方法，初始化暫不填值

    # [GeneralSpecifications]
    # 零件
    Component = []
    Component.append(
            ComponentInstance(
                ComponentType="Case",
                Number='1',
                Statement=None
            )
        )
    appearance_category = record.get('外觀尺寸編')
    for pin in pin_info_dict.get(appearance_category, []):
        Component.append(
            ComponentInstance(
                ComponentType="Pin",
                Number=pin.get('接腳編號'),
                Statement=pin.get('接腳功能')
            )
        )
    # 輸入/輸出的實例
    IO=[
        IOInstance(
            IOType="input",
            Number="1",
            PinPair=None # 因無判斷方法，初始化暫不填值
        )
    ]
    for i in range(OutputQuantity):
        IO.append(
            IOInstance(
                IOType="output",
                Number=str(i),
                PinPair=None # 因無判斷方法，初始化暫不填值
            )
        )
    # 操作溫度範圍
    OperatingAmbientTemperature=[]
    if record.get('操作溫度範圍'):
        try:
            lower, upper = RangeExtractor.extract_range(record.get('操作溫度範圍'))
            OperatingAmbientTemperature = [
                Instance(
                    ValueLabel=["低溫", "LowerLimit"],
                    ExactValue={
                        "Value": lower,
                        "Unit": "degC",
                        "SignalType": None
                    }
                ),
                Instance(
                    ValueLabel=["常溫", "Normal"],
                    ExactValue={
                        "Value": 25,
                        "Unit": "degC",
                        "SignalType": None
                    }
                ),
                Instance(
                    ValueLabel=["高溫", "UpperLimit"],
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
            break
    # 輸入電壓MAP
    input_voltage_map = {}
    # 輸入電壓的實例
    InputVoltage = []
    # 輸入電壓-最大值
    if record.get('輸入電壓最'):
        input_voltage_map[record.get('輸入電壓最')] = 'HighLine'
        InputVoltage.append(
            Instance(
                ValueLabel=["HighLine"],
                ExactValue={
                    "Value": record.get('輸入電壓最'),
                    "Unit": "volt",
                    "SignalType": "DC"
                }
            )
        )
    # 輸入電壓-中間值
    if record.get('輸入電壓中'):
        input_voltage_map[record.get('輸入電壓中')] = 'NominalLine'
        InputVoltage.append(
            Instance(
                ValueLabel=["NominalLine"],
                ExactValue={
                    "Value": record.get('輸入電壓中'),
                    "Unit": "volt",
                    "SignalType": "DC"
                }
            )
        )
    # 輸入電壓-最小值
    if record.get('輸入電壓2'):
        input_voltage_map[record.get('輸入電壓2')] = 'LowLine'
        InputVoltage.append(
            Instance(
                ValueLabel=["LowLine"],
                ExactValue={
                    "Value": record.get('輸入電壓2'),
                    "Unit": "volt",
                    "SignalType": "DC"
                }
            )
        )
    # 輸出電壓的實例
    OutputVoltage = []
    # 輸出電壓-額定值-輸出1
    if record.get('額定輸出1'):
        OutputVoltage.append(
            Instance(
                OutputNumber="1",
                ValueLabel=["Nominal", "額定值"],
                ExactValue={
                    "Value": record.get('額定輸出1'),
                    "Unit": "volt",
                    "SignalType": "DC"
                }
            )
        )
    # 輸出電壓-額定值-輸出2
    if record.get('額定輸出3'):
        OutputVoltage.append(
            Instance(
                OutputNumber="2",
                ValueLabel=["Nominal", "額定值"],
                ExactValue={
                    "Value": record.get('額定輸出3'),
                    "Unit": "volt",
                    "SignalType": "DC"
                }
            )
        )
    # 輸出電流MAP
    output_current_map = {}
    # 輸出電流的實例
    OutputCurrent = []
    # 輸出電流-滿載-輸出1
    if record.get('額定輸出2'):
        OutputCurrent.append(
            Instance(
                OutputNumber="1",
                ValueLabel=["MaximumLoad", "滿載"],
                ExactValue={
                    "Value": record.get('額定輸出2'),
                    "Unit": "milliampere",
                    "SignalType": "DC"
                }
            )
        )
    # 輸出電流-滿載-輸出2
    if record.get('額定輸出4'):
        OutputCurrent.append(
            Instance(
                OutputNumber="2",
                ValueLabel=["MaximumLoad", "滿載"],
                ExactValue={
                    "Value": record.get('額定輸出4'),
                    "Unit": "milliampere",
                    "SignalType": "DC"
                }
            )
        )
    # 輸出電流-輕載-輸出1
    if record.get('測試用輕載'):
        OutputCurrent.append(
            Instance(
                OutputNumber="1",
                ValueLabel=["MinimumLoad", "輕載"],
                ExactValue={
                    "Value": record.get('測試用輕載'),
                    "Unit": "milliampere",
                    "SignalType": "DC"
                }
            )
        )
    # 輸出電流-輕載-輸出2
    if record.get('測試用輕2'):
        OutputCurrent.append(
            Instance(
                OutputNumber="1",
                ValueLabel=["MinimumLoad", "輕載"],
                ExactValue={
                    "Value": record.get('測試用輕2'),
                    "Unit": "milliampere",
                    "SignalType": "DC"
                }
            )
        )
    # 輸出電流-空載
    for i in range(OutputQuantity):
        OutputCurrent.append(
            Instance(
                OutputNumber=str(i),
                ValueLabel=["NoLoad", "空載"],
                ExactValue={
                    "Value": 0,
                    "Unit": "milliampere",
                    "SignalType": "DC"
                }
            )
        )
    # 輸出電流-滿載值
    if record.get('額定輸出2') or record.get('額定輸出4'):
        total_output_current = abs(record.get('額定輸出2', 0) or 0) + abs(record.get('額定輸出4', 0) or 0)
        output_current_map[total_output_current] = 'MaximumLoad'
    # 輸出電流-輕載值
    if record.get('測試用輕載') or record.get('測試用輕2'):
        output_current = abs(record.get('測試用輕載', 0) or 0) + abs(record.get('測試用輕2', 0) or 0)
        output_current_map[output_current] = 'MinimumLoad'
    # 輸出電流-空載值
    output_current_map[0]='NoLoad'
    # 絕緣電壓的實例
    IsolationVoltage = []
    # 絕緣電壓-輸入/輸出
    if record.get('輸入對輸5'):
        if record.get('成品測試秒數'):
            duration = re.search(r'\d+\.?\d*', record.get('成品測試秒數', ''))
            IsolationVoltage.append(
                Instance(
                    Duration=f"{duration} second",
                    ComponentsGroup1="AllInputPins",
                    ComponentsGroup2="AllOutputPins",
                    ExactValue={
                        "Value": record.get('輸入對輸5'),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
                )
            )
        else:
            IsolationVoltage.append(
                Instance(
                    Duration=f"60 second",
                    ComponentsGroup1="AllInputPins",
                    ComponentsGroup2="AllOutputPins",
                    ExactValue={
                        "Value": record.get('輸入對輸5'),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
                )
            )
    # 絕緣電壓-輸入/Case
    if record.get('輸入對CASE'):
        if record.get('輸入對CASE測試秒數'):
            duration = re.search(r'\d+\.?\d*', record.get('輸入對CASE測試秒數', ''))
            IsolationVoltage.append(
                Instance(
                    Duration=f"{duration} second",
                    ComponentsGroup1="AllInputPins",
                    ComponentsGroup2="Case",
                    ExactValue={
                        "Value": record.get('輸入對CASE'),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
                )
            )
        else:
            IsolationVoltage.append(
                Instance(
                    Duration=f"60 second",
                    ComponentsGroup1="AllInputPins",
                    ComponentsGroup2="Case",
                    ExactValue={
                        "Value": record.get('輸入對CASE'),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
                )
            )
    # 絕緣電壓-輸出/Case
    if record.get('輸出對CASE'):
        if record.get('輸出對CASE測試秒數'):
            duration = re.search(r'\d+\.?\d*', record.get('輸出對CASE測試秒數', ''))
            IsolationVoltage.append(
                Instance(
                    Duration=f"{duration} second",
                    ComponentsGroup1="AllOutputPins",
                    ComponentsGroup2="Case",
                    ExactValue={
                        "Value": record.get('輸出對CASE'),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
                )
            )
        else:
            IsolationVoltage.append(
                Instance(
                    Duration=f"60 second",
                    ComponentsGroup1="AllOutputPins",
                    ComponentsGroup2="Case",
                    ExactValue={
                        "Value": record.get('輸出對CASE'),
                        "Unit": "volt",
                        "SignalType": "DC"
                    }
                )
            )
    # 絕緣電阻
    IsolationResistance = []
    if record.get('輸入對輸2'):
        IsolationResistance = [
            Instance(
                ComponentsGroup1="AllInputPins",
                ComponentsGroup2="AllOutputPins",
                ExactValue={
                    "Value": record.get('輸入對輸2'),
                    "Unit": "gigaohm",
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
        OutputVoltageTrimResistance = [
            Instance(
                ExactValue={
                    "Value": Decimal(record.get('輸出調整電壓電阻值')),
                    "Unit": "ohm",
                    "SignalType": None
                }
            )
        ]


    # [QualityTestSpecifications]
    # 輸入電流的實例
    QT_InputCurrent = []
    # 輸入電流-(@遠端控制狀態=工作 AND @輸入電壓=中間值 AND @輸出電流=滿載)
    if record.get('滿載輸入電流最大值'):
        QT_InputCurrent.append(
            Instance(
                RemoteControlMode="working",
                InputVoltage="NominalLine",
                OutputCurrent="MaximumLoad",
                Range={
                    "Lower": None,
                    "Upper": {
                        "Value": record.get('滿載輸入電流最大值'),
                        "Unit": "milliampere",
                        "SignalType": "DC"
                    }
                }
            )
        )
    # 輸入電流-(@遠端控制狀態=工作 AND @輸入電壓=指定值 AND @輸出電流=指定值)
    if record.get('負載電流最大值-規格') and record.get('負載電流最大值') and record.get('輸入電流@'):
        InputVoltage = input_voltage_map.get(record.get('輸入電流@'))
        OutputCurrent = output_current_map.get(record.get('負載電流最大值-規格'))
        if InputVoltage and OutputCurrent:
            QT_InputCurrent.append(
                Instance(
                    RemoteControlMode="working",
                    InputVoltage=InputVoltage,
                    OutputCurrent=OutputCurrent,
                    Range={
                        "Lower": None,
                        "Upper": {
                            "Value": record.get('負載電流最大值'),
                            "Unit": "milliampere",
                            "SignalType": "DC"
                        }
                    }
                )
            )
        else:
            print(f'拋棄"{record.get("主型號")}"電器測試特規輸入電流規格: InputVoltage={InputVoltage}, OutputCurrent={OutputCurrent}')
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
                        "Value": record.get('空載輸入2'),
                        "Unit": "milliampere",
                        "SignalType": "DC"
                    }
                }
            )
        )
    # 輸入電流-(@遠端控制狀態=待機 AND @輸入電壓=中間值 AND @輸出電流=空載)
    if record.get('待機輸入2'):
        QT_InputCurrent.append(
            Instance(
                RemoteControlMode="standby",
                InputVoltage="NominalLine",
                OutputCurrent="NoLoad",
                Range={
                    "Lower": None,
                    "Upper": {
                        "Value": record.get('待機輸入2'),
                        "Unit": "milliampere",
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
                        "Value": record.get('反射輸入2'),
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
    OutputVoltageSettingAccuracy = []
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
            OutputVoltageSettingAccuracy.append(
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
            OutputVoltageSettingAccuracy.append(
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
                ValueLabel="PeakToPeakMaximum",
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
                ValueLabel="PeakToPeakMaximum",
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
                ValueLabel="PeakToPeakExtreme",
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
                ValueLabel="PeakToPeakExtreme",
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
                ValueLabel="QuadraticMeanMaximum",
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
                ValueLabel="QuadraticMeanMaximum",
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
    # 短路輸入電流
    ShortCircuitProtectionInputCurrent = []
    if record.get('短路輸入電流最大值') and record.get('@Vin'):
        InputVoltage = input_voltage_map.get(record.get('@Vin'))
        ShortCircuitProtectionInputCurrent = [
            Instance(
                InputVoltage=InputVoltage,
                Range={
                    "Lower": None,
                    "Upper": {
                        "Value": record.get('短路輸入電流最大值'),
                        "Unit": "milliampere",
                        "SignalType": None
                    }
                }
            )
        ]
    # 過負載電流保護
    OverloadCurrentProtection = []
    if (record.get('過負載電流保護最小值') or record.get('過負載電流保護最大值')) and record.get('過負載電流@Vin'):
        InputVoltage = input_voltage_map.get(record.get('過負載電流@Vin'))
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
                InputVoltage=InputVoltage,
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
            "Value": record.get('遠端控制電壓最小值-ON'),
            "Unit": "volt",
            "SignalType": "DC"
        } if record.get('遠端控制電壓最小值-ON') else None
        Upper = {
            "Value": record.get('遠端控制電壓最大值-ON'),
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
            "Value": record.get('遠端控制電壓最小值-OFF'),
            "Unit": "volt",
            "SignalType": "DC"
        } if record.get('遠端控制電壓最小值-OFF') else None
        Upper = {
            "Value": record.get('遠端控制電壓最大值-OFF'),
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
        Lower = {
            "Value": record.get('遠端控制電壓最小值-ON'),
            "Unit": "volt",
            "SignalType": "DC"
        } if record.get('遠端控制電壓最小值-ON') else None
        Upper = {
            "Value": record.get('遠端控制電壓最大值-ON'),
            "Unit": "volt",
            "SignalType": "DC"
        } if record.get('遠端控制電壓最大值-ON') else None
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
    if (record.get('遠端控制電壓最小值-OFF') or record.get('遠端控制電壓最大值-OFF')):
        Lower = {
            "Value": record.get('遠端控制電壓最小值-OFF'),
            "Unit": "volt",
            "SignalType": "DC"
        } if record.get('遠端控制電壓最小值-OFF') else None
        Upper = {
            "Value": record.get('遠端控制電壓最大值-OFF'),
            "Unit": "volt",
            "SignalType": "DC"
        } if record.get('遠端控制電壓最大值-OFF') else None
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
                    ValueLabel="MaximumRange",
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
                    ValueLabel="MinimumRange",
                    Range={
                        "Lower": Lower,
                        "Upper": Upper
                    }
                )
            )


    # 產品元數據、分類信息
    product_meta = ProductMetaInstance(
        OutputQuantity=OutputQuantity,
        ConverterType=ConverterType,
        OutputRegulation=OutputRegulation,
        RemoteOnOffType=RemoteOnOffType,
        OutputTrim=OutputTrim,
        IoIsolation=IoIsolation,
        InsulationSystemType=InsulationSystemType,
        MountingType=MountingType,
        PackageType=PackageType,
        Applications=Applications
    )

    general_specifications = GeneralSpecifications(
        ProductMeta=product_meta,
        Component=Component,
        IO=IO,
        OperatingAmbientTemperature=OperatingAmbientTemperature,
        InputVoltage=InputVoltage,
        OutputVoltage=OutputVoltage,
        OutputCurrent=OutputCurrent,
        IsolationVoltage=IsolationVoltage,
        IsolationResistance=IsolationResistance,
        IsolationCapacitance=IsolationCapacitance,
        OutputVoltageTrimResistance=OutputVoltageTrimResistance
    )

    QualityTestSpecifications(
        InputCurrent=QT_InputCurrent,
        InputReflectedRippleCurrent=InputReflectedRippleCurrent,
        OutputVoltage=QT_OutputVoltage,
        OutputVoltageSettingAccuracy=OutputVoltageSettingAccuracy,
        OutputVoltageBalance=OutputVoltageBalance,
        LoadRegulation=LoadRegulation,
        LineRegulation=LineRegulation,
        RippleAndNoise=RippleAndNoise,
        TransientRecoveryTime=TransientRecoveryTime,
        TransientResponseDeviation=TransientResponseDeviation,
        Overshoot=Overshoot,
        Efficiency=Efficiency,
        ShortCircuitProtectionFrequency=ShortCircuitProtectionFrequency,
        ShortCircuitProtectionInputCurrent=ShortCircuitProtectionInputCurrent,
        OverloadCurrentProtection=OverloadCurrentProtection,
        RemoteControlInputVoltage=RemoteControlInputVoltage,
        RemoteControlInputCurrent=RemoteControlInputCurrent,
        OutputVoltageTrimRange=OutputVoltageTrimRange
    )