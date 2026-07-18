# -*- coding: utf-8 -*-
import re, os, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
fail = 0
for src in ["_src/Kawaguchi_seminar.html", "_src/Kawaguchi_seminar_en.html",
            "_src/Kawaguchi_seminar_video1.html", "_src/Kawaguchi_seminar_articles.html"]:
    with open(src, encoding="utf-8") as f:
        html = f.read()
    for href in re.findall(r'href="([^"#]+)"', html):
        if href.startswith(("http", "data:", "mailto:")):
            continue
        if "'" in href or "+" in href:  # JS-built dynamic href (e.g. 配布BOX list), not a static path
            continue
        target = os.path.join("docs", href)
        ok = os.path.exists(target)
        if not ok:
            fail += 1
            print(f"FAIL {src}: missing docs/{href}")
print("all local hrefs resolve in docs/" if fail == 0 else f"{fail} broken link(s)")
sys.exit(1 if fail else 0)
