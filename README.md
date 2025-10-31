from datetime import datetime

readme_path = "README.md"

# Данные файлов (можно расширять, новые файлы добавляются сюда)
files = [
    {"№": 26, "Файл": "26.txt", "Источник": "отфильтрованный SNI"},
    {"№": 4,  "Файл": "4.txt",  "Источник": "https://raw.githubusercontent.com/acymz/AutoVPN/refs/heads/main/data/V2.txt"},
    {"№": 5,  "Файл": "5.txt",  "Источник": "https://raw.githubusercontent.com/miladtahanian/V2RayCFGDumper/refs/heads/main/config.txt"},
    {"№": 6,  "Файл": "6.txt",  "Источник": "https://raw.githubusercontent.com/roosterkid/openproxylist/main/V2RAY_RAW.txt"},
]

vpn_posts = [
    {"№": 1, "Тип": "🟩 ВЛЕСС", "Дата": "2025-10-30 23:06", "Файл": "📄 vpn-files/all_posts.txt"},
    {"№": 1, "Тип": "🟩 ВЛЕСС", "Дата": "2025-10-30 16:13", "Файл": "📄 post_2025-10-30_13-13.txt"},
    {"№": 1, "Тип": "🟩 ВЛЕСС", "Дата": "2025-10-29 23:30", "Файл": "📄 post_2025-10-29_20-30.txt"},
    {"№": 1, "Тип": "🟩 ВЛЕСС", "Дата": "2025-10-28 19:00", "Файл": "📄 vpn-files/post_2025-10-28_19-00.txt"},
]

# Текущее время
now = datetime.now().strftime("%Y-%m-%d %H:%M (МСК)")

# Формируем текст README
content = f"ЧИТАЙТЕ\nP25-10-31 15:59 (МСК)

| № | Файл | Источник | Время |
|--|--|--|--|
| 26 | [`26.txt`](https://github.com/kort0881/vpn-key-vless/raw/refs/heads/main/githubmirror/26.txt) | filtered SNI | 2025-10-31 12:46 |
| 5 | [`5.txt`](https://github.com/kort0881/vpn-key-vless/raw/refs/heads/main/githubmirror/5.txt) | https://raw.githubusercontent.com/miladtahanian/V2RayCFGDumper/refs/heads/main/config.txt | 2025-10-31 12:46 |
| 7 | [`7.txt`](https://github.com/kort0881/vpn-key-vless/raw/refs/heads/main/githubmirror/7.txt) | https://github.com/Epodonios/v2ray-configs/raw/main/Splitted-By-Protocol/trojan.txt | 2025-10-31 12:46 |
| 25 | [`25.txt`](https://github.com/kort0881/vpn-key-vless/raw/refs/heads/main/githubmirror/25.txt) | https://raw.githubusercontent.com/V2RayRoot/V2RayConfig/refs/heads/main/Config/vless.txt | 2025-10-31 12:46 |

content += """
🔐 VPN-KEY-VLESS
Репозиторий автоматически собирает и сохраняет новые VPN-ключи — VLESS, VMESS, SS, Shadowsocks.
Ключи сохраняются в папке vpn-filesи githubmirror обновляются каждые 15 минут .
Дополнительно из Telegram-канала @vlesstrojan два раза в день добавляются по 10 выбранных ключей для быстрой проверки и доступа.

📋 Последние добавления
Открыть список
№	Тип	Дата	Файл
"""

for p in vpn_posts:
    content += f"{p['№']}\t{p['Тип']}\t{p['Дата']}\t{p['Файл']}\n"

# Перезаписываем README
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ README.md обновлён с актуальным временем и таблицами VPN-ключей.")


| № | Тип | Дата | Файл |
|:-:|:--|:--|:--|
| 1 | 🟩 VLESS | 2025-10-31 15:59 | [📄 vpn-files/all_posts.txt](vpn-files/all_posts.txt) |
| 1 | 🟩 VLESS | 2025-10-30 23:06 | [📄 vpn-files/all_posts.txt](vpn-files/all_posts.txt) |
| 1 | 🟩 VLESS | 2025-10-30 16:13 | [📄 post_2025-10-30_13-13.txt](post_2025-10-30_13-13.txt) |
| 1 | 🟩 VLESS | 2025-10-29 23:30 | [📄 post_2025-10-29_20-30.txt](post_2025-10-29_20-30.txt) |
| 1 | 🟩 VLESS | 2025-10-28 19:00 | [📄 vpn-files/post_2025-10-28_19-00.txt](vpn-files/post_2025-10-28_19-00.txt) |