# -*- coding: utf-8 -*-
"""SMTW ポータルを 1ページ → 4ページ構成に分割し、新規メルマガ2本を melmaga ページに追加する。
   入力: _src/Kawaguchi_seminar.html, _src/Kawaguchi_seminar_en.html
   出力: 上記2ファイルを index として残し、papers/melmaga/minutes の計8ファイルを _src に生成。
"""
import re, os, io

ROOT = os.path.dirname(os.path.abspath(__file__))
VAULT_NEW = r"C:\Users\keima\ObsidianVault\10 work\40 Still Modelling The World(SMTW)\Kawaguchi Seminar\10 DMM Mail Magazine\01_Original\New"

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def inline(s):
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    return s

REF_HEADERS = ('参考文献', '参考書', '出典', 'References')

def md_to_melmaga(md_path, date, title, aid):
    with io.open(md_path, encoding='utf-8') as f:
        md = f.read()
    blocks, cur = [], []
    for ln in md.split('\n'):
        s = ln.strip()
        if s == '':
            if cur:
                blocks.append(cur); cur = []
        else:
            cur.append(s)
    if cur:
        blocks.append(cur)

    out = []
    for blk in blocks:
        joined = ' '.join(blk).strip()
        # 単独太字 = 見出し
        if len(blk) == 1 and re.fullmatch(r'\*\*.+\*\*', blk[0]):
            out.append('<h4>' + esc(blk[0][2:-2]) + '</h4>')
            continue
        # 参考文献などの見出し（非太字）
        if joined in REF_HEADERS:
            out.append('<h4>' + esc(joined) + '</h4>')
            continue
        # コード的な例示行（"… → …"）は等幅ボックス
        if re.match(r'^["「].*(→|←)', joined):
            out.append('<p style="font-family:Consolas,\'Courier New\',monospace;'
                       'background:#f1f5f9;border:1px solid #e2e8f0;border-radius:4px;'
                       'padding:0.35rem 0.6rem;font-size:0.85rem;overflow-x:auto;'
                       'white-space:pre-wrap;">' + esc(joined) + '</p>')
            continue
        # 参考文献の本文（URL を含む）は小さめ
        if 'http' in joined:
            out.append('<p style="font-size:0.82rem;color:#64748b;word-break:break-all;">'
                       + inline(joined) + '</p>')
            continue
        out.append('<p>' + inline(joined) + '</p>')

    body = '\n'.join(out)
    cmt = ('<div class="smtw-cmt" data-aid="%s" data-atitle="%s"></div>'
           % (aid, esc('メルマガ %s %s' % (date, title))))
    return ('    <details class="melmaga" id="%s">\n'
            '      <summary><span class="mm-date">%s</span> %s</summary>\n'
            '      <div class="mm-body">\n%s\n%s\n      </div>\n'
            '    </details>\n' % (aid, date, esc(title), body, cmt))


def parse(path):
    with io.open(path, encoding='utf-8') as f:
        text = f.read()
    head = text[:text.index('</head>') + len('</head>')]
    h1 = re.search(r'<h1>.*?</h1>', text, re.S).group(0)
    subtitle = re.search(r'<p class="subtitle">.*?</p>', text, re.S).group(0)
    h2pos = [m.start() for m in re.finditer(r'<h2', text)]
    assert len(h2pos) == 8, '%s: expected 8 h2, got %d' % (path, len(h2pos))
    footer_pos = text.index('<footer')
    secs = [text[h2pos[i]:h2pos[i + 1]] for i in range(7)]
    comment = text[h2pos[7]:footer_pos].rstrip()
    footer = text[footer_pos:text.index('</footer>') + len('</footer>')]
    sm = re.search(r'<script>.*?</script>', text[footer_pos:], re.S)
    script = sm.group(0) if sm else ''
    return dict(head=head, h1=h1, subtitle=subtitle, secs=secs,
                comment=comment, footer=footer, script=script)


NAV_CSS = (
    "\n        .page-nav { display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:1.6rem; }\n"
    "        .page-nav a { flex:1 1 0; text-align:center; padding:0.6rem 0.7rem; background:#fff;"
    " border:1px solid #e2e8f0; border-radius:8px; color:#2c5282; text-decoration:none;"
    " font-size:0.9rem; font-weight:600; white-space:nowrap; }\n"
    "        .page-nav a:hover { box-shadow:0 2px 8px rgba(0,0,0,0.08); text-decoration:none; }\n"
    "        .page-nav a.active { background:#2c5282; color:#fff; border-color:#2c5282; }\n    "
)

# ファイル名（ja / en）
FILES = {
    'ja': {'index': 'Kawaguchi_seminar.html', 'papers': 'Kawaguchi_seminar_papers.html',
           'melmaga': 'Kawaguchi_seminar_melmaga.html', 'minutes': 'Kawaguchi_seminar_minutes.html'},
    'en': {'index': 'Kawaguchi_seminar_en.html', 'papers': 'Kawaguchi_seminar_papers_en.html',
           'melmaga': 'Kawaguchi_seminar_melmaga_en.html', 'minutes': 'Kawaguchi_seminar_minutes_en.html'},
}
NAV_LABELS = {
    'ja': [('index', 'トップ'), ('papers', '事前資料'), ('melmaga', 'メルマガ'), ('minutes', '議事メモ')],
    'en': [('index', 'Top'), ('papers', 'Pre-read'), ('melmaga', 'Newsletters'), ('minutes', 'Minutes')],
}
# アンカー所有ページ
ANCHOR_OWNER = {'sec1': 'index', 'sec2': 'minutes', 'sec3': 'papers', 'sec3-3': 'papers',
                'sec4': 'melmaga', 'sec5': 'minutes', 'sec6': 'minutes', 'sec7': 'minutes'}


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
    return re.sub(r'href="#(sec[0-9a-z-]*)"', repl, body)


def build_page(p, lang, active, body, has_form):
    head = p['head'].replace('</style>', NAV_CSS + '</style>')
    toggle_label = '🇬🇧 EN' if lang == 'ja' else '🇯🇵 JP'
    toggle_href = FILES['en' if lang == 'ja' else 'ja'][active]
    body = rewrite_anchors(body, lang)
    html = head + '\n<body>\n'
    html += '<a class="lang-toggle" href="%s">%s</a>\n' % (toggle_href, toggle_label)
    html += '<div class="container">\n'
    html += '    ' + p['h1'] + '\n'
    html += '    ' + p['subtitle'] + '\n\n'
    html += nav_html(lang, active) + '\n\n'
    html += body.strip('\n') + '\n\n'
    if has_form:
        html += '    ' + p['comment'].strip() + '\n\n'
    html += '    ' + p['footer'] + '\n'
    html += '</div>\n'
    if has_form:
        html += '\n' + p['script'] + '\n'
    html += '</body>\n</html>\n'
    return html


def main():
    # 新規メルマガ2本（JP）
    mm1 = md_to_melmaga(
        os.path.join(VAULT_NEW, '2026-05-23 「「楽になる」はずだったのに ―― AIはなぜ私たちを疲れさせるのか」の詳細.md'),
        '2026-05-23', '「楽になる」はずだったのに ―― AIはなぜ私たちを疲れさせるのか', 'mm-2026-05-23')
    mm2 = md_to_melmaga(
        os.path.join(VAULT_NEW, '2026-05-30 「大規模言語モデルの仕組み（１）：単語のベクトル化（埋め込み）」の詳細.md'),
        '2026-05-30', '大規模言語モデルの仕組み（１）：単語のベクトル化（埋め込み）', 'mm-2026-05-30')
    new_mm = mm1 + mm2

    for lang in ('ja', 'en'):
        src = os.path.join(ROOT, 'Kawaguchi_seminar.html' if lang == 'ja' else 'Kawaguchi_seminar_en.html')
        p = parse(src)
        sec1, sec2, sec3, sec4, sec5, sec6, sec7 = p['secs']

        # JP の melmaga セクションに新規2本を追加し、本数表記を更新
        if lang == 'ja':
            sec4 = sec4.rstrip() + '\n' + new_mm
            sec4 = sec4.replace('メルマガ5本', 'メルマガ7本')

        bodies = {
            'index':   sec1,
            'papers':  sec3,
            'melmaga': sec4,
            'minutes': sec2.rstrip() + '\n\n' + sec5.rstrip() + '\n\n' + sec6.rstrip() + '\n\n' + sec7.rstrip(),
        }
        for active, body in bodies.items():
            has_form = 'class="smtw-cmt"' in body
            html = build_page(p, lang, active, body, has_form)
            # minutes 内の「JP portal」リンクを minutes ページへ、melmaga 内は melmaga ページへ
            if active == 'minutes' and lang == 'en':
                html = html.replace('href="Kawaguchi_seminar.html"', 'href="%s"' % FILES['ja']['minutes'])
            if active == 'melmaga' and lang == 'en':
                html = html.replace('href="Kawaguchi_seminar.html"', 'href="%s"' % FILES['ja']['melmaga'])
            out_path = os.path.join(ROOT, FILES[lang][active])
            with io.open(out_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print('wrote %s (%d bytes, form=%s)' % (FILES[lang][active], len(html.encode('utf-8')), has_form))


if __name__ == '__main__':
    main()
