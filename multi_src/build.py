# -*- coding: utf-8 -*-
"""Генератор многостраничного SEO-варианта сайта «АэроТех 74»."""
import json
import os
import re
import shutil
from datetime import date
from content import (SITE, BASE, COMPANY, NAV, ORDER, SERVICES, PROJECTS,
                     REVIEWS, POSTS, BLOG_TOPICS)

# Переопределение домена и префикса через переменные окружения:
#   SITE=https://aerotech74.ru BASE= python3 multi_src/build.py
SITE = (os.environ.get("SITE") or SITE).rstrip("/")
BASE = os.environ.get("BASE", BASE).rstrip("/")
# NOINDEX=1 — тестовая площадка закрыта от индексации до переезда на домен
NOINDEX = os.environ.get("NOINDEX") == "1"

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, "..", "multi"))
SRC = os.path.abspath(os.path.join(ROOT, ".."))
TODAY = date(2026, 11, 7).isoformat()

ICONS = {
    "proektirovanie": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 26V9a3 3 0 013-3h14a3 3 0 013 3v17"/><path d="M4 26h24"/><path d="M11 12h10M11 17h10M11 22h5"/></svg>',
    "montazh": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M8 6v8a8 8 0 008 8h8"/><path d="M24 18l-4 4 4 4"/><circle cx="8" cy="24" r="3"/><path d="M17 6h9"/></svg>',
    "oborudovanie": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="6" width="24" height="12" rx="2"/><path d="M8 12h6M8 15h10"/><path d="M9 22v4M23 22v4M6 26h20"/><path d="M17 18v4"/></svg>',
    "servis": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M16 5v3M16 24v3M6.5 16h3M22.5 16h3M9.5 9.5l2 2M20.5 20.5l2 2M22.5 9.5l-2 2M11.5 20.5l-2 2"/><circle cx="16" cy="16" r="6"/><path d="M14 16l1.6 1.6L18.5 14"/></svg>',
    "rekonstrukciya": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M26 12a10 10 0 10-2.2 12"/><path d="M26 6v6h-6"/><path d="M16 11v5l4 2.5"/></svg>',
    "avtomatika": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="5" width="18" height="22" rx="2"/><path d="M12 11h8M12 15h8M12 19h4"/><path d="M4 26h24"/></svg>',
}

LOGO = ('<span class="logo__mark" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none">'
        '<path d="M16 4v24M4 16h24M7.5 7.5l17 17M24.5 7.5l-17 17" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>'
        '<circle cx="16" cy="16" r="4.6" fill="currentColor"/></svg></span>'
        '<span class="logo__text"><strong>АэроТех<span>74</span></strong><em>вентиляция · кондиционирование</em></span>')

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='8' fill='%2307182a'/%3E"
           "%3Cpath d='M16 6v20M6 16h20M9 9l14 14M23 9L9 23' stroke='%236fe3f4' stroke-width='2.4' stroke-linecap='round'/%3E"
           "%3Ccircle cx='16' cy='16' r='4' fill='%236fe3f4'/%3E%3C/svg%3E")


def href(path):
    return BASE + path


def canon(path):
    return SITE + path


NBSP = "\u00a0"
PREPS = ("в", "на", "с", "к", "от", "до", "по", "за", "из", "у", "о", "об",
         "для", "при", "без", "над", "под")


def typo(text):
    """Не оставляем предлоги в конце строки."""
    pattern = r"\s(" + "|".join(PREPS) + r")\s"
    return re.sub(pattern, lambda m: " " + m.group(1) + NBSP, text)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


# ------------------------------------------------------------------ layout
def head(title, desc, path, extra_json=None, og_type="website", noindex=False):
    robots = ("noindex, nofollow" if (noindex or NOINDEX)
              else "index, follow, max-image-preview:large")
    url = canon(path)
    graph = [ORG_NODE]
    if extra_json:
        graph.extend(extra_json)
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph},
                    ensure_ascii=False, indent=1)
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="АэроТех 74">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="theme-color" content="#07182a">
<link rel="icon" type="image/svg+xml" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{href('/assets/style.css')}">
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
<a class="skip-link" href="#main">Перейти к содержанию</a>
"""


ORG_NODE = {
    "@type": "HVACBusiness",
    "@id": SITE + "/#organization",
    "name": "АэроТех 74",
    "alternateName": "АэроТех74",
    "url": SITE + "/",
    "telephone": "+7-351-200-00-00",
    "email": COMPANY["email"],
    "priceRange": "₽₽",
    "description": "Проектирование, монтаж и сервисное обслуживание систем вентиляции и кондиционирования в Челябинске и области.",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "ул. Труда, 84, офис 312",
        "addressLocality": "Челябинск",
        "addressRegion": "Челябинская область",
        "postalCode": "454091",
        "addressCountry": "RU",
    },
    "geo": {"@type": "GeoCoordinates", "latitude": 55.1600, "longitude": 61.4025},
    "areaServed": [
        {"@type": "City", "name": "Челябинск"},
        {"@type": "AdministrativeArea", "name": "Челябинская область"},
    ],
    "openingHoursSpecification": {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "opens": "08:00",
        "closes": "20:00",
    },
    "foundingDate": "2012",
    "sameAs": [],
}


def breadcrumb_node(crumbs):
    items = []
    for i, (name, path) in enumerate(crumbs):
        node = {"@type": "ListItem", "position": i + 1, "name": name}
        if path is not None:
            node["item"] = canon(path)
        items.append(node)
    return {"@type": "BreadcrumbList", "itemListElement": items}


def faq_node(items):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in items
        ],
    }


def header(active):
    links = []
    for label, path, key in NAV:
        cls = ' class="is-active" aria-current="page"' if key == active else ""
        if key == "uslugi":
            sub = "".join(
                f'<a href="{href("/uslugi/" + s + "/")}">{SERVICES[s]["nav"]}</a>'
                for s in ORDER
            )
            links.append(f'<div class="nav__item"><a href="{href(path)}"{cls}>{label}</a>'
                         f'<div class="nav__sub">{sub}</div></div>')
        else:
            links.append(f'<a href="{href(path)}"{cls}>{label}</a>')

    return f"""<header class="header" id="header">
  <div class="container header__in">
    <a href="{href('/')}" class="logo" aria-label="АэроТех 74 — на главную">{LOGO}</a>
    <nav class="nav" id="nav" aria-label="Основная навигация">
      {''.join(links)}
    </nav>
    <div class="header__side">
      <div class="header__phone">
        <a href="tel:{COMPANY['phone_href']}">{COMPANY['phone']}</a>
        <span>{COMPANY['hours']}</span>
      </div>
      <a href="{href('/kontakty/')}" class="btn btn--primary btn--sm">Заказать расчёт</a>
      <button class="burger" id="burger" aria-label="Меню" aria-expanded="false" aria-controls="nav">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>
"""


def footer():
    services = "".join(
        f'<a href="{href("/uslugi/" + s + "/")}">{SERVICES[s]["nav"]}</a>' for s in ORDER
    )
    return f"""<footer class="footer">
  <div class="container footer__in">
    <div class="footer__brand">
      <a href="{href('/')}" class="logo logo--footer">{LOGO}</a>
      <p>Проектирование, монтаж и сервис систем вентиляции и кондиционирования в Челябинске и Челябинской области с 2012 года.</p>
      <div class="footer__contacts">
        <a href="tel:{COMPANY['phone_href']}">{COMPANY['phone']}</a>
        <a href="mailto:{COMPANY['email']}">{COMPANY['email']}</a>
      </div>
      <address class="footer__address">{COMPANY['address']}<br>{COMPANY['hours']}</address>
    </div>

    <div class="footer__col">
      <h4>Услуги</h4>
      {services}
    </div>

    <div class="footer__col">
      <h4>Компания</h4>
      <a href="{href('/o-kompanii/')}">О нас</a>
      <a href="{href('/proekty/')}">Выполненные работы</a>
      <a href="{href('/tseny/')}">Цены</a>
      <a href="{href('/blog/')}">Блог</a>
      <a href="{href('/kontakty/')}">Контакты</a>
    </div>

    <div class="footer__col footer__col--cta">
      <h4>Нужен расчёт?</h4>
      <p>Оставьте номер — перезвоним, уточним задачу и назовём вилку стоимости.</p>
      <a href="{href('/kontakty/#zayavka')}" class="btn btn--primary btn--sm">Оставить заявку</a>
    </div>
  </div>

  <div class="container footer__bottom">
    <span>© 2012–2026 {COMPANY['legal']}. ИНН {COMPANY['inn']}. Все права защищены.</span>
    <div>
      <a href="{href('/politika-konfidencialnosti/')}">Политика конфиденциальности</a>
      <a href="{href('/kontakty/')}">Контакты</a>
      <a href="#top">Наверх ↑</a>
    </div>
  </div>
</footer>
<script src="{href('/assets/app.js')}"></script>
</body>
</html>
"""


def crumbs_html(crumbs):
    items = []
    for i, (name, path) in enumerate(crumbs):
        if path is None:
            items.append(f'<li aria-current="page">{esc(name)}</li>')
        else:
            items.append(f'<li><a href="{href(path)}">{esc(name)}</a></li>')
    return f'<nav class="breadcrumbs" aria-label="Хлебные крошки"><ol>{"".join(items)}</ol></nav>'


def page_hero(crumbs, h1, lead, chips=(), buttons=""):
    chip_html = ""
    if chips:
        chip_html = '<ul class="hero-chips">' + "".join(
            f"<li>{esc(c)}</li>" for c in chips) + "</ul>"
    return f"""<section class="page-hero">
  <div class="container">
    {crumbs_html(crumbs)}
    <h1>{esc(typo(h1))}</h1>
    <p class="page-hero__lead">{esc(typo(lead))}</p>
    {chip_html}
    {buttons}
  </div>
</section>
"""


def sidebar(active_slug=None):
    items = []
    for s in ORDER:
        d = SERVICES[s]
        cls = ' class="is-active" aria-current="page"' if s == active_slug else ""
        items.append(f'<li><a href="{href("/uslugi/" + s + "/")}"{cls}>{d["nav"]}</a></li>')
    return f"""<aside class="side">
  <nav class="side-card" aria-label="Услуги">
    <p class="side-card__title">Услуги</p>
    <ul class="side-nav">{''.join(items)}</ul>
  </nav>

  <div class="side-card side-card--cta">
    <strong>Нужен расчёт?</strong>
    <p>Выезд инженера и замер — бесплатно. Смета с фиксацией цены в договоре.</p>
    <a href="tel:{COMPANY['phone_href']}" class="btn btn--primary btn--block btn--sm">{COMPANY['phone']}</a>
    <a href="{href('/kontakty/#zayavka')}" class="side-link">Оставить заявку →</a>
  </div>

  <div class="side-card">
    <p class="side-card__title">Контакты</p>
    <p class="side-contact"><a href="tel:{COMPANY['phone_href']}">{COMPANY['phone']}</a><br>
    <a href="mailto:{COMPANY['email']}">{COMPANY['email']}</a></p>
    <p class="side-contact">{COMPANY['address']}<br>{COMPANY['hours']}</p>
  </div>
</aside>"""


def service_card(slug, idx):
    d = SERVICES[slug]
    return f"""<article class="service">
  <div class="service__top">
    <span class="service__ico">{ICONS[slug]}</span>
    <span class="service__num">{idx:02d}</span>
  </div>
  <h3><a href="{href('/uslugi/' + slug + '/')}">{d['nav']}</a></h3>
  <p>{d['card_desc']}</p>
  <a href="{href('/uslugi/' + slug + '/')}" class="service__link">Подробнее <span>→</span></a>
</article>"""


def services_grid():
    return '<div class="services">' + "".join(
        service_card(s, i + 1) for i, s in enumerate(ORDER)) + "</div>"


def price_table(rows, head=("Работа", "Стоимость")):
    body = "".join(
        f"<tr><td>{esc(n)}</td><td>{esc(p)}</td></tr>" for n, p in rows)
    return (f'<table class="price-table"><thead><tr><th>{head[0]}</th>'
            f'<th>{head[1]}</th></tr></thead><tbody>{body}</tbody></table>')


def faq_block(items, title="Частые вопросы"):
    body = "".join(
        f'<details class="faq__item"{" open" if i == 0 else ""}>'
        f"<summary>{esc(q)}</summary><p>{esc(a)}</p></details>"
        for i, (q, a) in enumerate(items))
    return f'<section class="faq-section"><h2>{title}</h2><div class="faq">{body}</div></section>'


def cta_band(title="Рассчитаем стоимость вашей системы",
             text="Оставьте заявку — инженер перезвонит в течение 15 минут, уточнит задачу и назовёт вилку стоимости."):
    return f"""<section class="cta-band">
  <div class="container cta-band__in">
    <div>
      <h2>{esc(title)}</h2>
      <p>{esc(text)}</p>
    </div>
    <div class="cta-band__actions">
      <a href="tel:{COMPANY['phone_href']}" class="btn btn--primary btn--lg">{COMPANY['phone']}</a>
      <a href="{href('/kontakty/#zayavka')}" class="btn btn--ghost btn--lg">Оставить заявку</a>
    </div>
  </div>
</section>
"""


def related_block(slugs):
    cards = "".join(
        f"""<a class="related-card" href="{href('/uslugi/' + s + '/')}">
  <span class="related-card__ico">{ICONS[s]}</span>
  <span><strong>{SERVICES[s]['nav']}</strong><em>{SERVICES[s]['card_desc']}</em></span>
  <span class="related-card__arrow">→</span>
</a>""" for s in slugs)
    return f"""<section class="section section--ice">
  <div class="container">
    <h2 class="block-title">Другие услуги</h2>
    <div class="related">{cards}</div>
  </div>
</section>
"""


def project_card(p, i):
    media = f"media--{p['cat']}"
    svg = PROJECT_SVG[p["cat"]]
    params = "".join(f"<span>{esc(x)}</span>" for x in p["params"])
    return f"""<article class="project">
  <div class="project__media {media}">
    {svg}
    <span class="project__tag">{p['type']}</span>
  </div>
  <div class="project__body">
    <h3>{esc(p['title'])}</h3>
    <p>{esc(p['desc'])}</p>
    <div class="project__meta">{params}</div>
  </div>
</article>"""


PROJECT_SVG = {
    "home": '<svg viewBox="0 0 400 260" aria-hidden="true"><g stroke="#8FE6F2" stroke-opacity=".55" fill="none" stroke-width="2"><path d="M40 210h320M60 210V120l60-40 60 40v90M240 210v-70h110v70"/><circle cx="300" cy="60" r="16"/><path d="M284 60h32M300 44v32"/></g></svg>',
    "office": '<svg viewBox="0 0 400 260" aria-hidden="true"><g stroke="#A8D8FF" stroke-opacity=".5" fill="none" stroke-width="2"><rect x="50" y="40" width="300" height="180" rx="6"/><path d="M50 100h300M50 160h300M130 40v180M200 40v180M270 40v180"/><path d="M90 220h220"/></g></svg>',
    "retail": '<svg viewBox="0 0 400 260" aria-hidden="true"><g stroke="#FFE3B0" stroke-opacity=".6" fill="none" stroke-width="2"><path d="M30 80h340M30 80l20-25h300l20 25M60 80v150M340 80v150M60 230h280"/><path d="M140 230V120h120v110M200 120v110"/></g></svg>',
    "horeca": '<svg viewBox="0 0 400 260" aria-hidden="true"><g stroke="#FFC9B8" stroke-opacity=".55" fill="none" stroke-width="2"><path d="M40 190h320M70 190v-60h80v60M250 190v-80h90v80"/><circle cx="110" cy="108" r="12"/><circle cx="295" cy="86" r="10"/><path d="M170 190v-30h60v30"/></g></svg>',
    "industry": '<svg viewBox="0 0 400 260" aria-hidden="true"><g stroke="#9BE7C4" stroke-opacity=".55" fill="none" stroke-width="2"><path d="M30 210h340M70 210V90l50 25V90l50 25V90l50 25v95M300 210V110h60v100"/><path d="M100 60v20M180 55v25M90 150h60"/></g></svg>',
}


# ------------------------------------------------------------------ pages
def build_service(slug):
    d = SERVICES[slug]
    crumbs = [("Главная", "/"), ("Услуги", "/uslugi/"), (d["nav"], None)]
    sections = "".join(
        f"<h2>{esc(typo(h))}</h2>{html}" for h, html in d["sections"])
    prices = price_table(d["prices"])
    faq = faq_block(d["faq"])
    body = f"""{page_hero(crumbs, d['h1'], d['lead'], d['chips'])}
<section class="section">
  <div class="container layout">
    <div class="layout__main">
      <div class="prose">
        {sections}
      </div>
      <div class="price-block">
        <h2>Стоимость</h2>
        {prices}
        <p class="price-note">Цены ориентировочные, точная смета — после замера. Выезд инженера бесплатный.</p>
      </div>
      {faq}
    </div>
    {sidebar(slug)}
  </div>
</section>
{related_block(d['related'])}
{cta_band()}"""

    service_ld = {
        "@type": "Service",
        "name": d["h1"],
        "serviceType": d["nav"],
        "description": d["desc"],
        "url": canon("/uslugi/" + slug + "/"),
        "provider": {"@id": SITE + "/#organization"},
        "areaServed": {"@type": "City", "name": "Челябинск"},
        "offers": {
            "@type": "Offer",
            "priceCurrency": "RUB",
            "price": "18000",
            "availability": "https://schema.org/InStock",
            "url": canon("/uslugi/" + slug + "/"),
        },
    }
    write("/uslugi/" + slug + "/", head(d["title"], d["desc"], "/uslugi/" + slug + "/",
                                        [service_ld, breadcrumb_node(crumbs), faq_node(d["faq"])])
          + header("uslugi") + '<main id="main">' + body + "</main>" + footer())


def build_uslugi():
    crumbs = [("Главная", "/"), ("Услуги", None)]
    rows = []
    for s in ORDER:
        d = SERVICES[s]
        rows.append(f"""<a class="usluga-row" href="{href('/uslugi/' + s + '/')}">
  <span class="usluga-row__ico">{ICONS[s]}</span>
  <span class="usluga-row__text"><strong>{d['nav']}</strong><em>{d['card_desc']}</em></span>
  <span class="usluga-row__price">{d['prices'][0][1]}</span>
  <span class="usluga-row__arrow">→</span>
</a>""")

    body = f"""{page_hero(crumbs, "Услуги: вентиляция и кондиционирование в Челябинске",
                        "Проектируем, монтируем и обслуживаем системы для квартир, домов, офисов, магазинов и производств. Полный цикл — от расчёта до сервиса.",
                        ["Проект", "Монтаж", "Оборудование", "Сервис", "Автоматика"])}
<section class="section">
  <div class="container layout">
    <div class="layout__main">
      <div class="prose">
        <h2>Полный цикл работ по вентиляции и кондиционированию</h2>
        <p>Можно заказать отдельную услугу или весь цикл. Если система уже есть — начнём с обследования и подскажем, что дешевле: обслуживать или модернизировать.</p>
        <div class="usluga-list">{''.join(rows)}</div>

        <h2>Как выбрать услугу</h2>
        <p>Если вы только планируете систему, начните с <a href="{href('/uslugi/proektirovanie/')}">проектирования</a> — расчёт покажет, какое оборудование действительно нужно. Когда есть проект или понятная задача, переходите к <a href="{href('/uslugi/montazh/')}">монтажу</a>.</p>
        <p>Если оборудование ещё не выбрано, поможет <a href="{href('/uslugi/oborudovanie/')}">подбор и продажа</a>: сравним 2–3 варианта по цене и энергопотреблению. А чтобы система работала годами — <a href="{href('/uslugi/servis/')}">сервисное обслуживание</a> по договору.</p>
        <p>Для действующих объектов с устаревшей системой есть <a href="{href('/uslugi/rekonstrukciya/')}">реконструкция</a>, а для управления и мониторинга — <a href="{href('/uslugi/avtomatika/')}">автоматика и диспетчеризация</a>.</p>

        <h2>Частным и коммерческим клиентам</h2>
        <p>Для квартир и домов подбираем тихие решения с рекуперацией, скрытой прокладкой трасс и аккуратным монтажом. Для офисов, HoReCa и производств — системы под санитарные требования, с проектом, согласованием и исполнительной документацией.</p>
        <p>Работаем по 44-ФЗ и 223-ФЗ, готовим сметы, спецификации и полный пакет документов для сдачи объекта.</p>
      </div>
      {faq_block([
        ("С чего начать, если нужна вентиляция?", "С бесплатного выезда инженера: он оценит объект и скажет, нужен ли проект и какая система подойдёт."),
        ("Вы работаете с готовым проектом другого подрядчика?", "Да, проверяем проект на работоспособность и монтируем по нему."),
        ("Можно ли заказать только проект или только монтаж?", "Да, услуги доступны по отдельности."),
      ])}
    </div>
    {sidebar()}
  </div>
</section>
{cta_band()}"""

    write("/uslugi/", head("Услуги по вентиляции и кондиционированию в Челябинске — цены",
                           "Проектирование, монтаж, подбор оборудования, сервис, реконструкция и автоматика вентиляции в Челябинске. Полный цикл, гарантия до 5 лет, договор.",
                           "/uslugi/",
                           [breadcrumb_node(crumbs), faq_node([
                               ("С чего начать, если нужна вентиляция?", "С бесплатного выезда инженера."),
                               ("Вы работаете с готовым проектом другого подрядчика?", "Да, проверяем проект и монтируем по нему."),
                               ("Можно ли заказать только проект или только монтаж?", "Да, услуги доступны по отдельности."),
                           ])])
          + header("uslugi") + '<main id="main">' + body + "</main>" + footer())


def build_proekty():
    crumbs = [("Главная", "/"), ("Проекты", None)]
    cards = "".join(project_card(p, i) for i, p in enumerate(PROJECTS))
    body = f"""{page_hero(crumbs, "Выполненные работы: вентиляция и кондиционирование в Челябинске",
                        "840 объектов с 2012 года: от квартиры в новостройке до цеха с приточно-вытяжной установкой на 12 000 м³/ч.",
                        ["840 объектов", "Частные и коммерческие", "Гарантия до 5 лет"])}
<section class="section">
  <div class="container">
    <div class="projects">{cards}</div>
  </div>
</section>
<section class="section section--ice">
  <div class="container prose prose--center">
    <h2>Как мы считаем результат</h2>
    <p>За каждым проектом — расчёт воздухообмена, подбор оборудования и пусконаладка с замерами. Мы фиксируем параметры в протоколах, поэтому результат можно проверить: расход воздуха, уровень шума, температуры.</p>
    <p>Хотите посмотреть объект, похожий на ваш? Позвоните — подберём 2–3 кейса и расскажем, какие решения сработали.</p>
  </div>
</section>
{cta_band("Хотите такой же результат на своём объекте?", "Расскажите о задаче — предложим решение и назовём стоимость.")}"""

    write("/proekty/", head("Выполненные работы: вентиляция и кондиционирование в Челябинске",
                            "Портфолио АэроТех 74: коттеджи, офисы, магазины, рестораны и производства Челябинска. 840 объектов с 2012 года, параметры и сроки по каждому.",
                            "/proekty/",
                            [breadcrumb_node(crumbs)])
          + header("proekty") + '<main id="main">' + body + "</main>" + footer())


def build_tseny():
    crumbs = [("Главная", "/"), ("Цены", None)]
    tables = []
    for s in ORDER:
        d = SERVICES[s]
        tables.append(f"""<div class="price-block">
  <h2>{esc(d['nav'])} — цены</h2>
  {price_table(d['prices'])}
  <p class="price-note"><a href="{href('/uslugi/' + s + '/')}">Подробнее об услуге →</a></p>
</div>""")

    body = f"""{page_hero(crumbs, "Цены на вентиляцию и кондиционирование в Челябинске",
                        "Ориентировочные цены на проектирование, монтаж, оборудование и обслуживание. Точная смета — после бесплатного замера, с фиксацией в договоре.",
                        ["Смета за 15 минут", "Фиксация цены", "Без скрытых доплат"])}
<section class="section">
  <div class="container layout">
    <div class="layout__main">
      <div class="prose">
        <h2>Из чего складывается стоимость</h2>
        <p>Цена системы зависит от четырёх факторов: необходимого воздухообмена, класса оборудования, длины и сложности трасс, а также требований к автоматике. Поэтому корректная смета возможна только после замера.</p>
        <ul>
          <li><strong>Воздухообмен.</strong> Чем больше расход, тем мощнее установка и шире воздуховоды.</li>
          <li><strong>Оборудование.</strong> Разница между бюджетным и премиальным брендом — 2–3 раза при сопоставимой производительности.</li>
          <li><strong>Трассы.</strong> Скрытая прокладка и обход конструкций увеличивают стоимость монтажа.</li>
          <li><strong>Автоматика.</strong> Простой щит или диспетчеризация с мониторингом.</li>
        </ul>
      </div>
      {''.join(tables)}
      {faq_block([
        ("Почему цены указаны «от»?", "Потому что итоговая стоимость зависит от объекта. После замера мы фиксируем смету в договоре — она не меняется по ходу работ."),
        ("Можно ли сэкономить?", "Да: предложим 2–3 варианта с разным оборудованием, покажем, на чём можно сэкономить без потери качества."),
        ("Выезд и замер платные?", "Нет, выезд инженера и замер по Челябинску бесплатны."),
      ])}
    </div>
    {sidebar()}
  </div>
</section>
{cta_band()}"""

    write("/tseny/", head("Цены на вентиляцию и кондиционирование в Челябинске 2026",
                          "Цены на проектирование, монтаж и обслуживание вентиляции в Челябинске: проект от 18 000 ₽, монтаж от 9 000 ₽, обслуживание от 3 900 ₽. Смета после бесплатного замера.",
                          "/tseny/",
                          [breadcrumb_node(crumbs)])
          + header("tseny") + '<main id="main">' + body + "</main>" + footer())


def build_about():
    crumbs = [("Главная", "/"), ("О компании", None)]
    why = [
        ("Договор и фиксированная смета", "Цена в смете не меняется по ходу работ. Дополнительные работы — только по согласованию."),
        ("Соблюдаем сроки", "График работ — в договоре. За просрочку по нашей вине предусмотрена неустойка."),
        ("Свой склад и производство", "Воздуховоды, крепёж и расходники — на месте. Не зависим от поставок и не тянем сроки."),
        ("Опыт в сложных объектах", "Пищевые производства, медцентры, серверные, объекты с требованиями по шуму и чистоте."),
        ("Документы под ключ", "Акты, протоколы, паспорта систем, исполнительная документация для сдачи объекта."),
        ("Экономия на эксплуатации", "Рекуперация, частотное регулирование, датчики CO₂ — решения, которые снижают счета."),
    ]
    why_html = "".join(
        f'<div class="why__item"><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for t, d in why)
    reviews = "".join(f"""<div class="review">
  <div class="review__stars" aria-label="5 из 5">★★★★★</div>
  <p>{esc(text)}</p>
  <div class="review__who"><span>{esc(name[0])}</span><div><strong>{esc(name)}</strong><em>{esc(role)}</em></div></div>
</div>""" for name, role, text in REVIEWS)

    body = f"""{page_hero(crumbs, "О компании АэроТех 74",
                        "Инженерная команда из Челябинска: проектируем, монтируем и обслуживаем системы вентиляции и кондиционирования с 2012 года.",
                        ["С 2012 года", "36 специалистов", "840 объектов"])}
<section class="section">
  <div class="container layout">
    <div class="layout__main">
      <div class="prose">
        <h2>Кто мы</h2>
        <p>АэроТех 74 — инженерная компания в Челябинске. Начинали с монтажа бытовых кондиционеров, сегодня делаем системы для коттеджей, офисов, ресторанов, магазинов и производств. В штате 36 человек: проектировщики, монтажные бригады, сервисные инженеры и собственная сборка воздуховодов.</p>
        <p>Мы не продаём «оборудование по прайсу». Сначала считаем задачу, потом подбираем решение и фиксируем смету. Такой подход дороже на этапе продажи, но дешевле на этапе эксплуатации.</p>

        <h2>Цифры</h2>
        <table class="price-table"><tbody>
          <tr><td>Объектов сдано</td><td>840+</td></tr>
          <tr><td>Лет на рынке</td><td>14</td></tr>
          <tr><td>Специалистов в штате</td><td>36</td></tr>
          <tr><td>Гарантия на монтаж</td><td>до 5 лет</td></tr>
          <tr><td>Объектов сдано в срок</td><td>98%</td></tr>
        </tbody></table>

        <h2>Как мы работаем</h2>
        <p>Каждый объект ведёт инженер: он отвечает за расчёт, сроки и приёмку. Вы всегда знаете, на каком этапе находится проект, и получаете фотоотчёт по скрытым работам.</p>
        <p>Для коммерческих клиентов готовим полный пакет исполнительной документации и работаем по 44-ФЗ и 223-ФЗ.</p>

        <h2>Документы и гарантии</h2>
        <p>Гарантия на монтаж — до 5 лет, на оборудование — гарантия производителя. Все обязательства прописаны в договоре. Свой склад запчастей в Челябинске позволяет не ждать поставку из Москвы.</p>
      </div>

      <div class="why-grid">{why_html}</div>
      <h2 class="block-title">Отзывы клиентов</h2>
      <div class="reviews">{reviews}</div>
    </div>
    {sidebar()}
  </div>
</section>
{cta_band("Обсудим ваш объект?", "Приезжаем на замер бесплатно, по Челябинску и пригороду.")}"""

    write("/o-kompanii/", head("О компании АэроТех 74 — инженерная команда в Челябинске",
                               "АэроТех 74 — проектирование, монтаж и сервис вентиляции в Челябинске с 2012 года. 36 специалистов, 840 объектов, гарантия до 5 лет, свой склад.",
                               "/o-kompanii/",
                               [breadcrumb_node(crumbs)])
          + header("o-kompanii") + '<main id="main">' + body + "</main>" + footer())


def build_kontakty():
    crumbs = [("Главная", "/"), ("Контакты", None)]
    body = f"""{page_hero(crumbs, "Контакты",
                        "Офис в центре Челябинска, склад на Механической и бесплатный выезд инженера по городу и пригороду.",
                        ["Челябинск, ул. Труда, 84", COMPANY['hours']])}
<section class="section" id="zayavka">
  <div class="container layout">
    <div class="layout__main">
      <div class="prose">
        <h2>Как с нами связаться</h2>
        <p>Позвоните или оставьте заявку — ответим в течение 15 минут в рабочее время. Для расчёта достаточно площади объекта и адреса: инженер приедет, замерит и предложит решение.</p>
      </div>

      <div class="contact-cards">
        <div class="contact-card"><span>Телефон</span><a href="tel:{COMPANY['phone_href']}">{COMPANY['phone']}</a><em>пн–вс, 8:00–20:00</em></div>
        <div class="contact-card"><span>Почта</span><a href="mailto:{COMPANY['email']}">{COMPANY['email']}</a><em>ответ в течение дня</em></div>
        <div class="contact-card"><span>Офис</span><strong>{COMPANY['address']}</strong><em>приём по записи</em></div>
        <div class="contact-card"><span>Склад</span><strong>{COMPANY['warehouse']}</strong><em>самовывоз по договорённости</em></div>
      </div>

      <div class="map">
        <div class="map__grid" aria-hidden="true">
          <svg viewBox="0 0 1200 300" preserveAspectRatio="none">
            <rect width="1200" height="300" fill="#e7f0f7"/>
            <g stroke="#c9dcea" stroke-width="10"><path d="M0 120h1200M0 230h1200M180 0v300M520 0v300M880 0v300"/></g>
            <g stroke="#d8e7f1" stroke-width="4"><path d="M0 60h1200M0 180h1200M0 275h1200M90 0v300M340 0v300M700 0v300M1040 0v300"/></g>
            <path d="M0 200c180-40 260-120 460-100s300 90 520 40" stroke="#a9cfe6" stroke-width="14" fill="none"/>
          </svg>
        </div>
        <span class="map__label map__label--1">ул. Труда</span>
        <span class="map__label map__label--2">пр. Ленина</span>
        <div class="map__pin"><span></span><strong>ул. Труда, 84</strong></div>
        <div class="map__card">
          <strong>Офис АэроТех 74</strong>
          <span>{COMPANY['address']}</span>
          <span>{COMPANY['hours']}</span>
          <a href="tel:{COMPANY['phone_href']}" class="btn btn--primary btn--sm">Позвонить</a>
        </div>
      </div>

      <div class="contact-form-wrap">
        <h2 class="block-title">Оставить заявку</h2>
        <form class="form card-form" id="leadForm" novalidate>
          <label class="field"><span>Как к вам обращаться</span><input type="text" name="name" placeholder="Иван" required></label>
          <label class="field"><span>Телефон</span><input type="tel" name="phone" placeholder="+7 (___) ___-__-__" inputmode="tel" required></label>
          <label class="field"><span>Что нужно</span>
            <select name="type">
              <option>Проектирование</option><option>Монтаж</option><option>Подбор оборудования</option>
              <option>Сервисное обслуживание</option><option>Пока не знаю — нужна консультация</option>
            </select>
          </label>
          <label class="field"><span>Комментарий</span><textarea name="comment" rows="3" placeholder="Площадь объекта, адрес, сроки"></textarea></label>
          <button type="submit" class="btn btn--primary btn--block">Отправить заявку</button>
          <label class="check"><input type="checkbox" checked required><span>Согласен на обработку персональных данных</span></label>
          <div class="form__ok" role="status" aria-live="polite">
            <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M7.5 12.5l3 3 6-7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <div><strong>Заявка отправлена</strong><span>Инженер свяжется с вами в ближайшее время.</span></div>
            <a href="tel:{COMPANY['phone_href']}" class="form__ok-phone">{COMPANY['phone']}</a>
          </div>
        </form>
      </div>

      <div class="prose">
        <h2>Реквизиты</h2>
        <p>{COMPANY['legal']}<br>ИНН {COMPANY['inn']} · ОГРН {COMPANY['ogrn']}<br>{COMPANY['address']}</p>
      </div>
    </div>
    {sidebar()}
  </div>
</section>
{cta_band("Удобнее позвонить?", "Ответим на вопросы по телефону и запишем на бесплатный замер.")}"""

    write("/kontakty/", head("Контакты — АэроТех 74, Челябинск, ул. Труда, 84",
                             "Контакты АэроТех 74: Челябинск, ул. Труда, 84, офис 312. Телефон +7 (351) 200-00-00, пн–вс 8:00–20:00. Бесплатный выезд инженера.",
                             "/kontakty/",
                             [breadcrumb_node(crumbs)])
          + header("kontakty") + '<main id="main">' + body + "</main>" + footer())


def build_blog():
    crumbs = [("Главная", "/"), ("Блог", None)]
    post = POSTS[0]
    topics = "".join(f"<li>{esc(t)}</li>" for t in BLOG_TOPICS)
    body = f"""{page_hero(crumbs, "Блог о вентиляции и кондиционировании",
                        "Разбираем, как выбрать, смонтировать и обслуживать системы — без маркетинга и общих слов.",
                        ["Практика", "Цифры и нормативы"])}
<section class="section">
  <div class="container layout">
    <div class="layout__main">
      <a class="post-card" href="{href('/blog/' + post['slug'] + '/')}">
        <div class="post-card__media">{PROJECT_SVG['home']}<span class="project__tag">Гид</span></div>
        <div class="post-card__body">
          <div class="post-meta">{post['date_ru']} · {post['reading']}</div>
          <h2>{esc(post['title'])}</h2>
          <p>{esc(post['desc'])}</p>
          <span class="service__link">Читать статью <span>→</span></span>
        </div>
      </a>

      <div class="prose">
        <h2>Темы, которые готовим</h2>
        <p>Пишем о том, с чем сталкиваются владельцы квартир, офисов и производств. Если нужной темы нет — задайте вопрос, ответим и добавим в план.</p>
        <ul class="topics">{topics}</ul>
      </div>
    </div>
    {sidebar()}
  </div>
</section>
{cta_band("Не нашли ответ?", "Позвоните — инженер объяснит по телефону, без навязывания услуг.")}"""

    write("/blog/", head("Блог о вентиляции и кондиционировании — АэроТех 74",
                         "Статьи инженеров АэроТех 74: как выбрать вентиляцию, сколько стоит монтаж, как обслуживать систему. Практика для Челябинска.",
                         "/blog/",
                         [breadcrumb_node(crumbs)])
          + header("blog") + '<main id="main">' + body + "</main>" + footer())


def build_post():
    p = POSTS[0]
    path = "/blog/" + p["slug"] + "/"
    short = p["title"].split(":")[0]
    crumbs = [("Главная", "/"), ("Блог", "/blog/"), (short, None)]
    sections = "".join(f"<h2>{esc(typo(h))}</h2>{html}" for h, html in p["sections"])
    body = f"""{page_hero(crumbs, p['h1'], p['lead'], [p['date_ru'], p['reading'], "Инженеры АэроТех 74"])}
<section class="section">
  <div class="container layout">
    <div class="layout__main">
      <a class="back-link" href="{href('/blog/')}">← Все статьи</a>
      <article class="prose article">
        {sections}
        <div class="article-author">
          <div><strong>Материал подготовил инженерный отдел АэроТех 74</strong>
          <span>Проектирование и монтаж вентиляции в Челябинске с 2012 года</span></div>
        </div>
      </article>
      {faq_block(p['faq'])}
    </div>
    {sidebar()}
  </div>
</section>
{cta_band("Нужен расчёт под вашу квартиру?", "Бесплатный замер и смета с фиксацией цены.")}"""

    article_ld = {
        "@type": "Article",
        "headline": p["title"],
        "description": p["desc"],
        "datePublished": p["date"],
        "dateModified": p["date"],
        "mainEntityOfPage": canon(path),
        "author": {"@type": "Organization", "name": "АэроТех 74",
                   "url": SITE + "/"},
        "publisher": {"@id": SITE + "/#organization"},
        "inLanguage": "ru-RU",
    }
    write(path, head(p["title"], p["desc"], path,
                     [article_ld, breadcrumb_node(crumbs), faq_node(p["faq"])], og_type="article")
          + header("blog") + '<main id="main">' + body + "</main>" + footer())


def build_home():
    stats = [("840", "объектов сдано"), ("14", "лет на рынке"),
             ("36", "инженеров и монтажников"), ("5", "лет гарантии")]
    stats_html = "".join(
        f"<div><strong>{n}</strong><span>{t}</span></div>" for n, t in stats)
    projects = "".join(project_card(p, i) for i, p in enumerate(PROJECTS[:3]))
    post = POSTS[0]

    form = f"""<aside class="hero__card">
  <div class="form-card">
    <div class="form-card__head">
      <h2>Расчёт за 15 минут</h2>
      <p>Оставьте заявку — инженер перезвонит, уточнит задачу и назовёт вилку стоимости.</p>
    </div>
    <form class="form" id="leadForm" novalidate>
      <label class="field"><span>Как к вам обращаться</span><input type="text" name="name" placeholder="Иван" autocomplete="name" required></label>
      <label class="field"><span>Телефон</span><input type="tel" name="phone" placeholder="+7 (___) ___-__-__" inputmode="tel" required></label>
      <label class="field"><span>Тип объекта</span>
        <select name="type">
          <option>Квартира</option><option>Частный дом</option><option selected>Офис</option>
          <option>Магазин / салон</option><option>Кафе / ресторан</option><option>Производство / склад</option>
        </select>
      </label>
      <button type="submit" class="btn btn--primary btn--block">Рассчитать стоимость</button>
      <label class="check"><input type="checkbox" checked required><span>Согласен на обработку персональных данных</span></label>
      <p class="form__note">Без спама. Перезвоним в течение рабочего дня.</p>
      <div class="form__ok" role="status" aria-live="polite">
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M7.5 12.5l3 3 6-7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <div><strong>Заявка отправлена</strong><span>Инженер свяжется с вами в ближайшее время.</span></div>
        <a href="tel:{COMPANY['phone_href']}" class="form__ok-phone">{COMPANY['phone']}</a>
      </div>
    </form>
  </div>
</aside>"""

    body = f"""<main id="main">
<section class="hero">
  <div class="container hero__in">
    <div class="hero__copy">
      <span class="chip chip--glass"><i class="dot"></i> Работаем в Челябинске и области с 2012 года</span>
      <h1>Вентиляция и кондиционирование <span class="grad">под ключ</span> в&nbsp;Челябинске</h1>
      <p class="hero__sub">Проектируем, монтируем и обслуживаем системы для квартир, домов, офисов, магазинов и производств. Один подрядчик — от расчёта до сервиса.</p>
      <ul class="hero__points">
        <li><svg viewBox="0 0 20 20"><path d="M4 10.5l4 4 8-9" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg> Выезд инженера и замер — бесплатно</li>
        <li><svg viewBox="0 0 20 20"><path d="M4 10.5l4 4 8-9" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg> Смета с фиксацией цены в договоре</li>
        <li><svg viewBox="0 0 20 20"><path d="M4 10.5l4 4 8-9" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg> Гарантия на монтаж до 5 лет</li>
      </ul>
      <div class="hero__actions">
        <a href="{href('/kontakty/#zayavka')}" class="btn btn--primary btn--lg">Получить расчёт</a>
        <a href="{href('/proekty/')}" class="btn btn--ghost btn--lg">Смотреть работы</a>
      </div>
      <div class="hero__stats">{stats_html}</div>
    </div>
    {form}
  </div>
</section>

<section class="section section--tight">
  <div class="container">
    <div class="segments segments--two">
      <article class="segment">
        <div class="segment__icon"><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.5L16 5l12 9.5"/><path d="M7 13v13h18V13"/><path d="M13 26v-7h6v7"/></svg></div>
        <h2>Частным клиентам</h2>
        <p>Квартиры, дома, коттеджи, таунхаусы. Приточная вентиляция, кондиционеры, бризеры, рекуперация тепла.</p>
        <ul><li>Тихие системы — от 22 дБ</li><li>Аккуратный монтаж без пыли</li><li>Скрытая прокладка воздуховодов</li></ul>
        <a href="{href('/uslugi/')}" class="link-arrow">Услуги для дома <span>→</span></a>
      </article>
      <article class="segment segment--accent">
        <div class="segment__icon"><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="8" width="22" height="20" rx="2"/><path d="M11 4v6M21 4v6M5 15h22"/><path d="M11 21h4M11 24.5h8"/></svg></div>
        <h2>Коммерческим клиентам</h2>
        <p>Офисы, торговые центры, HoReCa, склады, производства, медицинские и учебные учреждения.</p>
        <ul><li>Работа по 44-ФЗ и 223-ФЗ</li><li>Проект и согласования</li><li>Сервис по договору 24/7</li></ul>
        <a href="{href('/uslugi/')}" class="link-arrow">Решения для бизнеса <span>→</span></a>
      </article>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section__head">
      <div><span class="eyebrow">Услуги</span><h2 class="h2">Полный цикл работ по вентиляции и кондиционированию</h2></div>
      <p class="section__lead">Берём объект целиком или отдельный этап. Все услуги — на отдельных страницах с ценами и сроками.</p>
    </div>
    {services_grid()}
  </div>
</section>

<section class="section section--ice">
  <div class="container">
    <div class="section__head">
      <div><span class="eyebrow">Портфолио</span><h2 class="h2">Выполненные работы</h2></div>
      <p class="section__lead">840 объектов в Челябинске и области — от квартиры до производственного цеха.</p>
    </div>
    <div class="projects">{projects}</div>
    <div class="projects__more"><a href="{href('/proekty/')}" class="btn btn--ghost">Все проекты</a></div>
  </div>
</section>

<section class="section section--dark">
  <div class="container">
    <div class="section__head section__head--light">
      <div><span class="eyebrow eyebrow--light">Почему мы</span><h2 class="h2">Инженерный подход вместо «продать и забыть»</h2></div>
      <p class="section__lead">Работаем по договору с фиксированной сметой, сдаём объект с протоколами и остаёмся на сервисе.</p>
    </div>
    <div class="why why--four">
      <div class="why__item"><h3>Считаем, а не угадываем</h3><p>Расчёт воздухообмена, теплопритоков и аэродинамики — до покупки оборудования.</p></div>
      <div class="why__item"><h3>Свои бригады</h3><p>Не передаём монтаж «свободным» подрядчикам. Отвечаем за качество и сроки.</p></div>
      <div class="why__item"><h3>Гарантия до 5 лет</h3><p>Обязательства прописаны в договоре, запчасти — на своём складе.</p></div>
      <div class="why__item"><h3>Документы под ключ</h3><p>Акты, протоколы, паспорта систем и исполнительная документация.</p></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container layout">
    <div class="layout__main prose">
      <h2>Вентиляция и кондиционирование в Челябинске: с чего начать</h2>
      <p>Климат Челябинска — резко континентальный: зимой до −35 °C, летом до +35 °C. Поэтому система должна работать в широком диапазоне температур: приточная установка с подогревом и защитой от обмерзания зимой и кондиционер с запасом мощности летом.</p>
      <p>Для квартиры или дома обычно достаточно приточно-вытяжной системы с рекуперацией: она подаёт свежий воздух и возвращает до 80% тепла. Для офиса, магазина или ресторана нужен расчёт под санитарные требования и количество людей, а для производства — местные отсосы и аспирация.</p>
      <p>Начать проще с бесплатного замера: инженер оценит объект, скажет, нужен ли <a href="{href('/uslugi/proektirovanie/')}">проект</a>, какое оборудование подойдёт и сколько будет стоить <a href="{href('/uslugi/montazh/')}">монтаж</a>. Если система уже есть — предложим <a href="{href('/uslugi/servis/')}">обслуживание</a> или <a href="{href('/uslugi/rekonstrukciya/')}">модернизацию</a>.</p>
      <p>Ориентировочные цены смотрите на странице <a href="{href('/tseny/')}">«Цены»</a>, примеры объектов — в <a href="{href('/proekty/')}">портфолио</a>.</p>
    </div>
    {sidebar()}
  </div>
</section>

<section class="section section--ice">
  <div class="container">
    <div class="section__head">
      <div><span class="eyebrow">Блог</span><h2 class="h2">Разбираемся в вентиляции без сложных слов</h2></div>
      <p class="section__lead">Статьи инженеров о выборе, монтаже и обслуживании систем.</p>
    </div>
    <a class="post-card" href="{href('/blog/' + post['slug'] + '/')}">
      <div class="post-card__media">{PROJECT_SVG['home']}<span class="project__tag">Гид</span></div>
      <div class="post-card__body">
        <div class="post-meta">{post['date_ru']} · {post['reading']}</div>
        <h3>{esc(post['title'])}</h3>
        <p>{esc(post['desc'])}</p>
        <span class="service__link">Читать статью <span>→</span></span>
      </div>
    </a>
    <div class="projects__more"><a href="{href('/blog/')}" class="btn btn--ghost">Все статьи</a></div>
  </div>
</section>

{cta_band("Рассчитаем стоимость вашей системы", "Бесплатный выезд, замер и смета с фиксацией цены в договоре.")}
</main>"""

    write("/", head("Вентиляция и кондиционирование в Челябинске — АэроТех 74",
                     "Проектирование, монтаж и обслуживание вентиляции и кондиционирования в Челябинске. Частные и коммерческие объекты, гарантия до 5 лет, бесплатный замер.",
                     "/")
          + header("") + body + footer())


def build_404():
    body = f"""<main id="main">
<section class="page-hero page-hero--404">
  <div class="container">
    <p class="error-code">404</p>
    <h1>Страница не найдена</h1>
    <p class="page-hero__lead">Возможно, страница переехала или в адресе опечатка. Вот основные разделы сайта.</p>
    <div class="hero__actions">
      <a href="{href('/')}" class="btn btn--primary">На главную</a>
      <a href="{href('/uslugi/')}" class="btn btn--ghost">Услуги</a>
      <a href="{href('/kontakty/')}" class="btn btn--ghost">Контакты</a>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">{services_grid()}</div>
</section>
</main>"""
    html = (head("Страница не найдена — АэроТех 74", "Страница не найдена. Перейдите на главную или выберите услугу.",
                 "/404/", noindex=True)
            + header("") + body + footer())
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(html)


def write(path, html):
    """path вида '/uslugi/montazh/' → multi/uslugi/montazh/index.html"""
    rel = path.strip("/")
    target_dir = os.path.join(OUT, rel) if rel else OUT
    os.makedirs(target_dir, exist_ok=True)
    with open(os.path.join(target_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)



def build_policy():
    crumbs = [("Главная", "/"), ("Политика конфиденциальности", None)]
    body = f"""{page_hero(crumbs, "Политика конфиденциальности",
                        "Как АэроТех 74 обрабатывает и защищает персональные данные посетителей сайта и клиентов.",
                        ["152-ФЗ", "Обновлено 07.11.2026"])}
<section class="section">
  <div class="container layout">
    <div class="layout__main">
      <div class="prose">
        <h2>1. Общие положения</h2>
        <p>Настоящая политика определяет порядок обработки персональных данных пользователей сайта {SITE} (далее — Сайт) и действует в отношении всей информации, которую {COMPANY['legal']} может получить о посетителе Сайта.</p>
        <p>Используя Сайт и отправляя заявку, пользователь подтверждает согласие с условиями настоящей политики.</p>

        <h2>2. Какие данные мы собираем</h2>
        <ul><li>имя, указанное в форме заявки;</li>
        <li>номер телефона и адрес электронной почты;</li>
        <li>адрес объекта и параметры помещения, если пользователь указал их в комментарии;</li>
        <li>обезличенные данные о посещении: IP-адрес, cookie, страницы и время визита.</li></ul>

        <h2>3. Цели обработки</h2>
        <ul><li>связь с пользователем по заявке и уточнение задачи;</li>
        <li>подготовка расчёта стоимости и коммерческого предложения;</li>
        <li>заключение и исполнение договора;</li>
        <li>улучшение работы Сайта и качества сервиса.</li></ul>

        <h2>4. Правовые основания</h2>
        <p>Обработка осуществляется на основании согласия пользователя, выраженного при отправке формы, а также в целях исполнения договора, стороной которого является пользователь.</p>

        <h2>5. Хранение и защита</h2>
        <p>Данные хранятся на серверах, размещённых на территории Российской Федерации, не дольше, чем требуется для достижения целей обработки. Доступ к ним имеют только уполномоченные сотрудники, связанные обязательствами конфиденциальности.</p>

        <h2>6. Передача третьим лицам</h2>
        <p>Мы не продаём и не передаём персональные данные третьим лицам, кроме случаев, предусмотренных законодательством, или когда это необходимо для исполнения договора (например, подрядной организации).</p>

        <h2>7. Права пользователя</h2>
        <p>Пользователь вправе запросить сведения об обработке своих данных, потребовать их уточнения, блокирования или удаления, а также отозвать согласие. Для этого напишите на <a href="mailto:{COMPANY['email']}">{COMPANY['email']}</a> или позвоните по телефону <a href="tel:{COMPANY['phone_href']}">{COMPANY['phone']}</a>.</p>

        <h2>8. Cookie</h2>
        <p>Сайт использует cookie для корректной работы интерфейса и анализа статистики. Пользователь может отключить cookie в настройках браузера — часть функций при этом может работать некорректно.</p>

        <h2>9. Контакты</h2>
        <p>{COMPANY['legal']}<br>{COMPANY['address']}<br>ИНН {COMPANY['inn']}<br><a href="mailto:{COMPANY['email']}">{COMPANY['email']}</a></p>
      </div>
    </div>
    {sidebar()}
  </div>
</section>
{cta_band("Остались вопросы по данным?", "Напишите нам — ответим и при необходимости удалим ваши данные.")}"""

    write("/politika-konfidencialnosti/",
          head("Политика конфиденциальности — АэроТех 74",
               "Политика обработки персональных данных АэроТех 74: какие данные собираем, цели, хранение, права пользователя и контакты.",
               "/politika-konfidencialnosti/",
               [breadcrumb_node(crumbs)])
          + header("") + '<main id="main">' + body + "</main>" + footer())


def build_files():
    pages = [("/", "1.0", "weekly"),
             ("/uslugi/", "0.9", "monthly"),
             ("/tseny/", "0.8", "monthly"),
             ("/proekty/", "0.7", "monthly"),
             ("/o-kompanii/", "0.6", "yearly"),
             ("/kontakty/", "0.6", "yearly"),
             ("/blog/", "0.6", "weekly"),
             ("/blog/" + POSTS[0]["slug"] + "/", "0.5", "yearly"),
             ("/politika-konfidencialnosti/", "0.3", "yearly")]
    for s in ORDER:
        pages.append(("/uslugi/" + s + "/", "0.8", "monthly"))

    urls = "\n".join(
        f"""  <url>
    <loc>{canon(p)}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{ch}</changefreq>
    <priority>{pr}</priority>
  </url>""" for p, pr, ch in pages)

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    if NOINDEX:
        robots = "User-agent: *\nDisallow: /\n"
    else:
        robots = f"""User-agent: *
Allow: /

Sitemap: {SITE}/sitemap.xml
"""
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)


def build_assets():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    shutil.copy(os.path.join(SRC, "styles.css"), os.path.join(OUT, "assets", "style.css"))
    extra = os.path.join(ROOT, "extra.css")
    shutil.copy(os.path.join(SRC, "script.js"), os.path.join(OUT, "assets", "app.js"))
    with open(os.path.join(OUT, "assets", "style.css"), "a", encoding="utf-8") as out:
        out.write("\n\n/* ============ multipage additions ============ */\n")
        with open(extra, encoding="utf-8") as f:
            out.write(f.read())


def main():
    os.makedirs(OUT, exist_ok=True)
    build_assets()
    build_home()
    build_uslugi()
    for s in ORDER:
        build_service(s)
    build_proekty()
    build_tseny()
    build_about()
    build_kontakty()
    build_blog()
    build_post()
    build_policy()
    build_404()
    build_files()
    print(f"built: {OUT}\nSITE={SITE}\nBASE={BASE or '/'}\nNOINDEX={'1' if NOINDEX else '0'}")


if __name__ == "__main__":
    main()
