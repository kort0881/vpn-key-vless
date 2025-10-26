import os
import requests
from github import Github, Auth
from datetime import datetime
import zoneinfo

# -------------------- Настройки --------------------
GITHUB_TOKEN = os.environ.get("MY_TOKEN")
REPO_NAME = "vpn-key-vless"  # твой репозиторий

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
    "https://raw.githubusercontent.com/V2RayRoot/V2RayConfig/refs/heads/main/Config/vless.txt",
]

# Создаём папку vpn-files, если нет
os.makedirs("vpn-files", exist_ok=True)

LOCAL_PATHS = [f"vpn-files/{i+1}.txt" for i in range(len(URLS))]
REMOTE_PATHS = [f"vpn-files/{i+1}.txt" for i in range(len(URLS))]

if not GITHUB_TOKEN:
    raise ValueError("MY_TOKEN не найден. Добавьте его в GitHub Secrets")

g = Github(auth=Auth.Token(GITHUB_TOKEN))
repo = g.get_repo(REPO_NAME)

def fetch_data(url):
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.text

def save_and_upload(idx):
    url = URLS[idx]
    local_path = LOCAL_PATHS[idx]
    remote_path = REMOTE_PATHS[idx]

    data = fetch_data(url)

    # Сохраняем локально
    with open(local_path, "w", encoding="utf-8") as f:
        f.write(data)
    print(f"Сохранено локально: {local_path}")

    # Загружаем на GitHub
    try:
        file_in_repo = repo.get_contents(remote_path)
        if file_in_repo.decoded_content.decode("utf-8") == data:
            print(f"Файл {remote_path} не изменился, пропускаем")
            return
        repo.update_file(
            path=remote_path,
            message=f"Обновление {remote_path}",
            content=data,
            sha=file_in_repo.sha
        )
        print(f"Файл {remote_path} обновлён в репозитории")
    except:
        repo.create_file(
            path=remote_path,
            message=f"Создание {remote_path}",
            content=data
        )
        print(f"Файл {remote_path} создан в репозитории")

for i in range(len(URLS)):
    try:
        save_and_upload(i)
    except Exception as e:
        print(f"Ошибка для {URLS[i]}: {e}")
