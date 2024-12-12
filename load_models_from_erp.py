import requests
import psycopg2

def get_product_data():
    url = "http://192.168.1.109/minmax-api-server/products/list"
    headers = {
        "X-API-Key": "58a702a6-335999a3-a987b4e5-8647f1b6"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 確保請求成功，否則會引發HTTPError
        json_data = response.json()
        data_list = json_data.get("data", [])
        return data_list
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return []

def transform_data(data_list):
    transformed_data = []
    for item in data_list:
        transformed_data.append({
            "型號": item.get("modelNumber"),
            "轉換類型": item.get("productType"),
            "系列": item.get("seriesNumber")
        })
    return transformed_data

def save_to_postgresql(data_list):
    try:
        # 建立與 PostgreSQL 的連接
        connection = psycopg2.connect(
            dbname="pg-productspec-db",
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()

        # 建立 "型號" 表格
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS 型號 (
            型號 CHARACTER VARYING PRIMARY KEY,
            轉換類型 CHARACTER VARYING,
            系列 CHARACTER VARYING
        );
        '''
        cursor.execute(create_table_query)
        connection.commit()

        # 插入數據
        insert_query = '''
        INSERT INTO 型號 (型號, 轉換類型, 系列) VALUES (%s, %s, %s)
        ON CONFLICT (型號) DO NOTHING;
        '''
        for item in data_list:
            cursor.execute(insert_query, (item["型號"], item["轉換類型"], item["系列"]))

        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error occurred: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()

# 使用範例
data = get_product_data()
transformed_data = transform_data(data)
save_to_postgresql(transformed_data)
