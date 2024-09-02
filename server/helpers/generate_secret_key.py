import os
import secrets

def update_secret_key():
    env_file = ".env"
    secret_key = secrets.token_hex(32)

    # 讀取 .env 文件並保留排版
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = []

    # 檢查並更新 SECRET_KEY
    key_found = False
    new_lines = []
    for line in lines:
        if line.strip().startswith("SECRET_KEY"):
            new_lines.append(f"SECRET_KEY{' ' * (44 - len('SECRET_KEY'))}= {secret_key}\n")
            key_found = True
        else:
            new_lines.append(line)

    if not key_found:
        # 保留排版並添加 SECRET_KEY
        new_lines.append(f"\n# Flask\nSECRET_KEY{' ' * (44 - len('SECRET_KEY'))}= {secret_key}\n")

    # 寫回 .env 文件
    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    update_secret_key()

