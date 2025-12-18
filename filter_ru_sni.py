#!/usr/bin/env python3
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CLEAN_DIR = os.path.join(BASE_PATH, "githubmirror", "clean")
OUT_DIR = os.path.join(BASE_PATH, "githubmirror", "ru-sni")

RU_SNI_DOMAINS = [
    # соцсети
    "vk.com", "ok.ru",
    # поисковики и почта
    "yandex.ru", "ya.ru", "yastatic.net",
    "mail.ru", "bk.ru", "inbox.ru", "list.ru",
    # банки
    "sberbank.ru", "online.sberbank.ru",
    "vtb.ru", "tinkoff.ru", "gazprombank.ru",
    # маркетплейсы и сервисы
    "ozon.ru", "wildberries.ru", "avito.ru",
    "hh.ru", "gosuslugi.ru",
]

def has_ru_sni(line: str) -> bool:
    s = line.lower()
    return any(d in s for d in RU_SNI_DOMAINS)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    for fname in os.listdir(CLEAN_DIR):
        if not fname.endswith(".txt"):
            continue
        src_path = os.path.join(CLEAN_DIR, fname)
        dst_path = os.path.join(OUT_DIR, fname)

        ru_keys = []
        with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if has_ru_sni(line):
                    ru_keys.append(line)

        with open(dst_path, "w", encoding="utf-8") as f:
            f.write("\n".join(ru_keys))

        print(f"{fname}: RU-SNI {len(ru_keys)}")

    print("Готово, смотри githubmirror/ru-sni")

if __name__ == "__main__":
    main()

