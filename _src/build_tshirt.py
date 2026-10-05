# -*- coding: utf-8 -*-
"""川口先生Tシャツ案ページ（日英兼用）を生成する。

  python _src/build_tshirt.py     → _src/Kawaguchi_seminar_tshirt.html（先生の写真入り・平文。.gitignore 済み）
  staticrypt … して docs/ へ（手順は build_photos_1003.py と同じ）

元画像は Vault の「川口先生Tシャツ デザイン案」（3 フォルダ＝3 ラウンド）。ページ内に縮小して埋め込む。
"""
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import portal_shell as S
import portal_media as M

HERE = S.HERE
OUT = os.path.join(HERE, "Kawaguchi_seminar_tshirt.html")
R1 = os.path.join(M.TSHIRT, "01_パターン案A-E（9-27〜10-3）")
R2 = os.path.join(M.TSHIRT, "02_レイアウト・モックアップ・版下（10-3 午前）")
R3 = os.path.join(M.TSHIRT, "03_絞込み（10-3 午後・D4と裏面Q4の組合せ）")

IMAGES = {  # key: (path, long edge, quality)
    "r1": (os.path.join(R2, "mockups_sheet.png"), 1500, 74),
    "l": (os.path.join(R2, "layouts_sheet.png"), 1700, 76),
    "r": (os.path.join(R2, "refined_sheet.png"), 1700, 76),
    "t": (os.path.join(R2, "textonly_sheet.png"), 1300, 76),
    "q": (os.path.join(R2, "text2_sheet.png"), 1700, 76),
    "d": (os.path.join(R2, "big_sheet.png"), 1300, 76),
    "combo": (os.path.join(R3, "combo_D4_Q4.png"), 1900, 78),
    "d4": (os.path.join(R3, "D4_mock_close.png"), 1000, 78),
    "s": (os.path.join(R3, "stage_sheet.png"), 1700, 76),
}


def fig(key, md, span, ja, en, alt_ja, alt_en, name):
    uri, (w, h) = md[key]
    return (f'<figure class="ts-fig fg-reveal" style="grid-column:span {span}"><img src="{uri}" width="{w}" height="{h}" decoding="async" '
            f'alt="{S.esc(alt_ja)} / {S.esc(alt_en)}" data-zoom data-name="{name}"><figcaption>'
            f'<span class="ja">{ja}</span><span class="en">{en}</span></figcaption></figure>')


def head(no, round_ja, round_en, h_ja, h_en, p_ja, p_en):
    return (f'<div class="ts-head fg-reveal"><span class="ts-no">{no}</span><div>'
            f'<p class="fg-eyebrow"><span class="ja">{round_ja}</span><span class="en">{round_en}</span></p>'
            f'<h2 class="fg-h2"><span class="ja">{h_ja}</span><span class="en">{h_en}</span></h2>'
            f'<p class="fg-sub"><span class="ja">{p_ja}</span><span class="en">{p_en}</span></p></div></div>')


def build():
    md = {}
    total = 0
    from PIL import Image
    for k, (path, edge, q) in IMAGES.items():
        uri, size, n = M.data_uri(path, edge, q)
        md[k] = (uri, size)
        total += n
    print(f"images: {total:,} bytes")

    css = CSS
    hdr = S.header("ja", "tshirt", inpage_lang=True)
    rounds = []
    rounds.append(
        '<section class="fg-section" id="r1"><div class="fg-wrap">'
        + head("01", "第1ラウンド · 9/27–10/3", "Round 1 · 9/27–10/3", "写真を主役に、5つの型",
               "Five types, with the photograph as the hero",
               "川口先生の講義中の写真に「MODELLING THE WORLD」と「STATISTICS × AI | SCHOLAR &amp; PRACTITIONER」を添える案から出発しました。A rive gauche、B slimane、C type stack、D editorial、E monogram。",
               "We started from a photograph of Prof. Kawaguchi lecturing, set with “MODELLING THE WORLD” and “STATISTICS × AI | SCHOLAR &amp; PRACTITIONER”. A rive gauche, B slimane, C type stack, D editorial, E monogram.")
        + '<div class="ts-grid">'
        + fig("r1", md, 7, "A〜E案を白Tに載せたモックアップ。写真の大きさと文字の組み方で表情が変わります。",
              "Patterns A–E mocked up on a white tee. Photo size and typesetting change the mood.",
              "A〜E案のモックアップ", "Mock-ups of patterns A–E", "tshirt_round1_A-E.jpg")
        + TYPES
        + '</div></div></section>')
    rounds.append(
        '<section class="fg-section is-alt" id="r2"><div class="fg-wrap">'
        + head("02", "第2ラウンド · 10/3 午前", "Round 2 · 10/3 morning", "切り口を5つに広げる",
               "Widening to five angles",
               "写真の置き方、配色、文字だけ、問いを刷る、大胆に刷る。同じ素材でも、Tシャツとしての「強さ」がまったく違って見えます。",
               "Where to place the photo, colour, type only, printing the question, printing boldly. The same material takes on very different strength as a T-shirt.")
        + '<div class="ts-grid">'
        + fig("l", md, 12, "<b>L1–L4 レイアウト</b>　前面ワンポイント＋背面ポートレート／ギャラリー・ラベル／ビッグタイプ／縦組み（各・表裏）。",
              "<b>L1–L4 Layouts</b>  one-point front + back portrait / gallery label / big type / vertical (front and back each).",
              "L1〜L4のレイアウト案", "Layouts L1–L4", "tshirt_round2_L.jpg")
        + fig("r", md, 12, "<b>R1–R3 リファイン</b>　写真をシャツに溶け込ませた3色。チャコール／ナチュラル／ネイビー。",
              "<b>R1–R3 Refined</b>  the photo blended into the shirt, in three colourways: charcoal, natural, navy.",
              "R1〜R3 3色", "R1–R3 colourways", "tshirt_round2_R.jpg")
        + fig("t", md, 6, "<b>T1–T4 文字だけ</b>　club／collegiate／block／citation（引用書式＋ y = f(world) + ε）。",
              "<b>T1–T4 Type only</b>  club / collegiate / block / citation (citation style with y = f(world) + ε).",
              "T1〜T4 文字だけの案", "Type-only designs T1–T4", "tshirt_round2_T.jpg")
        + fig("d", md, 6, "<b>D1–D4 大胆に刷る</b>　bootleg／magazine／typewall／bighead。ハーフトーンの肖像を大きく。",
              "<b>D1–D4 Printed boldly</b>  bootleg / magazine / typewall / bighead — a large halftone portrait.",
              "D1〜D4 大胆な案", "Bold designs D1–D4", "tshirt_round2_D.jpg")
        + fig("q", md, 12, "<b>Q1–Q4 問いを刷る</b>　THE QUESTION／MUSEUM WORDMARK／INSTITUTION／THE FOUR QUESTIONS（表裏）。",
              "<b>Q1–Q4 Printing the question</b>  THE QUESTION / MUSEUM WORDMARK / INSTITUTION / THE FOUR QUESTIONS (front and back).",
              "Q1〜Q4 問いを刷る案", "Question-led designs Q1–Q4", "tshirt_round2_Q.jpg")
        + '</div></div></section>')
    rounds.append(
        '<section class="fg-section" id="r3"><div class="fg-wrap">'
        + head("03", "第3ラウンド · 10/3 午後", "Round 3 · 10/3 afternoon", "表は D4、裏は Q4 へ絞り込む",
               "Narrowing to D4 on the front and Q4 on the back",
               "表は D4 bighead。MODELLING THE WORLD をレッドとブラックで切り、ハーフトーンの肖像と組みます。裏は Q4。川口先生の「四つの問い」を4行で。",
               "Front: D4 bighead — MODELLING THE WORLD cut in red and black beside a halftone portrait. Back: Q4 — Prof. Kawaguchi's four questions in four lines.")
        + '<div class="ts-grid">'
        + fig("d4", md, 5, "<b>D4 の近接ビュー。</b>ハーフトーンのドットが、布の上でどう見えるかを確かめるための拡大です。",
              "<b>D4 up close.</b> A close-up to judge how the halftone dots read on the fabric.",
              "D4の拡大", "D4 close-up", "tshirt_round3_D4_close.jpg")
        + BACK
        + '<div class="ts-note fg-reveal" style="grid-column:span 12"><h3><span class="ja">このラウンドで作った別案</span><span class="en">An alternative made in this round</span></h3>'
          '<p><span class="ja">このラウンドでは、写真を講義中のものからガウン姿のポートレートに差し替えた3色（S1 charcoal／S2 natural／S3 navy）も作っています。下の図です。</span>'
          '<span class="en">In this round we also made three colourways with the lecture photo swapped for a portrait of him in academic gown (S1 charcoal / S2 natural / S3 navy), shown below.</span></p></div>'
        + fig("s", md, 12, "<b>S1–S3</b>　ガウン姿の写真での3色。",
              "<b>S1–S3</b>  three colourways with the gown portrait.", "S1〜S3 3色", "S1–S3 colourways", "tshirt_round3_S.jpg")
        + '</div></div></section>')
    uri, (w, h) = md["combo"]
    final = (f'<div class="fg-wrap ts-final"><figure class="fg-reveal"><img src="{uri}" width="{w}" height="{h}" alt="表D4と裏Q4 / Front D4 and back Q4" decoding="async" data-zoom data-name="tshirt_current_D4-Q4.jpg">'
             '<figcaption><span class="ja"><b>いまの案</b>　表 D4 bighead ／ 裏 Q4 THE FOUR QUESTIONS</span><span class="en"><b>Current design</b>  Front D4 bighead / Back Q4 THE FOUR QUESTIONS</span></figcaption></figure></div>')
    make = """
<section class="fg-section is-ink" id="make"><div class="fg-wrap">
<div class="fg-reveal"><p class="fg-eyebrow"><span class="ja">つくる前に</span><span class="en">Before ordering</span></p>
<h2 class="fg-h2"><span class="ja">決めること、<em>選ぶこと</em></span><span class="en">What to decide, <em>what to choose</em></span></h2>
<p class="fg-sub"><span class="ja">2026-09-25 時点の各社サイトの表示にもとづく目安です。価格は店舗・在庫で変わります。</span><span class="en">Guide prices as shown on each site on 2026-09-25; they vary by shop and stock.</span></p></div>
<div class="ts-cols">
 <div class="ts-col fg-reveal"><h3><span class="ja">決めること</span><span class="en">To decide</span></h3>
  <ol><li><span class="ja"><b>枚数</b> — 30枚を境にシルクスクリーンが有利になります。</span><span class="en"><b>Quantity</b> — silk-screen becomes cheaper from about 30 pieces.</span></li>
  <li><span class="ja"><b>色数</b> — 1〜2色のロゴか、フルカラーの肖像か。</span><span class="en"><b>Colours</b> — a one- or two-colour logo, or a full-colour portrait.</span></li>
  <li><span class="ja"><b>ボディの色</b> — 白・淡色か、濃色か。</span><span class="en"><b>Body colour</b> — white/light or dark.</span></li>
  <li><span class="ja"><b>用途</b> — 先生への記念品か、ゼミ全員で着るものか。</span><span class="en"><b>Purpose</b> — a keepsake for Prof. Kawaguchi, or something for everyone to wear.</span></li></ol></div>
 <div class="ts-col fg-reveal"><h3><span class="ja">ボディの候補</span><span class="en">Body candidates</span></h3>
  <ul class="ts-list">
   <li><b>United Athle 5942-01</b> <span class="ja">6.2oz・コーマ糸。なめらかで上質、記念品向き。参考上代 税抜¥1,760〜。</span><span class="en">6.2oz, combed yarn: smooth and refined, good for a keepsake. List price from ¥1,760 (excl. tax).</span> <a href="https://united-athle.jp/ua/item/594201/" rel="noopener">united-athle.jp</a></li>
   <li><b>Printstar 00085-CVT</b> <span class="ja">5.6oz・17番手天竺。柔らかめ、無地 税込¥594（TMIX）。人数が多い・予算重視向き。</span><span class="en">5.6oz, 17-count jersey: softer; plain ¥594 incl. tax at TMIX. For larger groups or tight budgets.</span> <a href="https://tmix.jp/products/085-CVT" rel="noopener">tmix.jp</a></li>
   <li><b>United Athle 5001-01</b> <span class="ja">5.6oz。しっかりめ、色が61色と最多。参考上代 税抜¥1,260〜。</span><span class="en">5.6oz, sturdier, the widest colour range (61). List price from ¥1,260 (excl. tax).</span> <a href="https://united-athle.jp/ua/item/500101/" rel="noopener">united-athle.jp</a></li>
  </ul></div>
 <div class="ts-col fg-reveal"><h3><span class="ja">プリントの目安（TMIX）</span><span class="en">Print guide (TMIX)</span></h3>
  <ul class="ts-list">
   <li><b><span class="ja">インクジェット</span><span class="en">Inkjet</span></b> <span class="ja">1枚から。085-CVT 前面で、1枚 ¥3,509／10枚 ¥2,983／30枚 ¥2,632（各・1枚あたり、税込）。</span><span class="en">From one piece. 085-CVT front: ¥3,509 (1), ¥2,983 (10), ¥2,632 (30) each, incl. tax.</span></li>
   <li><b><span class="ja">シルクスクリーン</span><span class="en">Silk-screen</span></b> <span class="ja">30枚から。1色で 30枚 ¥1,321／50枚 ¥1,095（1枚あたり、税込）。</span><span class="en">From 30 pieces. One colour: ¥1,321 (30), ¥1,095 (50) each, incl. tax.</span> <a href="https://tmix.jp/products/085-CVT" rel="noopener">tmix.jp</a></li>
  </ul>
  <p class="ts-fine"><span class="ja">D4 のように色数が多い・肖像が入る案は、インクジェットかフルカラー対応の方式が前提になります。</span><span class="en">Designs with a portrait or many colours, like D4, assume inkjet or another full-colour method.</span></p></div>
</div></div></section>"""
    body = f"""<body>
{hdr}
<main id="main">
<section class="fg-pagehead ts-pagehead"><div class="fg-wrap">
 <p class="fg-kicker"><span class="ja">デザイン検討 · 2026.09.27–10.03</span><span class="en">Design study · 2026.09.27–10.03</span></p>
 <h1><span class="ja"><span class="ph">川口先生</span><span class="ph">Tシャツ案</span></span><span class="en">Prof. Kawaguchi's <em>T-shirt</em></span></h1>
 <p class="fg-lede"><span class="ja">写真を主役にしたA〜E案から出発し、文字だけ、問いを刷る、大胆に刷る、と切り口を広げ、10月3日の午後に「表 MODELLING THE WORLD × 裏 FOUR QUESTIONS」へ絞り込みました。</span><span class="en">We began with five photo-led patterns (A–E), widened to type-only, question-led and bold-print angles, and on the afternoon of October 3 narrowed to “MODELLING THE WORLD” on the front and “FOUR QUESTIONS” on the back.</span></p>
 <ul class="fg-chips"><li class="is-state"><span class="ja">検討中</span><span class="en">In progress</span></li><li><span class="ja">3ラウンド</span><span class="en">3 rounds</span></li><li><span class="ja">第2ラウンドは19案</span><span class="en">19 designs in round 2</span></li></ul>
 <div class="fg-actions"><a class="fg-btn is-solid" href="#r3"><span class="ja">いまの案を見る</span><span class="en">See the current design</span> <span aria-hidden="true">↓</span></a><a class="fg-btn" href="#make"><span class="ja">つくる前に決めること</span><span class="en">Before ordering</span></a></div>
</div></section>
{final}
{''.join(rounds)}
{make}
</main>
{S.footer("ja", inpage_lang=True)}
{S.body_script()}
</body></html>
"""
    html = ('<!DOCTYPE html>\n<html lang="ja"><head>'
            + S.shell_head("川口先生Tシャツ案｜AIx知的鍛錬塾 / Prof. Kawaguchi's T-shirt", "ja", css)
            + '</head>\n' + body)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(html)
    print(f"written {OUT}: {len(html):,} bytes")


TYPES = """<div class="ts-note ts-types fg-reveal" style="grid-column:span 5"><h3><span class="ja">5つの型</span><span class="en">The five types</span></h3><ol>
<li><b>A</b><span class="ja"><i>rive gauche</i> — 写真を中央に小さく、字間を開けた細い文字。</span><span class="en"><i>rive gauche</i> — a small centred photo under widely spaced thin type.</span></li>
<li><b>B</b><span class="ja"><i>slimane</i> — 写真を横いっぱいに。文字はさらに細く、さらに広く。</span><span class="en"><i>slimane</i> — the photo runs edge to edge; the type is thinner and wider still.</span></li>
<li><b>C</b><span class="ja"><i>type stack</i> — 写真なし。MODELLING／THE／WORLD の3段組。</span><span class="en"><i>type stack</i> — no photo; MODELLING / THE / WORLD stacked in three lines.</span></li>
<li><b>D</b><span class="ja"><i>editorial</i> — 写真に題字を直接重ねる、雑誌の表紙のような構成。</span><span class="en"><i>editorial</i> — the title laid directly over the photo, like a magazine cover.</span></li>
<li><b>E</b><span class="ja"><i>monogram</i> — M／T／W の縦組みモノグラムと写真。</span><span class="en"><i>monogram</i> — a vertical M / T / W monogram beside the photo.</span></li></ol></div>"""

BACK = """<div class="ts-back fg-reveal" style="grid-column:span 7"><p class="ts-back-tag">BACK <span>—</span> Q4</p>
<h3>FOUR QUESTIONS</h3><p class="by">for scholar-practitioners, by Kawaguchi Yuichiro</p>
<ol>
<li><b>01</b><span class="q">What is not independent of what?</span><span class="ja jq">何と何が独立でないか</span></li>
<li><b>02</b><span class="q">Where in the model did you write it?</span><span class="ja jq">モデルのどこに書いたか</span></li>
<li><b>03</b><span class="q">What breaks if you leave it out?</span><span class="ja jq">書かないと何が壊れるか</span></li>
<li><b>04</b><span class="q">What does your specification claim?</span><span class="ja jq">定式化は何を主張するか</span></li>
</ol><p class="ft">KAWAGUCHI SEMINAR — MODELLING THE WORLD</p></div>"""

CSS = """
.ts-pagehead h1{max-width:18em}
.ts-pagehead .fg-wrap{padding-bottom:clamp(110px,14vw,170px)}
.ts-final{position:relative;z-index:3;margin-top:calc(-1 * clamp(84px,11vw,140px))}
.ts-final figure{margin:0;border-radius:var(--r-lg);overflow:hidden;box-shadow:0 50px 100px -40px rgba(11,18,36,.7),0 0 0 1px rgba(11,18,36,.08);background:#e8e8e4}
.ts-final img{display:block;width:100%;height:auto}
.ts-final figcaption{background:#fff;padding:.9rem 1.3rem;font-size:.92rem;color:var(--muted);border-top:1px solid var(--line)}
.ts-final figcaption b{color:var(--ink)}
#r1.fg-section{padding-top:clamp(56px,7vw,90px)}
.ts-types ol{list-style:none;margin:0;padding:0}
.ts-types li{display:grid;grid-template-columns:2rem 1fr;gap:.2rem .6rem;padding:.65rem 0;border-bottom:1px solid #ffd3df;color:var(--muted);font-size:.93rem}
.ts-types li:last-child{border-bottom:0}
.ts-types li b{font-family:var(--f-disp);font-weight:200;font-size:1.7rem;line-height:1;color:var(--ink-2)}
.ts-types i{font-family:var(--f-disp);font-style:normal;font-weight:600;font-size:1.02rem;color:var(--ink)}
.ts-back{background:#fbfaf6;border:1px solid var(--line);border-radius:var(--r-lg);padding:clamp(1.4rem,3vw,2.4rem);box-shadow:var(--shadow);align-self:stretch}
.ts-back-tag{margin:0 0 1rem;font-size:.72rem;font-weight:800;letter-spacing:.2em;color:var(--muted)}
.ts-back h3{margin:0;font-size:clamp(1.8rem,4.2vw,3rem);line-height:1;font-weight:800;letter-spacing:.01em;color:#111;text-transform:uppercase}
.ts-back .by{margin:.5rem 0 1rem;font-family:var(--f-serif);font-style:italic;color:#444;font-size:1.05rem;padding-bottom:.9rem;border-bottom:1.5px solid #111}
.ts-back ol{list-style:none;margin:0;padding:0}
.ts-back li{display:grid;grid-template-columns:2.6rem 1fr;gap:0 .6rem;padding:.55rem 0;border-bottom:1px solid var(--line);align-items:baseline}
.ts-back li b{color:var(--ember);font-size:.95rem;letter-spacing:.06em}
.ts-back .q{font-family:var(--f-serif);font-size:clamp(1.15rem,2.2vw,1.55rem);color:#111}
.ts-back .jq{grid-column:2;font-size:.82rem;color:var(--muted)}
.ts-back .ft{margin:1rem 0 0;font-size:.68rem;letter-spacing:.2em;color:var(--muted)}
.ts-head{display:grid;grid-template-columns:auto 1fr;gap:1.2rem 2.2rem;align-items:start;margin-bottom:2.4rem}
.ts-no{font-family:var(--f-disp);font-size:clamp(4rem,10vw,7.5rem);line-height:.85;font-weight:200;color:var(--ink-2);letter-spacing:-.04em}
.is-alt .ts-no{color:var(--gold-deep)}
.ts-grid{display:grid;grid-template-columns:repeat(12,1fr);gap:18px}
.ts-fig{margin:0;background:var(--card);border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden;box-shadow:var(--shadow);display:flex;flex-direction:column}
.ts-fig img{display:block;width:100%;height:auto;background:#e8e8e4;transition:transform .6s var(--ease)}
.ts-fig:hover img{transform:scale(1.015)}
.ts-fig figcaption{padding:.9rem 1.2rem 1.1rem;font-size:.9rem;color:var(--muted);border-top:1px solid var(--line);line-height:1.7}
.ts-fig figcaption b{color:var(--ink)}
.ts-note{background:var(--gold-wash);border:1px solid #ffd3df;border-radius:var(--r-lg);padding:1.4rem 1.6rem;align-self:stretch;display:flex;flex-direction:column;justify-content:center}
.ts-note h3{margin:0 0 .5rem;font-size:1.05rem;color:var(--ink)}
.ts-note p{margin:0;color:var(--muted);font-size:.95rem}
.ts-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:2rem}
.ts-col h3{margin:0 0 1rem;font-size:1.05rem;color:var(--gold);letter-spacing:.04em;border-bottom:1px solid rgba(255,255,255,.18);padding-bottom:.7rem}
.ts-col ol,.ts-col ul{margin:0;padding:0 0 0 1.2rem;color:var(--on-ink-2);font-size:.94rem}
.ts-col li{margin-bottom:.8rem}
.ts-col li::marker{color:var(--gold)}
.ts-col b{color:#fff}
.ts-col a{color:var(--gold);white-space:nowrap}
.ts-list{list-style:none;padding:0!important}
.ts-list li{padding-left:0}
.ts-fine{margin:1rem 0 0;color:var(--on-ink-2);font-size:.85rem;border-left:2px solid var(--gold);padding-left:.8rem}
@media (max-width:860px){
  .ts-grid{grid-template-columns:1fr}
  .ts-grid > *{grid-column:auto!important}
  .ts-head{grid-template-columns:1fr}
  .ts-cols{grid-template-columns:1fr}
}
"""

if __name__ == "__main__":
    build()
