# -*- coding: utf-8 -*-
"""
build_boj_watcher.py — 知的鍛錬塾HP「日銀ウォッチャー」ページ生成スクリプト

BOJ Watch (daily-log) が吐く公開安全 export (seminar_feed.json) を読み、
既存サイト (Kawaguchi_seminar*.html) と同じデザイン語彙で
日銀ウォッチャー・ページ (Kawaguchi_seminar_boj.html) を生成する。

- 冪等: 同じ入力からは同一出力（now() などの揮発値を出力に含めない。
  「最終更新」は feed の "generated" 値をそのまま使う）。
- Windows cp932 回避のため入出力は明示的に UTF-8。
- 日銀公式 (boj.or.jp) 以外の URL は掲出しない（データ契約: 全て boj_official）。

データ契約は brief §3 に準拠:
  40 Wiki/_setup/BOJ Watch — 知的鍛錬塾HP連携ブリーフ.md
"""

import html
import json
import os
import sys
from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlparse

# ---- パス定数（Vault の export を正本として読む。疎結合＝ファイル受け渡し） ----
FEED_PATH = r"C:\Users\keima\ObsidianVault\40 Wiki\BOJ Watch\_export\seminar_feed.json"
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Kawaguchi_seminar_boj.html")

# 日銀公式ホスト許可リスト（これ以外は掲出しない）
ALLOWED_HOSTS = {"www.boj.or.jp", "boj.or.jp"}

# カテゴリ → バッジ CSS クラス（distinct colors）
CATEGORY_BADGE = OrderedDict([
    ("金融政策", "cat-mp"),
    ("講演・記者会見", "cat-speech"),
    ("統計", "cat-stats"),
    ("論文・レポート", "cat-paper"),
    ("その他", "cat-other"),
])

# 既存ポータルと同一の anvil favicon（視覚的アイデンティティを踏襲）
FAVICON = (
    "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMiAzMiI+"
    "PHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiByeD0iNyIgZmlsbD0iIzFmM2E1ZiIvPjxwYXRoIGQ9Ik0yNCAzIEwyNSA1LjUgTDI3LjUg"
    "NiBMMjUgNi41IEwyNCA5IEwyMyA2LjUgTDIwLjUgNiBMMjMgNS41IFoiIGZpbGw9IiNmNTllMGIiLz48cGF0aCBkPSJNMyAxNCBMMTAgMTEg"
    "TDI2IDExIEwyNiAxNSBMMjIgMTUgTDIwIDE5IEwyNCAxOSBMMjQuNSAyMyBMNy41IDIzIEw4IDE5IEwxMiAxOSBMMTAgMTUgTDMgMTUgWiIg"
    "ZmlsbD0iI2ZmZmZmZiIvPjwvc3ZnPg=="
)

WEEKDAY_JP = ["月", "火", "水", "木", "金", "土", "日"]


def esc(s):
    """テキスト用 HTML エスケープ。"""
    return html.escape("" if s is None else str(s), quote=False)


def esc_attr(s):
    """属性値用 HTML エスケープ。"""
    return html.escape("" if s is None else str(s), quote=True)


def host_ok(url):
    try:
        return urlparse(url).netloc.lower() in ALLOWED_HOSTS
    except Exception:
        return False


def jp_date_label(iso):
    """'2026-06-16' -> '6月16日（火）'"""
    d = datetime.strptime(iso, "%Y-%m-%d")
    return "{}月{}日（{}）".format(d.month, d.day, WEEKDAY_JP[d.weekday()])


def jp_month_label(ym):
    """'2026-06' -> '2026年6月'"""
    y, m = ym.split("-")
    return "{}年{}月".format(int(y), int(m))


CSS = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: "Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif;
            background: #f8fafc;
            color: #1a1a1a;
            line-height: 1.7;
            padding: 2.5rem 1rem;
        }
        .container { max-width: 760px; margin: 0 auto; }
        h1 { font-size: 1.6rem; color: #2c5282; margin-bottom: 0.4rem; }
        .subtitle {
            color: #64748b;
            font-size: 0.9rem;
            margin-bottom: 1.6rem;
            padding-bottom: 0.9rem;
            border-bottom: 2px solid #2c5282;
        }
        h2 {
            font-size: 1.15rem;
            color: #2c5282;
            margin-top: 2rem;
            margin-bottom: 0.8rem;
            padding-left: 0.6rem;
            border-left: 4px solid #2c5282;
            scroll-margin-top: 1rem;
        }
        h3.boj-date-group {
            font-size: 0.9rem;
            color: #1f3a5f;
            margin-top: 1.2rem;
            margin-bottom: 0.5rem;
            font-family: "Helvetica Neue", Arial, sans-serif;
        }
        a { color: #2c5282; }
        a:hover { text-decoration: underline; }
        .page-nav { display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:1.6rem; }
        .page-nav a { flex:1 1 0; text-align:center; padding:0.6rem 0.7rem; background:#fff; border:1px solid #e2e8f0; border-radius:8px; color:#2c5282; text-decoration:none; font-size:0.9rem; font-weight:600; white-space:nowrap; }
        .page-nav a:hover { box-shadow:0 2px 8px rgba(0,0,0,0.08); text-decoration:none; }
        .page-nav a.active { background:#2c5282; color:#fff; border-color:#2c5282; }
        .callout {
            background: #fff8e1;
            border-left: 4px solid #f59e0b;
            padding: 0.75rem 1rem;
            margin: 1rem 0 1.4rem;
            font-size: 0.9rem;
            color: #5b4a2f;
        }
        .legend { display:flex; flex-wrap:wrap; gap:0.5rem; margin: 0 0 1.2rem; }
        .month-index { display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.4rem; }
        .month-index a { font-size:0.85rem; color:#2c5282; background:#eef2f7; border:1px solid #e2e8f0; border-radius:5px; padding:0.25rem 0.7rem; text-decoration:none; }
        .month-index a:hover { background:#dbe4f0; text-decoration:none; }
        .boj-badge {
            display:inline-block;
            font-size:0.72rem;
            font-weight:600;
            padding:0.12rem 0.55rem;
            border-radius:3px;
            color:#fff;
            font-family:"Helvetica Neue", Arial, sans-serif;
            white-space:nowrap;
        }
        .cat-mp     { background:#2c5282; }
        .cat-speech { background:#0f766e; }
        .cat-stats  { background:#b45309; }
        .cat-paper  { background:#6d28d9; }
        .cat-other  { background:#475569; }
        .boj-item {
            background:#fff;
            border:1px solid #e2e8f0;
            border-radius:8px;
            padding:1rem 1.2rem;
            margin-bottom:0.9rem;
        }
        .boj-item .boj-meta { display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem; }
        .boj-item .boj-date { color:#64748b; font-size:0.82rem; font-family:"Helvetica Neue", Arial, sans-serif; }
        .boj-item .boj-title { font-weight:600; color:#1f3a5f; margin-bottom:0.5rem; }
        .boj-item .boj-summary { font-size:0.92rem; color:#334155; margin-bottom:0.5rem; }
        .boj-commentary {
            background:#f0f5fb;
            border-left:4px solid #2c5282;
            padding:0.55rem 0.8rem;
            margin:0.5rem 0;
            font-size:0.9rem;
            color:#1f3a5f;
        }
        .boj-commentary .lbl { font-weight:600; margin-right:0.4rem; }
        .boj-links { margin-top:0.5rem; }
        .boj-links a.boj-official {
            display:inline-block;
            padding:0.35rem 0.85rem;
            background:#2c5282;
            color:#fff;
            border-radius:4px;
            font-size:0.85rem;
            text-decoration:none;
        }
        .boj-links a.boj-official:hover { background:#1f3a5f; text-decoration:none; }
        .boj-tags { margin-top:0.5rem; }
        .boj-tags .tag {
            display:inline-block;
            font-size:0.75rem;
            color:#64748b;
            background:#eef2f7;
            border:1px solid #e2e8f0;
            border-radius:3px;
            padding:0.05rem 0.45rem;
            margin-right:0.3rem;
        }
        footer {
            margin-top: 3rem;
            font-size: 0.8rem;
            color: #94a3b8;
            text-align: center;
        }
"""


def render_item(it):
    cat = it.get("category", "その他")
    badge_cls = CATEGORY_BADGE.get(cat, "cat-other")
    title = it.get("title", "").strip()
    summary = it.get("summary", "").strip()
    commentary = it.get("commentary", "").strip()
    url = it.get("url", "").strip()
    tags = it.get("tags", []) or []

    parts = []
    parts.append('  <article class="boj-item" data-cat="{}">'.format(esc_attr(cat)))
    parts.append('    <div class="boj-meta">')
    parts.append('      <span class="boj-date">{}</span>'.format(esc(it.get("date", ""))))
    parts.append('      <span class="boj-badge {}">{}</span>'.format(badge_cls, esc(cat)))
    parts.append('    </div>')
    parts.append('    <div class="boj-title">{}</div>'.format(esc(title)))
    # summary はタイトルと異なる場合のみ表示（重複回避）
    if summary and summary != title:
        parts.append('    <p class="boj-summary">{}</p>'.format(esc(summary)))
    # 短評は存在する場合のみ表示（自作の中立的コメント）
    if commentary:
        parts.append(
            '    <div class="boj-commentary"><span class="lbl">短評</span>{}</div>'.format(esc(commentary))
        )
    # 日銀公式リンク（許可ホストのみ）
    if url and host_ok(url):
        parts.append('    <div class="boj-links">')
        parts.append(
            '      <a class="boj-official" href="{}" target="_blank" rel="noopener">日銀公式 →</a>'.format(esc_attr(url))
        )
        parts.append('    </div>')
    # タグ
    if tags:
        tag_html = "".join('<span class="tag">{}</span>'.format(esc(t)) for t in tags)
        parts.append('    <div class="boj-tags">{}</div>'.format(tag_html))
    parts.append('  </article>')
    return "\n".join(parts)


def build(feed):
    items = feed.get("items", [])
    generated = feed.get("generated", "")

    # 掲出は signal=="high" のみ（データ契約）＋日銀公式ホストのみ
    rendered = [it for it in items if it.get("signal") == "high" and host_ok(it.get("url", ""))]
    skipped = [it for it in items if it not in rendered]

    # 日付降順（新しい順）。同日は元の feed 順を安定的に保持。
    indexed = list(enumerate(rendered))
    indexed.sort(key=lambda p: (p[1].get("date", ""), -p[0]), reverse=True)
    ordered = [it for _, it in indexed]

    # 月別グルーピング（新しい月が先頭）
    months = OrderedDict()
    for it in ordered:
        ym = it.get("date", "")[:7]
        months.setdefault(ym, []).append(it)

    # --- 本文組み立て ---
    body = []

    # ページ内ナビ（既存ポータルと同じ page-nav 語彙。ここでは日銀ウォッチャーが active）
    body.append('    <nav class="page-nav">')
    body.append('        <a href="Kawaguchi_seminar.html">ポータル</a>')
    body.append('        <a href="Kawaguchi_seminar_papers.html">過去資料</a>')
    body.append('        <a href="Kawaguchi_seminar_minutes.html">議事メモ</a>')
    body.append('        <a href="Kawaguchi_seminar_boj.html" class="active">日銀ウォッチャー</a>')
    body.append('    </nav>')

    # 中立的な導入文（教育目的・投資推奨ではない）
    body.append('    <div class="callout">')
    body.append('      当コーナーは、日本銀行の公式発表（金融政策・講演・統計・調査論文等）のうち'
                '注目度の高い更新を、勉強会の読み物として中立・教育目的で整理したものです。'
                '<strong>投資助言・推奨ではありません。</strong>'
                '本文・資料は再掲せず、要点のみを添えて日銀公式ページへリンクします'
                '（一次情報は必ずリンク先の原文をご確認ください）。'
                '各項目の「短評」（メンタルモデルで読むための補助線）は順次追加していきます。')
    body.append('    </div>')

    # カテゴリ凡例
    body.append('    <div class="legend">')
    for cat, cls in CATEGORY_BADGE.items():
        body.append('      <span class="boj-badge {}">{}</span>'.format(cls, esc(cat)))
    body.append('    </div>')

    # 月インデックス（アーカイブ用アンカー）
    if len(months) > 1:
        body.append('    <div class="month-index">')
        for ym in months:
            body.append('      <a href="#m-{}">{}</a>'.format(ym, esc(jp_month_label(ym))))
        body.append('    </div>')

    # 月セクション → 日付サブグループ → カード
    for ym, mitems in months.items():
        body.append('    <h2 id="m-{}">{}</h2>'.format(ym, esc(jp_month_label(ym))))
        last_date = None
        for it in mitems:
            d = it.get("date", "")
            if d != last_date:
                body.append('    <h3 class="boj-date-group">{}</h3>'.format(esc(jp_date_label(d))))
                last_date = d
            body.append(render_item(it))

    subtitle = "日本銀行 新着情報のうち注目度の高い更新を、勉強会向けに中立・教育目的で整理"
    if generated:
        subtitle += " ／ 最終更新: {}".format(esc(generated))
    subtitle += " ／ 掲載 {} 件".format(len(ordered))

    doc = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>日銀ウォッチャー ｜ AIx知的鍛錬塾</title>
    <meta name="robots" content="noindex, nofollow">
    <link rel="icon" type="image/svg+xml" href="{favicon}">
    <style>{css}    </style>
</head>
<body>
<div class="container">
    <h1>日銀ウォッチャー</h1>
    <p class="subtitle">{subtitle}</p>
{body}
    <footer>参加者限定 ／ 出典: 日本銀行 (www.boj.or.jp) ／ 要約・短評は当塾による中立的整理（投資助言ではありません）</footer>
</div>
</body>
</html>
""".format(favicon=FAVICON, css=CSS, subtitle=subtitle, body="\n".join(body))

    return doc, len(ordered), skipped


def main():
    with open(FEED_PATH, "r", encoding="utf-8") as f:
        feed = json.load(f)

    doc, n_rendered, skipped = build(feed)

    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)

    print("[build_boj_watcher] wrote:", OUT_PATH)
    print("[build_boj_watcher] items rendered:", n_rendered)
    if skipped:
        print("[build_boj_watcher] WARNING skipped (non-high or non-boj host):", len(skipped))
        for it in skipped:
            print("   -", it.get("date"), it.get("signal"), it.get("url"))
    else:
        print("[build_boj_watcher] all feed items passed contract (signal=high, host=boj.or.jp)")


if __name__ == "__main__":
    main()
