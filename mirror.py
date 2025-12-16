#!/usr/bin/env python3
# mirror_with_sni.py
# Зеркалирование источников + SNI-фильтрация + сбор 26.txt
# Требует: requests, PyGithub
# ENV: MY_TOKEN (GitHub token)

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

if not GITHUB_TOKEN:
    raise SystemExit("MY_TOKEN not set")

g = Github(auth=Auth.Token(GITHUB_TOKEN))
repo = g.get_repo(REPO_NAME)

def now_moscow():
    return datetime.now(zoneinfo.ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M")

# -------------------- Core --------------------
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

def upload_file_if_changed(local_path: str, remote_path: str):
    with open(local_path, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        existing = repo.get_contents(remote_path)

        if existing.type != "file" or existing.encoding != "base64":
            repo.delete_file(
                remote_path,
                f"Cleanup invalid object {remote_path}",
                existing.sha,
            )
            raise GithubException(404, "recreate", None)

        remote_content = existing.decoded_content.decode("utf-8", errors="replace")
        if remote_content == content:
            print(f"{remote_path} — без изменений")
            return

        repo.update_file(
            remote_path,
            f"Update {remote_path} | {now_moscow()}",
            content,
            existing.sha,
        )
        print(f"{remote_path} обновлён")

    except GithubException as ge:
        if getattr(ge, "status", None) == 404:
            repo.create_file(
                remote_path,
                f"Add {remote_path} | {now_moscow()}",
                content,
            )
            print(f"{remote_path} создан")
        else:
            raise

def create_filtered_26():
    out = []
    for i in range(1, 26):
        p = os.path.join(LOCAL_DIR, f"{i}.txt")
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if any(d in line for d in SNI_DOMAINS):
                    out.append(line.strip())

    out = list(dict.fromkeys(out))
    p26 = os.path.join(LOCAL_DIR, "26.txt")
    with open(p26, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    return p26

def main():
    for i, url in enumerate(URLS, start=1):
        print(f"{i}. {url}")
        text = request_with_strategies(url)
        lp = os.path.join(LOCAL_DIR, f"{i}.txt")
        with open(lp, "w", encoding="utf-8") as f:
            f.write(text.replace("\r\n", "\n"))
        upload_file_if_changed(lp, f"{LOCAL_DIR}/{i}.txt")

    p26 = create_filtered_26()
    upload_file_if_changed(p26, f"{LOCAL_DIR}/26.txt")

if __name__ == "__main__":
    main()










