from pathlib import Path

base = Path(r"C:\Users\keima\OneDrive\Documents\Work\40 Still Modelling The World (SMTW)\_src")
src = base / "Kawaguchi_seminar.html"
blocks = (base / "melmaga_blocks.html").read_text(encoding="utf-8")
text = src.read_text(encoding="utf-8")

old = """    <h2>4. 議論の前提（川口先生メルマガ5本）</h2>
    <p>川口先生から「議論の前提とする」とアナウンスされたメルマガ。読了済みである前提で議論に入ります。</p>
    <ul>
        <li>2026/04/15 — 知的鍛錬の原理と方法は古びない</li>
        <li>2026/04/19 — AI は本当に「言葉の意味」を理解しているのか</li>
        <li>2026/04/28 — 生成 AI 利用に際しその仕組みをどの程度しっておくべきか</li>
        <li>2026/04/29 — AI の仕組み 2：なぜ大学入試で首席合格できるのか</li>
        <li>2026/05/03 — 自分の求める知識を探す方法</li>
    </ul>"""

new = """    <h2>4. 議論の前提（川口先生メルマガ5本）</h2>
    <p>川口先生から「議論の前提とする」とアナウンスされたメルマガ。本文は下の見出しをクリックして展開してください。</p>
""" + blocks

assert old in text, "old block not found"
src.write_text(text.replace(old, new), encoding="utf-8")
print("OK", len(text), "->", len(text) + len(new) - len(old))
