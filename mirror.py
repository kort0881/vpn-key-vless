#!/usr/bin/env python3
# mirror.py
# Синхронное зеркалирование источников + чистые подписки
# TTL + anti-duplicate + SNI + split large files
# ENV: MY_TOKEN

import os
import time
import json
import base64
import socket
import urllib.parse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from github import Github, Auth, GithubException
from datetime import datetime, timedelta
import zoneinfo

# -------------------- НАСТРОЙКИ --------------------
REPO_NAME = "kort0881/vpn-key-vless"
GITHUB_TOKEN = os.environ.get("MY_TOKEN")

LOCAL_DIR = "githubmirror"
SUBSCRIPTIONS_DIR = "subscriptions"
STATE_DIR = "state"
SEEN_FILE = os.path.join(STATE_DIR, "seen_keys.json")

TTL_HOURS = 12
TIMEOUT = 12
RETRIES = 2
POOL = 10
GITHUB_DELAY = 1.2
SPLIT_LINES = 50000

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

# -------------------- INIT --------------------
os.makedirs(LOCAL_DIR, exist_ok=True)
os.makedirs(SUBSCRIPTIONS_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

if not GITHUB_TOKEN:
    raise SystemExit("MY_TOKEN not set")

g = Github(auth=Auth.Token(GITHUB_TOKEN))
repo = g.get_repo(REPO_NAME)

def now_moscow():
    return datetime.now(zoneinfo.ZoneInfo("Europe/Moscow"))

# -------------------- HTTP --------------------
def build_session():
    s = requests.Session()
    adapter = HTTPAdapter(
        pool_connections=POOL,
        pool_maxsize=POOL,
        max_retries=Retry(
            total=RETRIES,
            backoff_factor=0.4,
            status_forcelist=(429, 500, 502, 503, 504),
        ),
    )
    s.mount("https://", adapter)
    s.headers.update({"User-Agent": CHROME_UA})
    return s

SESSION = build_session()

def fetch(url):
    r = SESSION.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text

# -------------------- UTILS --------------------
def is_valid_proxy(line):
    return line.startswith((
        "vless://", "vmess://", "trojan://", "ss://",
        "hysteria://", "hysteria2://", "hy2://", "tuic://"
    ))

def extract_key(line):
    try:
        u = urllib.parse.urlparse(line)
        return (u.hostname, u.port, u.scheme)
    except:
        return None

def load_seen():
    if not os.path.exists(SEEN_FILE):
        return {}
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_seen(data):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def split_and_upload(path, remote_base):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i in range(0, len(lines), SPLIT_LINES):
        part = lines[i:i + SPLIT_LINES]
        name = f"{remote_base}.part{i // SPLIT_LINES + 1}.txt"
        upload_content("".join(part), name)

def upload_content(content, remote_path):
    try:
        time.sleep(GITHUB_DELAY)
        existing = repo.get_contents(remote_path)
        if existing.decoded_content.decode("utf-8") == content:
            return
        repo.update_file(
            remote_path,
            f"Update {remote_path} | {now_moscow():%Y-%m-%d %H:%M}",
            content,
            existing.sha,
        )
    except GithubException as e:
        if getattr(e, "status", None) == 404:
            repo.create_file(
                remote_path,
                f"Add {remote_path} | {now_moscow():%Y-%m-%d %H:%M}",
                content,
            )

# -------------------- MAIN LOGIC --------------------
def main():
    print("Скачивание источников...")
    for i, url in enumerate(URLS, 1):
        try:
            text = fetch(url)
            with open(os.path.join(LOCAL_DIR, f"{i}.txt"), "w", encoding="utf-8") as f:
                f.write(text.replace("\r\n", "\n"))
        except Exception as e:
            print(f"Источник пропущен: {url}")
        time.sleep(0.5)

    seen = load_seen()
    now = now_moscow()
    ttl_limit = now - timedelta(hours=TTL_HOURS)

    uniq = {}
    sni = []

    print("Очистка и дедупликация...")
    for fname in os.listdir(LOCAL_DIR):
        with open(os.path.join(LOCAL_DIR, fname), "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or not is_valid_proxy(line):
                    continue

                if line not in seen:
                    seen[line] = now.isoformat()

                if datetime.fromisoformat(seen[line]) < ttl_limit:
                    continue

                key = extract_key(line)
                if not key:
                    continue

                uniq[key] = line
                if any(d in line for d in SNI_DOMAINS):
                    sni.append(line)

    save_seen(seen)

    all_keys = list(uniq.values())
    print(f"Итого ключей: {len(all_keys)}")

    raw = "\n".join(all_keys)
    b64 = base64.b64encode(raw.encode()).decode()

    raw_path = os.path.join(SUBSCRIPTIONS_DIR, "all.txt")
    b64_path = os.path.join(SUBSCRIPTIONS_DIR, "all_base64.txt")

    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(raw)
    with open(b64_path, "w", encoding="utf-8") as f:
        f.write(b64)

    split_and_upload(raw_path, "subscriptions/all")
    split_and_upload(b64_path, "subscriptions/all_base64")

    if sni:
        sni_raw = "\n".join(dict.fromkeys(sni))
        sni_b64 = base64.b64encode(sni_raw.encode()).decode()
        upload_content(sni_raw, "subscriptions/sni_filtered.txt")
        upload_content(sni_b64, "subscriptions/sni_filtered_base64.txt")

    print("Готово.")

if __name__ == "__main__":
    main()











