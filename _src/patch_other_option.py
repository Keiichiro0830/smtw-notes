# -*- coding: utf-8 -*-
"""コメントフォームの対象プルダウンに「その他」を追加し、選択時に自由記入欄を表示する。
   フォームスクリプトを含む全分割ファイルにパッチを当てる（JP/EN 自動判定）。"""
import re, os, io, glob

ROOT = os.path.dirname(os.path.abspath(__file__))

TXT = {
    'ja': {'otherLabel': 'その他', 'otherPh': '対象を自由にご記入ください', 'otherReq': '対象（その他）をご記入ください。'},
    'en': {'otherLabel': 'Other', 'otherPh': 'Describe the subject freely', 'otherReq': 'Please describe the subject.'},
}

def patch(text):
    if 'function buildMainForm' not in text:
        return text, False
    if 'value="other"' in text:
        return text, False  # already patched
    lang = 'ja' if 'generalLabel: "全体・運営について"' in text else 'en'
    t = TXT[lang]

    # 1) SMTW_CMT_TEXT に other* を追加（logTitle の後ろ）
    text = re.sub(
        r'(logTitle: "[^"]*")\s*\n(\s*)\};',
        lambda m: '%s,\n    otherLabel: "%s",\n    otherPh: "%s",\n    otherReq: "%s"\n%s};'
                  % (m.group(1), t['otherLabel'], t['otherPh'], t['otherReq'], m.group(2)),
        text, count=1)

    # 2) buildTargetOptions: グループ後に「その他」option を追加
    text = text.replace(
        "        html += group(SMTW_CMT_TEXT.grpMelmaga, melmagas);\n"
        "        return { html: html, count: papers.length + melmagas.length + 1 };",
        "        html += group(SMTW_CMT_TEXT.grpMelmaga, melmagas);\n"
        "        html += '<option value=\"other\">' + esc(SMTW_CMT_TEXT.otherLabel) + \"</option>\";\n"
        "        return { html: html, count: papers.length + melmagas.length + 2 };",
        1)

    # 3) box.innerHTML: 対象 select 行の直後に自由記入行（既定は非表示）
    text = text.replace(
        "'</label><select class=\"smtw-cmt-target\">' + opts.html + \"</select></div>\" +",
        "'</label><select class=\"smtw-cmt-target\">' + opts.html + \"</select></div>\" +\n"
        "            '<div class=\"smtw-cmt-row smtw-cmt-other-row\" style=\"display:none;\"><label>' + esc(SMTW_CMT_TEXT.otherLabel) +\n"
        "                '</label><input type=\"text\" class=\"smtw-cmt-other-input\" placeholder=\"' + esc(SMTW_CMT_TEXT.otherPh) + '\"></div>' +",
        1)

    # 4) 要素参照と change リスナー（logWrap 取得の直後）
    text = text.replace(
        '        const logWrap = box.querySelector(".smtw-cmt-log");\n',
        '        const logWrap = box.querySelector(".smtw-cmt-log");\n'
        '        const otherRow = box.querySelector(".smtw-cmt-other-row");\n'
        '        const otherInput = box.querySelector(".smtw-cmt-other-input");\n'
        '        targetEl.addEventListener("change", function () {\n'
        '            otherRow.style.display = (targetEl.value === "other") ? "" : "none";\n'
        '            if (targetEl.value === "other" && otherInput) { otherInput.focus(); }\n'
        '        });\n',
        1)

    # 5) selectedTarget: other のとき自由記入を atitle に
    text = text.replace(
        '            return { aid: aid, atitle: atitle };\n'
        '        }\n\n'
        '        btn.addEventListener("click",',
        '            if (aid === "other") { atitle = (otherInput && otherInput.value.trim()) || SMTW_CMT_TEXT.otherLabel; }\n'
        '            return { aid: aid, atitle: atitle };\n'
        '        }\n\n'
        '        btn.addEventListener("click",',
        1)

    # 6) 送信前バリデーション（other 選択かつ空ならエラー）
    text = text.replace(
        '            saveProfile(name, email);\n',
        '            if (tgt.aid === "other" && (!otherInput || !otherInput.value.trim())) { msg.className = "smtw-cmt-msg err"; msg.textContent = SMTW_CMT_TEXT.otherReq; if (otherInput) { otherInput.focus(); } return; }\n'
        '            saveProfile(name, email);\n',
        1)

    return text, True


def main():
    for path in sorted(glob.glob(os.path.join(ROOT, 'Kawaguchi_seminar*.html'))):
        if path.endswith('.bak') or path.endswith('.v1bak'):
            continue
        text = io.open(path, encoding='utf-8').read()
        new, changed = patch(text)
        if changed:
            io.open(path, 'w', encoding='utf-8').write(new)
        print('%s %s' % ('PATCHED' if changed else 'skip   ', os.path.basename(path)))


if __name__ == '__main__':
    main()
