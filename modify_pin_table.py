import re
import psycopg2
from dbfread import DBF
from decimal import Decimal

def extract_pin_number_str(input_string):
    if not input_string:
        return []
    numbers = re.findall(r'\d+', input_string)
    return numbers

def extract_diameter_str(input_string):
    if not input_string:
        return None, None
    pattern = r'([0-9.]+)\s*\[([0-9.]+)\]'
    match = re.match(pattern, input_string)
    if match:
        main_value = match.group(1)
        bracket_value = match.group(2)
        return main_value, bracket_value
    else:
        return None, None

# 解析 .dbf 文件
file_path = '接腳說明.dbf'
table = DBF(file_path, encoding='cp950')

# 構建修改後的記錄列表
modified_records = []
for record in table:
    if record.get('外觀尺力磅') and record.get('接腳磅號'):
        diameter_str = record.get('DIAMETER__')
        diameter_mm, _ = extract_diameter_str(diameter_str)

        pin_number_str = record.get('接腳磅號')
        for pin_number in extract_pin_number_str(pin_number_str):
            modified_record = {
                '外觀尺寸編號': record.get('外觀尺力磅'),
                '接腳編號': pin_number,
                '接腳功能': record.get('接腳功能'),
                '直徑(mm)': Decimal(diameter_mm) if diameter_mm else None
            }
            modified_records.append(modified_record)

# 連接 PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="pg-productspec-db",
    user="postgres",
    password="password"
)
cursor = conn.cursor()

# 檢查表是否存在
check_table_sql = '''
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_name = '接腳說明'
    AND table_schema = 'public'
);
'''

cursor.execute(check_table_sql)
table_exists = cursor.fetchone()[0]

# 如果表不存在，則創建表
if not table_exists:
    create_table_sql = '''
    CREATE TABLE "接腳說明" (
        id SERIAL PRIMARY KEY,
        "外觀尺寸編號" VARCHAR(255) NOT NULL,
        "接腳編號" VARCHAR(255) NOT NULL,
        "接腳功能" VARCHAR(255),
        "直徑_mm" NUMERIC,
        CONSTRAINT unique_pin UNIQUE ("外觀尺寸編號", "接腳編號")
    );
    '''
    cursor.execute(create_table_sql)
    conn.commit()
    print('創建了Table 接腳說明')

# 構建批量插入的 SQL 語句
insert_sql = '''
INSERT INTO "接腳說明" ("外觀尺寸編號", "接腳功能", "接腳編號", "直徑_mm")
VALUES (%s, %s, %s, %s)
ON CONFLICT ("外觀尺寸編號", "接腳編號") DO NOTHING;
'''

# 構建數據列表
data_to_insert = [(record['外觀尺寸編號'], record['接腳功能'], record['接腳編號'], record['直徑(mm)']) for record in modified_records]

# 使用 psycopg2 批量插入數據
cursor.executemany(insert_sql, data_to_insert)

conn.commit()
cursor.close()
conn.close()
