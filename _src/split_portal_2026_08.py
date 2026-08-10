# -*- coding: utf-8 -*-
"""
会員ポータルの1枚ページを、トップ（構造ハブ）＋ イベント別3ページに分割する。

  Kawaguchi_seminar.html        → トップ（何がいつあるかだけを見せる）
  Kawaguchi_seminar_0822.html   → 第5回 研究会（2026-08-22）
  Kawaguchi_seminar_1003.html   → 秋のシンポジウム（2026-10-03）
  Kawaguchi_seminar_prev.html   → 第4回（2026-07-18・開催済）＋事前資料＋アンケート

EN も同じ構成（_en サフィックス）。
分割は一度きり。以後は各ページを直接編集する。
"""
import io, os, sys, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = os.path.dirname(os.path.abspath(__file__))

def rd(p):
    return io.open(os.path.join(SRC, p), encoding='utf-8').read()

def wr(p, s):
    io.open(os.path.join(SRC, p), 'w', encoding='utf-8', newline='').write(s)

log = []
def must(cond, msg):
    if not cond:
        raise SystemExit('FAIL: ' + msg)
    log.append('ok  ' + msg)

HUB_CSS = """
        .hub { display:grid; grid-template-columns:1fr; gap:1rem; margin:1.4rem 0 2rem; }
        @media (min-width:640px) { .hub { grid-template-columns:1fr 1fr; } }
        .hub-card { display:block; background:#fff; border:1px solid #e2e8f0; border-left:5px solid #2c5282;
                    border-radius:10px; padding:1.1rem 1.3rem; text-decoration:none; color:inherit;
                    transition:box-shadow 0.15s; }
        .hub-card:hover { box-shadow:0 3px 12px rgba(0,0,0,0.09); text-decoration:none; }
        .hub-card .hc-when { font-size:0.82rem; color:#64748b; font-weight:600; }
        .hub-card .hc-title { font-size:1.05rem; color:#2c5282; font-weight:700; margin:0.25rem 0 0.55rem; }
        .hub-card ul { margin:0 0 0 1.1rem; font-size:0.9rem; color:#475569; }
        .hub-card li { margin-bottom:0.2rem; }
        .hub-card .hc-go { display:inline-block; margin-top:0.7rem; font-size:0.85rem; font-weight:600; color:#2c5282; }
        .hub-card.next { border-left-color:#b45309; background:#fffdf7; }
        .hub-card.next .hc-title { color:#b45309; }
        .hub-card.past { border-left-color:#94a3b8; }
        .hub-card.past .hc-title { color:#475569; }
        .hub-more { display:flex; flex-wrap:wrap; gap:0.5rem; margin:0 0 2rem; }
        .hub-more a { flex:1 1 30%; text-align:center; padding:0.75rem 0.8rem; background:#f8fafc;
                      border:1px solid #e2e8f0; border-radius:8px; color:#2c5282; text-decoration:none;
                      font-size:0.9rem; font-weight:600; }
        .hub-more a:hover { background:#fff; box-shadow:0 2px 8px rgba(0,0,0,0.06); text-decoration:none; }
"""

PAGES_JA = [('Kawaguchi_seminar.html', 0), ('Kawaguchi_seminar_0822.html', 1),
            ('Kawaguchi_seminar_1003.html', 2), ('Kawaguchi_seminar_prev.html', 3)]
PAGES_EN = [('Kawaguchi_seminar_en.html', 0), ('Kawaguchi_seminar_0822_en.html', 1),
            ('Kawaguchi_seminar_1003_en.html', 2), ('Kawaguchi_seminar_prev_en.html', 3)]

NAV_ITEMS_JA = [('Kawaguchi_seminar.html', 'トップ'),
                ('Kawaguchi_seminar_0822.html', '8/22 研究会'),
                ('Kawaguchi_seminar_1003.html', '10/3 シンポジウム'),
                ('Kawaguchi_seminar_prev.html', '第4回'),
                ('Kawaguchi_seminar_papers.html', '過去資料'),
                ('Kawaguchi_seminar_melmaga.html', 'メルマガ'),
                ('Kawaguchi_seminar_minutes.html', '議事メモ')]
NAV_ITEMS_EN = [('Kawaguchi_seminar_en.html', 'Top'),
                ('Kawaguchi_seminar_0822_en.html', 'Aug 22'),
                ('Kawaguchi_seminar_1003_en.html', 'Oct 3'),
                ('Kawaguchi_seminar_prev_en.html', '4th mtg'),
                ('Kawaguchi_seminar_papers_en.html', 'Archive'),
                ('Kawaguchi_seminar_melmaga_en.html', 'Newsletters'),
                ('Kawaguchi_seminar_minutes_en.html', 'Minutes')]

def nav(items, active_href):
    out = ['    <nav class="page-nav">']
    for href, label in items:
        cls = ' class="active"' if href == active_href else ''
        out.append('        <a href="%s"%s>%s</a>' % (href, cls, label))
    out.append('    </nav>')
    return '\n'.join(out)


def split(fname, marks):
    """marks: list of (name, start_marker). Blocks run marker-to-next-marker."""
    s = rd(fname)
    idx = []
    for name, m in marks:
        must(s.count(m) == 1, '%s: marker unique %r' % (fname, m[:40]))
        idx.append((name, s.index(m)))
    idx.sort(key=lambda t: t[1])
    blocks = {}
    for i, (name, pos) in enumerate(idx):
        end = idx[i + 1][1] if i + 1 < len(idx) else len(s)
        blocks[name] = s[pos:end]
    return s, blocks


# ============================== JA ==============================
MARKS_JA = [
    ('head',    '<!DOCTYPE html>'),
    ('h1',      '    <h1>AIx知的鍛錬塾 ポータル</h1>'),
    ('nav',     '    <nav class="page-nav">'),
    ('yotei',   '<div class="decision-box">'),
    ('s0822',   '<h2 id="sec5">'),
    ('s1003',   '<h2 id="sec-sympo">'),
    ('sprev',   '<h2 id="sec1">'),
    ('sdist',   '<h2 id="sec-dist">'),
    ('ssurvey', '<h2 id="sec3">'),
    ('scmt',    '<h2 style="margin-top:2.4rem;">第4回（7/18）事前コメント・質問フォーム</h2>'),
    ('supl',    '<h2 id="sec-submit"'),
]
full_ja, B = split('Kawaguchi_seminar.html', MARKS_JA)

head_ja = B['head']
must(head_ja.rstrip().endswith('<div class="container">'), 'JA: head block ends at container open')
must('</style>' in head_ja and '<title>' in head_ja, 'JA: head has style+title')
head_ja = head_ja.replace('    </style>', HUB_CSS + '    </style>', 1)

# container close + scripts + </html>
tail_start = B['supl'].index('    <footer>')
footer_and_scripts_ja = B['supl'][tail_start:]
must('</html>' in footer_and_scripts_ja and footer_and_scripts_ja.count('<script>') == 3,
     'JA: tail carries footer + 3 scripts')
upl_ja = B['supl'][:tail_start]

HUB_JA = """<div class="hub">
    <a class="hub-card next" href="Kawaguchi_seminar_0822.html">
        <div class="hc-when">2026年8月22日（土）10:00〜16:00 ／ 次回</div>
        <div class="hc-title">第5回 研究会 — エージェンティック時空統計学 入門</div>
        <ul>
            <li>早稲田 26号館11階 <strong>1102会議室</strong>（1101から変更）</li>
            <li><strong>事前に R と RStudio のインストール</strong>をお願いします</li>
            <li><strong>事前課題あり</strong>（2025年の演習を受講された方）</li>
        </ul>
        <span class="hc-go">→ 会場・時間割・事前課題・資料を見る</span>
    </a>
    <a class="hub-card" href="Kawaguchi_seminar_1003.html">
        <div class="hc-when">2026年10月3日（土）14:00〜17:00頃</div>
        <div class="hc-title">秋のシンポジウム — 今回は違うか？：ITブームとAIブームの違い</div>
        <ul>
            <li>同じく 26号館11階 1102会議室・約20名</li>
            <li><strong>メンバーの皆さまは参加前提</strong>でご予定ください</li>
            <li>終了後（17:30頃〜）に<strong>ゼミ会（懇親会）</strong></li>
        </ul>
        <span class="hc-go">→ テーマ・登壇・ゼミ会・8/26 学会を見る</span>
    </a>
    <a class="hub-card past" href="Kawaguchi_seminar_prev.html">
        <div class="hc-when">2026年7月18日（土）・開催済</div>
        <div class="hc-title">第4回 — ループ・エンジニアリング演習</div>
        <ul>
            <li>当日スライド・事前資料（全7点）</li>
            <li>第3回後アンケートの結果</li>
        </ul>
        <span class="hc-go">→ 前回の資料とアンケート結果を見る</span>
    </a>
    <a class="hub-card past" href="Kawaguchi_seminar_minutes.html">
        <div class="hc-when">第1回〜第4回</div>
        <div class="hc-title">議事メモ</div>
        <ul>
            <li>各回の議論の記録（ページ内タブで切替）</li>
        </ul>
        <span class="hc-go">→ 議事メモを読む</span>
    </a>
</div>

<div class="hub-more">
    <a href="Kawaguchi_seminar_papers.html">過去資料アーカイブ</a>
    <a href="Kawaguchi_seminar_melmaga.html">関連メルマガ</a>
    <a href="Kawaguchi_seminar_articles.html">日経記事×AI 課題</a>
</div>

"""

SUB_TOP_JA = ('    <p class="subtitle">次回は <strong>8月22日（土）10:00〜16:00</strong>（第5回 研究会・26号館11階 1102）'
              '／ <strong>10月3日（土）14:00〜17:00頃</strong>（秋のシンポジウム、終了後にゼミ会）。'
              '事前のお願いは <strong>R＋RStudio のインストール</strong>と<strong>事前課題</strong>です。'
              '<br><span style="font-size:0.85rem;">最終更新: 2026-08-10</span></p>\n')

def sub_simple_ja(text):
    return '    <p class="subtitle">%s</p>\n' % text

def page_ja(name, active, title, h1, subtitle, body, en_href):
    h = head_ja.replace('<title>AIx知的鍛錬塾 ポータル</title>', '<title>%s</title>' % title, 1)
    h = h.replace('<a class="lang-toggle" href="Kawaguchi_seminar_en.html">',
                  '<a class="lang-toggle" href="%s">' % en_href, 1)
    must('<title>%s</title>' % title in h, '%s: title set' % name)
    return (h + '\n    <h1>%s</h1>\n' % h1 + subtitle + '\n' + nav(NAV_ITEMS_JA, active) + '\n\n'
            + body.rstrip() + '\n\n' + footer_and_scripts_ja)

wr('Kawaguchi_seminar.html', page_ja(
    'top', 'Kawaguchi_seminar.html', 'AIx知的鍛錬塾 ポータル', 'AIx知的鍛錬塾 ポータル',
    SUB_TOP_JA, HUB_JA + B['sdist'] + '\n' + B['scmt'].replace(
        '<h2 style="margin-top:2.4rem;">第4回（7/18）事前コメント・質問フォーム</h2>',
        '<h2 style="margin-top:2.4rem;">コメント・ご質問フォーム</h2>').replace(
        '第4回に向けたご質問・ご要望、運営へのご意見をこちらからどうぞ。上の各資料カードからは資料ごとのコメントも送れます。',
        'ご質問・ご要望、運営へのご意見をこちらからどうぞ。各資料へのコメントは、'
        '<a href="Kawaguchi_seminar_prev.html">第4回のページ</a>の資料カードからお送りいただけます。')
    + '\n' + upl_ja,
    'Kawaguchi_seminar_en.html'))

wr('Kawaguchi_seminar_0822.html', page_ja(
    '0822', 'Kawaguchi_seminar_0822.html', '第5回 研究会（2026-08-22）｜AIx知的鍛錬塾',
    '第5回 研究会 — 2026年8月22日（土）',
    sub_simple_ja('研究会『大規模言語モデルと時空モデリング：依存の統計学アプローチ』'
                  '／ 早稲田大学 26号館11階 <strong>1102会議室</strong>（1101から変更）'
                  '／ <strong>10:00 開始 → 16:00 ラップアップ</strong>'
                  '<br><span style="font-size:0.85rem;">最終更新: 2026-08-10</span>'),
    B['s0822'], 'Kawaguchi_seminar_0822_en.html'))

wr('Kawaguchi_seminar_1003.html', page_ja(
    '1003', 'Kawaguchi_seminar_1003.html', '秋のシンポジウム（2026-10-03）｜AIx知的鍛錬塾',
    '秋のシンポジウム — 2026年10月3日（土）',
    sub_simple_ja('シンポジウム『今回は違うか？：ITブームとAIブームの違い』'
                  '／ 26号館11階 1102会議室 ／ <strong>14:00 開始 → 17:00頃 終了</strong>'
                  '／ 終了後にゼミ会（懇親会）'
                  '<br><span style="font-size:0.85rem;">最終更新: 2026-08-10</span>'),
    B['s1003'], 'Kawaguchi_seminar_1003_en.html'))

wr('Kawaguchi_seminar_prev.html', page_ja(
    'prev', 'Kawaguchi_seminar_prev.html', '第4回（2026-07-18・開催済）｜AIx知的鍛錬塾',
    '第4回 — 2026年7月18日（土・開催済）',
    sub_simple_ja('ループ・エンジニアリング演習 ／ 当日スライドと事前資料、第3回後アンケートの結果'
                  '。議論の記録は <a href="Kawaguchi_seminar_minutes.html">議事メモ</a> をご覧ください。'),
    B['sprev'] + '\n' + B['ssurvey'], 'Kawaguchi_seminar_prev_en.html'))

# ============================== EN ==============================
MARKS_EN = [
    ('head',    '<!DOCTYPE html>'),
    ('h1',      '    <h1>AI x Intellectual Forging Academy — Portal</h1>'),
    ('nav',     '    <nav class="page-nav">'),
    ('yotei',   '<div class="decision-box">'),
    ('s0822',   '<h2 id="sec5">'),
    ('s1003',   '<h2 id="sec-sympo">'),
    ('sprev',   '<h2 id="sec1">'),
    ('sdist',   '<h2 id="sec-dist">'),
    ('ssurvey', '<h2 id="sec3">'),
    ('scmt',    '<h2 style="margin-top:2.4rem;">Comments &amp; Questions for the 4th Meeting (July 18)</h2>'),
    ('supl',    '<h2 id="sec-submit"'),
]
full_en, E = split('Kawaguchi_seminar_en.html', MARKS_EN)

head_en = E['head']
must(head_en.rstrip().endswith('<div class="container">'), 'EN: head block ends at container open')
head_en = head_en.replace('    </style>', HUB_CSS + '    </style>', 1)
tail_start_en = E['supl'].index('    <footer>')
footer_and_scripts_en = E['supl'][tail_start_en:]
must('</html>' in footer_and_scripts_en and footer_and_scripts_en.count('<script>') == 3,
     'EN: tail carries footer + 3 scripts')
upl_en = E['supl'][:tail_start_en]

HUB_EN = """<div class="hub">
    <a class="hub-card next" href="Kawaguchi_seminar_0822_en.html">
        <div class="hc-when">Saturday, August 22, 2026, 10:00&ndash;16:00 &middot; next</div>
        <div class="hc-title">5th meeting &mdash; agentic spatio-temporal statistics, an introduction</div>
        <ul>
            <li>Waseda Bldg 26, 11F, <strong>Room 1102</strong> (changed from 1101)</li>
            <li>Please <strong>install R and RStudio</strong> beforehand</li>
            <li><strong>Advance task</strong> for those who took the 2025 exercises</li>
        </ul>
        <span class="hc-go">&rarr; venue, timetable, advance task, materials</span>
    </a>
    <a class="hub-card" href="Kawaguchi_seminar_1003_en.html">
        <div class="hc-when">Saturday, October 3, 2026, 14:00&ndash;around 17:00</div>
        <div class="hc-title">Autumn symposium &mdash; Is This Time Different? The IT Boom vs. the AI Boom</div>
        <ul>
            <li>Same Room 1102 &middot; about 20 people</li>
            <li><strong>Members: please treat attendance as assumed</strong></li>
            <li>A <strong>zemi-kai reception</strong> follows from about 17:30</li>
        </ul>
        <span class="hc-go">&rarr; theme, speakers, reception, the Aug 26 conference</span>
    </a>
    <a class="hub-card past" href="Kawaguchi_seminar_prev_en.html">
        <div class="hc-when">Saturday, July 18, 2026 &middot; held</div>
        <div class="hc-title">4th meeting &mdash; the loop-engineering exercise</div>
        <ul>
            <li>Session slides and all seven pre-reads</li>
            <li>Results of the post-3rd-meeting survey</li>
        </ul>
        <span class="hc-go">&rarr; last session&rsquo;s materials and survey</span>
    </a>
    <a class="hub-card past" href="Kawaguchi_seminar_minutes_en.html">
        <div class="hc-when">1st&ndash;4th meetings</div>
        <div class="hc-title">Minutes</div>
        <ul>
            <li>The record of each discussion (tabs on that page)</li>
        </ul>
        <span class="hc-go">&rarr; read the minutes</span>
    </a>
</div>

<div class="hub-more">
    <a href="Kawaguchi_seminar_papers_en.html">Archive of past materials</a>
    <a href="Kawaguchi_seminar_melmaga_en.html">Newsletter excerpts</a>
    <a href="Kawaguchi_seminar_articles.html">Nikkei &times; AI assignment</a>
</div>

"""

def page_en(name, active, title, h1, subtitle, body, ja_href):
    h = head_en.replace('<title>', '<title>', 1)
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, h, count=1, flags=re.S)
    h = h.replace('<a class="lang-toggle" href="Kawaguchi_seminar.html">',
                  '<a class="lang-toggle" href="%s">' % ja_href, 1)
    must('<title>%s</title>' % title in h, '%s: title set' % name)
    return (h + '\n    <h1>%s</h1>\n' % h1 + subtitle + '\n' + nav(NAV_ITEMS_EN, active) + '\n\n'
            + body.rstrip() + '\n\n' + footer_and_scripts_en)

def sub_en(text):
    return '    <p class="subtitle">%s</p>\n' % text

wr('Kawaguchi_seminar_en.html', page_en(
    'top', 'Kawaguchi_seminar_en.html', 'AI x Intellectual Forging Academy — Portal',
    'AI x Intellectual Forging Academy — Portal',
    sub_en('Next: <strong>Saturday, August 22, 10:00&ndash;16:00</strong> (5th meeting, Bldg 26, Room 1102) '
           '&middot; <strong>Saturday, October 3, 14:00&ndash;around 17:00</strong> (autumn symposium, reception to follow). '
           'What we ask of you beforehand: <strong>install R and RStudio</strong>, and the <strong>advance task</strong>.'
           '<br><span style="font-size:0.85rem;">Last updated: 2026-08-10</span>'),
    HUB_EN + E['sdist'] + '\n' + E['scmt'].replace(
        '<h2 style="margin-top:2.4rem;">Comments &amp; Questions for the 4th Meeting (July 18)</h2>',
        '<h2 style="margin-top:2.4rem;">Comments &amp; questions</h2>') + '\n' + upl_en,
    'Kawaguchi_seminar.html'))

wr('Kawaguchi_seminar_0822_en.html', page_en(
    '0822', 'Kawaguchi_seminar_0822_en.html', '5th meeting (2026-08-22) — AI x Intellectual Forging Academy',
    '5th meeting &mdash; Saturday, August 22, 2026',
    sub_en('Workshop: &ldquo;Large Language Models and Spatio-Temporal Modelling: A Statistical Approach to Dependence&rdquo; '
           '&middot; Waseda Bldg 26, 11F, <strong>Room 1102</strong> (changed from 1101) '
           '&middot; <strong>10:00 start &rarr; 16:00 wrap-up</strong>'
           '<br><span style="font-size:0.85rem;">Last updated: 2026-08-10</span>'),
    E['s0822'], 'Kawaguchi_seminar_0822.html'))

wr('Kawaguchi_seminar_1003_en.html', page_en(
    '1003', 'Kawaguchi_seminar_1003_en.html', 'Autumn symposium (2026-10-03) — AI x Intellectual Forging Academy',
    'Autumn symposium &mdash; Saturday, October 3, 2026',
    sub_en('Symposium: &ldquo;Is This Time Different? The IT Boom vs. the AI Boom&rdquo; '
           '&middot; Bldg 26, 11F, Room 1102 &middot; <strong>14:00 start &rarr; around 17:00</strong> '
           '&middot; zemi-kai reception to follow'
           '<br><span style="font-size:0.85rem;">Last updated: 2026-08-10</span>'),
    E['s1003'], 'Kawaguchi_seminar_1003.html'))

wr('Kawaguchi_seminar_prev_en.html', page_en(
    'prev', 'Kawaguchi_seminar_prev_en.html', '4th meeting (2026-07-18, held) — AI x Intellectual Forging Academy',
    '4th meeting &mdash; Saturday, July 18, 2026 (held)',
    sub_en('The loop-engineering exercise &middot; session slides and pre-reads, plus the post-3rd-meeting survey. '
           'For the discussion itself see the <a href="Kawaguchi_seminar_minutes_en.html">minutes</a>.'),
    E['sprev'] + '\n' + E['ssurvey'], 'Kawaguchi_seminar_prev.html'))

# ============ 3. 既存ページのナビを7項目に差し替え ============
OLD_NAV_RE = re.compile(r'[ \t]*<nav class="page-nav">.*?</nav>', re.S)
for f, items, active in [
        ('Kawaguchi_seminar_papers.html', NAV_ITEMS_JA, 'Kawaguchi_seminar_papers.html'),
        ('Kawaguchi_seminar_melmaga.html', NAV_ITEMS_JA, 'Kawaguchi_seminar_melmaga.html'),
        ('Kawaguchi_seminar_minutes.html', NAV_ITEMS_JA, 'Kawaguchi_seminar_minutes.html'),
        ('Kawaguchi_seminar_minutes1.html', NAV_ITEMS_JA, 'Kawaguchi_seminar_minutes.html'),
        ('Kawaguchi_seminar_minutes2.html', NAV_ITEMS_JA, 'Kawaguchi_seminar_minutes.html'),
        ('Kawaguchi_seminar_minutes3.html', NAV_ITEMS_JA, 'Kawaguchi_seminar_minutes.html'),
        ('Kawaguchi_seminar_papers_en.html', NAV_ITEMS_EN, 'Kawaguchi_seminar_papers_en.html'),
        ('Kawaguchi_seminar_melmaga_en.html', NAV_ITEMS_EN, 'Kawaguchi_seminar_melmaga_en.html'),
        ('Kawaguchi_seminar_minutes_en.html', NAV_ITEMS_EN, 'Kawaguchi_seminar_minutes_en.html'),
        ('Kawaguchi_seminar_minutes1_en.html', NAV_ITEMS_EN, 'Kawaguchi_seminar_minutes_en.html'),
        ('Kawaguchi_seminar_minutes2_en.html', NAV_ITEMS_EN, 'Kawaguchi_seminar_minutes_en.html'),
        ('Kawaguchi_seminar_minutes3_en.html', NAV_ITEMS_EN, 'Kawaguchi_seminar_minutes_en.html')]:
    s = rd(f)
    n = len(OLD_NAV_RE.findall(s))
    must(n == 1, '%s: exactly one page-nav (got %d)' % (f, n))
    s = OLD_NAV_RE.sub(lambda m: nav(items, active), s, count=1)
    wr(f, s)

# ============ 4. 事後チェック ============
for f in ['Kawaguchi_seminar.html', 'Kawaguchi_seminar_0822.html', 'Kawaguchi_seminar_1003.html',
          'Kawaguchi_seminar_prev.html', 'Kawaguchi_seminar_en.html', 'Kawaguchi_seminar_0822_en.html',
          'Kawaguchi_seminar_1003_en.html', 'Kawaguchi_seminar_prev_en.html']:
    s = rd(f)
    must(s.count('<script>') == 3 and s.count('</script>') == 3, '%s: 3 script blocks' % f)
    must(s.count('<div class="container">') == 1, '%s: one container' % f)
    must(s.rstrip().endswith('</html>'), '%s: ends with </html>' % f)
    must(s.count('<div') == s.count('</div>'), '%s: div balance' % f)
    must(s.count('<table') == s.count('</table>'), '%s: table balance' % f)
    must(s.count('class="page-nav"') == 1, '%s: one nav' % f)
    must(s.count('<h1>') == 1, '%s: one h1' % f)
    # SVG の <title> がグラフ内に入るため、head 内だけを数える
    must(s.count('<title>', 0, s.index('</head>')) == 1, '%s: one <title> in head' % f)

print('\n'.join(log))
print('\n分割完了: 8ページ + 既存12ページのナビ差し替え')
