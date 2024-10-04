import json
from pathlib import Path
from mongoengine import connect
from server.models.spec import ProductModel, GeneralSpecifications, QualityTestSpecifications, ProductTypeInstance, ComponentInstance, IOInstance, Instance

# Connect to MongoDB using the provided connection string.
connect(host='mongodb://localhost:27017/testdataplatform-db')

# Insert data from a JSON file into the MongoDB database.
def insert_data_from_json(file_path):
    """
    從指定的 JSON 文件中讀取數據並將其插入到 MongoDB 數據庫中。

    Args:
        file_path (Path): JSON 文件的路徑。

    Raises:
        Exception: 如果文件讀取或數據解析過程中發生錯誤，將拋出異常。

    Side Effects:
        將讀取的數據作為新文檔保存到 MongoDB 數據庫中。
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Parse and create GeneralSpecifications from the JSON data
    general_specifications = GeneralSpecifications(
        ProductType=ProductTypeInstance(**data["GeneralSpecifications"]["ProductType"]),
        OutputQuantity=data["GeneralSpecifications"]["OutputQuantity"],
        Component=[ComponentInstance(**component) for component in data["GeneralSpecifications"]["Component"]["Instances"]],
        IO=[IOInstance(**io_data) for io_data in data["GeneralSpecifications"]["IO"]["Instances"]],
        OperatingAmbientTemperature=[Instance(**temp) for temp in data["GeneralSpecifications"]["OperatingAmbientTemperature"]["Instances"]],
        InputVoltage=[Instance(**volt) for volt in data["GeneralSpecifications"]["InputVoltage"]["Instances"]],
        OutputVoltage=[Instance(**volt) for volt in data["GeneralSpecifications"]["OutputVoltage"]["Instances"]],
        OutputCurrent=[Instance(**current) for current in data["GeneralSpecifications"]["OutputCurrent"]["Instances"]],
        IsolationVoltage=[Instance(**iso_volt) for iso_volt in data["GeneralSpecifications"]["IsolationVoltage"]["Instances"]],
        IsolationResistance=[Instance(**iso_res) for iso_res in data["GeneralSpecifications"]["IsolationResistance"]["Instances"]],
        IsolationCapacitance=[Instance(**iso_cap) for iso_cap in data["GeneralSpecifications"]["IsolationCapacitance"]["Instances"]],
    )

    # Parse and create QualityTestSpecifications from the JSON data
    quality_test_specifications = QualityTestSpecifications(
        InputCurrent=[Instance(**ic) for ic in data["QualityTestSpecifications"]["InputCurrent"]["Instances"]],
        InputReflectedRippleCurrent=[Instance(**irr) for irr in data["QualityTestSpecifications"]["InputReflectedRippleCurrent"]["Instances"]],
        OutputVoltage=[Instance(**ov) for ov in data["QualityTestSpecifications"]["OutputVoltage"]["Instances"]],
        OutputVoltageSettingAccuracy=[Instance(**ovsa) for ovsa in data["QualityTestSpecifications"]["OutputVoltageSettingAccuracy"]["Instances"]],
        OutputVoltageBalance=[Instance(**ovb) for ovb in data["QualityTestSpecifications"]["OutputVoltageBalance"]["Instances"]],
        LoadRegulation=[Instance(**lr) for lr in data["QualityTestSpecifications"]["LoadRegulation"]["Instances"]],
        LineRegulation=[Instance(**linr) for linr in data["QualityTestSpecifications"]["LineRegulation"]["Instances"]],
        RippleAndNoise=[Instance(**rn) for rn in data["QualityTestSpecifications"]["RippleAndNoise"]["Instances"]],
        TransientRecoveryTime=[Instance(**trt) for trt in data["QualityTestSpecifications"]["TransientRecoveryTime"]["Instances"]],
        TransientResponseDeviation=[Instance(**trd) for trd in data["QualityTestSpecifications"]["TransientResponseDeviation"]["Instances"]],
        Overshoot=[Instance(**os) for os in data["QualityTestSpecifications"]["Overshoot"]["Instances"]],
        Efficiency=[Instance(**eff) for eff in data["QualityTestSpecifications"]["Efficiency"]["Instances"]],
        ShortCircuitProtectionInputCurrent=[Instance(**scpic) for scpic in data["QualityTestSpecifications"]["ShortCircuitProtectionInputCurrent"]["Instances"]],
        OverloadCurrentProtection=[Instance(**op) for op in data["QualityTestSpecifications"]["OverloadCurrentProtection"]["Instances"]],
        RemoteControlInputVoltage=[Instance(**rciv) for rciv in data["QualityTestSpecifications"]["RemoteControlInputVoltage"]["Instances"]],
        RemoteControlInputCurrent=[Instance(**rcic) for rcic in data["QualityTestSpecifications"]["RemoteControlInputCurrent"]["Instances"]],
    )

    # Create a ProductModel instance and save it to the database
    product = ProductModel(
        Model=data["Model"],
        GeneralSpecifications=general_specifications,
        QualityTestSpecifications=quality_test_specifications
    )
    
    # Save the product data to the database
    product.save()
    print(f"Data for model {product.Model} saved successfully!")

if __name__ == "__main__":
    # Insert data from a JSON file into the MongoDB database
    insert_data_from_json(Path('docs/spec_data_structure_example.json'))
