import os
import re
import requests
from datetime import datetime

# ================= НАСТРОЙКИ =================

BASE_DIR = "getmirror"

SOURCES_DIR = os.path.join(BASE_DIR, "sources")
NEW_DIR = os.path.join(BASE_DIR, "new")
CLEAN_DIR = os.path.join(BASE_DIR, "clean")

SOURCES = [
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

PROTOCOLS = [
    "vless", "vmess", "trojan", "ss",
    "hysteria", "hysteria2", "hy2", "tuic"
]

# ================= ФУНКЦИИ =================

def mkdirs():
    for p in [SOURCES_DIR, NEW_DIR, CLEAN_DIR]:
        os.makedirs(p, exist_ok=True)

def download_sources():
    print("Скачиваем источники...")
    for i, url in enumerate(SOURCES, 1):
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                with open(os.path.join(SOURCES_DIR, f"source_{i}.txt"), "w", encoding="utf-8", errors="ignore") as f:
                    f.write(r.text)
                print(f"{i}/{len(SOURCES)} OK")
            else:
                print(f"{i}/{len(SOURCES)} пропущен")
        except:
            print(f"{i}/{len(SOURCES)} ошибка")

def extract_keys():
    all_keys = []

    pattern = re.compile(r'^(vless|vmess|trojan|ss|hysteria2?|hy2|tuic)://.+$', re.IGNORECASE)

    for file in os.listdir(SOURCES_DIR):
        path = os.path.join(SOURCES_DIR, file)
        with open(path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if pattern.match(line):
                    all_keys.append(line)

    return all_keys

def save_new(keys):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(NEW_DIR, f"NEW_{ts}.txt")
    with open(path, "w", encoding="utf-8") as f:
        for k in keys:
            f.write(k + "\n")

def clean_and_split(keys):
    unique = set(keys)

    buckets = {p: [] for p in PROTOCOLS}

    for k in unique:
        for p in PROTOCOLS:
            if k.lower().startswith(p + "://"):
                buckets[p].append(k)
                break

    for proto, items in buckets.items():
        if items:
            with open(os.path.join(CLEAN_DIR, f"{proto}.txt"), "w", encoding="utf-8") as f:
                for i in items:
                    f.write(i + "\n")

    print("\nСортировка завершена:")
    for proto in PROTOCOLS:
        print(f"{proto}: {len(buckets[proto])}")

# ================= ЗАПУСК =================

if __name__ == "__main__":
    mkdirs()
    download_sources()
    keys = extract_keys()
    save_new(keys)
    clean_and_split(keys)
    print("\nГотово. Структура getmirror приведена в порядок.")











