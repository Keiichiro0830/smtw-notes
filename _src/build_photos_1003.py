# -*- coding: utf-8 -*-
"""10/3 シンポジウム・ゼミ会の写真ページ（JA/EN 兼用 1 ファイル）を生成する。

入力: 70 Mtg/20261003 シンポジウム/写真/*.heic, *.MOV, *_n.jpg（ローカルのみ・リポジトリ外）
出力: _src/Kawaguchi_seminar_1003_photos.html（写真を base64 で埋め込んだ平文。.gitignore 済み）

公開リポジトリに顔写真を平文で置かないため、このファイルは git に載せない。
staticrypt で暗号化した docs/ 側だけを公開する（手順は末尾の docstring 参照）。

  python _src/build_photos_1003.py
  staticrypt _src/Kawaguchi_seminar_1003_photos.html -p Kawaguchi --short -d encrypted \
      -t _staticrypt_template.html --template-title "知的鍛錬塾 / Kawaguchi Seminar"
  cp encrypted/Kawaguchi_seminar_1003_photos.html docs/

要件: pip install pillow pillow-heif ／ ffmpeg が PATH にあること。
"""
import base64, glob, hashlib, io, os, subprocess, sys, tempfile
from html import escape
from PIL import Image, ImageOps
import pillow_heif

pillow_heif.register_heif_opener()

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "70 Mtg", "20261003 シンポジウム", "写真"))
if not os.path.isdir(SRC):
    SRC = r"C:\Users\keima\OneDrive\Documents\Work\40 Still Modelling The World (SMTW)\70 Mtg\20261003 シンポジウム\写真"
OUT = os.path.join(HERE, "Kawaguchi_seminar_1003_photos.html")

# 集合写真の抜粋（ファイル名の時刻部分）。
#   A: 松前が撮影側で写っていない版 / D: 松前が写っている版 / W: 早稲田の W ポーズ（A と同じ並び）
GROUP = ["080422695", "080423224", "080525829", "080524966", "080527509"]
WPOSE = ["080451277", "080451660"]
PARTY = ["110820184", "110832545", "110834214", "110834648", "110835186", "110837370", "110838050",
         "110838881", "110839540", "110840165", "110840854", "110842227", "110842834", "110843592", "110844112"]
VIDEO = "110822000"

# 当日の様子（講演・パネル・質疑）。メッセンジャー経由の *_n.jpg を、ファイル名順に並べたときの添字で指定。
# 並びはプログラム順の目安（撮影順ではない）。添字 9 は 8 と同一ファイル（"(1)" 付き）なので使わない。
SESSION_ORDER = [16, 11, 20, 24, 18, 19, 7, 0, 6, 12, 17, 21, 13, 14, 2, 22, 1, 4, 3, 5, 10, 15, 8, 23]
SESSION_EDGE, SESSION_Q = 1100, 64

GROUP_EDGE, GROUP_Q = 1280, 68
PARTY_EDGE, PARTY_Q = 860, 66


def src_path(stamp, ext):
    return os.path.join(SRC, f"20261003_{stamp}_iOS.{ext}")


def jpeg_b64(stamp, edge, q):
    im = ImageOps.exif_transpose(Image.open(src_path(stamp, "heic"))).convert("RGB")
    im.thumbnail((edge, edge), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode(), im.size, len(buf.getvalue())


def session_files():
    fs = sorted(glob.glob(os.path.join(SRC, "*_n*.jpg")))
    assert len(fs) == 25, len(fs)
    assert hashlib.md5(open(fs[8], "rb").read()).digest() == hashlib.md5(open(fs[9], "rb").read()).digest()
    return [fs[i] for i in SESSION_ORDER]


def session_b64(path):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    im.thumbnail((SESSION_EDGE, SESSION_EDGE), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=SESSION_Q, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode(), im.size, len(buf.getvalue())


def video_b64():
    with tempfile.TemporaryDirectory() as td:
        mp4, poster = os.path.join(td, "v.mp4"), os.path.join(td, "p.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src_path(VIDEO, "MOV"), "-map", "0:v:0", "-map", "0:a:0",
                        "-vf", "scale=-2:960,fps=30", "-c:v", "libx264", "-crf", "27", "-preset", "slow",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", mp4], check=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1", "-i", mp4, "-frames:v", "1",
                        "-vf", "scale=-2:480", "-q:v", "6", poster], check=True)
        v, p = open(mp4, "rb").read(), open(poster, "rb").read()
    return base64.b64encode(v).decode(), base64.b64encode(p).decode(), len(v)


def figure(b64, size, alt_ja, alt_en, cap_ja, cap_en, name):
    w, h = size
    cap = ""
    if cap_ja:
        cap = (f'<figcaption><span class="ja">{cap_ja}</span><span class="en">{cap_en}</span></figcaption>')
    return (f'<figure class="ph {"land" if w >= h else "port"}">'
            f'<img decoding="async" src="data:image/jpeg;base64,{b64}" width="{w}" height="{h}" '
            f'alt="{escape(alt_ja)} / {escape(alt_en)}" data-name="{name}">{cap}</figure>')


def build():
    sizes = {}
    parts = {"group": [], "w": [], "party": [], "session": []}
    total = 0

    def add(bucket, stamp, edge, q, alt_ja, alt_en, cap_ja="", cap_en=""):
        nonlocal total
        b64, size, n = jpeg_b64(stamp, edge, q)
        total += n
        sizes[stamp] = n
        parts[bucket].append(figure(b64, size, alt_ja, alt_en, cap_ja, cap_en, f"20261003_{stamp}.jpg"))

    for s in GROUP:
        add("group", s, GROUP_EDGE, GROUP_Q, "シンポジウム終了後の集合写真", "Group photo after the symposium")
    for s in WPOSE:
        add("w", s, GROUP_EDGE, GROUP_Q, "早稲田の W を手で組んだ集合写真", "Group photo making the Waseda W sign with our hands")
    for s in PARTY:
        add("party", s, PARTY_EDGE, PARTY_Q, "ゼミ会（神楽坂）の様子", "Scene from the zemi-kai in Kagurazaka")
    for i, path in enumerate(session_files(), 1):
        b64, size, n = session_b64(path)
        total += n
        sizes[f"session{i:02d}"] = n
        parts["session"].append(figure(b64, size, "シンポジウム当日の会場の様子", "Scene from the symposium room",
                                       "", "", f"20261003_symposium_{i:02d}.jpg"))
    vb, pb, vn = video_b64()
    total += vn
    video = (f'<figure class="ph port video"><video controls playsinline preload="metadata" '
             f'poster="data:image/jpeg;base64,{pb}" src="data:video/mp4;base64,{vb}"></video>'
             f'<figcaption><span class="ja">動画（6秒）</span><span class="en">Video (6 s)</span></figcaption></figure>')

    html = TEMPLATE
    html = html.replace("{{GROUP}}", "\n".join(parts["group"]))
    html = html.replace("{{W}}", "\n".join(parts["w"]))
    html = html.replace("{{SESSION}}", chr(10).join(parts["session"]))
    html = html.replace("{{PARTY}}", "\n".join(parts["party"]) + "\n" + video)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"images+video raw bytes: {total:,}  ({total/1e6:.2f} MB)")
    print(f"written {OUT}: {os.path.getsize(OUT):,} bytes")
    for k, v in sizes.items():
        print(" ", k, f"{v/1000:.0f} KB")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>10/3 当日の写真｜AIx知的鍛錬塾</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMiAzMiI+PHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiByeD0iNyIgZmlsbD0iIzFmM2E1ZiIvPjxwYXRoIGQ9Ik0yNCAzIEwyNSA1LjUgTDI3LjUgNiBMMjUgNi41IEwyNCA5IEwyMyA2LjUgTDIwLjUgNiBMMjMgNS41IFoiIGZpbGw9IiNmNTllMGIiLz48cGF0aCBkPSJNMyAxNCBMMTAgMTEgTDI2IDExIEwyNiAxNSBMMjIgMTUgTDIwIDE5IEwyNCAxOSBMMjQuNSAyMyBMNy41IDIzIEw4IDE5IEwxMiAxOSBMMTAgMTUgTDMgMTUgWiIgZmlsbD0iI2ZmZmZmZiIvPjwvc3ZnPg==">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: "Yu Gothic UI", "Yu Gothic", "Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif;
               background: #f8fafc; color: #1a1a1a; line-height: 1.7; padding: 2.5rem 1rem; }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { font-size: 1.6rem; color: #2c5282; margin-bottom: 0.4rem; }
        .subtitle { color: #64748b; font-size: 0.9rem; margin-bottom: 1.6rem; padding-bottom: 0.9rem; border-bottom: 2px solid #2c5282; }
        h2 { font-size: 1.15rem; color: #2c5282; margin-top: 2.2rem; margin-bottom: 0.5rem; padding-left: 0.6rem; border-left: 4px solid #2c5282; }
        p.lead { color: #475569; font-size: 0.92rem; margin-bottom: 0.9rem; }
        a { color: #2c5282; }
        .page-nav { display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:1.6rem; }
        .page-nav a { flex:1 1 0; text-align:center; padding:0.6rem 0.7rem; background:#fff; border:1px solid #e2e8f0; border-radius:8px; color:#2c5282; text-decoration:none; font-size:0.9rem; font-weight:600; white-space:nowrap; }
        .page-nav a:hover { box-shadow:0 2px 8px rgba(0,0,0,0.08); }
        .page-nav a.active { background:#2c5282; color:#fff; border-color:#2c5282; }
        .lang-toggle { position: fixed; top: 1rem; right: 1rem; z-index: 100; padding: 0.5rem 0.9rem; background: #fff;
                       border: 1px solid #cbd5e1; border-radius: 6px; color: #2c5282; font: inherit; font-size: 0.85rem; font-weight: 600;
                       cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,0.08); }
        .lang-toggle:hover { background: #2c5282; color: #fff; border-color: #2c5282; }
        html[lang="ja"] .en, html[lang="en"] .ja { display: none; }
        .gallery { display: grid; gap: 0.8rem; grid-template-columns: repeat(2, 1fr); align-items: start; }
        .gallery.cols3 { grid-template-columns: repeat(3, 1fr); }
        .ph { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.4rem; margin: 0; }
        .ph img, .ph video { display: block; width: 100%; height: auto; border-radius: 4px; cursor: zoom-in; background: #e2e8f0; }
        .ph video { cursor: default; }
        .ph figcaption { font-size: 0.8rem; color: #64748b; padding: 0.3rem 0.2rem 0; }
        @media (max-width: 720px) { .gallery, .gallery.cols3 { grid-template-columns: 1fr 1fr; gap: 0.5rem; } .gallery.group { grid-template-columns: 1fr; } }
        @media (max-width: 600px) { .lang-toggle { top: 0.5rem; right: 0.5rem; padding: 0.4rem 0.7rem; font-size: 0.78rem; } }
        .lb { position: fixed; inset: 0; z-index: 200; display: none; background: rgba(15,23,42,0.92); align-items: center; justify-content: center; flex-direction: column; padding: 1rem; }
        .lb.open { display: flex; }
        .lb img { max-width: 100%; max-height: calc(100vh - 4.5rem); object-fit: contain; }
        .lb .bar { margin-top: 0.7rem; display: flex; gap: 0.6rem; }
        .lb .bar a, .lb .bar button { padding: 0.4rem 0.9rem; background: #fff; border: 1px solid #cbd5e1; border-radius: 6px; color: #2c5282; font: inherit; font-size: 0.85rem; font-weight: 600; text-decoration: none; cursor: pointer; }
        footer { margin-top: 3rem; font-size: 0.8rem; color: #94a3b8; text-align: center; }
    </style>
</head>
<body>
<button class="lang-toggle" id="lang-toggle" type="button">🇬🇧 EN</button>
<div class="container">

    <h1><span class="ja">10月3日 当日の写真</span><span class="en">Photos from October 3</span></h1>
    <p class="subtitle"><span class="ja">秋のシンポジウムの集合写真・当日の様子と、神楽坂でのゼミ会（懇親会）の写真です。写真をクリックすると拡大・保存できます。</span><span class="en">Group photos and scenes from the autumn symposium, and photos from the zemi-kai (reception) in Kagurazaka. Click a photo to enlarge or save it.</span></p>

    <nav class="page-nav">
        <a href="Kawaguchi_seminar.html"><span class="ja">トップ</span><span class="en">Top</span></a>
        <a href="Kawaguchi_seminar_0822.html"><span class="ja">8/22 研究会</span><span class="en">Aug 22</span></a>
        <a href="Kawaguchi_seminar_1003.html" class="active"><span class="ja">10/3 シンポジウム</span><span class="en">Oct 3</span></a>
        <a href="Kawaguchi_seminar_minutes.html"><span class="ja">議事メモ</span><span class="en">Minutes</span></a>
    </nav>

    <h2><span class="ja">集合写真（シンポジウム終了後・26号館 1102）</span><span class="en">Group photos (after the symposium, Room 1102)</span></h2>
    <p class="lead"><span class="ja">撮影者が途中で交代したため、写っているメンバーが写真ごとに少し異なります。両方の版を載せています。</span><span class="en">The photographer changed partway through, so who appears in the frame differs slightly between shots; both versions are included.</span></p>
    <div class="gallery group">
{{GROUP}}
    </div>

    <h2><span class="ja">早稲田の「W」</span><span class="en">The Waseda “W”</span></h2>
    <div class="gallery">
{{W}}
    </div>

    <h2><span class="ja">シンポジウムの様子（講演・パネル・質疑）</span><span class="en">Scenes from the symposium (talks, panel, Q&amp;A)</span></h2>
    <p class="lead"><span class="ja">撮影順ではなく、場面ごとにおおまかに並べています。</span><span class="en">Roughly grouped by scene, not in shooting order.</span></p>
    <div class="gallery">
{{SESSION}}
    </div>

    <h2><span class="ja">ゼミ会（懇親会）— 神楽坂・ALEGRIA</span><span class="en">Zemi-kai — ALEGRIA, Kagurazaka</span></h2>
    <div class="gallery cols3">
{{PARTY}}
    </div>

    <footer><span class="ja">参加者限定 ／ 転載禁止</span><span class="en">Participants only / Do not redistribute</span></footer>
</div>

<div class="lb" id="lb" role="dialog" aria-modal="true">
    <img id="lb-img" alt="">
    <div class="bar"><a id="lb-dl" href="#" download><span class="ja">保存</span><span class="en">Save</span></a><button type="button" id="lb-close"><span class="ja">閉じる</span><span class="en">Close</span></button></div>
</div>

<script>
(function () {
    var root = document.documentElement, btn = document.getElementById("lang-toggle");
    function setLang(l) {
        root.lang = l;
        btn.textContent = l === "ja" ? "🇬🇧 EN" : "🇯🇵 日本語";
        try { localStorage.setItem("smtw_photos_lang", l); } catch (e) {}
    }
    var saved = "ja";
    try { saved = localStorage.getItem("smtw_photos_lang") || ((navigator.language || "").indexOf("ja") === 0 ? "ja" : "en"); } catch (e) {}
    setLang(saved === "en" ? "en" : "ja");
    btn.addEventListener("click", function () { setLang(root.lang === "ja" ? "en" : "ja"); });

    var lb = document.getElementById("lb"), lbImg = document.getElementById("lb-img"), lbDl = document.getElementById("lb-dl");
    function close() { lb.classList.remove("open"); lbImg.removeAttribute("src"); }
    document.addEventListener("click", function (e) {
        var t = e.target;
        if (t.tagName === "IMG" && t.closest(".ph")) {
            lbImg.src = t.src; lbImg.alt = t.alt; lbDl.href = t.src; lbDl.download = t.getAttribute("data-name") || "photo.jpg";
            lb.classList.add("open");
        } else if (t === lb || t.id === "lb-close" || t.closest("#lb-close")) { close(); }
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
