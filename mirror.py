#!/usr/bin/env python3
# mirror_with_sni.py
# Скрипт: зеркалирование источников + попытки обхода (SNI / IP + Host) + сбор 26-го файла
# Требует: requests, PyGithub
# Задайте в окружении: MY_TOKEN (GitHub token с правами на репозиторий kort0881/vpn-key-vless)

import os
import re
import time
import socket
import base64
import json
import urllib.parse
import urllib3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from github import Github, Auth, GithubException
from datetime import datetime
import zoneinfo

# -------------------- Настройки --------------------
REPO_NAME = "kort0881/vpn-key-vless"
GITHUB_TOKEN = os.environ.get("MY_TOKEN")
LOCAL_DIR = "githubmirror"
os.makedirs(LOCAL_DIR, exist_ok=True)

TIMEOUT = 12
RETRIES = 2
REQUESTS_POOL = 10

CHROME_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")

URLS = [
    # уже существующие ссылки
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

    # новые ссылки (добавлены)
    "https://raw.githubusercontent.com/lagzian/SS-Collector/main/mix_clash.yaml",
    "https://raw.githubusercontent.com/Argh94/V2RayAutoConfig/refs/heads/main/configs/Vless.txt",
    "https://raw.githubusercontent.com/Argh94/V2RayAutoConfig/refs/heads/main/configs/Hysteria2.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_list.json"
]

SNI_DOMAINS = [
    "stats.vk-portal.net", "sun6-21.userapi.com", "avatars.mds.yandex.net",
    "queuev4.vk.com", "sync.browser.yandex.net", "top-fwz1.mail.ru",
    "online.sberbank.ru", "ozone.ru", "vk.com", "www.wildberries.ru",
    "yandex.ru", "www.ozon.ru", "ok.ru", "www.ivi.ru", "hh.ru",
]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def build_session(max_pool_size=REQUESTS_POOL):
    s = requests.Session()
    adapter = HTTPAdapter(
        pool_connections=max_pool_size,
        pool_maxsize=max_pool_size,
        max_retries=Retry(total=RETRIES, backoff_factor=0.4,
                          status_forcelist=(429, 500, 502, 503, 504),
                          allowed_methods=frozenset(["GET", "HEAD"]))
    )
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({"User-Agent": CHROME_UA})
    return s

SESSION = build_session()

if not GITHUB_TOKEN:
    raise SystemExit("ERROR: переменная окружения MY_TOKEN не задана")

g = Github(auth=Auth.Token(GITHUB_TOKEN))
repo = g.get_repo(REPO_NAME)

def now_moscow():
    zone = zoneinfo.ZoneInfo("Europe/Moscow")
    return datetime.now(zone).strftime("%Y-%m-%d %H:%M")

def safe_filename(i: int):
    return f"{i}.txt"

def request_with_strategies(url: str) -> str:
    errors = []
    try:
        r = SESSION.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return r.text
    except Exception as e:
        errors.append(f"https normal: {e}")
    try:
        r = SESSION.get(url, timeout=TIMEOUT, verify=False)
        r.raise_for_status()
        return r.text
    except Exception as e:
        errors.append(f"https verify=False: {e}")
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme == "https":
            url_http = parsed._replace(scheme="http").geturl()
            r = SESSION.get(url_http, timeout=TIMEOUT, verify=False)
            r.raise_for_status()
            return r.text
    except Exception as e:
        errors.append(f"http fallback: {e}")
    try:
        parsed = urllib.parse.urlparse(url)
        host = parsed.hostname
        if host:
            ip = socket.gethostbyname(host)
            path = parsed.path or "/"
            if parsed.query:
                path += "?" + parsed.query
            for scheme in ("https", "http"):
                try_url = f"{scheme}://{ip}{path}"
                headers = {"Host": host}
                r = SESSION.get(try_url, timeout=TIMEOUT, headers=headers, verify=False)
                r.raise_for_status()
                return r.text
    except Exception as e:
        errors.append(f"ip+host attempt: {e}")
    raise Exception("All strategies failed: " + " | ".join(errors))

def save_local(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def upload_file_if_changed(local_path: str, remote_path: str):
    with open(local_path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        existing = repo.get_contents(remote_path)
        remote_content = existing.decoded_content.decode("utf-8", errors="replace")
        if remote_content == content:
            print(f"🔄 {remote_path} — без изменений, пропускаем")
            return False
        repo.update_file(remote_path, f"Update {remote_path} | {now_moscow()}", content, existing.sha)
        print(f"✅ {remote_path} обновлён (update)")
        return True
    except GithubException as ge:
        if getattr(ge, "status", None) == 404:
            repo.create_file(remote_path, f"Add {remote_path} | {now_moscow()}", content)
            print(f"✅ {remote_path} создан (create)")
            return True
        print(f"❌ Ошибка GitHub: {ge}")
        return False

def create_filtered_26():
    collected = []
    for i in range(1, 26):
        p = os.path.join(LOCAL_DIR, f"{i}.txt")
        if not os.path.exists(p):
            continue
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    s = line.strip()
                    if s and any(d in s for d in SNI_DOMAINS):
                        collected.append(s)
        except Exception as e:
            print(f"⚠️ Ошибка чтения {p}: {e}")
    unique_full = list(dict.fromkeys(collected))
    out_path = os.path.join(LOCAL_DIR, "26.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        for ln in unique_full:
            f.write(ln + "\n")
    print(f"📁 Создан {out_path} ({len(unique_full)} строк)")
    return out_path

def main():
    for i, url in enumerate(URLS, start=1):
        filename = safe_filename(i)
        local_path = os.path.join(LOCAL_DIR, filename)
        remote_path = f"{LOCAL_DIR}/{filename}"
        print(f"--- {i}. {url}")
        try:
            text = request_with_strategies(url)
            text = text.replace("\r\n", "\n")
            save_local(local_path, text)
            upload_file_if_changed(local_path, remote_path)
        except Exception as e:
            print(f"❌ Ошибка при скачивании {url}: {e}")

    path26 = create_filtered_26()
    upload_file_if_changed(path26, f"{LOCAL_DIR}/26.txt")

if __name__ == "__main__":
    main()







