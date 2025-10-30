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
from collections import defaultdict

# -------------------- Настройки --------------------
REPO_NAME = "kort0881/vpn-key-vless"
GITHUB_TOKEN = os.environ.get("MY_TOKEN")  # <- убедись, что это задано в secrets/ENV
LOCAL_DIR = "githubmirror"
os.makedirs(LOCAL_DIR, exist_ok=True)

# Таймауты и повторные попытки
TIMEOUT = 12
RETRIES = 2
REQUESTS_POOL = 10

# User-Agent
CHROME_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")

# -------------------- Источники (1..25) --------------------
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
    "https://raw.githubusercontent.com/STR97/STRUGOV/refs/heads/main/STR.BYPASS#STR.BYPASS%F0%9F%91%BE",
    "https://raw.githubusercontent.com/V2RayRoot/V2RayConfig/refs/heads/main/Config/vless.txt",
]

# Убедимся, что URLS длина 25
if len(URLS) < 25:
    raise SystemExit("ERROR: ожидается 25 источников в списке URLS")

# -------------------- SNI-домены для фильтра 26-го файла --------------------
SNI_DOMAINS = [
    "stats.vk-portal.net", "sun6-21.userapi.com", "avatars.mds.yandex.net",
    "queuev4.vk.com", "sync.browser.yandex.net", "top-fwz1.mail.ru",
    "online.sberbank.ru", "ozone.ru", "vk.com", "www.wildberries.ru",
    "yandex.ru", "www.ozon.ru", "ok.ru", "www.ivi.ru", "hh.ru",
    # можно добавлять ещё
]

# -------------------- HTTP session with retries --------------------
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

# -------------------- GitHub --------------------
if not GITHUB_TOKEN:
    raise SystemExit("ERROR: переменная окружения MY_TOKEN не задана (GitHub token)")

g = Github(auth=Auth.Token(GITHUB_TOKEN))
repo = g.get_repo(REPO_NAME)

# -------------------- Утилиты --------------------
def now_moscow():
    zone = zoneinfo.ZoneInfo("Europe/Moscow")
    return datetime.now(zone).strftime("%Y-%m-%d %H:%M")

def safe_filename(i: int):
    return f"{i}.txt"

def request_with_strategies(url: str) -> str:
    """
    Попробовать несколько стратегий:
    1) HTTPS normal
    2) HTTPS verify=False
    3) HTTP
    4) Resolve host -> IP, request to ip with Host header (попытка обхода SNI)
    Возвращает текст при успехе, иначе выбрасывает исключение.
    """
    # 1) https normal
    errors = []
    try:
        r = SESSION.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return r.text
    except Exception as e:
        errors.append(f"https normal: {e}")

    # 2) https verify=False
    try:
        r = SESSION.get(url, timeout=TIMEOUT, verify=False)
        r.raise_for_status()
        return r.text
    except Exception as e:
        errors.append(f"https verify=False: {e}")

    # 3) http (замена https->http)
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme == "https":
            url_http = parsed._replace(scheme="http").geturl()
            r = SESSION.get(url_http, timeout=TIMEOUT, verify=False)
            r.raise_for_status()
            return r.text
    except Exception as e:
        errors.append(f"http fallback: {e}")

    # 4) попытка запроса к IP с Host header
    try:
        parsed = urllib.parse.urlparse(url)
        host = parsed.hostname
        if host:
            try:
                ip = socket.gethostbyname(host)
            except Exception as e:
                raise Exception(f"DNS resolve failed: {e}")
            # соберём путь + query
            path = parsed.path or "/"
            if parsed.query:
                path += "?" + parsed.query
            # формируем URL по IP (http first)
            for scheme in ("https", "http"):
                try_url = f"{scheme}://{ip}{path}"
                headers = {"Host": host}
                r = SESSION.get(try_url, timeout=TIMEOUT, headers=headers, verify=False)
                r.raise_for_status()
                return r.text
            # если не удалось — упадёт ниже
    except Exception as e:
        errors.append(f"ip+host attempt: {e}")

    raise Exception("All strategies failed: " + " | ".join(errors))

def save_local(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def upload_file_if_changed(local_path: str, remote_path: str):
    """
    Загрузить файл в репо только если изменился контент.
    Обрабатывает создание и обновление, retry при конфликте SHA.
    """
    with open(local_path, "r", encoding="utf-8") as f:
        content = f.read()

    attempts = 5
    for attempt in range(1, attempts+1):
        try:
            try:
                existing = repo.get_contents(remote_path)
                remote_content = existing.decoded_content.decode("utf-8", errors="replace")
                if remote_content == content:
                    print(f"🔄 {remote_path} — без изменений, пропускаем")
                    return False
                # обновляем
                repo.update_file(remote_path, f"Update {remote_path} | {now_moscow()}", content, existing.sha)
                print(f"✅ {remote_path} обновлён (update)")
                return True
            except GithubException as ge:
                # если файл не найден — создаём
                status = getattr(ge, "status", None)
                if status == 404:
                    repo.create_file(remote_path, f"Add {remote_path} | {now_moscow()}", content)
                    print(f"✅ {remote_path} создан (create)")
                    return True
                else:
                    raise
        except GithubException as e_upd:
            # конфликт SHA или др. проблемы — retry
            if getattr(e_upd, "status", None) == 409 and attempt < attempts:
                wait = 0.5 * (2 ** (attempt - 1))
                print(f"⚠️ Конфликт при загрузке {remote_path}, попытка {attempt}/{attempts}, жду {wait}s")
                time.sleep(wait)
                continue
            else:
                print(f"❌ Ошибка GitHub при загрузке {remote_path}: {e_upd}")
                return False
        except Exception as e:
            print(f"❌ Непредвиденная ошибка при загрузке {remote_path}: {e}")
            return False
    return False

# -------------------- Основная логика --------------------
def create_filtered_26():
    """
    Читает локальные файлы 1..25, собирает строки, содержащие SNI_DOMAINS,
    убирает дубликаты (строка + host:port), записывает githubmirror/26.txt
    """
    collected = []
    for i in range(1, 26):
        p = os.path.join(LOCAL_DIR, f"{i}.txt")
        if not os.path.exists(p):
            continue
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    s = line.strip()
                    if not s: continue
                    # если в строке есть любой SNI домен — берем
                    if any(d in s for d in SNI_DOMAINS):
                        collected.append(s)
        except Exception as e:
            print(f"⚠️ Ошибка чтения {p}: {e}")

    # Удалим дубликаты: сначала полные совпадения
    unique_full = list(dict.fromkeys(collected))

    # Попробуем вытянуть host:port и отфильтровать дубликаты по host:port
    hostport_set = set()
    final = []
    hostport_re = re.compile(r'(?P<host>(?:\d{1,3}\.){3}\d{1,3}|[A-Za-z0-9\-\._]+):(?P<port>\d{2,5})')
    for line in unique_full:
        hp = None
        # Попробуем парсить URI
        try:
            if "vmess://" in line:
                # vmess base64 json
                payload = line.split("vmess://", 1)[1].strip()
                try:
                    decoded = base64.b64decode(payload + "=" * (-len(payload) % 4)).decode("utf-8", errors="ignore")
                    j = json.loads(decoded)
                    host = j.get("add") or j.get("host") or j.get("ip")
                    port = j.get("port")
                    if host and port:
                        hp = f"{host}:{port}"
                except Exception:
                    hp = None
        except Exception:
            pass

        if not hp:
            m = hostport_re.search(line)
            if m:
                hp = f"{m.group('host')}:{m.group('port')}"

        if hp:
            key = hp.lower()
            if key in hostport_set:
                continue
            hostport_set.add(key)

        final.append(line)

    out_path = os.path.join(LOCAL_DIR, "26.txt")
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            for ln in final:
                f.write(ln + "\n")
        print(f"📁 Создан {out_path} ({len(final)} строк после фильтрации)")
    except Exception as e:
        print(f"❌ Не удалось записать {out_path}: {e}")
    return out_path

def main():
    updated = []
    # скачиваем 1..25
    for i, url in enumerate(URLS, start=1):
        filename = safe_filename(i)
        local_path = os.path.join(LOCAL_DIR, filename)
        remote_path = f"{LOCAL_DIR}/{filename}"

        print(f"--- {i}. {url}")
        try:
            text = request_with_strategies(url)
            # нормализуем CRLF
            text = text.replace("\r\n", "\n")
            save_local(local_path, text)
            # загрузка в GitHub если изменилось
            changed = upload_file_if_changed(local_path, remote_path)
            if changed:
                updated.append((i, filename, url))
        except Exception as e:
            print(f"❌ Ошибка при скачивании {url}: {e}")

    # создаём 26-й файл с фильтром SNI и уникализацией
    path26 = create_filtered_26()
    # загружаем 26
    upload_file_if_changed(path26, f"{LOCAL_DIR}/26.txt")

    # обновляем README (простая логика: вставляем/заменяем таблицу с последними обновлёнными файлами)
    try:
        readme_path = "README.md"
        try:
            readme_file = repo.get_contents(readme_path)
            old_content = readme_file.decoded_content.decode("utf-8")
            sha = readme_file.sha
        except GithubException as ge:
            # если нет README
            old_content = ""
            sha = None

        # Формируем строку времени
        ts = now_moscow()
        header = f"🕓 Последнее обновление: {ts} (МСК)\n\n"
        # Соберём несколько строк таблицы (последние 10 файлов по updated)
        table_lines = ["| № | Файл | Источник | Время |", "|--|--|--|--|"]
        # берем последние 10 изменений (если нет — добавим 26)
        recent = updated[-10:] if updated else []
        # добавим 26 в начало, чтобы видно было
        recent = [(26, "26.txt", "filtered SNI")] + recent
        for idx, fname, src in recent:
            raw = f"https://github.com/{REPO_NAME}/raw/refs/heads/main/{LOCAL_DIR}/{fname}"
            table_lines.append(f"| {idx} | [`{fname}`]({raw}) | {src} | {ts} |")

        new_table = header + "\n".join(table_lines) + "\n\n"

        # Если README есть — заменим блок между маркерами (или просто добавим в начало)
        if old_content:
            # Попробуем заменить блок "🕓 Последнее обновление:" если есть
            if "🕓 Последнее обновление:" in old_content:
                new_content = re.sub(r"🕓 Последнее обновление:.*?(?:\n\n|$)", new_table, old_content, flags=re.S)
            else:
                new_content = new_table + old_content
        else:
            new_content = "# VPN-KEY-VLESS\n\n" + new_table

        # Запишем обратно
        if sha:
            repo.update_file(readme_path, f"Update README | {ts}", new_content, sha)
            print("📄 README.md обновлён (update)")
        else:
            repo.create_file(readme_path, f"Create README | {ts}", new_content)
            print("📄 README.md создан (create)")
    except Exception as e:
        print(f"⚠️ Ошибка при обновлении README: {e}")

if __name__ == "__main__":
    main()





