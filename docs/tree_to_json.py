import json
import re

def parse_tree_to_json_v13(file_path):
    tree = {'name': 'root', 'children': []}
    stack = [tree]

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            stripped_line = line.rstrip()

            # 跳過空行及無意義標題
            if not stripped_line or re.search(r"(列出磁碟區|磁碟區|PATH|資料夾|根目錄|root|^\s*$)", stripped_line, re.IGNORECASE):
                continue

            # 使用正則表達式匹配縮進符號
            match = re.match(r"([\|\\+\s\-]*)\s*(.*)", stripped_line)
            if not match:
                continue

            indent_symbols, name = match.groups()

            # 統一處理 '+---' 和 '\---' 為層級指示符號，計算層次級別
            indent_level = indent_symbols.count('|') + indent_symbols.count('+') + indent_symbols.count('\\')

            # 去除名稱中的多餘符號和空格
            name = re.sub(r"[\"\'\(\)XXXX]", "", name).strip()

            # 檢查是否為有效名稱
            if not name or re.match(r'^\s*$', name):
                continue

            # 建立節點
            node = {'name': name, 'children': []}

            # 根據縮進層級調整 stack
            while len(stack) > indent_level + 1:
                stack.pop()

            # 添加新節點到當前層級
            stack[-1]['children'].append(node)
            stack.append(node)

    return tree

# 將解析結果存儲為 JSON 文件
tree_json_v13 = parse_tree_to_json_v13("產品屬性(業務部鄭全宏友情提供).txt")
with open("tree_fixed_v13.json", "w", encoding="utf-8") as json_file:
    json.dump(tree_json_v13, json_file, ensure_ascii=False, indent=4)
