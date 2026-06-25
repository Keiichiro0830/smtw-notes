# -*- coding: utf-8 -*-
"""既存ポータル各ページの .page-nav に「リスクプレミア」タブを追加し、
   docs/index.html（平文ランディング）に特別セクションのカードを追加する。冪等。"""
import io, os, re, glob
ROOT = os.path.dirname(os.path.abspath(__file__))   # _src
REPO = os.path.dirname(ROOT)
DOCS = os.path.join(REPO, "docs")

JP_HREF = "Kawaguchi_seminar_riskpremia.html"
EN_HREF = "Kawaguchi_seminar_riskpremia_en.html"

def patch_nav():
    nav_close = re.compile(r'(\n[ \t]*)</nav>')
    for path in sorted(glob.glob(os.path.join(ROOT, "Kawaguchi_seminar*.html"))):
        base = os.path.basename(path)
        if "riskpremia" in base:
            continue
        t = io.open(path, encoding="utf-8").read()
        if 'class="page-nav"' not in t:
            continue
        is_en = base.endswith("_en.html")
        href = EN_HREF if is_en else JP_HREF
        label = "Risk Premia" if is_en else "リスクプレミア"
        if href in t:
            print("skip(already)", base); continue
        link = '\n        <a href="%s">%s</a>' % (href, label)
        new, n = nav_close.subn(lambda m: link + m.group(0), t, count=1)
        if n:
            io.open(path, "w", encoding="utf-8", newline="\n").write(new)
            print("nav patched:", base)
        else:
            print("no </nav>:", base)

def patch_index():
    path = os.path.join(DOCS, "index.html")
    t = io.open(path, encoding="utf-8").read()
    if JP_HREF in t:
        print("skip(already) index.html"); return
    card = (
        '        <li>\n'
        '            <a href="%s">\n'
        '                <span class="date">特別セクション</span><br>\n'
        '                リスクプレミア分析 — 日本株の鍵リスク（東証33業種 × マクロAPT, 1987–2026）\n'
        '            </a>\n'
        '        </li>\n' % JP_HREF)
    marker = '<ul class="meeting-list">\n'
    i = t.find(marker)
    if i == -1:
        print("index.html: marker not found"); return
    j = i + len(marker)
    new = t[:j] + card + t[j:]
    io.open(path, "w", encoding="utf-8", newline="\n").write(new)
    print("index.html card added")

if __name__ == "__main__":
    patch_nav()
    patch_index()
