# -*- coding: utf-8 -*-
"""ポータルを組み立てて暗号化し、docs/ へ置く（リポジトリ直下で実行）。

  python _src/deploy_portal.py            通常（写真ページは作り直さない）
  python _src/deploy_portal.py --photos   写真ページ（約30秒〜）も作り直す

1. portal_shell.py   既存ページ（日英）に共通のヘッダー・ページ見出し・テーマを当てる（冪等）
2. build_home.py     ホーム（日英）を生成
3. build_tshirt.py   川口先生Tシャツ案を生成
4. build_photos_1003.py（--photos のとき）
5. staticrypt        パスワード付きに暗号化 → encrypted/ → docs/ へコピー
そのあと  node _src/verify_build.mjs  で復号して中身を確認する。

写真入りの平文（ホーム・写真・Tシャツ案）は .gitignore 済み。公開されるのは暗号化された docs/ だけ。
"""
import os, shutil, subprocess, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.chdir(ROOT)
PY = sys.executable

THEMED = [
    "Kawaguchi_seminar_0822", "Kawaguchi_seminar_0822_en", "Kawaguchi_seminar_1003", "Kawaguchi_seminar_1003_en",
    "Kawaguchi_seminar_prev", "Kawaguchi_seminar_prev_en", "Kawaguchi_seminar_papers", "Kawaguchi_seminar_papers_en",
    "Kawaguchi_seminar_melmaga", "Kawaguchi_seminar_melmaga_en", "Kawaguchi_seminar_minutes", "Kawaguchi_seminar_minutes_en",
    "Kawaguchi_seminar_minutes1", "Kawaguchi_seminar_minutes2", "Kawaguchi_seminar_minutes3", "Kawaguchi_seminar_minutes4",
    "Kawaguchi_seminar_minutes5", "Kawaguchi_seminar_minutes1_en", "Kawaguchi_seminar_minutes2_en", "Kawaguchi_seminar_minutes3_en",
]
GENERATED = ["Kawaguchi_seminar", "Kawaguchi_seminar_en", "Kawaguchi_seminar_tshirt", "Kawaguchi_seminar_1003_photos"]


def run(*cmd, shell=False):
    print("$", " ".join(cmd))
    subprocess.run(cmd if not shell else " ".join(f'"{c}"' if " " in c else c for c in cmd), check=True, shell=shell)


def main():
    photos = "--photos" in sys.argv
    run(PY, "_src/portal_shell.py")
    run(PY, "_src/build_home.py")
    run(PY, "_src/build_tshirt.py")
    if photos:
        run(PY, "_src/build_photos_1003.py")
    names = THEMED + GENERATED
    if not photos and not os.path.exists("_src/Kawaguchi_seminar_1003_photos.html"):
        names.remove("Kawaguchi_seminar_1003_photos")
    srcs = [f"_src/{n}.html" for n in names]
    run("staticrypt", *srcs, "-p", "Kawaguchi", "--short", "-d", "encrypted", "-t", "_staticrypt_template.html",
        "--template-title", "知的鍛錬塾 / Kawaguchi Seminar", shell=True)
    for n in names:
        shutil.copyfile(f"encrypted/{n}.html", f"docs/{n}.html")
    print(f"deployed {len(names)} pages to docs/")


if __name__ == "__main__":
    main()
