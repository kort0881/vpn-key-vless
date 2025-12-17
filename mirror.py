#!/usr/bin/env python3
# mirror_sync.py
# Синхронное зеркалирование источников + чистые подписки (TTL + TCP + SNI + anti-duplicate)
# ENV: MY_TOKEN

import os
import socket
import base64
import json
import time
import urllib.parse
import urllib3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from github import Github, Auth, GithubException, InputGitTreeElement
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
TCP_TIMEOUT = 2.0
REQUESTS_POOL = 10
RETRIES = 2
GITHUB_DELAY = 1.5
CHROME_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
             "AppleWebKit/537.36 (KHTML, like Gecko) "
             "Chrome/138.0.0.0 Safari/537.36")

os.makedirs(LOCAL_DIR, exist_ok=True)
os.makedirs(SUBSCRIPTIONS_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

# -------------------- GITHUB --------------------
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

def fetch_url(url):
    try:
        r = SESSION.get(url, timeout=12, verify=False)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"Ошибка {url}: {e}")
        return None

# -------------------- TTL STATE --------------------
def load_seen():
    if not os.path.exists(SEEN_FILE):
        return {}
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_seen(data):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------------------- PROXY UTILS --------------------
def is_valid_proxy(line):
    return line.startswith((
        "vless://","vmess://","trojan://","ss://",
        "hysteria://","hysteria2://","hy2://","tuic://"
    ))

def extract_host_port(line):
    try:
        u = urllib.parse.urlparse(line)
        return u.hostname, u.port, u.scheme
    except:
        return None, None, None

def tcp_alive(host, port, cache):
    key = f"{host}:{port}"
    if key in cache:
        return cache[key]
    try:
        with socket.create_connection((host, port), timeout=TCP_TIMEOUT):
            cache[key] = True
            return True
    except:
        cache[key] = False
        return False

# -------------------- UPLOAD --------------------
def upload_file(local_path, remote_path):
    with open(local_path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        time.sleep(GITHUB_DELAY)
        existing = repo.get_contents(remote_path)
        if existing.decoded_content.decode("utf-8") == content:
            return
        repo.update_file(remote_path,
                         f"Update {remote_path} | {now_moscow().strftime('%Y-%m-%d %H:%M')}",
                         content,
                         existing.sha)
        print(f"{remote_path} обновлён")
    except GithubException as ge:
        if getattr(ge, "status", None) == 404:
            repo.create_file(remote_path,
                             f"Add {remote_path} | {now_moscow().strftime('%Y-%m-%d %H:%M')}",
                             content)
            print(f"{remote_path} создан")
        else:
            print(f"Ошибка GitHub: {ge}")

# -------------------- MAIN LOGIC --------------------
def create_subscriptions():
    seen = load_seen()
    now = now_moscow()
    ttl_limit = now - timedelta(hours=TTL_HOURS)

    tcp_cache = {}
    all_keys = []
    ip_seen = set()

    for fname in os.listdir(LOCAL_DIR):
        path = os.path.join(LOCAL_DIR, fname)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or not is_valid_proxy(line):
                    continue

                if line not in seen:
                    seen[line] = now.isoformat()

                first_seen = datetime.fromisoformat(seen[line])
                if first_seen < ttl_limit:
                    continue

                host, port, scheme = extract_host_port(line)
                if not host or not port or not scheme:
                    continue

                key = (host, port, scheme)
                if key in ip_seen:
                    continue

                if not tcp_alive(host, port, tcp_cache):
                    continue

                ip_seen.add(key)
                all_keys.append(line)

    save_seen(seen)

    all_keys = list(dict.fromkeys(all_keys))
    print(f"Живых ключей после TCP: {len(all_keys)}")

    # RAW/base64
    raw_path = os.path.join(SUBSCRIPTIONS_DIR, "all.txt")
    b64_path = os.path.join(SUBSCRIPTIONS_DIR, "all_base64.txt")
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_keys))
    with open(b64_path, "w", encoding="utf-8") as f:
        f.write(base64.b64encode("\n".join(all_keys).encode()).decode())
    upload_file(raw_path, f"{SUBSCRIPTIONS_DIR}/all.txt")
    upload_file(b64_path, f"{SUBSCRIPTIONS_DIR}/all_base64.txt")

    # SNI filter
    sni_keys = [k for k in all_keys if any(d in k for d in SNI_DOMAINS)]
    if sni_keys:
        sni_raw = os.path.join(SUBSCRIPTIONS_DIR, "sni_filtered.txt")
        sni_b64 = os.path.join(SUBSCRIPTIONS_DIR, "sni_filtered_base64.txt")
        with open(sni_raw, "w", encoding="utf-8") as f:
            f.write("\n".join(sni_keys))
        with open(sni_b64, "w", encoding="utf-8") as f:
            f.write(base64.b64encode("\n".join(sni_keys).encode()).decode())
        upload_file(sni_raw, f"{SUBSCRIPTIONS_DIR}/sni_filtered.txt")
        upload_file(sni_b64, f"{SUBSCRIPTIONS_DIR}/sni_filtered_base64.txt")

def main():
    # Очистка локальной папки
    for d in [LOCAL_DIR, SUBSCRIPTIONS_DIR]:
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))

    # Скачивание источников
    for i, url in enumerate(URLS, start=1):
        print(f"{i}/{len(URLS)}: {url}")
        text = fetch_url(url)
        if text:
            path = os.path.join(LOCAL_DIR, f"{i}.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text.replace("\r\n","\n"))
            time.sleep(GITHUB_DELAY)

    create_subscriptions()

if __name__ == "__main__":
    main()













