"""Convert 5 メルマガ markdown files to HTML <details> blocks for embedding."""
import re
from pathlib import Path
import html

VAULT = Path(r"C:\Users\keima\OneDrive\アプリ\remotely-save\Obsidian Vault\10 work\40 Still Modelling The World(SMTW)\Kawaguchi Seminar\10 DMM Mail Magazine\01_Original\New")

FILES = [
    ("2026-04-15", "知的鍛錬の原理と方法は古びない", "2026-04-15 知的鍛錬の原理と方法は古びない.md"),
    ("2026-04-19", "AIは本当に「言葉の意味」を理解しているのか — 「確率的オウム」論争", "2026-04-19 「AIは本当に「言葉の意味」を理解しているのか—「確率的なオウム」か」の詳細.md"),
    ("2026-04-28", "生成AI利用に際しその仕組みをどの程度知っておくべきか — 知的生産の作法", "2026-04-28 「生成AI利用に際しその仕組みをどの程度しっておくべきか：知的生産の作法」の詳細.md"),
    ("2026-04-29", "AIの仕組み 2 — なぜ大学入試で首席合格できるのか", "2026-04-29 なぜ大学入試で首席合格できるのか  の詳細.md"),
    ("2026-05-03", "自分のもとめる知識を探す方法", "2026-05-03 「自分のもとめる知識を探す方法」の詳細.md"),
]


def md_to_html(md_text: str) -> str:
    """Convert raw メルマガ markdown to clean HTML.
    - Blank line separates paragraphs.
    - Consecutive non-blank lines = same paragraph (joined w/o space; Japanese).
    - **bold** -> <strong>
    - Lines like '==' or '--' separators are dropped.
    - Bullet '•' or '・' starts a list.
    """
    # Normalize and split into raw lines
    lines = md_text.replace("\r\n", "\n").split("\n")

    # Group into paragraph chunks separated by blank lines.
    # Also break before lines that look like a chapter heading or numbered list item,
    # since the source files often run those together without blank lines.
    chunks: list[list[str]] = []
    cur: list[str] = []
    chapter_re = re.compile(r"^(第[一二三四五六七八九十0-9]+章|[①-⑩]|\d+\.\s|・)")
    for ln in lines:
        s = ln.strip()
        if not s:
            if cur:
                chunks.append(cur)
                cur = []
        else:
            # Drop horizontal-rule lines that originated as separators
            if re.fullmatch(r"=+", s) or re.fullmatch(r"-+", s):
                if cur:
                    chunks.append(cur)
                    cur = []
                continue
            # Force paragraph break for chapter headings / numbered items
            if chapter_re.match(s) and cur:
                chunks.append(cur)
                cur = []
            cur.append(s)
    if cur:
        chunks.append(cur)

    out: list[str] = []
    for chunk in chunks:
        # Detect bullet list
        if all(re.match(r"^[•・]\s*", l) for l in chunk):
            out.append("<ul>")
            for l in chunk:
                item = re.sub(r"^[•・]\s*", "", l)
                out.append(f"  <li>{render_inline(item)}</li>")
            out.append("</ul>")
            continue

        # Detect heading (single line wrapped in **...** OR starting with 第N章)
        if len(chunk) == 1:
            l = chunk[0]
            m_bold = re.fullmatch(r"\*\*(.+?)\*\*", l)
            if m_bold:
                out.append(f"<h4>{render_inline(m_bold.group(1))}</h4>")
                continue
            if re.match(r"^第[一二三四五六七八九十0-9]+章", l):
                out.append(f"<h4>{render_inline(l)}</h4>")
                continue

        # Plain paragraph: join lines without space (Japanese)
        joined = "".join(chunk)
        out.append(f"<p>{render_inline(joined)}</p>")

    return "\n".join(out)


def render_inline(s: str) -> str:
    s = html.escape(s)
    # Restore ** as <strong>
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    # Linkify naked URLs
    s = re.sub(r"(https?://[^\s<]+)", r'<a href="\1" target="_blank" rel="noopener">\1</a>', s)
    return s


def build():
    parts = []
    for date_str, title, fname in FILES:
        p = VAULT / fname
        text = p.read_text(encoding="utf-8")
        body_html = md_to_html(text)
        block = f"""    <details class="melmaga">
      <summary><span class="mm-date">{date_str}</span> {html.escape(title)}</summary>
      <div class="mm-body">
{body_html}
      </div>
    </details>"""
        parts.append(block)
    return "\n".join(parts)


if __name__ == "__main__":
    out = build()
    Path(r"C:\Users\keima\OneDrive\Documents\Work\40 Still Modelling The World (SMTW)\_src\melmaga_blocks.html").write_text(out, encoding="utf-8")
    print("OK", len(out), "chars")
