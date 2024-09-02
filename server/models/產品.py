from typing import List, Dict, Optional, Literal
from server.models.電器特性物件 import 輸入, 輸出, 輸入電壓, 輸入電流, 輸出電壓


class 產品:
    def __init__(
            self,
            model_number: str,
            ) -> None:
        self.model_number: str = model_number
        self.output_quantity: int = 0
        self.input: Dict[str, 輸入] = {}
        self.outputs: Dict[str, 輸出] = {}
        self.input_voltage_definitions: Dict[Literal['LowLine', 'NominalLine', 'HighLine'], 輸入電壓] = {}
        self.output_voltage_definitions: Dict[str, 輸出電壓] = {}
        self.output_current_definitions: Dict[str, Dict[Literal['NoLoad', 'MinimumLoad', 'MaximumLoad'], 輸入電流]] = {}
        self.quality_test_spec = []

    def get_output_key_number(self, output: 輸出) -> Optional[str]:
        for key_number, out in self.outputs.items():
            if out is output:
                return key_number
            
    def load_spec(self, spec_json) -> None:
        pass
