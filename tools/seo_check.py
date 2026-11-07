# -*- coding: utf-8 -*-
"""Проверка внутренних ссылок и SEO-полей многостраничного макета."""
import json
import re
import sys
import urllib.request
from collections import deque

START = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8712/multi/"


def get(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return r.status, r.read().decode("utf-8", "replace")


def main():
    seen, queue = set(), deque([START])
    pages, errors, warnings = [], [], []

    while queue:
        url = queue.popleft().split("#")[0]
        if url in seen:
            continue
        seen.add(url)
        try:
            status, html = get(url)
        except Exception as exc:  # noqa
            errors.append(f"{url} → {exc}")
            continue
        if status != 200:
            errors.append(f"{url} → HTTP {status}")
            continue

        title = (re.search(r"<title>(.*?)</title>", html, re.S) or [None, ""])[1].strip()
        desc = (re.search(r'<meta name="description" content="(.*?)"', html) or [None, ""])[1]
        h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S)
        canonical = (re.search(r'<link rel="canonical" href="(.*?)"', html) or [None, ""])[1]
        robots = (re.search(r'<meta name="robots" content="(.*?)"', html) or [None, ""])[1]
        ld_blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)

        pages.append({"url": url, "title": title, "desc": desc,
                      "h1": len(h1), "canonical": canonical, "robots": robots})

        if len(h1) != 1:
            errors.append(f"{url}: H1 = {len(h1)}")
        if not title:
            errors.append(f"{url}: нет title")
        if len(title) > 75:
            warnings.append(f"{url}: title {len(title)} символов")
        if not desc:
            errors.append(f"{url}: нет description")
        if len(desc) > 180:
            warnings.append(f"{url}: description {len(desc)} символов")
        if not canonical:
            errors.append(f"{url}: нет canonical")
        if "noindex" not in robots and "noindex" not in url:
            if not canonical.startswith("https://"):
                errors.append(f"{url}: canonical не абсолютный")

        for block in ld_blocks:
            try:
                json.loads(block)
            except Exception as exc:  # noqa
                errors.append(f"{url}: JSON-LD ошибка — {exc}")

        for href in re.findall(r'<a [^>]*href="([^"]+)"', html):
            if href.startswith("/multi/"):
                absolute = "http://127.0.0.1:8712" + href
                if absolute not in seen:
                    queue.append(absolute)

    dup_titles = {}
    for p in pages:
        dup_titles.setdefault(p["title"], []).append(p["url"])

    print(f"Страниц проверено: {len(pages)}")
    for p in pages:
        print(f"  {p['url'].replace('http://127.0.0.1:8712', '')}"
              f" │ H1:{p['h1']} │ title:{len(p['title'])} │ desc:{len(p['desc'])}")
    print("\nПроблемы:", len(errors))
    for e in errors:
        print("  ✗", e)
    print("\nПредупреждения:", len(warnings))
    for w in warnings:
        print("  ·", w)
    dups = {t: u for t, u in dup_titles.items() if len(u) > 1}
    print("\nДубли title:", len(dups))
    for t, u in dups.items():
        print("  ", t, "→", u)


if __name__ == "__main__":
    main()
