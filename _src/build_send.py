# -*- coding: utf-8 -*-
"""先生・事務局用の一斉配布ページを生成する。

  python _src/build_send.py     → _src/Kawaguchi_seminar_send.html（平文。.gitignore 済み。公開は暗号化した docs/ 版）

ページには秘密を置かない。送信の可否は GAS 側でシート「配布設定」の合言葉と照合して決める
（リポジトリは公開で、GAS の URL は誰でも分かる前提）。宛先は GAS 側のシート「名簿」。
流れ: 合言葉 → 名簿を確認 → 件名・本文・ファイル → テスト送信 → 全員へ配布（人数を確認するダイアログ）。
GAS が v6 未満（?ping=1 に distSend が無い）の間は「準備中」と表示して送らない。
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import portal_shell as S

HERE = S.HERE
OUT = os.path.join(HERE, "Kawaguchi_seminar_send.html")


def endpoint():
    s = io.open(os.path.join(HERE, "theme", "legacy_home_ja.html"), encoding="utf-8").read()
    m = re.search(r'const SMTW_CMT_ENDPOINT = "(https://script\.google\.com/macros/s/[A-Za-z0-9_-]+/exec)"', s)
    if not m:
        raise SystemExit("GAS endpoint not found in theme/legacy_home_ja.html")
    return m.group(1)


CSS = """
.sd{font-family:"Yu Gothic UI","Yu Gothic",var(--f-ui)}
.sd .fg-wrap{max-width:860px}
.sd-step{border-top:1px solid var(--line);padding:28px 0 32px;display:grid;grid-template-columns:56px 1fr;gap:0 18px}
.sd-step:first-child{border-top:0;padding-top:0}
.sd-no{font-family:var(--f-disp);font-weight:300;font-size:2.4rem;line-height:1;color:var(--ink-2)}
.sd-step h2{margin:.15rem 0 .3rem;font-size:1.2rem;font-weight:700;color:var(--ink);border:0;padding:0}
.sd-step p.sd-help{margin:0 0 1rem;color:var(--muted);font-size:.92rem}
.sd-step.is-off{opacity:.45}
.sd-step.is-off input,.sd-step.is-off textarea,.sd-step.is-off button{pointer-events:none}
.sd label{display:block;font-weight:700;font-size:.9rem;margin:1rem 0 .35rem;color:var(--ink)}
.sd input[type=text],.sd input[type=password],.sd textarea{width:100%;box-sizing:border-box;font:inherit;font-size:1rem;
  padding:.7rem .8rem;border:1px solid #b9c0cc;border-radius:3px;background:#fff;color:var(--text)}
.sd textarea{min-height:12rem;line-height:1.7}
.sd input:focus-visible,.sd textarea:focus-visible,.sd button:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
.sd input[type=file]{font:inherit;font-size:.95rem;max-width:100%}
.sd-row{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:1rem}
.sd-pass{display:flex;gap:10px;flex-wrap:wrap}
.sd-pass input{flex:1 1 220px}
.sd button{font:inherit;font-weight:700;font-size:.95rem;padding:.75rem 1.2rem;border-radius:3px;cursor:pointer;
  border:1px solid var(--ink);background:#fff;color:var(--ink);min-height:44px}
.sd button.is-solid{background:var(--ink);color:#fff}
.sd button.is-send{background:#9b1c31;border-color:#9b1c31;color:#fff}
.sd button:disabled{opacity:.5;cursor:not-allowed}
.sd-roster{margin-top:1rem;padding:14px 16px;background:var(--gold-wash);border-left:3px solid var(--gold);font-size:.92rem;display:none}
.sd-roster.is-on{display:block}
.sd-roster b{color:var(--ink)}
.sd-roster .sd-miss{color:#9b1c31}
.sd-files{font-size:.88rem;color:var(--muted);margin-top:.4rem}
.sd-msg{margin-top:1rem;font-size:.95rem;min-height:1.6em}
.sd-msg.ok{color:#1d6b3a}
.sd-msg.err{color:#9b1c31}
.sd-msg.busy{color:var(--muted)}
.sd-note{margin-top:2rem;color:var(--muted);font-size:.85rem;border-top:1px solid var(--line);padding-top:1rem}
@media (max-width:600px){.sd-step{grid-template-columns:1fr}.sd-no{font-size:1.6rem;margin-bottom:.4rem}.sd .fg-wrap{padding:0 16px}}
"""

JS = r"""
(function () {
  "use strict";
  var EP = "__ENDPOINT__";
  var MAX_TOTAL = 20 * 1024 * 1024;
  var ERR = {
    "bad-passphrase": "合言葉が違います。",
    "locked": "合言葉の誤りが続いたため、1時間ほど受け付けを止めています。時間をおいてお試しください。",
    "passphrase-not-set": "合言葉がまだ設定されていません。事務局（松前）にご連絡ください。",
    "not-setup": "配布機能の初期設定が済んでいません。事務局（松前）にご連絡ください。",
    "need-subject": "件名を入力してください。",
    "need-body": "本文かファイルのどちらかを入れてください。",
    "no-recipients": "名簿に配信先がいません。事務局（松前）にご連絡ください。",
    "too-many": "配信先が上限を超えています。事務局（松前）にご連絡ください。",
    "quota": "今日のメール送信の上限に達しています。明日あらためてお送りください。",
    "no-test-to": "テスト送信先が設定されていません。事務局（松前）にご連絡ください。",
    "no-nonce": "画面を読み込み直してから、もう一度お試しください。",
    "mail-failed": "資料は配布BOXに載りましたが、メールは送れませんでした。もう一度は押さず、事務局（松前）にご連絡ください。"
  };
  function $(s) { return document.querySelector(s); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function mb(n) { return (n / 1048576).toFixed(1); }
  function newNonce() {
    try { return crypto.randomUUID(); } catch (e) { return String(Date.now()) + "-" + Math.random().toString(36).slice(2); }
  }
  function say(el, cls, text) { el.className = "sd-msg" + (cls ? " " + cls : ""); el.textContent = text; }
  function post(obj) {
    // Content-Type を付けない text/plain の simple request にして CORS preflight を避ける（提出BOXと同じ）
    return fetch(EP, { method: "POST", body: JSON.stringify(obj) }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    });
  }
  function errText(res) {
    if (res && res.error && ERR[res.error]) return ERR[res.error];
    return "送信に失敗しました（" + ((res && res.error) || "不明") + "）。事務局（松前）にご連絡ください。";
  }
  function readB64(file) {
    return new Promise(function (resolve, reject) {
      var r = new FileReader();
      r.onload = function () { resolve({ filename: file.name, mimeType: file.type || "application/octet-stream", data: String(r.result).split(",")[1] || "" }); };
      r.onerror = function () { reject(r.error); };
      r.readAsDataURL(file);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var pass = $("#sd-pass"), checkBtn = $("#sd-check"), roster = $("#sd-roster"), msg1 = $("#sd-msg1");
    var step2 = $("#sd-step2"), step3 = $("#sd-step3");
    var subj = $("#sd-subject"), body = $("#sd-body"), files = $("#sd-files"), flist = $("#sd-filelist");
    var testBtn = $("#sd-test"), sendBtn = $("#sd-send"), msg3 = $("#sd-msg3");
    var count = 0, nonce = newNonce(), busy = false;

    function lock(on) {
      busy = on;
      [checkBtn, testBtn, sendBtn].forEach(function (b) { b.disabled = on; });
      if (!on && count === 0) { testBtn.disabled = true; sendBtn.disabled = true; }
    }
    function enable(on) {
      step2.classList.toggle("is-off", !on); step3.classList.toggle("is-off", !on);
      testBtn.disabled = !on; sendBtn.disabled = !on;
      step2.setAttribute("aria-disabled", on ? "false" : "true"); step3.setAttribute("aria-disabled", on ? "false" : "true");
    }
    enable(false);

    // バックエンドが v6（distSend）か確かめる。違えば準備中にして何も送らない
    fetch(EP + "?ping=1").then(function (r) { return r.json(); }).then(function (p) {
      if (!p || !p.distSend) throw new Error("not-ready");
    }).catch(function () {
      checkBtn.disabled = true; pass.disabled = true;
      say(msg1, "err", "配布機能は準備中です。資料はこれまでどおりメールでお送りください。");
    });

    // 合言葉を変えたら名簿の確認からやり直す
    pass.addEventListener("input", function () { count = 0; enable(false); roster.classList.remove("is-on"); });

    files.addEventListener("change", function () {
      var t = 0, n = [];
      for (var i = 0; i < files.files.length; i++) { t += files.files[i].size; n.push(files.files[i].name); }
      flist.textContent = n.length ? "選択中: " + n.join("、") + "（合計 " + mb(t) + " MB）" : "";
      nonce = newNonce();
    });
    [subj, body].forEach(function (el) { el.addEventListener("input", function () { nonce = newNonce(); }); });

    checkBtn.addEventListener("click", function () {
      if (busy) return;
      if (!pass.value) { say(msg1, "err", "合言葉を入力してください。"); pass.focus(); return; }
      lock(true); say(msg1, "busy", "確認しています…");
      post({ kind: "dist", action: "check", passphrase: pass.value }).then(function (res) {
        if (!res || !res.ok) throw res;
        count = res.recipients.length;
        roster.innerHTML =
          "<b>配信先 " + count + "名</b>：" + esc(res.recipients.join("、")) +
          (res.missing && res.missing.length ? "<br><span class=\"sd-miss\"><b>届かない方 " + res.missing.length + "名</b>：" + esc(res.missing.join("、")) + "（アドレス未登録など）</span>" : "") +
          "<br>メールの宛先（To）と返信先：" + esc(res.replyTo) + "。メンバーは BCC で、互いのアドレスは見えません。";
        roster.classList.add("is-on");
        sendBtn.textContent = "全員へ配布する（" + count + "名）";
        say(msg1, "ok", "確認できました。下に進んでください。");
        lock(false); enable(count > 0);
      }).catch(function (res) {
        lock(false); enable(false); roster.classList.remove("is-on");
        say(msg1, "err", res instanceof Error ? "通信に失敗しました。時間をおいてお試しください。" : errText(res));
      });
    });

    function collect() {
      var s = subj.value.trim(), b = body.value.trim(), fs = [], t = 0;
      for (var i = 0; i < files.files.length; i++) { fs.push(files.files[i]); t += files.files[i].size; }
      if (!s) { say(msg3, "err", ERR["need-subject"]); subj.focus(); return null; }
      if (!b && !fs.length) { say(msg3, "err", ERR["need-body"]); body.focus(); return null; }
      if (t > MAX_TOTAL) { say(msg3, "err", "ファイルは合計20MBまでにしてください（いま " + mb(t) + " MB）。"); return null; }
      return { subject: s, body: b, files: fs };
    }

    function run(action) {
      if (busy) return;
      var c = collect(); if (!c) return;
      if (action === "send") {
        var names = c.files.map(function (f) { return f.name; }).join("、") || "（なし）";
        if (!window.confirm("メンバー " + count + "名に BCC で送ります。送ると取り消せません。\n\n件名：" + c.subject + "\nファイル：" + names + "\n\nよろしいですか？")) return;
      }
      lock(true);
      say(msg3, "busy", action === "send" ? "送信しています…（ファイルが大きいと1分ほどかかります）" : "テスト送信しています…");
      Promise.all(c.files.map(readB64)).then(function (enc) {
        return post({ kind: "dist", action: action, passphrase: pass.value, subject: c.subject, body: c.body,
                      files: action === "test" ? enc.map(function (f) { return { filename: f.filename }; }) : enc,
                      nonce: nonce });
      }).then(function (res) {
        if (!res || !res.ok) throw res;
        if (action === "test") {
          say(msg3, "ok", "テストメールを " + res.to + " に送りました。内容を確かめてから「全員へ配布する」を押してください。");
        } else if (res.duplicate) {
          say(msg3, "ok", "この内容はすでに送信済みです（二重には送っていません）。");
        } else {
          say(msg3, "ok", "✓ " + res.sent + "名に送りました。資料はポータルの配布BOXにも載っています。");
          subj.value = ""; body.value = ""; files.value = ""; flist.textContent = ""; nonce = newNonce();
        }
        lock(false);
      }).catch(function (res) {
        lock(false);
        say(msg3, "err", res instanceof Error ? "通信に失敗しました。もう一度押しても二重には送られません。" : errText(res));
      });
    }
    testBtn.addEventListener("click", function () { run("test"); });
    sendBtn.addEventListener("click", function () { run("send"); });
  });
})();
"""


def build():
    hdr = S.header("ja", "send")
    meta = dict(kicker="先生・事務局用", title="資料を<em>一斉配布</em>する",
                lede="ここから送った資料は、知的鍛錬塾のメンバー全員にメール（BCC）で届き、ポータルの配布BOXにも載ります。",
                chips=["合言葉が必要", "BCC で送信", "ファイルは合計20MBまで"], actions=[])
    head = S.pagehead("ja", meta, crumb_parent="Kawaguchi_seminar.html", crumb_label="一斉配布")
    body = f"""<body class="sd">
{hdr}
<main id="main">
{head}
<section class="fg-section"><div class="fg-wrap">
<div class="sd-step" id="sd-step1">
  <div class="sd-no" aria-hidden="true">01</div>
  <div>
    <h2>合言葉を入れて、宛先を確かめる</h2>
    <p class="sd-help">合言葉は先生と事務局だけが知っている言葉です（ポータルのパスワードとは別）。</p>
    <label for="sd-pass">合言葉</label>
    <div class="sd-pass"><input type="password" id="sd-pass" autocomplete="off"><button type="button" class="is-solid" id="sd-check">名簿を確認</button></div>
    <div class="sd-roster" id="sd-roster" aria-live="polite"></div>
    <div class="sd-msg" id="sd-msg1" role="status" aria-live="polite"></div>
  </div>
</div>
<div class="sd-step is-off" id="sd-step2">
  <div class="sd-no" aria-hidden="true">02</div>
  <div>
    <h2>件名・本文・ファイル</h2>
    <p class="sd-help">本文はそのままメールになります。資料は添付ではなく、Google ドライブのリンクとしてメールに入ります。</p>
    <label for="sd-subject">件名</label>
    <input type="text" id="sd-subject" maxlength="200" placeholder="例：第7回の事前資料">
    <label for="sd-body">本文</label>
    <textarea id="sd-body" placeholder="皆様、&#10;&#10;（本文）&#10;&#10;川口"></textarea>
    <label for="sd-files">ファイル（複数可・合計20MBまで）</label>
    <input type="file" id="sd-files" multiple>
    <div class="sd-files" id="sd-filelist"></div>
  </div>
</div>
<div class="sd-step is-off" id="sd-step3">
  <div class="sd-no" aria-hidden="true">03</div>
  <div>
    <h2>テストしてから、全員へ</h2>
    <p class="sd-help">「テスト送信」は事務局の1名だけに届きます（資料は保存しません）。届いた内容を見てから「全員へ配布する」を押してください。</p>
    <div class="sd-row"><button type="button" id="sd-test">テスト送信（事務局に1通）</button><button type="button" class="is-send" id="sd-send">全員へ配布する</button></div>
    <div class="sd-msg" id="sd-msg3" role="status" aria-live="polite"></div>
  </div>
</div>
<p class="sd-note">送信元のアドレスは事務局の Gmail で、差出人名は「知的鍛錬塾 事務局」と表示されます。宛先の追加や修正は事務局（松前）までご連絡ください。</p>
</div></section>
</main>
{S.footer("ja")}
<script>{JS.replace("__ENDPOINT__", endpoint())}</script>
{S.body_script()}
</body></html>
"""
    html = ('<!DOCTYPE html>\n<html lang="ja"><head>'
            + S.shell_head("一斉配布｜AIx知的鍛錬塾", "ja", CSS)
            + '</head>\n' + body)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(html)
    print(f"written {OUT}: {len(html):,} bytes")


if __name__ == "__main__":
    build()
