# -*- coding: utf-8 -*-
"""ポータル共通の「殻」（ヘッダー・ページ見出し・フッター・テーマ CSS/JS）。

  python _src/portal_shell.py            既存ページ（日英）にテーマを適用する（何度流しても同じ結果になる）

新規ページ（ホーム・写真・T シャツ案）は build_home.py / build_photos_1003.py / build_tshirt.py が
このモジュールの shell_head / header / footer を使って組み立てる。

既存ページの本文には手を入れない。変えるのは次の3点だけ。
  1. <head> にテーマ CSS を足す（旧 CSS のあとに置き、同名クラスを上書き）
  2. 旧 <h1>・.subtitle・.page-nav・.lang-toggle を外し、ヘッダーと「ページ見出し」に置き換える
  3. 末尾にフッターとスクリプトを足す
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@200;300;400;500;600;700&amp;family=Noto+Sans+JP:wght@300;400;500;700&amp;display=swap" rel="stylesheet">')
FAVICON = ("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMiAzMiI+PHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiByeD0iMyIgZmlsbD0iIzIyMzA1NSIvPjxwYXRoIGQ9Ik0yNCAzIDI1IDUuNSAyNy41IDYgMjUgNi41IDI0IDkgMjMgNi41IDIwLjUgNiAyMyA1LjVaIiBmaWxsPSIjZmZiN2NhIi8+PHBhdGggZD0iTTMgMTQgMTAgMTEgMjYgMTEgMjYgMTUgMjIgMTUgMjAgMTkgMjQgMTkgMjQuNSAyMyA3LjUgMjMgOCAxOSAxMiAxOSAxMCAxNSAzIDE1WiIgZmlsbD0iI2ZmZmZmZiIvPjwvc3ZnPg==")
ANVIL = ('<svg viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="#223055"/>'
         '<path d="M24 3 25 5.5 27.5 6 25 6.5 24 9 23 6.5 20.5 6 23 5.5Z" fill="#ffb7ca"/>'
         '<path d="M3 14 10 11 26 11 26 15 22 15 20 19 24 19 24.5 23 7.5 23 8 19 12 19 10 15 3 15Z" fill="#fff"/></svg>')

# nav: key, 日本語, English, JA file, EN file
NAV = [
    ("home", "ホーム", "Home", "Kawaguchi_seminar.html", "Kawaguchi_seminar_en.html"),
    ("minutes", "議事メモ", "Minutes", "Kawaguchi_seminar_minutes.html", "Kawaguchi_seminar_minutes_en.html"),
    ("library", "資料", "Library", "Kawaguchi_seminar_papers.html", "Kawaguchi_seminar_papers_en.html"),
    ("photos", "写真", "Photos", "Kawaguchi_seminar_1003_photos.html", "Kawaguchi_seminar_1003_photos.html"),
    ("tshirt", "Tシャツ案", "T-shirt", "Kawaguchi_seminar_tshirt.html", "Kawaguchi_seminar_tshirt.html"),
]
KURODA = "papers/2026-10-03/Kuroda_20261003_Causal_Inference_AI_Era_Aircon.pdf"
SUBNAV_LIB = [("Kawaguchi_seminar_papers.html", "過去資料", "Kawaguchi_seminar_papers_en.html", "Past materials"),
              ("Kawaguchi_seminar_melmaga.html", "関連メルマガ", "Kawaguchi_seminar_melmaga_en.html", "Newsletters"),
              ("Kawaguchi_seminar_articles.html", "日経記事×AI課題", "Kawaguchi_seminar_articles.html", "Nikkei × AI")]


def _p(ja, en, **kw):
    return {"ja": ja, "en": en, **kw}


# ファイル名 → ページの“顔”。stale になる「次回」の言い回しは使わない（状態は日付から導く）。
PAGES = {
    "Kawaguchi_seminar_0822.html": dict(en="Kawaguchi_seminar_0822_en.html", nav="home", crumb="第5回", ja=dict(
        kicker="第5回 研究会 · 2026.08.22", title='<span class="ph">エージェンティック</span><span class="ph">時空統計学</span> <span class="ph">入門</span>',
        lede="大規模言語モデルと時空モデリング：依存の統計学アプローチ。午前は講話と演習、午後は川口先生による Claude Code の実演。",
        chips=["開催済", "10:00–16:00", "早稲田大学 26号館11階 1102"],
        actions=[("議事メモを読む", "Kawaguchi_seminar_minutes5.html", True)])),
    "Kawaguchi_seminar_0822_en.html": dict(en="Kawaguchi_seminar_0822.html", nav="home", crumb="5th meeting", ja=dict(
        kicker="5th meeting · 2026.08.22", title="Agentic spatio-temporal statistics: an introduction",
        lede="Large language models and spatio-temporal modelling — a statistical approach to dependence. Lectures and exercises in the morning, a live Claude Code demonstration in the afternoon.",
        chips=["Held", "10:00–16:00", "Waseda Univ., Bldg 26, 11F, Room 1102"],
        actions=[("Read the minutes", "Kawaguchi_seminar_minutes5.html", True)])),
    "Kawaguchi_seminar_1003.html": dict(en="Kawaguchi_seminar_1003_en.html", nav="home", crumb="秋のシンポジウム", ja=dict(
        kicker="秋のシンポジウム · 2026.10.03", title='<span class="ph">今回は違うか？</span> <span class="ph">ITブームと</span><span class="ph">AIブームの違い</span>',
        lede="川口先生の基調講演、飯沼先生・黒田先生の講演、パネルディスカッション、全体討論。終了後は神楽坂でゼミ会（懇親会）を開きました。",
        chips=["開催済", "14:00–17:00", "26号館11階 1102", "約30名"],
        actions=[("当日の写真", "Kawaguchi_seminar_1003_photos.html", True), ("議事メモ", "Kawaguchi_seminar_minutes.html", False),
                 ("黒田先生の資料（PDF）", KURODA, False)])),
    "Kawaguchi_seminar_1003_en.html": dict(en="Kawaguchi_seminar_1003.html", nav="home", crumb="Autumn symposium", ja=dict(
        kicker="Autumn symposium · 2026.10.03", title="Is this time different? The IT boom vs. the AI boom",
        lede="Keynote by Prof. Kawaguchi, talks by Prof. Iinuma and Prof. Kuroda, a panel and an open discussion — followed by the zemi-kai reception in Kagurazaka.",
        chips=["Held", "14:00–17:00", "Bldg 26, 11F, Room 1102", "about 30 people"],
        actions=[("Photos", "Kawaguchi_seminar_1003_photos.html", True), ("Minutes", "Kawaguchi_seminar_minutes.html", False),
                 ("Prof. Kuroda's slides (PDF)", KURODA, False)])),
    "Kawaguchi_seminar_prev.html": dict(en="Kawaguchi_seminar_prev_en.html", nav="home", crumb="第4回", ja=dict(
        kicker="第4回 研究会 · 2026.07.18", title='<span class="ph">ループ・</span><span class="ph">エンジニアリング</span><span class="ph">演習</span>',
        lede="企業におけるAI活用 — DXからAXへ。当日スライド、事前資料、第3回後アンケートの結果をまとめています。",
        chips=["開催済", "10:30〜", "早稲田大学 26号館13階"],
        actions=[("議事メモを読む", "Kawaguchi_seminar_minutes4.html", True)])),
    "Kawaguchi_seminar_prev_en.html": dict(en="Kawaguchi_seminar_prev.html", nav="home", crumb="4th meeting", ja=dict(
        kicker="4th meeting · 2026.07.18", title="The loop-engineering exercise",
        lede="AI in the enterprise — from DX to AX. Slides from the day, pre-reads and the results of the survey taken after the 3rd meeting.",
        chips=["Held", "10:30–", "Waseda Univ., Bldg 26, 13F"],
        actions=[("Read the minutes", "Kawaguchi_seminar_minutes4.html", True)])),
    "Kawaguchi_seminar_papers.html": dict(en="Kawaguchi_seminar_papers_en.html", nav="library", subnav=True, ja=dict(
        kicker="資料庫", title="過去資料アーカイブ",
        lede="各回の事前読了資料。論文、川口先生の配布資料、メンタルモデルの教材をまとめています。", chips=[], actions=[])),
    "Kawaguchi_seminar_papers_en.html": dict(en="Kawaguchi_seminar_papers.html", nav="library", subnav=True, ja=dict(
        kicker="Library", title="Archive of past materials",
        lede="Pre-reads for each meeting: papers, Prof. Kawaguchi's handouts and mental-model teaching material.", chips=[], actions=[])),
    "Kawaguchi_seminar_melmaga.html": dict(en="Kawaguchi_seminar_melmaga_en.html", nav="library", subnav=True, ja=dict(
        kicker="資料庫", title="関連メルマガ",
        lede="議論の前提となった川口先生のメルマガから、今回の議論に関わる回を抜粋しています。", chips=[], actions=[])),
    "Kawaguchi_seminar_melmaga_en.html": dict(en="Kawaguchi_seminar_melmaga.html", nav="library", subnav=True, ja=dict(
        kicker="Library", title="Related newsletters",
        lede="Excerpts from Prof. Kawaguchi's newsletter that frame the discussions.", chips=[], actions=[])),
}
MINUTES = {  # stem → (JA 回, JA 日付, EN 回, EN date)
    "": ("秋のシンポジウム", "2026年10月3日", "Autumn symposium", "October 3, 2026"),
    "5": ("第5回", "2026年8月22日", "5th meeting", "August 22, 2026"),
    "4": ("第4回", "2026年7月18日", "4th meeting", "July 18, 2026"),
    "3": ("第3回", "2026年6月20日", "3rd meeting", "June 20, 2026"),
    "2": ("第2回", "2026年5月9日", "2nd meeting", "May 9, 2026"),
    "1": ("第1回", "2026年4月11日", "1st meeting", "April 11, 2026"),
}
for k, (jn, jd, en_n, en_d) in MINUTES.items():
    ja_file = f"Kawaguchi_seminar_minutes{k}.html"
    en_file = {"": "Kawaguchi_seminar_minutes_en.html", "1": "Kawaguchi_seminar_minutes1_en.html", "2": "Kawaguchi_seminar_minutes2_en.html",
               "3": "Kawaguchi_seminar_minutes3_en.html"}.get(k, "Kawaguchi_seminar_minutes_en.html")
    PAGES[ja_file] = dict(en=en_file, nav="minutes", ja=dict(
        kicker=f"議事メモ · {jn}", title=f"{jn} 議事メモ" if k else "秋のシンポジウム 議事メモ",
        lede=f"{jd}の議論の記録です。ページ内のタブで、第1〜5回とシンポジウムを切り替えられます。", chips=[], actions=[]))
# 英語の議事メモは 1〜3 回と「第4回（minutes_en）」のみ
for k, (jn, jd, en_n, en_d) in MINUTES.items():
    if k in ("1", "2", "3"):
        PAGES[f"Kawaguchi_seminar_minutes{k}_en.html"] = dict(en=f"Kawaguchi_seminar_minutes{k}.html", nav="minutes", ja=dict(
            kicker=f"Minutes · {en_n}", title=f"Minutes of the {en_n}", lede=f"Record of the discussion on {en_d}. Use the tabs on this page to move between meetings.", chips=[], actions=[]))
PAGES["Kawaguchi_seminar_minutes_en.html"] = dict(en="Kawaguchi_seminar_minutes.html", nav="minutes", ja=dict(
    kicker="Minutes · 4th meeting", title="Minutes of the 4th meeting",
    lede="Record of the discussion on July 18, 2026. Use the tabs on this page to move between meetings.", chips=[], actions=[]))

STRINGS = {
    "ja": dict(lang="ja", skip="本文へ移動", menu="メニュー", other="EN", other_label="English", home_crumb="開催記録", lib_crumb="資料庫",
               foot="参加者限定 ／ 転載禁止 ／ 著作権は各論文の権利者に帰属", updated="最終更新", brand="AIx知的鍛錬塾"),
    "en": dict(lang="en", skip="Skip to content", menu="Menu", other="JA", other_label="日本語", home_crumb="Sessions", lib_crumb="Library",
               foot="Participants only / Do not redistribute / Copyright of each paper remains with its holder", updated="Last updated", brand="AIx Intellectual Forging"),
}


def read(name):
    return io.open(os.path.join(HERE, "theme", name), encoding="utf-8", newline="").read()


def theme_css():
    css = read("forge.css")
    # 日英兼用ページ（写真・T シャツ案）用
    css += "\nhtml[lang=\"ja\"] .en,html[lang=\"en\"] .ja{display:none!important}\n"
    return css


def theme_js():
    return read("forge.js")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def header(lang, active, other_href=None, inpage_lang=False):
    S = STRINGS[lang]
    i = 0 if lang == "ja" else 1
    links = []
    for key, ja, en, jf, ef in NAV:
        label = (ja, en)[i]
        href = (jf, ef)[i]
        cur = ' aria-current="page"' if key == active else ""
        if inpage_lang:
            links.append(f'<a href="{jf}" data-href-ja="{jf}" data-href-en="{ef}"{cur}><span class="ja">{ja}</span><span class="en">{en}</span></a>')
        else:
            links.append(f'<a href="{href}"{cur}>{label}</a>')
    home = NAV[0][3 + i]
    if inpage_lang:
        sw = f'<button class="fg-lang" type="button" data-inpage-lang aria-label="Language">{S["other"]}</button>'
    elif other_href:
        sw = f'<a class="fg-lang" href="{other_href}" lang="{ "en" if lang == "ja" else "ja"}" aria-label="{S["other_label"]}">{S["other"]}</a>'
    else:
        sw = ""
    return ('<!--fg:header--><a class="fg-skip" href="#main">' + S["skip"] + '</a>'
            '<header class="fg-header"><div class="fg-wrap fg-header-in">'
            f'<a class="fg-brand" href="{home}" data-href-ja="{NAV[0][3]}" data-href-en="{NAV[0][4]}">{ANVIL}<span><b>{S["brand"]}</b><small>Kawaguchi Seminar</small></span></a>'
            f'<button class="fg-menu" type="button" aria-expanded="false" aria-controls="fg-nav">{S["menu"]}</button>'
            f'<nav class="fg-nav" id="fg-nav" aria-label="main">{"".join(links)}</nav>{sw}'
            '</div><i class="fg-progress" aria-hidden="true"></i></header><!--/fg:header-->')


def pagehead(lang, meta, updated=None, crumb_parent=None, crumb_label=None):
    S = STRINGS[lang]
    crumb = ""
    if crumb_label and crumb_parent:
        crumb = (f'<nav class="fg-crumb" aria-label="breadcrumb"><a href="{crumb_parent}">{S["home_crumb"]}</a>'
                 f'<span aria-hidden="true">/</span><span>{esc(crumb_label)}</span></nav>')
    chips = "".join(f'<li class="{"is-state" if n == 0 and c in ("開催済", "Held") else ""}">{esc(c)}</li>' for n, c in enumerate(meta["chips"]))
    if updated:
        chips += f'<li>{S["updated"]} {updated}</li>'
    chips = f'<ul class="fg-chips">{chips}</ul>' if chips else ""
    acts = "".join(f'<a class="fg-btn{" is-solid" if solid else ""}" href="{h}">{esc(t)} <span aria-hidden="true">→</span></a>' for t, h, solid in meta["actions"])
    acts = f'<div class="fg-actions">{acts}</div>' if acts else ""
    return ('<!--fg:pagehead--><section class="fg-pagehead"><div class="fg-wrap">' + crumb +
            f'<p class="fg-kicker">{esc(meta["kicker"])}</p><h1>{meta["title"]}</h1>'
            f'<p class="fg-lede">{meta["lede"]}</p>{chips}{acts}</div></section><!--/fg:pagehead-->')


def subnav(lang, current):
    i = 0 if lang == "ja" else 2
    items = "".join(f'<a href="{t[i]}"{" aria-current=\"page\"" if t[i] == current else ""}>{t[i + 1]}</a>' for t in SUBNAV_LIB)
    return f'<!--fg:subnav--><div class="fg-subnav"><div class="fg-wrap">{items}</div></div><!--/fg:subnav-->'


def footer(lang, inpage_lang=False):
    S = STRINGS[lang]
    i = 0 if lang == "ja" else 1
    if inpage_lang:
        nav = "".join(f'<a href="{jf}" data-href-ja="{jf}" data-href-en="{ef}"><span class="ja">{ja}</span><span class="en">{en}</span></a>' for key, ja, en, jf, ef in NAV)
        note = f'<span class="ja">{STRINGS["ja"]["foot"]}</span><span class="en">{STRINGS["en"]["foot"]}</span>'
    else:
        nav = "".join(f'<a href="{(jf, ef)[i]}">{(ja, en)[i]}</a>' for key, ja, en, jf, ef in NAV)
        note = S["foot"]
    return (f'<!--fg:footer--><footer class="fg-footer"><div class="fg-wrap"><span>{note}</span>'
            f'<span class="fg-fnav">{nav}</span></div></footer><!--/fg:footer-->')


def shell_head(title, lang, extra_css=""):
    return ('<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{esc(title)}</title><meta name="color-scheme" content="light">'
            f'<link rel="icon" type="image/svg+xml" href="{FAVICON}">'
            '<script>document.documentElement.classList.add("js")</script>'
            f'{FONTS}<style id="forge-css">{theme_css()}{extra_css}</style>')


def body_script():
    return f'<!--fg:js--><script id="forge-js">{theme_js()}</script><!--/fg:js-->'


# ----------------------------------------------------------------------------
def strip(html, tag):
    return re.sub(rf"<!--fg:{tag}-->.*?<!--/fg:{tag}-->", "", html, flags=re.S)


def apply_to(path):
    name = os.path.basename(path)
    meta_all = PAGES.get(name)
    if not meta_all:
        return None
    lang = "en" if name.endswith("_en.html") else "ja"
    m = meta_all["ja"]
    html = io.open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in html
    html = html.replace("\r\n", "\n")
    html = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", html)  # 旧ナビに残っていた制御文字（□の原因）

    # 旧サブタイトルから「最終更新」だけ拾う
    sub = re.search(r'<p class="subtitle">(.*?)</p>', html, re.S)
    upd = None
    if sub:
        mu = re.search(r"(?:最終更新|Last updated)[:：]\s*(\d{4}-\d{2}-\d{2})", re.sub(r"<[^>]+>", "", sub.group(1)))
        upd = mu.group(1) if mu else None
    if upd is None:  # 2回目以降: 前回つくったページ見出しから拾う
        mu = re.search(r"(?:最終更新|Last updated) (\d{4}-\d{2}-\d{2})", html)
        upd = mu.group(1) if mu else None
    for t in ("header", "pagehead", "subnav", "footer", "js", "head"):
        html = strip(html, t)
    html = html.replace('<main id="main">', "").replace("</main>" + chr(10), "")
    html = re.sub(r'<a class="lang-toggle"[^>]*>.*?</a>\s*', "", html, flags=re.S)
    html = re.sub(r'<nav class="page-nav">.*?</nav>\s*', "", html, flags=re.S)
    html = re.sub(r'<p class="subtitle">.*?</p>\s*', "", html, flags=re.S)
    html = re.sub(r'(<div class="container">\s*)<h1[^>]*>.*?</h1>\s*', r"\1", html, count=1, flags=re.S)
    # <title>
    doc_title = re.sub(r"<[^>]+>", "", m["title"])
    doc_title = re.sub(r"\s+", " ", doc_title).strip() + "｜" + STRINGS[lang]["brand"]
    html = re.sub(r"<title>.*?</title>", lambda _: f"<title>{esc(doc_title)}</title>", html, count=1, flags=re.S)
    head_add = ('<!--fg:head--><script>document.documentElement.classList.add("js")</script>' + FONTS +
                f'<style id="forge-css">{theme_css()}</style><!--/fg:head-->')
    html = html.replace("</head>", head_add + "</head>", 1)
    other = meta_all["en"]
    home = NAV[0][3 if lang == "ja" else 4]
    top = header(lang, meta_all["nav"], other_href=other) + "\n"
    top += pagehead(lang, m, updated=upd, crumb_parent=home, crumb_label=meta_all.get("crumb")) + "\n"
    if meta_all.get("subnav"):
        top += subnav(lang, name) + "\n"
    html = re.sub(r"(<body[^>]*>)", lambda mo: mo.group(1) + "\n" + top + '<main id="main">', html, count=1)
    # 本文の最後（</body> の直前）にフッターとスクリプト。<main> は .container の直後で閉じる
    html = html.replace("</body>", "</main>\n" + footer(lang) + "\n" + body_script() + "\n</body>", 1)
    if crlf:
        html = html.replace("\n", "\r\n")
    io.open(path, "w", encoding="utf-8", newline="").write(html)
    return name


if __name__ == "__main__":
    done = []
    for n in sorted(PAGES):
        p = os.path.join(HERE, n)
        if os.path.exists(p):
            apply_to(p)
            done.append(n)
    print(f"themed {len(done)} pages")
    for n in done:
        print(" ", n)
