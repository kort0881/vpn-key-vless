#!/usr/bin/env python3
# mirror_with_sni.py
# Скрипт: зеркалирование источников + попытки обхода (SNI / IP + Host) + сбор 26-го файла
# Требует: requests, PyGithub
# Задайте в окружении: MY_TOKEN (GitHub token с правами на репозиторий kort0881/vpn-key-vless)

import os
import socket
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

CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
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

    # ---- ДОБАВЛЕННЫЕ XRAY ИСТОЧНИКИ ----
    "https://raw.githubusercontent.com/NiREvil/vless/main/sub/SSTime",
    "https://raw.githubusercontent.com/ndsphonemy/proxy-sub/main/speed.txt",
    "https://raw.githubusercontent.com/Mahdi0024/ProxyCollector/master/sub/proxies.txt",
    "https://raw.githubusercontent.com/Mosifree/-FREE2CONFIG/refs/heads/main/Reality",
    "https://raw.githubusercontent.com/MrMohebi/xray-proxy-grabber-telegram/master/collected-proxies/row-url/all.txt",
]

SNI_DOMAINS = [
    "stats.vk-portal.net", "sun6-21.userapi.com", "avatars.mds.yandex.net",
    "queuev4.vk.com", "sync.browser.yandex.net", "top-fwz1.mail.ru",
    "online.sberbank.ru", "ozone.ru", "vk.com", "www.wildberries.ru",
    "yandex.ru", "www.ozon.ru", "ok.ru", "www.ivi.ru", "hh.ru",
]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def build_session():
    s = requests.Session()
    adapter = HTTPAdapter(
        pool_connections=REQUESTS_POOL,
        pool_maxsize=REQUESTS_POOL,
        max_retries=Retry(
            total=RETRIES,
            backoff_factor=0.4,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "HEAD"])
        )
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
    return datetime.now(zoneinfo.ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M")

def request_with_strategies(url: str) -> str:
    try:
        r = SESSION.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return r.text
    except Exception:
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname:
            ip = socket.gethostbyname(parsed.hostname)
            path = parsed.path or "/"
            if parsed.query:
                path += "?" + parsed.query
            r = SESSION.get(
                f"https://{ip}{path}",
                headers={"Host": parsed.hostname},
                timeout=TIMEOUT,
                verify=False
            )
            r.raise_for_status()
            return r.text
    raise Exception("All strategies failed")

def upload_file_if_changed(local_path, remote_path):
    with open(local_path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        existing = repo.get_contents(remote_path)
        if existing.decoded_content.decode("utf-8", errors="ignore") == content:
            return
        repo.update_file(remote_path, f"Update {remote_path} | {now_moscow()}",
                         content, existing.sha)
    except GithubException:
        repo.create_file(remote_path, f"Add {remote_path} | {now_moscow()}", content)

def create_filtered_26():
    collected = []
    for i in range(1, 26):
        path = os.path.join(LOCAL_DIR, f"{i}.txt")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                s = line.strip()
                if s and any(d in s for d in SNI_DOMAINS):
                    collected.append(s)
    out = os.path.join(LOCAL_DIR, "26.txt")
    with open(out, "w", encoding="utf-8") as f:
        for x in dict.fromkeys(collected):
            f.write(x + "\n")
    return out

def main():
    for i, url in enumerate(URLS, start=1):
        local = os.path.join(LOCAL_DIR, f"{i}.txt")
        with open(local, "w", encoding="utf-8") as f:
            f.write(request_with_strategies(url).replace("\r\n", "\n"))
        upload_file_if_changed(local, f"{LOCAL_DIR}/{i}.txt")

    path26 = create_filtered_26()
    upload_file_if_changed(path26, f"{LOCAL_DIR}/26.txt")

if __name__ == "__main__":
    main()










