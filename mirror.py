#!/usr/bin/env python3
# mirror_clean_sort.py
# Скачивание источников + очистка + сортировка по протоколам
# Требует: requests
# ENV: нет

import os
import socket
import urllib.parse
import urllib3
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -------------------- Настройки --------------------
LOCAL_DIR = "getmirror"
NEW_DIR = os.path.join(LOCAL_DIR, "new")
CLEAN_DIR = os.path.join(LOCAL_DIR, "clean")

os.makedirs(LOCAL_DIR, exist_ok=True)
os.makedirs(NEW_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)

TIMEOUT = 12
RETRIES = 2
REQUESTS_POOL = 10

CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/138.0.0.0 Safari/537.36"
)

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
    "https://raw.githubusercontent.com/STR97/STRUGOV/refs/heads/main/STR.BYPASS",
    "https://raw.githubusercontent.com/V2RayRoot/V2RayConfig/refs/heads/main/Config/vless.txt",
    "https://raw.githubusercontent.com/lagzian/SS-Collector/main/mix_clash.yaml",
    "https://raw.githubusercontent.com/Argh94/V2RayAutoConfig/refs/heads/main/configs/Vless.txt",
    "https://raw.githubusercontent.com/Argh94/V2RayAutoConfig/refs/heads/main/configs/Hysteria2.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_list.json",
    "https://raw.githubusercontent.com/NiREvil/vless/main/sub/SSTime",
    "https://raw.githubusercontent.com/ndsphonemy/proxy-sub/main/speed.txt",
    "https://raw.githubusercontent.com/Mahdi0024/ProxyCollector/master/sub/proxies.txt",
    "https://raw.githubusercontent.com/Mosifree/-FREE2CONFIG/refs/heads/main/Reality",
    "https://raw.githubusercontent.com/MrMohebi/xray-proxy-grabber-telegram/master/collected-proxies/row-url/all.txt",
]

SNI_DOMAINS = [
    "vk.com", "yandex.ru", "ozon.ru", "wildberries.ru",
    "sberbank.ru", "mail.ru", "ivi.ru", "hh.ru",
]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -------------------- HTTP --------------------
def build_session():
    s = requests.Session()
    adapter = HTTPAdapter(
        pool_connections=REQUESTS_POOL,
        pool_maxsize=REQUESTS_POOL,
        max_retries=Retry(
            total=RETRIES,
            backoff_factor=0.4,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET"]),
        ),
    )
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({"User-Agent": CHROME_UA})
    return s

SESSION = build_session()

def request_with_strategies(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname

    try:
        r = SESSION.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return r.text
    except Exception:
        pass

    if host:
        ip = socket.gethostbyname(host)
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query

        r = SESSION.get(
            f"https://{ip}{path}",
            headers={"Host": host},
            timeout=TIMEOUT,
            verify=False,
        )
        r.raise_for_status()
        return r.text

    raise RuntimeError("All strategies failed")

# -------------------- Проверка протоколов --------------------
def is_valid_proxy(line: str) -> bool:
    protocols = ['vless://', 'vmess://', 'trojan://', 'ss://',
                 'hysteria://', 'hysteria2://', 'hy2://', 'tuic://']
    return any(line.startswith(p) for p in protocols)

def get_protocol(line: str) -> str:
    for p in ['vless', 'vmess', 'trojan', 'ss', 'hysteria', 'hysteria2', 'hy2', 'tuic']:
        if line.startswith(p + "://"):
            return p
    return "other"

# -------------------- Основной процесс --------------------
def main():
    # Очистка папок new и clean
    for folder in os.listdir(NEW_DIR):
        path = os.path.join(NEW_DIR, folder)
        if os.path.isfile(path):
            os.remove(path)
    for folder in os.listdir(CLEAN_DIR):
        path = os.path.join(CLEAN_DIR, folder)
        if os.path.isfile(path):
            os.remove(path)

    # Создание поддиректорий clean по протоколам
    protocols = ['vless', 'vmess', 'trojan', 'ss', 'hysteria', 'hysteria2', 'hy2', 'tuic', 'other']
    for p in protocols:
        os.makedirs(os.path.join(CLEAN_DIR, p), exist_ok=True)

    # Скачиваем источники
    print("Скачиваем источники...")
    new_files = []
    for idx, url in enumerate(URLS, 1):
        try:
            text = request_with_strategies(url)
            new_path = os.path.join(NEW_DIR, f"new{idx}.txt")
            with open(new_path, "w", encoding="utf-8") as f:
                f.write(text.replace("\r\n", "\n"))
            new_files.append(new_path)
            print(f"{idx}/{len(URLS)} скачан")
        except Exception as e:
            print(f"Ошибка {idx}: {e}")

    # Обработка новых файлов и сортировка по протоколам
    print("\nСортируем и чистим ключи...")
    all_keys = set()
    for file in new_files:
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or not is_valid_proxy(line):
                    continue
                if any(d in line for d in SNI_DOMAINS):
                    continue
                all_keys.add(line)

    # Разделяем по протоколам и записываем
    protocol_files = {p: set() for p in protocols}
    for key in all_keys:
        p = get_protocol(key)
        protocol_files[p].add(key)

    for p, keys in protocol_files.items():
        path = os.path.join(CLEAN_DIR, p, f"{p}_clean.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(keys)))
        print(f"{p}: {len(keys)} ключей")

    print("\nГотово! Новые ключи в папке 'new', чистые по протоколам в 'clean'.")

if __name__ == "__main__":
    main()











