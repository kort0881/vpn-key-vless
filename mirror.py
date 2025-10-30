import os
import requests
from github import Github, Auth, GithubException
from datetime import datetime
import zoneinfo
import re

# -------------------- ПАПКА --------------------
LOCAL_DIR = "vpn-files"
os.makedirs(LOCAL_DIR, exist_ok=True)

# -------------------- GITHUB --------------------
GITHUB_TOKEN = os.environ.get("MY_TOKEN")
REPO_NAME = "kort0881/vpn-key-vless"

g = Github(auth=Auth.Token(GITHUB_TOKEN))
repo = g.get_repo(REPO_NAME)

# -------------------- URLS --------------------
URLS = [
    "https://github.com/sakha1370/OpenRay/raw/refs/heads/main/output/all_valid_proxies.txt",
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/main/protocols/vl.txt",
    "https://raw.githubusercontent.com/yitong2333/proxy-minging/refs/heads/main/v2ray.txt",
    "https://raw.githubusercontent.com/acymz/AutoVPN/refs/heads/main/data/V2.txt",
    "https://raw.githubusercontent.com/miladtahanian/V2RayCFGDumper/refs/heads/main/config.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/V2RAY_RAW.txt",
    "https://github.com/Epodonios/v2ray-configs/raw/main/Splitted-By-Protocol/trojan.txt",
    "https://raw.githubusercontent.com/YasserDivaR/pr0xy/refs/heads/main/ShadowSocks2021.txt",
    "https://raw.githubusercontent.com/mohamadfg-dev/telegram-v2ray-configs-collector/refs/heads/main/category/vless.txt",
    "https://raw.githubusercontent.com/mheidari98/.proxy/refs/heads/main/vless",
    "https://raw.githubusercontent.com/youfoundamin/V2rayCollector/main/mixed_iran.txt",
    "https://raw.githubusercontent.com/mheidari98/.proxy/refs/heads/main/all",
    "https://github.com/Kwinshadow/TelegramV2rayCollector/raw/refs/heads/main/sublinks/mix.txt",
    "https://github.com/LalatinaHub/Mineral/raw/refs/heads/master/result/nodes",
    "https://raw.githubusercontent.com/miladtahanian/multi-proxy-config-fetcher/refs/heads/main/configs/proxy_configs.txt",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/refs/heads/main/sub",
    "https://github.com/MhdiTaheri/V2rayCollector_Py/raw/refs/heads/main/sub/Mix/mix.txt",
    "https://github.com/Epodonios/v2ray-configs/raw/main/Splitted-By-Protocol/vmess.txt",
    "https://github.com/MhdiTaheri/V2rayCollector/raw/refs/heads/main/sub/mix",
    "https://raw.githubusercontent.com/mehran1404/Sub_Link/refs/heads/main/V2RAY-Sub.txt",
    "https://raw.githubusercontent.com/shabane/kamaji/master/hub/merged.txt",
    "https://raw.githubusercontent.com/wuqb2i4f/xray-config-toolkit/main/output/base64/mix-uri",
    "https://raw.githubusercontent.com/AzadNetCH/Clash/refs/heads/main/AzadNet.txt",
    "https://raw.githubusercontent.com/STR97/STRUGOV/refs/heads/main/STR.BYPASS#STR.BYPASS%F0%9F%91%BE",
    "https://raw.githubusercontent.com/V2RayRoot/V2RayConfig/refs/heads/main/Config/vless.txt"
]

# -------------------- ВРЕМЯ --------------------
zone = zoneinfo.ZoneInfo("Europe/Moscow")
timestamp = datetime.now(zone).strftime("%Y-%m-%d %H:%M")

# -------------------- ФИЛЬТР ДЛЯ VLESS --------------------
def filter_sni(content: str, keyword="vless") -> str:
    return "\n".join(line for line in content.splitlines() if keyword in line)

# -------------------- ОЧИСТКА СТАРЫХ ФАЙЛОВ --------------------
try:
    contents = repo.get_contents(LOCAL_DIR)
    for file in contents:
        if file.name.endswith(".txt"):
            repo.delete_file(file.path, f"🧹 Remove old {file.name} before update", file.sha)
    print("🧹 Старые посты удалены")
except Exception as e:
    print(f"⚠️ Не удалось удалить старые файлы: {e}")

# -------------------- СКАЧАТЬ И ОБНОВИТЬ --------------------
updated_files = []

for i, url in enumerate(URLS, start=1):
    filename = f"{i}.txt"
    local_path = os.path.join(LOCAL_DIR, filename)

    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        content = r.text

        if i == 26:
            content = filter_sni(content, keyword="vless")

        with open(local_path, "w", encoding="utf-8") as f:
            f.write(content)

        remote_path = f"{LOCAL_DIR}/{filename}"
        try:
            file = repo.get_contents(remote_path)
            if file.decoded_content.decode("utf-8") != content:
                repo.update_file(remote_path, f"Update {filename} | {timestamp}", content, file.sha)
        except GithubException:
            repo.create_file(remote_path, f"Add {filename} | {timestamp}", content)

        updated_files.append((i, filename, url))
        print(f"✅ {filename} обновлён")
    except Exception as e:
        print(f"❌ Ошибка {filename}: {e}")

# -------------------- ОБНОВИТЬ README --------------------
def update_readme():
    try:
        readme_file = repo.get_contents("README.md")
        old_content = readme_file.decoded_content.decode("utf-8")
    except GithubException as e:
        if getattr(e, "status", None) == 404:
            old_content = ""
        else:
            print(f"❌ Ошибка чтения README.md: {e}")
            return

    table_header = "| № | Файл | Источник | Время | Дата |\n|--|--|--|--|--|"
    table_rows = []

    for i, filename, url in updated_files:
        raw_url = f"https://github.com/{REPO_NAME}/raw/refs/heads/main/{LOCAL_DIR}/{filename}"
        table_rows.append(f"| {i} | [`{filename}`]({raw_url}) | [{url}]({url}) | {timestamp.split()[1]} | {timestamp.split()[0]} |")

    new_table = table_header + "\n" + "\n".join(table_rows)

    if old_content:
        table_pattern = r"\| № \| Файл \| Источник \| Время \| Дата \|[\s\S]*"
        new_content = re.sub(table_pattern, new_table, old_content)
    else:
        new_content = "# VPN Key VLESS\n\n" + new_table

    try:
        if old_content:
            repo.update_file("README.md", f"Update README | {timestamp}", new_content, readme_file.sha)
        else:
            repo.create_file("README.md", f"Add README | {timestamp}", new_content)
        print("📄 README.md обновлён")
    except GithubException as e:
        print(f"❌ Ошибка обновления README.md: {e}")

update_readme()




