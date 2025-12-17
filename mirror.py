#!/usr/bin/env python3
# mirror_clean_arch.py
# Правильный агрегатор: raw → normalized → filtered → subscriptions

import os
import socket
import base64
import urllib.parse
import urllib3
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from github import Github, Auth, GithubException
from datetime import datetime
import zoneinfo

# ================== CONFIG ==================
REPO_NAME = "kort0881/vpn-key-vless"
GITHUB_TOKEN = os.environ.get("MY_TOKEN")

BASE_DIR = "data"
RAW_DIR = f"{BASE_DIR}/raw"
NORM_DIR = f"{BASE_DIR}/normalized"
FILTER_DIR = f"{BASE_DIR}/filtered"
SUB_DIR = f"{BASE_DIR}/subscriptions"

for d in (RAW_DIR, NORM_DIR, FILTER_DIR, SUB_DIR):
    os.makedirs(d, exist_ok=True)

TIMEOUT = 12
RETRIES = 2
POOL = 10
DELAY = 1.2

URLS = [
    # твой список источников — без изменений
]

SNI_DOMAINS = [
    "vk.com", "yandex.ru", "ozon.ru", "wildberries.ru",
    "sberbank.ru", "mail.ru", "ivi.ru", "hh.ru",
]

BLACKLIST = [
    "example.com", "localhost", "127.0.0.1", "@test"
]

PROTOCOLS = (
    "vless://", "vmess://", "trojan://", "ss://",
    "hysteria://", "hysteria2://", "hy2://", "tuic://"
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================== HTTP ==================
def build_session():
    s = requests.Session()
    s.mount("https://", HTTPAdapter(
        pool_connections=POOL,
        pool_maxsize=POOL,
        max_retries=Retry(total=RETRIES, backoff_factor=0.4)
    ))
    s.headers["User-Agent"] = "Mozilla/5.0"
    return s

SESSION = build_session()

g = Github(auth=Auth.Token(GITHUB_TOKEN))
repo = g.get_repo(REPO_NAME)

def now():
    return datetime.now(zoneinfo.ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M")

# ================== CORE ==================
def fetch(url: str) -> str:
    try:
        r = SESSION.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return r.text
    except Exception:
        parsed = urllib.parse.urlparse(url)
        ip = socket.gethostbyname(parsed.hostname)
        return SESSION.get(
            f"https://{ip}{parsed.path}",
            headers={"Host": parsed.hostname},
            verify=False,
            timeout=TIMEOUT
        ).text

def is_proxy(line: str) -> bool:
    return line.startswith(PROTOCOLS)

def normalize(text: str):
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if not is_proxy(line):
            continue
        if any(b in line.lower() for b in BLACKLIST):
            continue
        yield line

def fingerprint(uri: str) -> str:
    p = urllib.parse.urlparse(uri)
    return f"{p.scheme}:{p.netloc}:{p.path}"

def upload(local, remote):
    with open(local, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        old = repo.get_contents(remote)
        if old.decoded_content.decode() == content:
            return
        repo.update_file(remote, f"Update {remote} | {now()}", content, old.sha)
    except GithubException:
        repo.create_file(remote, f"Add {remote} | {now()}", content)

# ================== PIPELINE ==================
def main():
    seen = set()
    buckets = {
        "vless": [],
        "vmess": [],
        "trojan": [],
        "ss": []
    }

    # -------- RAW + NORMALIZE --------
    for i, url in enumerate(URLS, 1):
        name = f"{i:03}.txt"
        raw_path = f"{RAW_DIR}/{name}"

        print(f"[{i}/{len(URLS)}] {url}")
        text = fetch(url)

        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(text)

        upload(raw_path, f"{RAW_DIR}/{name}")

        for line in normalize(text):
            fp = fingerprint(line)
            if fp in seen:
                continue
            seen.add(fp)

            if line.startswith("vless://"):
                buckets["vless"].append(line)
            elif line.startswith("vmess://"):
                buckets["vmess"].append(line)
            elif line.startswith("trojan://"):
                buckets["trojan"].append(line)
            elif line.startswith("ss://"):
                buckets["ss"].append(line)

    # -------- NORMALIZED --------
    for k, v in buckets.items():
        path = f"{NORM_DIR}/{k}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(v))
        upload(path, f"{NORM_DIR}/{k}.txt")

    # -------- FILTERED (SNI) --------
    sni = [
        x for x in buckets["vless"]
        if any(d in x for d in SNI_DOMAINS)
    ]

    sni_path = f"{FILTER_DIR}/sni_ru.txt"
    with open(sni_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sni))
    upload(sni_path, f"{FILTER_DIR}/sni_ru.txt")

    # -------- SUBSCRIPTIONS --------
    all_keys = []
    for v in buckets.values():
        all_keys.extend(v)

    all_path = f"{SUB_DIR}/all.txt"
    with open(all_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_keys))
    upload(all_path, f"{SUB_DIR}/all.txt")

    all_b64 = base64.b64encode("\n".join(all_keys).encode()).decode()
    b64_path = f"{SUB_DIR}/all_base64.txt"
    with open(b64_path, "w", encoding="utf-8") as f:
        f.write(all_b64)
    upload(b64_path, f"{SUB_DIR}/all_base64.txt")

    print("✅ Готово. Архитектура чистая.")

if __name__ == "__main__":
    main()














