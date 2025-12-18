#!/usr/bin/env python3
# Mirror.py
# Скачивание и сортировка прокси-ключей
# Требует: requests

import os
import requests
import base64

# -------------------- Настройки --------------------
LOCAL_DIR = "githubmirror"
NEW_DIR = os.path.join(LOCAL_DIR, "new")
CLEAN_DIR = os.path.join(LOCAL_DIR, "clean")

# Протоколы
PROTOCOLS = ["vless", "vmess", "trojan", "ss", "hysteria", "hysteria2", "hy2", "tuic"]

# Источники
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

# -------------------- Функции --------------------
def is_valid_proxy(line):
    line = line.strip().lower()
    return any(line.startswith(p + "://") for p in PROTOCOLS)

def get_protocol(line):
    line = line.strip().lower()
    for p in PROTOCOLS:
        if line.startswith(p + "://"):
            return p
    return "other"

def download_sources():
    all_lines = []
    print("Скачиваем источники...")
    for i, url in enumerate(URLS, 1):
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            lines = r.text.splitlines()
            all_lines.extend([l.strip() for l in lines if l.strip()])
            print(f"{i}/{len(URLS)} ОК")
        except Exception as e:
            print(f"{i}/{len(URLS)} ошибка: {e}")
    return all_lines

def save_new(all_lines):
    os.makedirs(NEW_DIR, exist_ok=True)
    new_file = os.path.join(NEW_DIR, "new_keys.txt")
    with open(new_file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_lines))
    print(f"\nСохранено {len(all_lines)} новых ключей в '{NEW_DIR}'")

def save_clean(all_lines):
    os.makedirs(CLEAN_DIR, exist_ok=True)
    clean_counts = {p: 0 for p in PROTOCOLS + ["other"]}
    unique_lines = list(dict.fromkeys(all_lines))  # удаляем дубли
    for line in unique_lines:
        proto = get_protocol(line)
        path = os.path.join(CLEAN_DIR, proto)
        os.makedirs(path, exist_ok=True)
        fname = os.path.join(path, "clean_keys.txt")
        with open(fname, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        clean_counts[proto] += 1
    print("\nСортировка и очистка завершены:")
    for p, c in clean_counts.items():
        print(f"{p}: {c} ключей")

# -------------------- Основная логика --------------------
def main():
    all_lines = download_sources()
    all_lines = [l for l in all_lines if is_valid_proxy(l)]
    save_new(all_lines)
    save_clean(all_lines)
    print("\n✅ Готово. Новые ключи в 'new', чистые по протоколам в 'clean'.")

if __name__ == "__main__":
    main()












