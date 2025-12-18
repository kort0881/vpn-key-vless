#!/usr/bin/env python3
# Mirror.py — CLEAN MIRROR VERSION (with host:port:scheme de-dup and fixed BASE_DIR)

import os
import shutil
import requests
import urllib.parse

# Базовый путь — рядом с mirror.py
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

BASE_DIR = os.path.join(BASE_PATH, "githubmirror")
NEW_DIR = os.path.join(BASE_DIR, "new")
CLEAN_DIR = os.path.join(BASE_DIR, "clean")

PROTOCOLS = [
    "vless", "vmess", "trojan", "ss",
    "hysteria", "hysteria2", "hy2", "tuic"
]

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

def clean_start():
    if os.path.exists(BASE_DIR):
        shutil.rmtree(BASE_DIR)
    os.makedirs(NEW_DIR, exist_ok=True)
    os.makedirs(CLEAN_DIR, exist_ok=True)

def protocol_of(line: str):
    for p in PROTOCOLS:
        if line.startswith(p + "://"):
            return p
    return None

def extract_host_port_scheme(line: str):
    try:
        u = urllib.parse.urlparse(line)
        return u.hostname, u.port, u.scheme
    except Exception:
        return None, None, None

def main():
    clean_start()

    all_keys = []

    print("Скачиваем источники...")
    for i, url in enumerate(URLS, 1):
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            for line in r.text.splitlines():
                line = line.strip()
                if protocol_of(line):
                    all_keys.append(line)
            print(f"{i}/{len(URLS)} ОК")
        except Exception:
            print(f"{i}/{len(URLS)} ошибка")

    # NEW (сырые ключи)
    new_path = os.path.join(NEW_DIR, "all_new.txt")
    with open(new_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_keys))

    # Анти-дубликат по host:port:scheme
    seen_ip = set()
    clean_keys = []

    for line in all_keys:
        host, port, scheme = extract_host_port_scheme(line)
        if not host or not port or not scheme:
            continue
        key = (host, port, scheme)
        if key in seen_ip:
            continue
        seen_ip.add(key)
        clean_keys.append(line)

    # CLEAN
    unique = list(dict.fromkeys(clean_keys))
    buckets = {p: [] for p in PROTOCOLS}

    for k in unique:
        p = protocol_of(k)
        if p:
            buckets[p].append(k)

    for p, items in buckets.items():
        out_path = os.path.join(CLEAN_DIR, f"{p}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(items))
        print(f"{p}: {len(items)}")

    print("\nГОТОВО. githubmirror пересобран с нуля.")

if __name__ == "__main__":
    main()














