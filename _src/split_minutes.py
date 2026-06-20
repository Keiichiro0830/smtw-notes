# -*- coding: utf-8 -*-
"""議事メモページを 1ページ → 回ごとの3ページに分割（第1回/第2回/第3回、日英）。
   各ページ上部に回ジャンプナビ（meeting-nav）を付与し、リンクを再マップ。
   入力: Kawaguchi_seminar_minutes(_en).html（6つのh2セクション・同順）
   出力: minutes(_en)=第3回 / minutes2(_en)=第2回 / minutes1(_en)=第1回
"""
import re, os, io

ROOT = os.path.dirname(os.path.abspath(__file__))

SRC = {'ja': 'Kawaguchi_seminar_minutes.html', 'en': 'Kawaguchi_seminar_minutes_en.html'}
OUT = {
    'ja': {'m3': 'Kawaguchi_seminar_minutes.html', 'm2': 'Kawaguchi_seminar_minutes2.html', 'm1': 'Kawaguchi_seminar_minutes1.html'},
    'en': {'m3': 'Kawaguchi_seminar_minutes_en.html', 'm2': 'Kawaguchi_seminar_minutes2_en.html', 'm1': 'Kawaguchi_seminar_minutes1_en.html'},
}
SUBNAV = {
    'ja': [('m3', '第3回（最新・06-20）'), ('m2', '第2回（05-09）'), ('m1', '第1回（04-11）')],
    'en': [('m3', '3rd · latest (06-20)'), ('m2', '2nd (05-09)'), ('m1', '1st (04-11)')],
}
TOGGLE = {'ja': ('Kawaguchi_seminar', '🇬🇧 EN'), 'en': ('Kawaguchi_seminar', '🇯🇵 JP')}

MEETING_CSS = (
    "\n        .meeting-nav { display:flex; flex-wrap:wrap; gap:0.4rem; margin:-0.6rem 0 1.6rem; }\n"
    "        .meeting-nav a { flex:1 1 0; text-align:center; padding:0.45rem 0.6rem; background:#eef2f7;"
    " border:1px solid #cbd5e1; border-radius:6px; color:#475569; text-decoration:none;"
    " font-size:0.82rem; white-space:nowrap; }\n"
    "        .meeting-nav a:hover { background:#dbe4f0; text-decoration:none; }\n"
    "        .meeting-nav a.active { background:#1f3a5f; color:#fff; border-color:#1f3a5f; font-weight:600; }\n    "
)

# EN twin filenames for lang-toggle
EN_TWIN = {'m3': 'Kawaguchi_seminar_minutes_en.html', 'm2': 'Kawaguchi_seminar_minutes2_en.html', 'm1': 'Kawaguchi_seminar_minutes1_en.html'}
JA_TWIN = {'m3': 'Kawaguchi_seminar_minutes.html', 'm2': 'Kawaguchi_seminar_minutes2.html', 'm1': 'Kawaguchi_seminar_minutes1.html'}


def strip_trailing_links(block):
    # 末尾の nav-link / lang-switch 段落を除去
    return re.sub(r'<p style="margin-top:1\.4rem;">\s*<a class="(?:nav-link|lang-switch)".*?</a>\s*</p>\s*',
                  '', block, flags=re.S).rstrip()


def build(lang):
    text = io.open(os.path.join(ROOT, SRC[lang]), encoding='utf-8').read()
    head = text[:text.index('</head>') + len('</head>')]
    if '.meeting-nav' not in head:
        head = head.replace('</style>', MEETING_CSS + '</style>')
    h1 = re.search(r'<h1>.*?</h1>', text, re.S).group(0)
    subtitle = re.search(r'<p class="subtitle">.*?</p>', text, re.S).group(0)
    pagenav = re.search(r'<nav class="page-nav">.*?</nav>', text, re.S).group(0)
    footer = re.search(r'<footer>.*?</footer>', text, re.S).group(0)

    nav_end = text.index('</nav>') + len('</nav>')
    footer_start = text.index('<footer')
    content = text[nav_end:footer_start]

    h2pos = [m.start() for m in re.finditer(r'<h2', content)]
    assert len(h2pos) == 6, '%s: expected 6 h2, got %d' % (lang, len(h2pos))
    blk = [content[h2pos[i]:h2pos[i + 1]] for i in range(5)] + [content[h2pos[5]:]]
    # blk[0]=第2回開催情報 [1]=第2回アジェンダ [2]=当日参加予定 [3]=第1回議事メモ [4]=第2回議事メモ [5]=第3回議事メモ

    bodies = {
        'm3': strip_trailing_links(blk[5]),
        'm2': (blk[0] + blk[1] + blk[2] + blk[4]).rstrip(),
        'm1': blk[3].rstrip(),
    }

    # --- リンク再マップ ---
    if lang == 'ja':
        bodies['m2'] = bodies['m2'].replace('Kawaguchi_seminar_minutes.html#sec7',
                                            'Kawaguchi_seminar_minutes2.html#sec7')
    else:
        bodies['m2'] = bodies['m2'].replace('Kawaguchi_seminar_minutes_en.html#sec7',
                                            'Kawaguchi_seminar_minutes2_en.html#sec7')
        # EN本文中の「JP portal」リンク（bare minutes.html）を各回のJPページへ
        bodies['m2'] = bodies['m2'].replace('"Kawaguchi_seminar_minutes.html"',
                                            '"Kawaguchi_seminar_minutes2.html"')
        bodies['m1'] = bodies['m1'].replace('"Kawaguchi_seminar_minutes.html"',
                                            '"Kawaguchi_seminar_minutes1.html"')

    for key in ('m3', 'm2', 'm1'):
        # meeting-nav
        items = []
        for k, label in SUBNAV[lang]:
            cls = ' class="active"' if k == key else ''
            items.append('<a href="%s"%s>%s</a>' % (OUT[lang][k], cls, label))
        meeting_nav = '    <nav class="meeting-nav">\n        ' + '\n        '.join(items) + '\n    </nav>'
        # lang-toggle
        twin = EN_TWIN[key] if lang == 'ja' else JA_TWIN[key]
        toggle = '<a class="lang-toggle" href="%s">%s</a>' % (twin, TOGGLE[lang][1])

        html = head + '\n<body>\n' + toggle + '\n<div class="container">\n'
        html += '    ' + h1 + '\n    ' + subtitle + '\n\n'
        html += pagenav + '\n' + meeting_nav + '\n\n'
        html += bodies[key].strip('\n') + '\n\n    ' + footer + '\n</div>\n</body>\n</html>\n'

        io.open(os.path.join(ROOT, OUT[lang][key]), 'w', encoding='utf-8').write(html)
        print('wrote %s (%d bytes)' % (OUT[lang][key], len(html.encode('utf-8'))))


def main():
    for lang in ('ja', 'en'):
        build(lang)


if __name__ == '__main__':
    main()
