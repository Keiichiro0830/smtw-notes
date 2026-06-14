# -*- coding: utf-8 -*-
"""ポータル再編 v2: トップを「第3回ハブ（開催情報＋事前資料＋質問フォーム）」に集約し、
   それ以外（第2回開催情報・過去資料アーカイブ・メルマガ・議事メモ）を他ページへ。
   入力: 現在の4分割ファイル（v1 出力）。出力: 同じ8ファイルを再編して上書き。
"""
import re, os, io

ROOT = os.path.dirname(os.path.abspath(__file__))

FILES = {
    'ja': {'index': 'Kawaguchi_seminar.html', 'papers': 'Kawaguchi_seminar_papers.html',
           'melmaga': 'Kawaguchi_seminar_melmaga.html', 'minutes': 'Kawaguchi_seminar_minutes.html'},
    'en': {'index': 'Kawaguchi_seminar_en.html', 'papers': 'Kawaguchi_seminar_papers_en.html',
           'melmaga': 'Kawaguchi_seminar_melmaga_en.html', 'minutes': 'Kawaguchi_seminar_minutes_en.html'},
}
NAV_LABELS = {
    'ja': [('index', '第3回'), ('papers', '過去資料'), ('melmaga', 'メルマガ'), ('minutes', '議事メモ')],
    'en': [('index', '3rd Mtg'), ('papers', 'Archive'), ('melmaga', 'Newsletters'), ('minutes', 'Minutes')],
}
M = {'ja': {'logi3': '第3回（予定）'}, 'en': {'logi3': '3rd meeting (upcoming)'}}
HEAD = {
    'ja': {
        'top_logi':     '<h2 id="sec1">第3回（2026-06-20）開催情報</h2>',
        'top_materials':'<h2 id="sec3-3">事前読了資料（第3回向け）</h2>',
        'archive_h2':   '<h2 id="sec3">第2回（2026-05-09）向け 事前読了資料（アーカイブ）</h2>',
        'minutes_logi': '<h2 id="sec1b">第2回（2026-05-09）開催情報</h2>',
    },
    'en': {
        'top_logi':     '<h2 id="sec1">3rd meeting (2026-06-20) — logistics</h2>',
        'top_materials':'<h2 id="sec3-3">Pre-read materials (for the 3rd meeting)</h2>',
        'archive_h2':   '<h2 id="sec3">Pre-read papers — 2nd meeting (2026-05-09), archive</h2>',
        'minutes_logi': '<h2 id="sec1b">2nd meeting (2026-05-09) — logistics</h2>',
    },
}
ANCHOR_OWNER = {'sec3-3': 'index', 'sec3': 'papers', 'sec2': 'minutes', 'sec5': 'minutes',
                'sec6': 'minutes', 'sec7': 'minutes', 'sec1': 'index', 'sec1b': 'minutes',
                'sec4': 'melmaga'}

NAV_CSS = (
    "\n        .page-nav { display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:1.6rem; }\n"
    "        .page-nav a { flex:1 1 0; text-align:center; padding:0.6rem 0.7rem; background:#fff;"
    " border:1px solid #e2e8f0; border-radius:8px; color:#2c5282; text-decoration:none;"
    " font-size:0.9rem; font-weight:600; white-space:nowrap; }\n"
    "        .page-nav a:hover { box-shadow:0 2px 8px rgba(0,0,0,0.08); text-decoration:none; }\n"
    "        .page-nav a.active { background:#2c5282; color:#fff; border-color:#2c5282; }\n    "
)


def load(path):
    t = io.open(path, encoding='utf-8').read()
    head = t[:t.index('</head>') + len('</head>')]
    h1 = re.search(r'<h1>.*?</h1>', t, re.S).group(0)
    subtitle = re.search(r'<p class="subtitle">.*?</p>', t, re.S).group(0)
    nav_end = t.index('</nav>') + len('</nav>')
    footer_start = t.index('<footer')
    footer = t[footer_start:t.index('</footer>') + len('</footer>')]
    cf = t.find('id="smtw-cmt-form"')
    if cf != -1:
        cf_h2 = t.rfind('<h2', nav_end, cf)
        content = t[nav_end:cf_h2]
        comment = t[cf_h2:footer_start].rstrip()
    else:
        content = t[nav_end:footer_start]
        comment = ''
    sm = re.search(r'<script>.*?</script>', t[footer_start:], re.S)
    script = sm.group(0) if sm else ''
    return dict(head=head, h1=h1, subtitle=subtitle, footer=footer,
                content=content.strip('\n'), comment=comment, script=script)


def strip_lead_h3(block):
    return re.sub(r'^\s*<h3[^>]*>.*?</h3>\s*', '', block, count=1, flags=re.S).strip()


def nav_html(lang, active):
    parts = []
    for key, label in NAV_LABELS[lang]:
        cls = ' class="active"' if key == active else ''
        parts.append('<a href="%s"%s>%s</a>' % (FILES[lang][key], cls, label))
    return '    <nav class="page-nav">\n        ' + '\n        '.join(parts) + '\n    </nav>'


def rewrite_anchors(body, lang):
    def repl(m):
        anchor = m.group(1)
        owner = ANCHOR_OWNER.get(anchor)
        if not owner:
            return m.group(0)
        return 'href="%s#%s"' % (FILES[lang][owner], anchor)
    return re.sub(r'href="[^"]*#(sec[0-9a-z-]+)"', repl, body)


def assemble(lang, active, ref, body, script):
    head = ref['head']
    if '.page-nav' not in head:
        head = head.replace('</style>', NAV_CSS + '</style>')
    toggle_label = '🇬🇧 EN' if lang == 'ja' else '🇯🇵 JP'
    toggle_href = FILES['en' if lang == 'ja' else 'ja'][active]
    body = rewrite_anchors(body, lang)
    html = head + '\n<body>\n'
    html += '<a class="lang-toggle" href="%s">%s</a>\n' % (toggle_href, toggle_label)
    html += '<div class="container">\n'
    html += '    ' + ref['h1'] + '\n'
    html += '    ' + ref['subtitle'] + '\n\n'
    html += nav_html(lang, active) + '\n\n'
    html += body.strip('\n') + '\n\n'
    html += '    ' + ref['footer'] + '\n'
    html += '</div>\n'
    if script:
        html += '\n' + script + '\n'
    html += '</body>\n</html>\n'
    return html


def main():
    for lang in ('ja', 'en'):
        d = {k: load(os.path.join(ROOT, FILES[lang][k])) for k in FILES[lang]}
        idx, pap, mel, mins = d['index'], d['papers'], d['melmaga'], d['minutes']

        # --- sec1 を 第2回 / 第3回 に分割 ---
        c1 = idx['content']
        i3 = c1.index(M[lang]['logi3'])
        h3_3rd = c1.rfind('<h3', 0, i3)
        first_h3 = c1.index('<h3')
        table_2nd = strip_lead_h3(c1[first_h3:h3_3rd])
        table_3rd = strip_lead_h3(c1[h3_3rd:])

        # --- sec3 を 3.1 / 3.2 に分割 ---
        c3 = pap['content']
        m32 = re.search(r'<h3[^>]*>\s*3\.2 ', c3)
        sec3_1 = c3[:m32.start()].rstrip()
        sec3_2 = c3[m32.start():].rstrip()

        # 3.1: 旧 h2(sec3) を top_materials に置換、内側 3.1 h3 を除去
        s31 = re.sub(r'<h2 id="sec3">.*?</h2>', HEAD[lang]['top_materials'], sec3_1, count=1, flags=re.S)
        s31 = re.sub(r'<h3 id="sec3-3"[^>]*>.*?</h3>\s*', '', s31, count=1, flags=re.S)
        # 3.2: 旧 h3(3.2) を archive_h2 に置換
        s32 = re.sub(r'<h3[^>]*>\s*3\.2 .*?</h3>', HEAD[lang]['archive_h2'], sec3_2, count=1, flags=re.S)

        # --- 各ページ本文 ---
        top_body = (HEAD[lang]['top_logi'] + '\n' + table_3rd + '\n\n'
                    + s31 + '\n\n    ' + pap['comment'].strip())
        pap_body = s32 + '\n\n    ' + pap['comment'].strip()
        mel_body = mel['content'] + '\n\n    ' + mel['comment'].strip()
        mins_body = (HEAD[lang]['minutes_logi'] + '\n' + table_2nd + '\n\n' + mins['content'])

        pages = {
            'index':   (top_body,  pap['script']),
            'papers':  (pap_body,  pap['script']),
            'melmaga': (mel_body,  mel['script']),
            'minutes': (mins_body, ''),
        }
        for active, (body, script) in pages.items():
            html = assemble(lang, active, idx, body, script)
            out = os.path.join(ROOT, FILES[lang][active])
            io.open(out, 'w', encoding='utf-8').write(html)
            print('wrote %s (%d bytes, form=%s)' % (FILES[lang][active],
                  len(html.encode('utf-8')), bool(script)))


if __name__ == '__main__':
    main()
