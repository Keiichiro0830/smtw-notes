# -*- coding: utf-8 -*-
"""ポータルのホーム（日・英）を生成する。

  python _src/build_home.py       → _src/Kawaguchi_seminar.html / _src/Kawaguchi_seminar_en.html

ホームは「開催記録の年表」を軸にする。ページ上部の状態表示（LATEST / NEXT）は、ブラウザ側で
今日の日付と年表の日付を比べて決めるので、「次回」と書いたまま古くなることがない。
配布BOX・コメント・ファイル提出BOX は旧ホームの部品とスクリプトをそのまま使う（theme/legacy_home_*.html）。
写真は base64 で埋め込む（暗号化したページの中にだけ存在する）。要: pillow, pillow-heif。
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import portal_shell as S
import portal_media as M

HERE = S.HERE
T = {"ja": 0, "en": 1}

# 年表。href は (ja, en)。英語版が無いページは日本語ページへ。
EVENTS = [
    dict(date="2027-01-30", big="01.30", tag=("第8回", "8TH"), upcoming=True,
         title=("第8回 研究会（2027年1月30日・土）", "8th meeting (Sat 30 Jan 2027)"),
         desc=("10:30 開始。早稲田大学 26号館（部屋は追ってご案内します）。2月は入試期間のため早稲田の施設が使えません。",
               "Starts 10:30. Waseda Bldg 26 — room to be announced. Waseda facilities are closed in February for entrance exams."),
         label=("第8回 研究会", "the 8th meeting"), links=[]),
    dict(date="2026-12-05", big="12.05", tag=("第7回", "7TH"), upcoming=True,
         title=("第7回 研究会（12月5日・土）", "7th meeting (Sat 5 Dec)"),
         desc=("10:30 開始。早稲田大学 26号館（部屋は追ってご案内します）。",
               "Starts 10:30. Waseda Bldg 26 — room to be announced."),
         label=("第7回 研究会", "the 7th meeting"), links=[]),
    dict(date="2026-11-07", big="11.07", tag=("第6回", "6TH"), upcoming=True,
         title=("第6回 研究会（11月7日・土）", "6th meeting (Sat 7 Nov)"),
         desc=("10:30 開始。早稲田大学 26号館、これまでと同じ部屋の予定です。11月からは、各自が作った資料を持ち寄って議論する形を川口先生が提案されています。",
               "Starts 10:30. Waseda Bldg 26, in our usual room. From November, Prof. Kawaguchi proposes that each member brings material they have written, as the basis for discussion."),
         label=("第6回 研究会", "the 6th meeting"), links=[]),
    dict(date="2026-10-03", big="10.03", tag=("シンポジウム", "SYMPOSIUM"),
         title=("秋のシンポジウム『今回は違うか？：ITブームとAIブームの違い』", "Autumn symposium: Is this time different? The IT boom vs. the AI boom"),
         desc=("川口先生の基調講演、飯沼先生・黒田先生の講演、パネル、全体討論。終了後は神楽坂でゼミ会。",
               "Keynote by Prof. Kawaguchi, talks by Prof. Iinuma and Prof. Kuroda, a panel and an open discussion — then the zemi-kai in Kagurazaka."),
         label=("秋のシンポジウム", "the autumn symposium"),
         links=[(("記録を見る", "Record"), ("Kawaguchi_seminar_1003.html", "Kawaguchi_seminar_1003_en.html"), True),
                (("議事メモ", "Minutes (JA)"), ("Kawaguchi_seminar_minutes.html",) * 2, False),
                (("写真", "Photos"), ("Kawaguchi_seminar_1003_photos.html",) * 2, False)]),
    dict(date="2026-08-22", big="08.22", tag=("第5回", "5TH"),
         title=("研究会『エージェンティック時空統計学 入門』", "Meeting: Agentic spatio-temporal statistics, an introduction"),
         desc=("大規模言語モデルと時空モデリング：依存の統計学アプローチ。午後は川口先生による Claude Code の実演。",
               "Large language models and spatio-temporal modelling. In the afternoon, a live Claude Code demonstration by Prof. Kawaguchi."),
         label=("第5回 研究会", "the 5th meeting"),
         links=[(("開催情報", "Record"), ("Kawaguchi_seminar_0822.html", "Kawaguchi_seminar_0822_en.html"), True),
                (("議事メモ", "Minutes (JA)"), ("Kawaguchi_seminar_minutes5.html",) * 2, False)]),
    dict(date="2026-07-18", big="07.18", tag=("第4回", "4TH"),
         title=("ループ・エンジニアリング演習", "The loop-engineering exercise"),
         desc=("企業におけるAI活用 — DXからAXへ。「自分のループ」を設計して共有しました。",
               "AI in the enterprise — from DX to AX. Each member designed and shared their own loop."),
         label=("第4回 研究会", "the 4th meeting"),
         links=[(("開催情報", "Record"), ("Kawaguchi_seminar_prev.html", "Kawaguchi_seminar_prev_en.html"), True),
                (("議事メモ", "Minutes"), ("Kawaguchi_seminar_minutes4.html", "Kawaguchi_seminar_minutes_en.html"), False)]),
    dict(date="2026-06-20", big="06.20", tag=("第3回", "3RD"),
         title=("LLM勉強会", "LLM study session"),
         desc=("仕組み・活用・メンタルモデルと金融応用。LLM三部作などを事前資料にしました。",
               "How LLMs work, how to use them, mental models and finance applications — with the LLM trilogy as pre-reading."),
         label=("第3回", "the 3rd meeting"),
         links=[(("事前資料", "Pre-reads"), ("Kawaguchi_seminar_papers.html", "Kawaguchi_seminar_papers_en.html"), True),
                (("議事メモ", "Minutes"), ("Kawaguchi_seminar_minutes3.html", "Kawaguchi_seminar_minutes3_en.html"), False)]),
    dict(date="2026-05-09", big="05.09", tag=("第2回", "2ND"),
         title=("科学におけるAI ／ ブラックボックスから抜け出す", "AI in science / Out of the black box"),
         desc=("Agrawal らと Chen らの NBER 論文を題材に、「AI専門家」になる塾とは何かを議論しました。",
               "Using NBER papers by Agrawal et al. and Chen et al., we discussed what it means to train as an AI-expert scientist."),
         label=("第2回", "the 2nd meeting"),
         links=[(("議事メモ", "Minutes"), ("Kawaguchi_seminar_minutes2.html", "Kawaguchi_seminar_minutes2_en.html"), True)]),
    dict(date="2026-04-11", big="04.11", tag=("第1回", "1ST"),
         title=("キックオフ", "Kick-off"),
         desc=("川口先生の退職後も知的交流を続ける少人数の議論グループとして出発しました。",
               "Launched as a small discussion group to continue the intellectual exchange after Prof. Kawaguchi's retirement."),
         label=("第1回", "the 1st meeting"),
         links=[(("議事メモ", "Minutes"), ("Kawaguchi_seminar_minutes1.html", "Kawaguchi_seminar_minutes1_en.html"), True)]),
]

QUESTIONS = [
    ("何と何が独立でないか", "What is not independent of what?"),
    ("モデルのどこに書いたか", "Where in the model did you write it?"),
    ("書かないと何が壊れるか", "What breaks if you leave it out?"),
    ("定式化は何を主張するか", "What does your specification claim?"),
]
MARQUEE = ["Planning Capital・計画資本", "IID と依存性", "Loop Engineering", "Agentic 時空統計学", "Statistical Model Thinker",
           "ITブーム × AIブーム", "Four Questions"]

COPY = {
    "ja": dict(
        title="AIx知的鍛錬塾 ポータル｜川口ゼミ",
        h1='知を、<span class="ac">鍛える</span>。<span class="en">Forging intellect, with AI.</span>',
        lede="川口有一郎先生と、統計モデルと生成AIをじっくり鍛える少人数ゼミ。2026年4月に始まり、10月3日のシンポジウムまで6回の集まりを重ねました。11月からも月に一度、続けます。",
        btn1="今後の日程", btn2="シンポジウムの記録",
        photo_cap=("2026.10.03　秋のシンポジウム", "Waseda 26-1102"),
        status_label="最新", status_txt="秋のシンポジウム（10.03）開催済み — 写真・議事メモを公開中",
        s_sched=("今後の日程", "次の<em>3回</em>が決まりました。", "いずれも土曜日、早稲田大学 26号館で開きます。手帳に入れておいてください。"),
        sched_meta=("土", "10:30 開始", "早稲田大学 26号館"),
        sched_next="次回",
        sched_note="会場の部屋と当日の進め方は、各回の前にこのページとメッセンジャーでお知らせします。2月は入試期間のため早稲田の施設が使えず、お休みです。",
        s_log=("開催記録", "月に一度、<em>積み重ねた</em>6回。", "上の3つが今後の予定、その下が開催済みの記録です。各回の資料と議事メモへは、ボタンから進めます。"),
        s_new=("最新の更新", "10月3日の<em>記録</em>が揃いました。", "写真、議事メモ、黒田先生の資料、そして川口先生Tシャツの検討。"),
        tiles=dict(photo=("PHOTOS", "10/3 当日の写真", "集合写真・シンポジウムの様子・ゼミ会。写真49枚と動画1本。", "写真を見る →"),
                   shirt=("T-SHIRT", "川口先生Tシャツ案", "3ラウンドの検討。表は「MODELLING THE WORLD」、裏は「FOUR QUESTIONS」へ。", "検討の経過を見る →"),
                   minutes=("MINUTES", "10/3 議事メモ", "基調講演からパネル、全体討論まで。", "読む →"),
                   slides=("SLIDES", "黒田先生の発表資料", "『AI時代における統計的因果推論の教育と研究』全31枚（PDF）", "PDFを開く →")),
        s_q=("鍛錬の型", "手を動かす前に、<em>四つの問い</em>。", "川口先生が示す、統計モデルを組むときの確認項目です。Tシャツの裏面にも入れる案です。"),
        s_lib=("資料庫", "<em>資料</em>はここに。", "過去の事前資料、メルマガ、日経記事の課題。"),
        cards=[("ARCHIVE", "過去資料アーカイブ", "第2回・第3回の事前読了資料。論文と川口先生の配布資料。", "開く →", "Kawaguchi_seminar_papers.html"),
               ("NEWSLETTER", "関連メルマガ", "議論の前提となった川口先生のメルマガの抜粋。", "開く →", "Kawaguchi_seminar_melmaga.html"),
               ("ASSIGNMENT", "日経記事 × AI 課題", "日経記事を題材にした、AI活用の演習課題。", "開く →", "Kawaguchi_seminar_articles.html")],
        s_tools=("共有と提出", "<em>配る</em>、集める。", "先生・事務局からの共有ファイル、コメント、ファイルの提出はここから。"),
        dist_p="川口先生・事務局がドライブの配布フォルダに置いたファイルが、ここに自動で一覧表示されます（ページを開くたびに最新化）。ファイルは Google Drive で開きます。",
        dist_h="配布BOX（先生・事務局からの共有ファイル）", dist_loading="読み込み中…",
        cmt_h="コメント・ご質問フォーム",
        cmt_p='ご質問・ご要望、運営へのご意見をこちらからどうぞ。各資料へのコメントは、<a href="Kawaguchi_seminar_prev.html">第4回のページ</a>の資料カードからお送りいただけます。',
        cmt_aid="general", cmt_atitle="全体・運営",
        sub_h="ファイル提出BOX",
        sub_p="演習の成果物（「自分のループ」設計メモなど）や、共有したい資料を、川口先生へ直接お送りいただけます（複数可・合計20MBまで）。お送りいただいたファイルは川口先生にメールで届き、控えが事務局のドライブに保存されます。"),
    "en": dict(
        title="AIx Intellectual Forging Academy — Kawaguchi Seminar",
        h1='Forging <span class="ac">intellect</span>,<span class="en">with AI.</span>',
        lede="A small seminar with Prof. Yuichiro Kawaguchi on statistical modelling and generative AI. Since April 2026 we have met six times, up to the autumn symposium on October 3 — and we continue monthly from November.",
        btn1="Upcoming dates", btn2="Symposium record",
        photo_cap=("2026.10.03  Autumn symposium", "Waseda 26-1102"),
        status_label="Latest", status_txt="Autumn symposium (10.03) held — photos and minutes are up",
        s_sched=("Upcoming", "The next <em>three dates</em> are set.", "All on Saturdays, at Waseda University, Building 26. Please save the dates."),
        sched_meta=("SAT", "Starts 10:30", "Waseda Bldg 26"),
        sched_next="NEXT",
        sched_note="The room and the plan for each day will be posted here and on Messenger before each meeting. There is no meeting in February: Waseda facilities are closed for entrance exams.",
        s_log=("Sessions", "Six meetings, <em>one month</em> at a time.", "The top three are upcoming; below them, the meetings held so far. Each session links to its materials and minutes."),
        s_new=("What's new", "The <em>record</em> of October 3 is complete.", "Photos, minutes, Prof. Kuroda's slides — and the T-shirt design study."),
        tiles=dict(photo=("PHOTOS", "Oct 3 photos", "Group photos, the symposium itself and the zemi-kai. 49 photos and one video.", "See the photos →"),
                   shirt=("T-SHIRT", "T-shirt design study", "Three rounds. MODELLING THE WORLD on the front, FOUR QUESTIONS on the back.", "See how it evolved →"),
                   minutes=("MINUTES", "Oct 3 minutes (JA)", "From the keynote through the panel to the open discussion.", "Read →"),
                   slides=("SLIDES", "Prof. Kuroda's slides", "Teaching and research in statistical causal inference in the AI era — 31 slides (PDF).", "Open the PDF →")),
        s_q=("The craft", "Before you model, <em>four questions</em>.", "Prof. Kawaguchi's checklist for building a statistical model. Proposed for the back of the T-shirt, too."),
        s_lib=("Library", "Materials, <em>in one place</em>.", "Past pre-reads, newsletters and the Nikkei × AI assignment."),
        cards=[("ARCHIVE", "Archive of past materials", "Pre-reads for the 2nd and 3rd meetings: papers and Prof. Kawaguchi's handouts.", "Open →", "Kawaguchi_seminar_papers_en.html"),
               ("NEWSLETTER", "Related newsletters", "Excerpts from the newsletter that frame the discussions.", "Open →", "Kawaguchi_seminar_melmaga_en.html"),
               ("ASSIGNMENT", "Nikkei × AI assignment", "An exercise on using AI with newspaper articles.", "Open →", "Kawaguchi_seminar_articles.html")],
        s_tools=("Share & submit", "<em>Receive</em> and send.", "Files from Prof. Kawaguchi and the secretariat, comments and file submissions."),
        dist_p="Files placed in the Drive distribution folder by Prof. Kawaguchi or the secretariat are listed here automatically (refreshed every time the page opens). Files open in Google Drive.",
        dist_h="Distribution box (files from Prof. Kawaguchi &amp; the secretariat)", dist_loading="Loading…",
        cmt_h="Comments &amp; questions",
        cmt_p='Send questions, requests or feedback on how the seminar is run. Per-material comments can be sent from the material cards on the <a href="Kawaguchi_seminar_prev_en.html">4th-meeting page</a>.',
        cmt_aid="general-en", cmt_atitle="General / Operations",
        sub_h="File submission box",
        sub_p="Send your exercise outputs (e.g., your own-loop design memo) or any material you would like to share directly to Prof. Kawaguchi (multiple files, up to 20 MB total). Files are delivered by email, with a copy kept in the secretariat's Drive."),
}


def legacy_parts(lang):
    s = io.open(os.path.join(HERE, "theme", f"legacy_home_{lang}.html"), encoding="utf-8", newline="").read().replace("\r\n", "\n")
    style = re.search(r"<style>(.*?)</style>", s, re.S).group(1)
    h2 = s.find('<h2 id="sec-dist">')
    scripts = s[s.find("<script>", s.find("<footer>", h2)):s.find("</body>")]
    return style, scripts


def media():
    out = {}
    out["hero"], sz, n1 = M.data_uri(M.heic("080451277"), 1500, 70, (0.10, 0.27, 0.90, 0.84))
    out["m1"], _, n2 = M.data_uri(M.heic("080525829"), 700, 66, (0.10, 0.26, 0.90, 0.72))
    out["m2"], _, n3 = M.data_uri(M.heic("110834214"), 700, 66, (0.05, 0.12, 0.95, 0.80))
    out["m3"], _, n4 = M.data_uri(M.session(11), 700, 66)
    out["shirt"], _, n5 = M.data_uri(os.path.join(M.TSHIRT, "03_絞込み（10-3 午後・D4と裏面Q4の組合せ）", "combo_D4_Q4.png"), 1100, 70)
    out["_bytes"] = n1 + n2 + n3 + n4 + n5
    return out


def ledger(lang):
    i = T[lang]
    rows = []
    for e in EVENTS:
        links = "".join(f'<a href="{h[i]}"{" class=\"is-main\"" if main else ""}>{t[i]}</a>' for t, h, main in e["links"])
        if links:
            links = f'<div class="links">{links}</div>'
        tbd = ' class="is-tbd"' if e.get("tbd") else ""
        rows.append(
            f'<li data-date="{e["date"]}" data-label-ja="{e["label"][0]}" data-label-en="{e["label"][1]}"{tbd}>'
            f'<div class="no">{e["big"]}<small>{e["tag"][i]}</small></div>'
            f'<div><h3>{e["title"][i]}</h3><p>{e["desc"][i]}</p></div>{links}</li>')
    return '<ol class="fg-ledger">' + "".join(rows) + "</ol>"


def schedule(lang):
    """ヒーロー直下の「今後の日程」。EVENTS の upcoming 行を日付順に並べる（過ぎた回と次回の印は forge.js が付ける）。"""
    i = T[lang]
    c = COPY[lang]
    wd, tm, venue = c["sched_meta"]
    cards = []
    for e in sorted((e for e in EVENTS if e.get("upcoming")), key=lambda e: e["date"]):
        y = e["date"][:4]
        cards.append(
            f'<li data-date="{e["date"]}"><span class="flag">{c["sched_next"]}</span>'
            f'<div class="d">{e["big"]}<small>{y} · {wd}</small></div>'
            f'<div class="t">{e["tag"][i]}</div>'
            f'<div class="m"><span>{tm}</span><span>{venue}</span></div></li>')
    return '<ol class="fg-sched-list fg-reveal">' + "".join(cards) + "</ol>"


def hero_dates(lang):
    """ヒーロー内の一行版。スマホでは「今後の日程」セクションが折り返しの下になるため、ここでも日付を見せる。"""
    c = COPY[lang]
    ds = "".join(f'<li data-date="{e["date"]}"><b>{int(e["big"][:2])}/{int(e["big"][3:])}</b>（{c["sched_meta"][0]}）</li>' if lang == "ja"
                 else f'<li data-date="{e["date"]}"><b>{e["big"].replace(".", "/")}</b> {c["sched_meta"][0].title()}</li>'
                 for e in sorted((e for e in EVENTS if e.get("upcoming")), key=lambda e: e["date"]))
    return f'<a class="fg-dates" href="#schedule"><span>{c["s_sched"][0]}</span><ol>{ds}</ol></a>'


def build(lang, md):
    c = COPY[lang]
    i = T[lang]
    style, scripts = legacy_parts(lang)
    head = ('<!DOCTYPE html>\n<html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>%s</title><meta name="color-scheme" content="light"><link rel="icon" type="image/svg+xml" href="%s">'
            '<script>document.documentElement.classList.add("js")</script>%s'
            '<style id="legacy-css">%s</style><style id="forge-css">%s%s</style></head>\n'
            % (lang, S.esc(c["title"]), S.FAVICON, S.FONTS, style, S.theme_css(), HOME_CSS))
    other = "Kawaguchi_seminar_en.html" if lang == "ja" else "Kawaguchi_seminar.html"
    hdr = S.header(lang, "home", other_href=other)
    h = lambda t, fn: f'<a class="fg-tile {fn[0]}" href="{fn[1]}">{fn[2]}<span class="tag">{t[0]}</span><h3>{t[1]}</h3><p>{t[2]}</p><span class="go">{t[3]}</span></a>'
    tl = c["tiles"]
    photo_tile = h(tl["photo"], ("t-a", "Kawaguchi_seminar_1003_photos.html",
                                 f'<div class="mosaic"><img src="{md["m1"]}" alt="" decoding="async"><img src="{md["m2"]}" alt="" decoding="async"><img src="{md["m3"]}" alt="" decoding="async"></div>'))
    shirt_tile = h(tl["shirt"], ("t-b", "Kawaguchi_seminar_tshirt.html", f'<img src="{md["shirt"]}" alt="" decoding="async">'))
    min_tile = h(tl["minutes"], ("t-c", "Kawaguchi_seminar_minutes.html", '<span class="big">10.03</span>'))
    sld_tile = h(tl["slides"], ("t-d", S.KURODA, '<span class="big">31</span>'))
    qs = "".join(f'<li class="fg-reveal" style="--d:{n * .08:.2f}s"><div class="n">0{n + 1}</div><h3>{q[0] if lang == "ja" else q[1]}</h3><p>{q[1] if lang == "ja" else ""}</p></li>' for n, q in enumerate(QUESTIONS))
    cards = "".join(f'<a class="fg-card fg-reveal" style="--d:{n * .08:.2f}s" href="{k[4]}"><span class="tag">{k[0]}</span><h3>{k[1]}</h3><p>{k[2]}</p><span class="go">{k[3]}</span></a>' for n, k in enumerate(c["cards"]))
    mq = "".join(f"<span>{m}</span>" for m in MARQUEE)
    sec = lambda key, cls="": (f'<p class="fg-eyebrow">{c[key][0]}</p><h2 class="fg-h2">{c[key][1]}</h2><p class="fg-sub">{c[key][2]}</p>')
    body = f"""<body>
{hdr}
<main id="main">
<section class="fg-hero"><div class="fg-wrap fg-hero-in">
  <div>
    <h1>{c["h1"]}</h1>
    <p class="fg-lede">{c["lede"]}</p>
    <div class="fg-status" id="fg-status" data-latest-ja="{COPY["ja"]["status_txt"]}" data-latest-en="{COPY["en"]["status_txt"]}"><span class="fg-dot" aria-hidden="true"></span><b>{c["status_label"]}</b><span class="st">{c["status_txt"]}</span></div>
    {hero_dates(lang)}
    <div class="fg-actions"><a class="fg-btn is-solid" href="#schedule">{c["btn1"]} <span aria-hidden="true">↓</span></a>
    <a class="fg-btn" href="{"Kawaguchi_seminar_1003.html" if lang == "ja" else "Kawaguchi_seminar_1003_en.html"}">{c["btn2"]} <span aria-hidden="true">→</span></a></div>
  </div>
  <figure class="fg-hero-photo"><img src="{md["hero"]}" alt="{S.esc(c["photo_cap"][0])}" width="1500" decoding="async"><figcaption><span>{c["photo_cap"][0]}</span><b>{c["photo_cap"][1]}</b></figcaption></figure>
</div></section>

<section class="fg-section fg-sched" id="schedule"><div class="fg-wrap">
  <div class="fg-reveal">{sec("s_sched")}</div>
  {schedule(lang)}
  <p class="fg-note fg-reveal">{c["sched_note"]}</p>
</div></section>
<div class="fg-marquee" aria-hidden="true"><div class="fg-marquee-track">{mq}{mq}</div></div>

<section class="fg-section" id="log"><div class="fg-wrap">
  <div class="fg-reveal">{sec("s_log")}</div>
  {ledger(lang)}
</div></section>

<section class="fg-section is-alt" id="new"><div class="fg-wrap">
  <div class="fg-reveal">{sec("s_new")}</div>
  <div class="fg-bento fg-reveal">{photo_tile}{shirt_tile}{min_tile}{sld_tile}</div>
</div></section>

<section class="fg-section is-ink" id="craft"><div class="fg-wrap">
  <div class="fg-reveal">{sec("s_q")}</div>
  <ol class="fg-q">{qs}</ol>
</div></section>

<section class="fg-section" id="lib"><div class="fg-wrap">
  <div class="fg-reveal">{sec("s_lib")}</div>
  <div class="fg-cards">{cards}</div>
</div></section>

<section class="fg-section is-alt fg-tools" id="tools"><div class="fg-wrap fg-reveal">{sec("s_tools")}</div>
<div class="container">
<h2 id="sec-dist">{c["dist_h"]}</h2>
<p class="fg-note">{c["dist_p"]}</p>
<div id="smtw-dist" class="smtw-dist"><p class="smtw-dist-status">{c["dist_loading"]}</p></div>

<h2>{c["cmt_h"]}</h2>
<p class="fg-note">{c["cmt_p"]}</p>
<div id="smtw-cmt-form" class="smtw-cmt smtw-cmt-main" data-aid="{c["cmt_aid"]}" data-atitle="{c["cmt_atitle"]}"></div>

<h2 id="sec-submit">{c["sub_h"]}</h2>
<p class="fg-note">{c["sub_p"]}</p>
<div id="smtw-upl-form" class="smtw-cmt smtw-upl"></div>
</div></section>
</main>
{S.footer(lang)}
{scripts}
{S.body_script()}
</body></html>
"""
    return head + body


HOME_CSS = """
.fg-note{color:var(--muted);font-size:.92rem;max-width:62ch}
.fg-ledger li.is-tbd .no{font-size:clamp(2rem,4vw,2.8rem);padding-top:.5rem}
.fg-sched{padding-bottom:clamp(40px,6vw,72px)}
.fg-sched-list{list-style:none;margin:1.6rem 0 1.2rem;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:0;border-top:2px solid var(--ink);border-bottom:1px solid var(--line-2)}
.fg-sched-list li{position:relative;padding:1.8rem 1.4rem 1.6rem;border-left:1px solid var(--line-2)}
.fg-sched-list li:first-child{border-left:0}
.fg-sched-list .flag{display:none;position:absolute;left:1.4rem;top:-.72rem;background:var(--ember);color:#fff;font-size:.68rem;font-weight:800;letter-spacing:.18em;padding:.2rem .7rem;border-radius:999px}
.fg-sched-list li.is-next{background:var(--gold-wash)}
.fg-sched-list li.is-next .flag{display:inline-block}
.fg-sched-list li.is-past{display:none}
.fg-sched-list .d{font-family:var(--f-disp);font-size:clamp(3rem,6.4vw,4.6rem);line-height:1;letter-spacing:-.02em;color:var(--ink);font-weight:700}
.fg-sched-list .d small{display:block;font-family:var(--f-ui);font-size:.8rem;font-weight:800;letter-spacing:.16em;color:var(--muted);margin-top:.6rem}
.fg-sched-list .t{margin-top:1rem;font-size:1.05rem;font-weight:800;color:var(--ink)}
.fg-sched-list .m{display:flex;flex-direction:column;margin-top:.3rem;font-size:.92rem;color:var(--muted)}
.fg-dates{display:flex;flex-wrap:wrap;align-items:baseline;gap:.4rem 1rem;margin-top:1rem;max-width:36rem;color:var(--on-ink);text-decoration:none}
.fg-dates>span{font-size:.78rem;font-weight:800;letter-spacing:.14em;color:var(--gold)}
.fg-dates ol{display:flex;flex-wrap:wrap;gap:.2rem 1.1rem;list-style:none;margin:0;padding:0}
.fg-dates li{font-size:.95rem;color:var(--on-ink-2)}
.fg-dates li b{font-family:var(--f-disp);font-size:1.5rem;font-weight:700;color:#fff;letter-spacing:-.01em}
.fg-dates li.is-next b{color:var(--gold)}
.fg-dates li.is-past{display:none}
.fg-dates:hover li b{text-decoration:underline;text-underline-offset:4px;text-decoration-thickness:1px}
@media (max-width:820px){.fg-sched-list{grid-template-columns:1fr}.fg-sched-list li{border-left:0;border-top:1px solid var(--line-2)}.fg-sched-list li:first-child{border-top:0}}
"""

if __name__ == "__main__":
    md = media()
    print("media bytes:", f'{md["_bytes"]:,}')
    for lang, name in (("ja", "Kawaguchi_seminar.html"), ("en", "Kawaguchi_seminar_en.html")):
        html = build(lang, md)
        io.open(os.path.join(HERE, name), "w", encoding="utf-8", newline="\n").write(html)
        print(name, f"{len(html):,} bytes")
