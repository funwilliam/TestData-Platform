# 根目錄執行 `python -m unittest discover -s tests`

import unittest
from decimal import Decimal
# 假設您的函數位於 server/helpers/utils.py 中的 utils 模組中
from server.helpers.utils import RangeExtractor

extract_range = RangeExtractor.extract_range

class TestExtractRange(unittest.TestCase):
    def test_unexpected_spaces(self):
        """
        測試含有意外空格的輸入。

        這些測試案例包含了在數字和符號之間插入多餘的空格，
        以確保函數能夠正確地忽略空格並解析數值。
        """
        test_cases = [
            (' - 1 . 2 3 e 3 ~ + 4 . 5 6 e 2 ', (Decimal('-1230'), Decimal('456'))),
            (' 50    to   100 ', (Decimal('50'), Decimal('100'))),
            (' from    -100    to   500 ', (Decimal('-100'), Decimal('500'))),
            (' ±  1 ', (Decimal('-1'), Decimal('1'))),
            (' {   1 ', (Decimal('-1'), Decimal('1'))),
            (' +   -   1 ', (Decimal('-1'), Decimal('1'))),
            (' -  0 . 5  ~  +  0 . 5 ', (Decimal('-0.5'), Decimal('0.5'))),
            (' -1 . 2 3 e - 4 ~ +4 . 5 6 e -2 ', (Decimal('-0.000123'), Decimal('0.0456'))),
            (' 1 0 0 to 2 0 0 ', (Decimal('100'), Decimal('200'))),
            (' from  - 5 0  to  + 5 0 ', (Decimal('-50'), Decimal('50'))),
            (' ±  2 . 5 e 2 ', (Decimal('-250'), Decimal('250'))),
            (' {  3 . 1 4 ', (Decimal('-3.14'), Decimal('3.14'))),
            (' +  -  1 . 6  ', (Decimal('-1.6'), Decimal('1.6'))),
            (' +1 ~ +2 ', (Decimal('1'), Decimal('2'))),
            (' -1~ +1 ', (Decimal('-1'), Decimal('1'))),
            (' - 1e 2 ~ + 1 e 2 ', (Decimal('-100'), Decimal('100'))),
            (' 5 0 0 ~ 1 0 0 0 ', (Decimal('500'), Decimal('1000'))),
            (' -1 . 0 0 1 ~ 1 . 0 0 1 ', (Decimal('-1.001'), Decimal('1.001'))),
            (' 0 ~ +1 ', (Decimal('0'), Decimal('1'))),
            (' -1 ~ 0 ', (Decimal('-1'), Decimal('0'))),
            (' + / - 7 . 7 ', (Decimal('-7.7'), Decimal('7.7'))),
        ]
        for input_str, expected in test_cases:
            result = extract_range(input_str)
            print(f"Test Unexpected Spaces | Input: '{input_str}' | Expected: {expected} | Result: {result}")
            self.assertEqual(result, expected)

    def test_omitted_positive_sign(self):
        """
        測試省略正號的輸入。

        確保函數能夠正確解析省略了正號的正數，以及顯式標明正號的數值。
        """
        test_cases = [
            ('1~2', (Decimal('1'), Decimal('2'))),
            ('+1~+2', (Decimal('1'), Decimal('2'))),
            ('1e2~2e2', (Decimal('100'), Decimal('200'))),
            ('+1e2~+2e2', (Decimal('100'), Decimal('200'))),
            ('1.5~2.5', (Decimal('1.5'), Decimal('2.5'))),
            ('+1.5~+2.5', (Decimal('1.5'), Decimal('2.5'))),
            ('1.0e3~2.0e3', (Decimal('1000'), Decimal('2000'))),
            ('+1.0e3~+2.0e3', (Decimal('1000'), Decimal('2000'))),
            ('1~+2', (Decimal('1'), Decimal('2'))),
            ('+1~2', (Decimal('1'), Decimal('2'))),
            ('±1', (Decimal('-1'), Decimal('1'))),
            ('{1', (Decimal('-1'), Decimal('1'))),
            ('+-1', (Decimal('-1'), Decimal('1'))),
            ('±1.5', (Decimal('-1.5'), Decimal('1.5'))),
            ('{2e3', (Decimal('-2000'), Decimal('2000'))),
            ('+-1.23e-4', (Decimal('-0.000123'), Decimal('0.000123'))),
            ('± 1', (Decimal('-1'), Decimal('1'))),
            ('{ 1', (Decimal('-1'), Decimal('1'))),
            ('+ - 1', (Decimal('-1'), Decimal('1'))),
            ('1~+2', (Decimal('1'), Decimal('2'))),
            ('+1~2', (Decimal('1'), Decimal('2'))),
            ('+0~+1', (Decimal('0'), Decimal('1'))),
        ]
        for input_str, expected in test_cases:
            result = extract_range(input_str)
            print(f"Test Omitted Positive Sign | Input: '{input_str}' | Expected: {expected} | Result: {result}")
            self.assertEqual(result, expected)

    def test_negative_sign_in_symmetric(self):
        """
        測試對稱範圍中包含負號的數值。

        檢查函數是否能夠正確處理如 '±-1.5e2' 這樣的輸入，並返回正確的範圍。
        """
        test_cases = [
            ('±-1', (Decimal('-1'), Decimal('1'))),
            ('{ -2', (Decimal('-2'), Decimal('2'))),
            ('+- -3', (Decimal('-3'), Decimal('3'))),
            ('± -1.5e2', (Decimal('-150'), Decimal('150'))),
            ('±-0.5', (Decimal('-0.5'), Decimal('0.5'))),
            ('{ -1.23e-4', (Decimal('-0.000123'), Decimal('0.000123'))),
            ('+- -2.5e3', (Decimal('-2500'), Decimal('2500'))),
            ('± -3.14', (Decimal('-3.14'), Decimal('3.14'))),
            ('{ -0.001', (Decimal('-0.001'), Decimal('0.001'))),
            ('+- -5e-2', (Decimal('-0.05'), Decimal('0.05'))),
            ('± -100', (Decimal('-100'), Decimal('100'))),
            ('{ -200', (Decimal('-200'), Decimal('200'))),
            ('+- -300', (Decimal('-300'), Decimal('300'))),
            ('± -0', (Decimal('0'), Decimal('0'))),
            ('{ -0', (Decimal('0'), Decimal('0'))),
            ('+- -0', (Decimal('0'), Decimal('0'))),
            ('± -1e0', (Decimal('-1'), Decimal('1'))),
            ('{ -2e1', (Decimal('-20'), Decimal('20'))),
            ('+- -3e2', (Decimal('-300'), Decimal('300'))),
            ('± -4e-1', (Decimal('-0.4'), Decimal('0.4'))),
            ('+/- -6.6e-1', (Decimal('-0.66'), Decimal('0.66'))),
        ]
        for input_str, expected in test_cases:
            result = extract_range(input_str)
            print(f"Test Negative Sign in Symmetric | Input: '{input_str}' | Expected: {expected} | Result: {result}")
            self.assertEqual(result, expected)

    def test_range_parsing(self):
        """
        測試 'from X to Y' , 'X to Y' , 'X/Y' 格式的解析。

        確保函數能夠正確解析 'to' , '/' 格式。
        """
        test_cases = [
            ('from -100 to 500', (Decimal('-100'), Decimal('500'))),
            ('from100to200', (Decimal('100'), Decimal('200'))),
            ('from -1e2 to 2.5e2', (Decimal('-100'), Decimal('250'))),
            ('from-50to+50', (Decimal('-50'), Decimal('50'))),
            ('from 0 to 1', (Decimal('0'), Decimal('1'))),
            ('from -0.5 to 0.5', (Decimal('-0.5'), Decimal('0.5'))),
            ('from -1e-1 to 1e-1', (Decimal('-0.1'), Decimal('0.1'))),
            ('from -2e2 to 2e2', (Decimal('-200'), Decimal('200'))),
            ('from -1000 to 1000', (Decimal('-1000'), Decimal('1000'))),
            ('from -3.14 to 3.14', (Decimal('-3.14'), Decimal('3.14'))),
            ('from-1to1', (Decimal('-1'), Decimal('1'))),
            ('from -5e3 to 5e3', (Decimal('-5000'), Decimal('5000'))),
            ('from -0 to +0', (Decimal('0'), Decimal('0'))),
            ('from -0.001 to 0.001', (Decimal('-0.001'), Decimal('0.001'))),
            ('from -1e-3 to 1e-3', (Decimal('-0.001'), Decimal('0.001'))),
            ('from -50 to +50', (Decimal('-50'), Decimal('50'))),
            ('from+1to+2', (Decimal('1'), Decimal('2'))),
            ('from-2to-1', (Decimal('-2'), Decimal('-1'))),
            ('from -1e2 to +1e2', (Decimal('-100'), Decimal('100'))),
            ('100 to 200', (Decimal('100'), Decimal('200'))),
            ('-40 to +71', (Decimal('-40'), Decimal('71'))),
            ('100to200', (Decimal('100'), Decimal('200'))),
            ('-1e2to2.5e2', (Decimal('-100'), Decimal('250'))),
            ('-50to+50', (Decimal('-50'), Decimal('50'))),
            ('0to1', (Decimal('0'), Decimal('1'))),
            ('-0.5to0.5', (Decimal('-0.5'), Decimal('0.5'))),
            ('+2.2/-5.5', (Decimal('-5.5'), Decimal('2.2'))),
        ]
        for input_str, expected in test_cases:
            result = extract_range(input_str)
            print(f"Test Range Parsing | Input: '{input_str}' | Expected: {expected} | Result: {result}")
            self.assertEqual(result, expected)

    def test_text_with_numbers(self):
        """
        測試包含其他文字的輸入。

        確保函數能夠從包含其他文字的字串中提取出數值範圍。
        """
        test_cases = [
            ('Base plate:-40 to +100', (Decimal('-40'), Decimal('100'))),
            ('範圍:-40 to +100', (Decimal('-40'), Decimal('100'))),
            ('Temperature range is from -20 to 50 degrees', (Decimal('-20'), Decimal('50'))),
            ('Limits: -1e2 ~ 1e2', (Decimal('-100'), Decimal('100'))),
            ('Measurement ± 0.5%', (Decimal('-0.5'), Decimal('0.5'))),
            ('Tolerance {0.01', (Decimal('-0.01'), Decimal('0.01'))),
            ('Deviation +-2e-3', (Decimal('-0.002'), Decimal('0.002'))),
            ('Range: 0 to 1', (Decimal('0'), Decimal('1'))),
            ('Speed -100~100 km/h', (Decimal('-100'), Decimal('100'))),
            ('嘿嘿嘿>< +/-66.66', (Decimal('-66.66'), Decimal('66.66'))),
        ]
        for input_str, expected in test_cases:
            try:
                result = extract_range(input_str)
                print(f"Test Text with Numbers | Input: '{input_str}' | Expected: {expected} | Result: {result}")
                self.assertEqual(result, expected)
            except ValueError as e:
                self.fail(f"Input '{input_str}' 應該解析成功，但拋出了 ValueError: {e}")

    def test_scientific_notation(self):
        """
        測試科學記號格式的解析。

        檢查函數對於包含科學記號的數值能否正確解析，並處理正負指數等情況。
        """
        test_cases = [
            ('-1.23e3~+4.56e2', (Decimal('-1230'), Decimal('456'))),
            ('1e2~2e2', (Decimal('100'), Decimal('200'))),
            ('-5e-1~5e-1', (Decimal('-0.5'), Decimal('0.5'))),
            ('±1e3', (Decimal('-1000'), Decimal('1000'))),
            ('{2.5e-2', (Decimal('-0.025'), Decimal('0.025'))),
            ('-1e-3~1e-3', (Decimal('-0.001'), Decimal('0.001'))),
            ('-2.5e2~2.5e2', (Decimal('-250'), Decimal('250'))),
            ('-3.14e0~3.14e0', (Decimal('-3.14'), Decimal('3.14'))),
            ('-6e+2~6e+2', (Decimal('-600'), Decimal('600'))),
            ('±7.89e-4', (Decimal('-0.000789'), Decimal('0.000789'))),
            ('{1.23e1', (Decimal('-12.3'), Decimal('12.3'))),
            ('-9e9~9e9', (Decimal('-9E+9'), Decimal('9E+9'))),
            ('-1e-9~1e-9', (Decimal('-1E-9'), Decimal('1E-9'))),
            ('±5e5', (Decimal('-500000'), Decimal('500000'))),
            ('{7e-7', (Decimal('-7E-7'), Decimal('7E-7'))),
            ('-8.5e2~8.5e2', (Decimal('-850'), Decimal('850'))),
            ('-2e0~2e0', (Decimal('-2'), Decimal('2'))),
            ('±4.5e-3', (Decimal('-0.0045'), Decimal('0.0045'))),
            ('{6.7e+1', (Decimal('-67'), Decimal('67'))),
            ('-9.9e-2~9.9e-2', (Decimal('-0.099'), Decimal('0.099'))),
            ('+-3.7e-3', (Decimal('-0.0037'), Decimal('0.0037'))),
            ('+/-9.5e-3', (Decimal('-0.0095'), Decimal('0.0095'))),
        ]
        for input_str, expected in test_cases:
            result = extract_range(input_str)
            print(f"Test Scientific Notation | Input: '{input_str}' | Expected: {expected} | Result: {result}")
            self.assertEqual(result, expected)

    def test_edge_cases(self):
        """
        測試邊界情況和極端數值。

        測試包含極大或極小數字、空字串以及零值範圍的解析。
        """
        test_cases = [
            ('', None),  # 空字符串
            ('±0', (Decimal('0'), Decimal('0'))),  # 對稱零值
            ('from 0 to 0', (Decimal('0'), Decimal('0'))),  # 零值範圍
            ('-1e9~1e9', (Decimal('-1000000000'), Decimal('1000000000'))),  # 極端大數
            ('±1e-9', (Decimal('-1e-9'), Decimal('1e-9'))),  # 極端小數
        ]
        for input_str, expected in test_cases:
            if expected is None:
                with self.assertRaises(ValueError):
                    extract_range(input_str)
            else:
                result = extract_range(input_str)
                self.assertEqual(result, expected)

    def test_invalid_inputs(self):
        """
        測試無效輸入的處理。

        確保函數在遇到無效的輸入時，能夠拋出 ValueError，並提供適當的錯誤訊息。
        """
        invalid_cases = [
            '-5~',
            '100 ~ -50',
            '1',
            '',
            'abc',
            '±   ',
            'from to',
            '~~',
            '±abc',
            'from 100',
            'to 200',
            '100~abc',
            '±',
            '{',
            '+-',
            '+- ',
            'fromto',
            '+++',
            '--',
            '==',
            '1~',
            '~2',
            'fromto',
            'from ~ to',
            '±±1',
            '{{1',
            '++1--2',
            'number',
            '±-',
            'from-',
            'to+',
            '1e2~abc',
            'abc~1e2',
            '1e~2e',
            '1.2.3~4.5.6',
            '1e2e3~4e5',
            '±~1',
            '~±1',
            'from~to',
            '-40 - +71',   # 測試使用 '-' 作為範圍分隔符的情況，應視為無效輸入
            '100 - 200',   # 同上
            '1 – 2',       # 使用 '–'（長破折號）作為分隔符
            '3 — 4',       # 使用 '—'（長破折號）作為分隔符
        ]
        for input_str in invalid_cases:
            with self.subTest(input_str=input_str):
                try:
                    result = extract_range(input_str)
                    print(f"Test Invalid Inputs | Input: '{input_str}' | Should Raise ValueError but got: {result}")
                    self.fail(f"Input '{input_str}' 應該拋出 ValueError, 實際輸出為 '{result}'")
                except ValueError as e:
                    print(f"Test Invalid Inputs | Input: '{input_str}' | Correctly Raised ValueError")

if __name__ == '__main__':
    unittest.main()
