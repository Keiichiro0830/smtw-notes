# -*- coding: utf-8 -*-
"""第4回事前資料: ビデオ講義アーカイブ + 日経記事課題ページを _src に生成する。
入力: Obsidianビデオ講義ノート(+スライドjpg), Vault添付の日経スキャン3点。
出力: _src/Kawaguchi_seminar_video1.html, _src/Kawaguchi_seminar_articles.html
画像はすべて base64 data URI で埋め込み(staticryptで暗号化されるHTML内に閉じる)。
"""
import base64, os, re, sys

SRC = os.path.dirname(os.path.abspath(__file__))
VAULT = r"C:\Users\keima\ObsidianVault"
NOTE = os.path.join(VAULT, r"10 work\40 Still Modelling The World(SMTW)\Kawaguchi Seminar\60 ビデオ講義\2026-06-22 不動産金融市場について（川口有一郎 ビデオ講義）.md")
SLIDES_DIR = os.path.join(VAULT, r"10 work\40 Still Modelling The World(SMTW)\Kawaguchi Seminar\60 ビデオ講義\20260622_不動産金融市場_slides")
ATT0620 = os.path.join(VAULT, r"01 Daily\Kawaguchi Seminar\attachments\2026-06-20")

FAVICON = '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMiAzMiI+PHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiByeD0iNyIgZmlsbD0iIzFmM2E1ZiIvPjxwYXRoIGQ9Ik0yNCAzIEwyNSA1LjUgTDI3LjUgNiBMMjUgNi41IEwyNCA5IEwyMyA2LjUgTDIwLjUgNiBMMjMgNS41IFoiIGZpbGw9IiNmNTllMGIiLz48cGF0aCBkPSJNMyAxNCBMMTAgMTEgTDI2IDExIEwyNiAxNSBMMjIgMTUgTDIwIDE5IEwyNCAxOSBMMjQuNSAyMyBMNy41IDIzIEw4IDE5IEwxMiAxOSBMMTAgMTUgTDMgMTUgWiIgZmlsbD0iI2ZmZmZmZiIvPjwvc3ZnPg==">'

CSS = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: "Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif; background: #f8fafc; color: #1a1a1a; line-height: 1.7; padding: 2.5rem 1rem; }
        .container { max-width: 760px; margin: 0 auto; }
        h1 { font-size: 1.5rem; color: #2c5282; margin-bottom: 0.4rem; }
        .subtitle { color: #64748b; font-size: 0.9rem; margin-bottom: 1.6rem; padding-bottom: 0.9rem; border-bottom: 2px solid #2c5282; }
        h2 { font-size: 1.15rem; color: #2c5282; margin-top: 2rem; margin-bottom: 0.8rem; padding-left: 0.6rem; border-left: 4px solid #2c5282; }
        h3 { font-size: 1rem; color: #1f3a5f; margin-top: 1.6rem; margin-bottom: 0.4rem; }
        p { margin-bottom: 0.8rem; }
        ul { margin-left: 1.4rem; margin-bottom: 0.8rem; }
        li { margin-bottom: 0.3rem; }
        a { color: #2c5282; }
        .backnav { margin-bottom: 1.2rem; font-size: 0.9rem; }
        .infobox { background: #eef2f7; border-left: 4px solid #2c5282; border-radius: 6px; padding: 0.8rem 1rem; font-size: 0.9rem; color: #1f3a5f; margin-bottom: 1.2rem; }
        .slide-img { width: 100%; height: auto; border: 1px solid #e2e8f0; border-radius: 6px; margin: 0.3rem 0 0.6rem; display: block; }
        .ts { color: #94a3b8; font-size: 0.8rem; font-weight: normal; margin-left: 0.5rem; }
        details { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.8rem 1rem; margin: 1rem 0; }
        summary { cursor: pointer; font-weight: 600; color: #1f3a5f; }
        .transcript { margin-top: 0.8rem; font-size: 0.85rem; color: #475569; max-height: 60vh; overflow-y: auto; white-space: pre-wrap; }
        .notice { background: #fff7ed; border: 1px solid #fdba74; border-radius: 8px; padding: 0.8rem 1rem; font-size: 0.85rem; color: #7c2d12; margin: 1.2rem 0; }
        footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 0.8rem; text-align: center; }
"""

def data_uri(path):
    with open(path, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def inline_md(t):
    t = esc(t)
    t = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", t)
    t = re.sub(r"\[\[([^\]]+)\]\]", r"\1", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"\1", t)
    return t

def paras_to_html(lines):
    """Plain lines (no headings/images) -> <p>/<ul> html."""
    out, buf, ul = [], [], []
    def flush_p():
        if buf:
            out.append("<p>" + inline_md(" ".join(buf)) + "</p>")
            buf.clear()
    def flush_ul():
        if ul:
            out.append("<ul>" + "".join("<li>" + inline_md(x) + "</li>" for x in ul) + "</ul>")
            ul.clear()
    for ln in lines:
        s = ln.strip()
        if not s:
            flush_p(); flush_ul(); continue
        if s.startswith("- "):
            flush_p(); ul.append(s[2:]); continue
        flush_ul(); buf.append(s)
    flush_p(); flush_ul()
    return "\n".join(out)

# ---------- parse note ----------
with open(NOTE, encoding="utf-8") as f:
    raw = f.read()

body = raw.split("---", 2)[2]  # drop frontmatter

# 内部メモ由来の文・リンク行を除去
body = body.replace("これは Kei の[[reference_ai_self_review_policy|AI自己検証ポリシー]]と直結する実例。", "")
body = re.sub(r"^- 関連：.*$", "", body, flags=re.M)

def section(name, nxt):
    m = re.search(r"^## " + re.escape(name) + r"\s*$(.*?)(?=^## " + re.escape(nxt) + r"\s*$)", body, re.S | re.M)
    return m.group(1) if m else ""

summary_md = section("全体サマリー", "キーポイント")
keypoints_md = section("キーポイント", "スライド別ハイライト")
m = re.search(r"^## スライド別ハイライト\s*$(.*?)(?=^## スクリプトログ)", body, re.S | re.M)
slides_md = m.group(1)
m = re.search(r"^## スクリプトログ（全文文字起こし）\s*$(.*)", body, re.S | re.M)
transcript_md = m.group(1)
transcript_md = re.sub(r"\n---\s*\n\*この[^*]*\*\s*$", "", transcript_md).strip()

# slides
slide_blocks = re.split(r"^### ", slides_md, flags=re.M)[1:]
slides_html = []
for blk in slide_blocks:
    lines = blk.splitlines()
    head = lines[0]
    hm = re.match(r"(スライド\s*\d+\s*—\s*.*?)[　\s]*`([^`]*)`\s*$", head)
    if hm:
        title, ts = hm.group(1), hm.group(2)
    else:
        title, ts = head, ""
    img = None
    rest = []
    for ln in lines[1:]:
        im = re.match(r"!\[[^\]]*\]\(([^)]+)\)", ln.strip())
        if im:
            img = os.path.join(os.path.dirname(NOTE), im.group(1).replace("/", os.sep))
        else:
            rest.append(ln)
    h = ["<h3>" + inline_md(title) + (f'<span class="ts">{esc(ts)}</span>' if ts else "") + "</h3>"]
    if img:
        h.append(f'<img class="slide-img" loading="lazy" alt="{esc(title)}" src="{data_uri(img)}">')
    h.append(paras_to_html(rest))
    slides_html.append("\n".join(h))

transcript_lines = [ln.strip() for ln in transcript_md.splitlines() if ln.strip()]
transcript_html = esc("\n".join(transcript_lines))

video_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ビデオ講義アーカイブ：2026年6月期 不動産金融市場について ｜ AIx知的鍛錬塾</title>
    {FAVICON}
    <style>{CSS}    </style>
</head>
<body>
<div class="container">
    <h1>ビデオ講義アーカイブ<br>2026年6月期 不動産金融市場について</h1>
    <p class="subtitle">川口有一郎先生 ／ 収録 2026-06-24・約34分・全34スライド ／ YouTube限定公開（現在は非公開）のアーカイブ ／ 参加者限定・転載禁止</p>
    <p class="backnav">← <a href="Kawaguchi_seminar.html">第4回ページに戻る</a>　｜　<a href="Kawaguchi_seminar_papers.html">過去資料</a></p>

    <div class="infobox">このビデオ講義は 2026-06-24 に川口先生が YouTube 限定公開で共有されたもので（6/26 にいったん閉鎖）、現在は視聴できません。本ページはその代替アーカイブとして、全34スライドと講義ノート・自動文字起こしログを収録しています。月次の不動産金融市場解説と、生成AI（Claude）の出力を1問ずつ検証・訂正していく「AIリテラシーの実演」の二段構えです。「LLMの仕組み」三部作（理論）に対する実例側の教材として、第4回のテーマ「企業におけるAI活用」にもつながります。</div>

<h2>全体サマリー</h2>
{paras_to_html(summary_md.splitlines())}

<h2>キーポイント</h2>
{paras_to_html(keypoints_md.splitlines())}

<h2>スライド別ハイライト</h2>
{chr(10).join(slides_html)}

<h2>講義ログ（自動文字起こし・全文）</h2>
    <details>
        <summary>クリックで展開（YouTube自動字幕より作成・タイムスタンプ付き）</summary>
        <div class="transcript">{transcript_html}</div>
    </details>

    <footer>参加者限定 ／ 転載禁止 ／ スライド・講義内容の著作権は川口有一郎先生に帰属 ／ スライド画像は録画から自動抽出、ログは自動字幕（誤変換を含みます）</footer>
</div>
</body>
</html>
"""

with open(os.path.join(SRC, "Kawaguchi_seminar_video1.html"), "w", encoding="utf-8") as f:
    f.write(video_html)
print("video page written:", len(video_html), "chars,", len(slides_html), "slides")

# ---------- articles page ----------
arts = [
    ("日経 2026-06-17「株式と債券の動きに矛盾」（1）",
     os.path.join(ATT0620, "スキャン_20260617日経0617株式と債券の動きに矛盾（１）.jpg")),
    ("日経 2026-06-17「株式と債券の動きに矛盾」（2）",
     os.path.join(ATT0620, "スキャン_20260617 (2)日経0617株式と債券の動きに矛盾（２）.jpg")),
    ("日経 2026-06-14「バブルマネー争奪」— 世界のマネーサプライ（M2）推移グラフ",
     os.path.join(ATT0620, "スキャン_20260620日経0614バブルマネー争奪＿M2グラフ.jpg")),
]
arts_html = []
for title, path in arts:
    arts_html.append(f"<h3>{esc(title)}</h3>\n<img class=\"slide-img\" loading=\"lazy\" alt=\"{esc(title)}\" src=\"{data_uri(path)}\">")

articles_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>日経記事×AI 課題 ｜ AIx知的鍛錬塾</title>
    {FAVICON}
    <style>{CSS}    </style>
</head>
<body>
<div class="container">
    <h1>日経記事×AI 課題（第4回 事前資料）</h1>
    <p class="subtitle">川口先生 2026-06-20 メール共有 ／ 参加者限定・転載禁止</p>
    <p class="backnav">← <a href="Kawaguchi_seminar.html">第4回ページに戻る</a>　｜　<a href="Kawaguchi_seminar_papers.html">過去資料</a></p>

    <div class="infobox">第3回のランチ後に出た「日経記事×AI」メルマガ企画案を受けて、川口先生が例として挙げた日経記事のスキャンです。<strong>課題：お時間のあるときに、下の新聞記事を自分のAI（Claude / Gemini / ChatGPT など）に読み込ませて、記事を評価させてみてください。</strong>その結果を第4回の議論やコメントフォームにお寄せいただければ、格好の題材になります。</div>

    <p>3枚目は世界のマネーサプライ（M2）の推移を示すグラフ（日経新聞）で、先生が第3回で言及された「大量にお札を刷った」ことの一つの証拠です。なお先生ご自身が月次M2データを Claude や Gemini に作成させようとしたところ失敗した、との付記もありました——データの実在性・出所を確かめずに生成AIに数値を作らせることの危うさを示す好例でもあります。</p>

{chr(10).join(arts_html)}

    <div class="notice">新聞記事のスキャンは著作権保護の観点から、この暗号化ページ内にのみ埋め込んでいます（画像ファイルとしては公開していません）。ダウンロード・再配布・SNS等への転載はお控えください。</div>

    <footer>参加者限定 ／ 転載禁止 ／ 記事の著作権は日本経済新聞社に帰属</footer>
</div>
</body>
</html>
"""

with open(os.path.join(SRC, "Kawaguchi_seminar_articles.html"), "w", encoding="utf-8") as f:
    f.write(articles_html)
print("articles page written:", len(articles_html), "chars")
