from datetime import datetime

readme_path = "README.md"

# Данные файлов
files = [
    {"№": 26, "Файл": "26.txt", "Источник": "отфильтрованный SNI"},
    {"№": 4, "Файл": "4.txt", "Источник": "https://raw.githubusercontent.com/acymz/AutoVPN/refs/heads/main/data/V2.txt"},
    {"№": 5, "Файл": "5.txt", "Источник": "https://raw.githubusercontent.com/miladtahanian/V2RayCFGDumper/refs/heads/main/config.txt"},
    {"№": 6, "Файл": "6.txt", "Источник": "https://raw.githubusercontent.com/roosterkid/openproxylist/main/V2RAY_RAW.txt"},
]

# Данные VPN-постов
vpn_posts = [
    {"№": 1, "Тип": "🟩 ВЛЕСС", "Дата": "2025-10-30 23:06", "Файл": "📄 vpn-files/all_posts.txt"},
    {"№": 1, "Тип": "🟩 ВЛЕСС", "Дата": "2025-10-30 16:13", "Файл": "📄 post_2025-10-30_13-13.txt"},
    {"№": 1, "Тип": "🟩 ВЛЕСС", "Дата": "2025-10-29 23:30", "Файл": "📄 post_2025-10-29_20-30.txt"},
    {"№": 1, "Тип": "🟩 ВЛЕСС", "Дата": "2025-10-28 19:00", "Файл": "📄 vpn-files/post_2025-10-28_19-00.txt"},
]

# Текущее время
now = datetime.now().strftime("%Y-%m-%d %H:%M (МСК)")

# Формируем контент README
content = f"""ЧИТАЙТЕ
🕓 Последнее обновление: {now}

№	Файл	Источник	Время
"""

for f in files:
    content += f"{f['№']}\t{f['Файл']}\t{f['Источник']}\t{now}\n"

content += """
🔐 VPN-KEY-VLESS
Репозиторий автоматически собирает и сохраняет новые VPN-ключи — VLESS, VMESS, SS, Shadowsocks.
Ключи сохраняются в папке vpn-files и githubmirror обновляются каждые 15 минут.
Дополнительно из Telegram-канала @vlesstrojan два раза в день добавляются по 10 выбранных ключей для быстрой проверки и доступа.

📋 Последние добавления
№	Тип	Дата	Файл
"""

for p in vpn_posts:
    content += f"{p['№']}\t{p['Тип']}\t{p['Дата']}\t{p['Файл']}\n"

# Сохраняем README
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ README.md обновлён.")
