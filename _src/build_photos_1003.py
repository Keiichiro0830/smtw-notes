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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import portal_shell as S
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



def figure(b64, size, alt_ja, alt_en, cap_ja, cap_en, name, span=None):
    w, h = size
    cap = ""
    if cap_ja:
        cap = (f'<figcaption><span class="ja">{cap_ja}</span><span class="en">{cap_en}</span></figcaption>')
    style = f' style="grid-column:span {span}"' if span else ""
    return (f'<figure class="shot {"land" if w >= h else "port"} fg-reveal"{style}>'
            f'<img decoding="async" src="data:image/jpeg;base64,{b64}" width="{w}" height="{h}" '
            f'alt="{escape(alt_ja)} / {escape(alt_en)}" data-zoom data-name="{name}">{cap}</figure>')


def build():
    sizes = {}
    parts = {"group": [], "w": [], "party": [], "session": []}
    total = 0

    def add(bucket, stamp, edge, q, alt_ja, alt_en, cap_ja="", cap_en="", span=None):
        nonlocal total
        b64, size, n = jpeg_b64(stamp, edge, q)
        total += n
        sizes[stamp] = n
        parts[bucket].append(figure(b64, size, alt_ja, alt_en, cap_ja, cap_en, f"20261003_{stamp}.jpg", span))

    for n, s in enumerate(GROUP):
        add("group", s, GROUP_EDGE, GROUP_Q, "シンポジウム終了後の集合写真", "Group photo after the symposium", span=6 if n < 2 else 4)
    for s in WPOSE:
        add("w", s, GROUP_EDGE, GROUP_Q, "早稲田の W を手で組んだ集合写真", "Group photo making the Waseda W sign with our hands", span=6)
    for s in PARTY:
        add("party", s, PARTY_EDGE, PARTY_Q, "ゼミ会（神楽坂）の様子", "Scene from the zemi-kai in Kagurazaka", span=3)
    for i, path in enumerate(session_files(), 1):
        b64, size, n = session_b64(path)
        total += n
        sizes[f"session{i:02d}"] = n
        parts["session"].append(figure(b64, size, "シンポジウム当日の会場の様子", "Scene from the symposium room",
                                       "", "", f"20261003_symposium_{i:02d}.jpg", span=4))
    vb, pb, vn = video_b64()
    total += vn
    video = (f'<figure class="shot port video fg-reveal" style="grid-column:span 3"><video controls playsinline preload="metadata" '
             f'poster="data:image/jpeg;base64,{pb}" src="data:video/mp4;base64,{vb}"></video>'
             f'<figcaption><span class="ja">動画（6秒）</span><span class="en">Video (6 s)</span></figcaption></figure>')

    body = BODY
    body = body.replace("{{W}}", "\n".join(parts["w"]))
    body = body.replace("{{GROUP}}", "\n".join(parts["group"]))
    body = body.replace("{{SESSION}}", "\n".join(parts["session"]))
    body = body.replace("{{PARTY}}", "\n".join(parts["party"]) + "\n" + video)
    html = ('<!DOCTYPE html>\n<html lang="ja"><head>'
            + S.shell_head("10/3 当日の写真｜AIx知的鍛錬塾 / Photos from October 3", "ja", CSS)
            + '</head>\n<body>\n' + S.header("ja", "photos", inpage_lang=True) + '\n<main id="main">\n' + body
            + '\n</main>\n' + S.footer("ja", inpage_lang=True) + "\n" + S.body_script() + "\n</body></html>\n")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"images+video raw bytes: {total:,}  ({total/1e6:.2f} MB)")
    print(f"written {OUT}: {os.path.getsize(OUT):,} bytes")


CSS = """
.ph-pagehead .fg-wrap{padding-bottom:clamp(110px,14vw,170px)}
.ph-final{position:relative;z-index:3;margin-top:calc(-1 * clamp(84px,11vw,140px))}
.ph-t{display:inline-block}
.ph-grid{display:grid;grid-template-columns:repeat(12,1fr);gap:14px;align-items:start}
.shot{margin:0;background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden;box-shadow:var(--shadow);display:flex;flex-direction:column}
.shot img,.shot video{display:block;width:100%;height:auto;background:#d9d4c5;transition:transform .6s var(--ease)}
.shot:hover img{transform:scale(1.02)}
.shot figcaption{padding:.55rem .9rem .7rem;font-size:.84rem;color:var(--muted);border-top:1px solid var(--line)}
.ph-final .ph-grid{gap:16px}
.ph-final .shot{border-radius:var(--r-lg);box-shadow:0 50px 100px -40px rgba(11,18,36,.7)}
@media (max-width:860px){.ph-grid{grid-template-columns:1fr 1fr}.ph-grid > *{grid-column:auto!important}.ph-final .ph-grid{grid-template-columns:1fr}}
"""

BODY = """<section class="fg-pagehead ph-pagehead"><div class="fg-wrap">
 <p class="fg-kicker"><span class="ja">2026.10.03 · 秋のシンポジウムとゼミ会</span><span class="en">2026.10.03 · Autumn symposium and zemi-kai</span></p>
 <h1><span class="ja"><span class="ph-t">10月3日の</span><span class="ph-t">写真</span></span><span class="en">Photos from <em>October 3</em></span></h1>
 <p class="fg-lede"><span class="ja">シンポジウム終了後の集合写真、会場の様子、そして神楽坂のゼミ会（懇親会）。写真をクリックすると拡大・保存できます。</span><span class="en">Group photos after the symposium, scenes from the room, and the zemi-kai in Kagurazaka. Click a photo to enlarge or save it.</span></p>
 <ul class="fg-chips"><li><span class="ja">写真 46枚</span><span class="en">46 photos</span></li><li><span class="ja">動画 1本</span><span class="en">1 video</span></li></ul>
 <div class="fg-actions"><a class="fg-btn is-solid" href="#group"><span class="ja">集合写真</span><span class="en">Group photos</span> <span aria-hidden="true">↓</span></a><a class="fg-btn" href="#room"><span class="ja">シンポジウムの様子</span><span class="en">The symposium</span></a><a class="fg-btn" href="#party"><span class="ja">ゼミ会</span><span class="en">Zemi-kai</span></a></div>
</div></section>
<div class="fg-wrap ph-final"><div class="ph-grid">
{{W}}
</div></div>

<section class="fg-section" id="group"><div class="fg-wrap">
 <div class="fg-reveal"><p class="fg-eyebrow"><span class="ja">集合写真</span><span class="en">Group photos</span></p>
 <h2 class="fg-h2"><span class="ja">全員で、<em>1102</em>にて。</span><span class="en">All together, in <em>Room 1102</em>.</span></h2>
 <p class="fg-sub"><span class="ja">撮影者が途中で交代したため、写っているメンバーが写真ごとに少し異なります。両方の版を載せています。上の2枚は、早稲田の「W」を手で組んだ写真です。</span><span class="en">The photographer changed partway through, so who appears in the frame differs slightly between shots; both versions are included. The two photos above show the Waseda “W” made with our hands.</span></p></div>
 <div class="ph-grid">
{{GROUP}}
 </div>
</div></section>

<section class="fg-section is-alt" id="room"><div class="fg-wrap">
 <div class="fg-reveal"><p class="fg-eyebrow"><span class="ja">シンポジウムの様子</span><span class="en">The symposium</span></p>
 <h2 class="fg-h2"><span class="ja">講演、パネル、<em>質疑</em>。</span><span class="en">Talks, panel and <em>Q&amp;A</em>.</span></h2>
 <p class="fg-sub"><span class="ja">撮影順ではなく、場面ごとにおおまかに並べています。</span><span class="en">Roughly grouped by scene, not in shooting order.</span></p></div>
 <div class="ph-grid">
{{SESSION}}
 </div>
</div></section>

<section class="fg-section" id="party"><div class="fg-wrap">
 <div class="fg-reveal"><p class="fg-eyebrow"><span class="ja">ゼミ会（懇親会）</span><span class="en">Zemi-kai</span></p>
 <h2 class="fg-h2"><span class="ja">神楽坂、<em>ALEGRIA</em>。</span><span class="en">Kagurazaka, <em>ALEGRIA</em>.</span></h2>
 <p class="fg-sub"><span class="ja">「2026年 川口ゼミ懇親会」のプレートと花火で。最後に動画が1本あります。</span><span class="en">With a plate marked “2026 Kawaguchi Seminar reception” and a sparkler. One short video at the end.</span></p></div>
 <div class="ph-grid">
{{PARTY}}
 </div>
</div></section>"""

if __name__ == "__main__":
    build()
