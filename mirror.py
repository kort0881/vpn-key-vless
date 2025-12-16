#!/usr/bin/env python3
# mirror_with_sni.py
# Зеркалирование источников + создание компактных подписок
# Требует: requests, PyGithub
# ENV: MY_TOKEN (GitHub token)

import os
import socket
import base64
import urllib.parse
import urllib3
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from github import Github, Auth, GithubException, InputGitTreeElement
from datetime import datetime
import zoneinfo

# -------------------- Настройки --------------------
REPO_NAME = "kort0881/vpn-key-vless"
GITHUB_TOKEN = os.environ.get("MY_TOKEN")

LOCAL_DIR = "githubmirror"
SUBSCRIPTIONS_DIR = "subscriptions"
os.makedirs(LOCAL_DIR, exist_ok=True)
os.makedirs(SUBSCRIPTIONS_DIR, exist_ok=True)

TIMEOUT = 12
RETRIES = 2
REQUESTS_POOL = 10
GITHUB_DELAY = 1.5

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
        time.sleep(GITHUB_DELAY)
        existing = repo.get_contents(remote_path)

        if existing.type != "file" or existing.encoding != "base64":
            time.sleep(GITHUB_DELAY)
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

        time.sleep(GITHUB_DELAY)
        repo.update_file(
            remote_path,
            f"Update {remote_path} | {now_moscow()}",
            content,
            existing.sha,
        )
        print(f"{remote_path} обновлён")

    except GithubException as ge:
        if getattr(ge, "status", None) == 404:
            time.sleep(GITHUB_DELAY)
            repo.create_file(
                remote_path,
                f"Add {remote_path} | {now_moscow()}",
                content,
            )
            print(f"{remote_path} создан")
        else:
            raise

def upload_large_file_via_git(local_path: str, remote_path: str):
    """Загрузка больших файлов через Git API"""
    try:
        with open(local_path, "rb") as f:
            content = f.read()
        
        # Создаём blob
        time.sleep(GITHUB_DELAY)
        blob = repo.create_git_blob(content.decode('utf-8'), 'utf-8')
        
        # Получаем текущий коммит main
        time.sleep(GITHUB_DELAY)
        ref = repo.get_git_ref('heads/main')
        commit = repo.get_git_commit(ref.object.sha)
        
        # Создаём tree element
        element = InputGitTreeElement(
            path=remote_path,
            mode='100644',
            type='blob',
            sha=blob.sha
        )
        
        # Создаём новый tree
        time.sleep(GITHUB_DELAY)
        base_tree = repo.get_git_tree(commit.tree.sha)
        new_tree = repo.create_git_tree([element], base_tree)
        
        # Создаём коммит
        time.sleep(GITHUB_DELAY)
        new_commit = repo.create_git_commit(
            f"Update {remote_path} | {now_moscow()}",
            new_tree,
            [commit]
        )
        
        # Обновляем референс
        time.sleep(GITHUB_DELAY)
        ref.edit(new_commit.sha)
        
        print(f"{remote_path} загружен через Git API")
    except Exception as e:
        print(f"Ошибка загрузки {remote_path}: {e}")

def is_valid_proxy(line: str) -> bool:
    """Проверка, является ли строка валидным прокси-ключом"""
    protocols = ['vless://', 'vmess://', 'trojan://', 'ss://', 
                 'hysteria://', 'hysteria2://', 'hy2://', 'tuic://']
    return any(line.startswith(p) for p in protocols)

def create_filtered_file():
    """Создаёт файл с SNI-фильтрацией"""
    total = len(URLS)
    out = []
    
    for i in range(1, total + 1):
        p = os.path.join(LOCAL_DIR, f"{i}.txt")
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if any(d in line for d in SNI_DOMAINS):
                    out.append(line.strip())

    out = list(dict.fromkeys(out))
    final_file = os.path.join(LOCAL_DIR, f"{total + 1}.txt")
    with open(final_file, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    return final_file

def create_subscriptions():
    """Создаёт ТОЛЬКО 4 основных файла подписок"""
    print("\n" + "="*60)
    print("Создание подписок...")
    
    all_keys = []
    
    # Собираем все ключи
    total = len(URLS)
    for i in range(1, total + 1):
        p = os.path.join(LOCAL_DIR, f"{i}.txt")
        if not os.path.exists(p):
            continue
            
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or not is_valid_proxy(line):
                    continue
                all_keys.append(line)
    
    # Удаляем дубликаты
    all_keys = list(dict.fromkeys(all_keys))
    print(f"Всего уникальных ключей: {len(all_keys)}")
    
    # Создаём ТОЛЬКО 4 файла
    subscriptions = []
    
    # 1. Все ключи (raw) - через Git API
    all_raw = os.path.join(SUBSCRIPTIONS_DIR, "all.txt")
    with open(all_raw, "w", encoding="utf-8") as f:
        f.write("\n".join(all_keys))
    subscriptions.append(("all.txt", len(all_keys), True))
    
    # 2. Все ключи (base64) - через Git API
    all_b64 = os.path.join(SUBSCRIPTIONS_DIR, "all_base64.txt")
    with open(all_b64, "w", encoding="utf-8") as f:
        content = "\n".join(all_keys)
        encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        f.write(encoded)
    subscriptions.append(("all_base64.txt", len(all_keys), True))
    
    # 3. SNI-фильтрованные
    sni_file = os.path.join(LOCAL_DIR, f"{total + 1}.txt")
    if os.path.exists(sni_file):
        with open(sni_file, "r", encoding="utf-8") as f:
            sni_keys = [line.strip() for line in f if line.strip() and is_valid_proxy(line.strip())]
        
        if sni_keys:
            # SNI raw
            sni_raw = os.path.join(SUBSCRIPTIONS_DIR, "sni_filtered.txt")
            with open(sni_raw, "w", encoding="utf-8") as f:
                f.write("\n".join(sni_keys))
            subscriptions.append(("sni_filtered.txt", len(sni_keys), False))
            
            # SNI base64
            sni_b64 = os.path.join(SUBSCRIPTIONS_DIR, "sni_filtered_base64.txt")
            with open(sni_b64, "w", encoding="utf-8") as f:
                content = "\n".join(sni_keys)
                encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
                f.write(encoded)
            subscriptions.append(("sni_filtered_base64.txt", len(sni_keys), False))
    
    # Загружаем на GitHub
    print("\nЗагрузка подписок на GitHub...")
    for filename, count, use_git_api in subscriptions:
        try:
            local_path = os.path.join(SUBSCRIPTIONS_DIR, filename)
            remote_path = f"{SUBSCRIPTIONS_DIR}/{filename}"
            
            if use_git_api:
                upload_large_file_via_git(local_path, remote_path)
            else:
                upload_file_if_changed(local_path, remote_path)
                
        except Exception as e:
            print(f"Ошибка загрузки {filename}: {e}")
    
    # Выводим итоговую информацию
    print("\n" + "="*60)
    print("✅ Подписки созданы!")
    print("="*60)
    print("\nСтатистика:")
    for filename, count, _ in subscriptions:
        print(f"  {filename}: {count} ключей")
    
    print(f"\n📌 Ссылки на подписки:")
    for filename, _, _ in subscriptions:
        print(f"https://raw.githubusercontent.com/{REPO_NAME}/main/{SUBSCRIPTIONS_DIR}/{filename}")
    print("="*60 + "\n")

def main():
    # Скачиваем и зеркалируем источники
    for i, url in enumerate(URLS, start=1):
        print(f"{i}/{len(URLS)}. {url}")
        try:
            text = request_with_strategies(url)
            lp = os.path.join(LOCAL_DIR, f"{i}.txt")
            with open(lp, "w", encoding="utf-8") as f:
                f.write(text.replace("\r\n", "\n"))
            upload_file_if_changed(lp, f"{LOCAL_DIR}/{i}.txt")
        except Exception as e:
            print(f"Ошибка: {e}")

    # Создаём SNI-фильтрованный файл
    final = create_filtered_file()
    final_name = os.path.basename(final)
    upload_file_if_changed(final, f"{LOCAL_DIR}/{final_name}")
    
    # Создаём подписки
    create_subscriptions()

if __name__ == "__main__":
    main()













