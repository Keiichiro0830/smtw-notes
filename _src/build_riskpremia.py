# -*- coding: utf-8 -*-
"""SMTW ポータル 特別セクション「リスクプレミア分析」生成スクリプト.

出力:
  _src/Kawaguchi_seminar_riskpremia.html      (JP 本体・staticrypt対象)
  _src/Kawaguchi_seminar_riskpremia_en.html   (EN スタブ・staticrypt対象)
  docs/risk_premia_comments.json              (図ごと解説本文の実体・平文/ブラウザ編集可)

設計:
  - ページ構造(タイトル/画像/33業種凡例/figカード骨格)は暗号化HTML側に残す。
  - 編集対象の解説本文は [data-cmt-key] プレースホルダに分離し、復号後 fetch で描画。
  - #edit + GitHub PAT でブラウザ編集 → Contents API で comments.json を commit。
  - 図ごとコメント/スレッドは既存 smtw-cmt(GAS→Sheet) を移植して再利用。
"""
import io, os, json, re

ROOT = os.path.dirname(os.path.abspath(__file__))            # _src
REPO = os.path.dirname(ROOT)                                  # repo root
DOCS = os.path.join(REPO, "docs")

REPO_SLUG = "Keiichiro0830/smtw-notes"
GEN_DATE = "2026-06-25"

# ---------------------------------------------------------------------------
# 1) 図ごと解説本文（編集可能・JSON へ分離）  key = data-cmt-key
# ---------------------------------------------------------------------------
COMMENTS = {
"tldr": """<ol>
  <li><b class="lead">為替（円ドル）リスクが最大の体系的ドライバー。</b>
    市場リターンとの同時相関は <b>+0.196</b>（全マクロ変数中で最大）、瞬時的因果は <b>χ²=16.3, p=0.00005</b> と高度に有意。
    <u>円安 ↔ 株高</u>が同月内で連動する。ただし「為替が翌月の株を予測する」リード・ラグ因果は無し（Granger p=0.24）＝<b>同時連動であって先行指標ではない</b>。</li>
  <li><b class="lead">ボラティリティ集中（危機）リスク。</b>
    市場リスクは時間的に均一でなく、<b>1990-91年バブル崩壊</b>と<b>2008年GFC</b>の数ヶ月に極端に集中（月次ボラ約9〜11%）。GARCH持続性 α+β=0.88、無条件の年率ボラ <b>約18.6%</b>。</li>
  <li><b class="lead">教科書マクロ2ファクター（生産IIP・物価CPI）は“鍵”ではなかった。</b>
    市場リターンとの同時相関は 0.04 前後と極めて弱く、Fama-MacBethのリスクプレミアムも統計的に非有意（t≈−1.0／−0.9）。
    日本株の断面はこの2ファクターでは十分に説明されない。</li>
</ol>""",

"p1": """<p>市場リターンの“素材”。1987年の1758 → 1990年初のバブル天井（約2880）→ 長期低迷 → 2012-05に底<b>719</b> → アベノミクス以降の上昇 → 2026-02に過去最高<b>3939</b>、足元3727。水準そのものはトレンドを持つ非定常系列なので、分析では対数変化率（リターン）に変換して使う。</p>""",

"p2": """<p>本レポートの主役。1987年153円 → 2012-01に超円高<b>76円</b>（震災・欧州危機）→ 2024年以降の円安<b>161円</b>、足元157円。<b>この為替の月次変化が、後段で「市場リターンと最も強く連動するマクロ変数」として浮かび上がる</b>。日本企業の輸出採算・海外利益の円換算を通じ、為替は株価の体系的ドライバーになっている。</p>""",

"p3": """<p>1987年18.7ドル → 1998-12にアジア危機の底11.3 → 2008-06のピーク133.9 → 足元100.3。市場リターンとの同時相関は+0.099と2番目だが、為替の半分程度。コモディティ・リスクオン局面の代理変数。</p>""",

"p4": """<p>鉱工業生産の月次成長率（SD≈2.1%）。最大の外れ値は<b>2011-03に −18.0%</b>（東日本大震災の生産停止）と<b>2011-05に +6.6%</b>（反動増）。実体経済ファクターの素材だが、市場リターンとの同時相関は+0.037と弱い。</p>""",

"p5": """<p>33業種リターン行列の代表1本を可視化した確認用プロット（SD6.2%、−26%〜+22%）。「33業種ぶんこういう系列がある」ことの確認で、分析的含意は薄い。業種番号と定義は本ページ上部の<a href="#legend">「東証33業種 番号⇄定義」</a>を参照。</p>""",

"p6": """<p>IIP変化率をARIMA(1,0,2)で回した残差＝「予想外」成分。形はP4とほぼ同一（震災が支配的）。SDも2.06%でほぼ不変＝<b>全期間ではIIP変化率はほぼホワイトノイズ</b>で予測可能成分が乏しい。APTでは株価を動かすのは“サプライズ”だけなので、この残差を第一ファクターに使う。</p>""",

"p7": """<p>CPIをARIMA(0,1,5)で処理した残差（SD0.34%）。最大<b>+1.94%は2014-04（消費税8%増税）</b>、最小−1.19%は1989-11（バブル末期）。インフレの“サプライズ”を綺麗に拾う第二ファクター。ただし市場リターンとの同時相関は+0.046と弱い。</p>""",

"p8": """<p><b>これが「市場リターン」そのもの</b>。月次SD≈5.3%。最大のドローダウンは<b>1990-09に −22.8%</b>（バブル崩壊初期）、次いで<b>2008-11前後</b>（GFC）。グラフ上で振れ幅が太くなる時期＝リスクが高い時期で、それを次ページのGARCHが定量化する。なお<u>この市場リターンと最も連動するのは為替（+0.196）</u>。</p>""",

"p9": """<p>市場リターンのリスク（分散＝ボラの2乗）の時系列。推定値 ω=3.33, α₁=0.128, β₁=0.756、<b>持続性 α+β=0.884</b>（＝荒れた相場は数ヶ月続く＝ボラのクラスタリング）。無条件分散から逆算した<b>年率ボラは約18.6%</b>。</p>
<div class="callout">
  <b>市場リスクが極端に高かった月 TOP（条件付き月次ボラ）</b>
  <table class="keytbl">
    <tr><th>月</th><th>月次ボラ</th><th>イベント</th></tr>
    <tr class="rank1"><td>1990-11</td><td class="num">11.0%</td><td>バブル崩壊</td></tr>
    <tr><td>1990-12 / 10</td><td class="num">10.6% / 10.5%</td><td>バブル崩壊</td></tr>
    <tr class="rank1"><td>2008-11</td><td class="num">10.4%</td><td>リーマンショック</td></tr>
    <tr><td>1991-01〜03</td><td class="num">8.5〜9.6%</td><td>バブル崩壊の余波</td></tr>
    <tr><td>2008-12</td><td class="num">9.3%</td><td>GFC</td></tr>
  </table>
  <p style="margin:8px 0 0">＝市場リターンのリスクは<b>2つの危機（1990-91・2008）に集中</b>。コロナ(2020)ですらこの2つには及ばない。これが「いつリスクが顕在化するか」の答え。</p>
</div>""",

"p10": """<p>各業種リターンを生産ショックに回帰した感応度。範囲−0.40〜+0.42。正に大きい＝<b>証券・その他金融・不動産・小売</b>（景気敏感）、負＝鉱業・石油・医薬・鉄鋼（ディフェンシブ／コモディティ）。符号は直感どおり。</p>""",

"p11": """<p>範囲−0.14〜+2.63。突出して<b>鉱業 +2.63</b>、次いで倉庫+1.66・建設+1.55・海運+1.50（実物資産／コモディティ性＝インフレに強い）。ほぼ全業種が正で、株式がある程度インフレヘッジになる像。</p>""",

"p12": """<p>赤破線=5%水準。<b>5%有意は33業種中わずか1業種（その他金融）</b>。＝個別業種の生産感応度は統計的にほぼ非有意で、推定精度は低い。</p>""",

"p13": """<p>同じく<b>5%有意は1業種（鉱業）のみ</b>。インフレ感応も鉱業を除けば統計的に有意でない。符号パターンは綺麗だが「効いている」とは言い切れない。</p>""",

"p14": """<p>毎月の断面回帰から得る「生産リスク1単位あたりの月次リターン」。平均<b>−0.442%/月、SD9.17、t≈−1.05</b>。<b class="num-neg">統計的にゼロと区別できない</b>。月次の振れが平均比で桁違いに大きい。2009・2011前後に大きな負スパイク。</p>""",

"p15": """<p>平均<b>−0.086%/月、SD2.13、t≈−0.87</b>。これも<b class="num-neg">非有意</b>。＝インフレリスクに対して市場が安定した対価を払っている証拠は無い。</p>""",

"p16": """<p>右肩下がりで最終−208%。特に<b>2008–2011に急落</b>（GFC＋震災で景気敏感株が叩かれた局面）。見栄えはするが、非有意な月次λの単純累積なので<b>大半はノイズの積み上がり</b>。トレンドに見えても統計的裏付けは弱い。</p>""",

"p17": """<p>最終−40%、緩やかな低下。P16同様、非有意系列の累積であり強い結論は引けない。</p>""",

"conclusion": """<ol>
  <li><b>為替が一番のリスクファクター。</b> 日本株（TOPIX）のリターンは円ドルと同月で最も強く連動する（相関0.196・瞬時因果 p&lt;0.0001）。ポートフォリオの実効的な為替エクスポージャーを把握・管理することが、マーケットリスク管理の中心。</li>
  <li><b>リスクは平時には小さく、危機に集中する。</b> 年率ボラ18.6%は“平均”に過ぎず、実際は1990-91・2008のような数ヶ月に極端に偏る（月次ボラ10%超）。テールリスク／レジーム転換への備え（ボラ連動のポジション調整）が効く。</li>
  <li><b>生産・物価ショックは“価格付けされたリスク”ではない。</b> CRR型2ファクターのリスクプレミアムは非有意。少なくともこの期間の日本株断面では、IIP/CPIサプライズを取りに行く戦略の理論的裏付けは弱い。</li>
  <li><b>次の一手（精度向上）：</b> ① 為替・TERM・原油を加えた3〜5ファクターへの拡張、② Newey-West標準誤差で正式なt検定、③ サブ期間分割（バブル／失われた20年／アベノミクス）で構造変化を確認。</li>
</ol>""",
}

# ---------------------------------------------------------------------------
# 2) figカードのメタ（番号・タイトル・タグ・図ファイル）と章構成
# ---------------------------------------------------------------------------
# tagclass: t-mkt(市場) / t-diag(診断) / t-fac(ファクター)
FIGS = {
 1:("TOPIX（水準）","t-diag","前提確認"),
 2:("為替 USD/JPY（水準）","t-mkt","市場リスク本命"),
 3:("原油 WTI（水準）","t-diag","前提確認"),
 4:("IIP対数変化率（%）","t-fac","ファクター素材"),
 5:("業種1（水産・農林）リターン（%）","t-diag","診断プロット"),
 6:("FIP：予期せぬIIPショック","t-fac","ファクター①"),
 7:("FCPI：予期せぬCPIショック","t-fac","ファクター②"),
 8:("TOPIXリターン（%）— 分析対象の市場リターン","t-mkt","市場リスク核心"),
 9:("GARCH(1,1) 条件付き分散（市場リスクの時間変動）","t-mkt","鍵リスク②"),
 10:("IIPベータ（業種別の景気感応度）","t-fac","ローディング"),
 11:("CPIベータ（業種別のインフレ感応度）","t-fac","ローディング"),
 12:("IIPベータのp値","t-diag","有意性チェック"),
 13:("CPIベータのp値","t-diag","有意性チェック"),
 14:("IIPリスクプレミアム（月次λ）","t-fac","リスクの価格①"),
 15:("CPIリスクプレミアム（月次λ）","t-fac","リスクの価格②"),
 16:("IIP累積リスクプレミアム","t-diag","累積"),
 17:("CPI累積リスクプレミアム","t-diag","累積"),
}
SECTIONS = [
 ("A. 生データの水準（P1–P3）", [1,2,3]),
 ("B. 変化率とファクターショックの抽出（P4–P8）", [4,5,6,7,8]),
 ("C. 市場リターンのボラティリティ（P9）", [9]),
 ("D. 第一段回帰：業種のファクター感応度ベータ（P10–P13）", [10,11,12,13]),
 ("E. 第二段：リスクの価格 Fama-MacBeth（P14–P17）", [14,15,16,17]),
]

# 東証33業種 番号⇄定義（CSV TS33_87-1_latest.csv の列順と照合済）
LEGEND = [
 (1,"水産・農林業","Fisheries","診断用に代表表示（P5）"),
 (2,"鉱業","Mining","CPIβ最大 +2.63／CPIで唯一5%有意（P11,P13）"),
 (3,"建設業","Construction","CPIβ +1.55（インフレ耐性）"),
 (4,"食料品","Grocery（Foods）",""),
 (5,"繊維製品","Textile",""),
 (6,"パルプ・紙","Pulp",""),
 (7,"化学","Chemical",""),
 (8,"医薬品","Pharmaceutical","IIPβ負（ディフェンシブ, P10）"),
 (9,"石油・石炭製品","Oil","IIPβ負（コモディティ）"),
 (10,"ゴム製品","Rubber",""),
 (11,"ガラス・土石製品","Glass",""),
 (12,"鉄鋼","Steel","IIPβ負"),
 (13,"非鉄金属","Non-ferrous",""),
 (14,"金属製品","Metallurgical（Metal Products）",""),
 (15,"機械","Machinery",""),
 (16,"電気機器","Electric",""),
 (17,"輸送用機器","Transport",""),
 (18,"精密機器","Precision",""),
 (19,"その他製品","Product（Other Products）",""),
 (20,"電気・ガス業","Gas（Electric Power &amp; Gas）",""),
 (21,"陸運業","LandTransport",""),
 (22,"海運業","Shipping","CPIβ +1.50"),
 (23,"空運業","Aviation",""),
 (24,"倉庫・運輸関連業","Warehouse","CPIβ +1.66"),
 (25,"情報・通信業","Telecom（Info &amp; Comm）",""),
 (26,"卸売業","Wholesale",""),
 (27,"小売業","Retail","IIPβ正（景気敏感, P10）"),
 (28,"銀行業","Banking",""),
 (29,"証券・商品先物取引業","Securities","IIPβ正（景気敏感）"),
 (30,"保険業","Insurance",""),
 (31,"その他金融業","OtherFinance","IIPβ最大 +0.42／IIPで唯一5%有意（P10,P12）"),
 (32,"不動産業","RealEstate","IIPβ正（景気敏感）"),
 (33,"サービス業","Service",""),
]

# ---------------------------------------------------------------------------
# 3) 既存ポータルから移植する smtw-cmt（CSS は別途、JS は本ファイル末尾の SMTW_CMT_JS）
# ---------------------------------------------------------------------------
SMTW_CMT_CSS = """
        /* ===== 記事別コメント欄 (smtw-cmt) — 既存ポータルから移植 ===== */
        .smtw-cmt { background:#f8fafc; border:1px solid #e2e8f0; border-left:4px solid #1f3a5f; border-radius:8px; padding:0.9rem 1.1rem; margin-top:0.9rem; }
        .smtw-cmt .smtw-cmt-head { font-size:0.9rem; font-weight:600; color:#1f3a5f; margin-bottom:0.4rem; }
        .smtw-cmt .smtw-cmt-note { font-size:0.78rem; color:#94a3b8; margin-bottom:0.7rem; line-height:1.5; }
        .smtw-cmt .smtw-cmt-row { margin-bottom:0.55rem; }
        .smtw-cmt label { display:block; font-size:0.78rem; color:#64748b; margin-bottom:0.2rem; }
        .smtw-cmt input[type="text"], .smtw-cmt input[type="email"], .smtw-cmt textarea { width:100%; font:inherit; font-size:0.9rem; color:#1a1a1a; padding:0.45rem 0.6rem; border:1px solid #cbd5e1; border-radius:5px; background:#fff; box-sizing:border-box; resize:vertical; }
        .smtw-cmt input:focus, .smtw-cmt textarea:focus { outline:none; border-color:#1f3a5f; box-shadow:0 0 0 2px rgba(31,58,95,0.12); }
        .smtw-cmt .smtw-cmt-hp { display:none; }
        .smtw-cmt button.smtw-cmt-send { display:inline-block; padding:0.5rem 1.2rem; background:#1f3a5f; color:#fff; border:none; border-radius:5px; font:inherit; font-size:0.9rem; font-weight:600; cursor:pointer; transition:background 0.15s; }
        .smtw-cmt button.smtw-cmt-send:hover { background:#2c5282; }
        .smtw-cmt button.smtw-cmt-send:disabled { background:#94a3b8; cursor:default; }
        .smtw-cmt .smtw-cmt-msg { font-size:0.85rem; margin-top:0.5rem; min-height:1em; }
        .smtw-cmt .smtw-cmt-msg.ok { color:#15803d; font-weight:600; }
        .smtw-cmt .smtw-cmt-msg.err { color:#b91c1c; }
        .smtw-cmt .smtw-cmt-log { margin-top:0.8rem; border-top:1px dashed #cbd5e1; padding-top:0.6rem; }
        .smtw-cmt .smtw-cmt-log-title { font-size:0.78rem; color:#64748b; margin-bottom:0.4rem; }
        .smtw-cmt .smtw-cmt-log-item { background:#fff; border:1px solid #e2e8f0; border-radius:5px; padding:0.45rem 0.65rem; margin-bottom:0.4rem; font-size:0.85rem; color:#334155; }
        .smtw-cmt .smtw-cmt-log-item .smtw-cmt-log-date { display:block; font-size:0.72rem; color:#94a3b8; margin-bottom:0.15rem; }
        .smtw-cmt-main { margin-top:1rem; }
        .smtw-cmt select.smtw-cmt-target { width:100%; font:inherit; font-size:0.9rem; color:#1a1a1a; padding:0.45rem 0.6rem; border:1px solid #cbd5e1; border-radius:5px; background:#fff; box-sizing:border-box; }
        .smtw-cmt select.smtw-cmt-target:focus { outline:none; border-color:#1f3a5f; box-shadow:0 0 0 2px rgba(31,58,95,0.12); }
        .smtw-cmt-jump { text-align:right; margin-top:0.6rem; }
        .smtw-cmt-jump a { font-size:0.8rem; color:#64748b; text-decoration:none; cursor:pointer; }
        .smtw-cmt-jump a:hover { color:#1f3a5f; text-decoration:underline; }
"""

# 既存ポータル _src/Kawaguchi_seminar.html の smtw-cmt JS を verbatim 移植
SMTW_CMT_JS = r"""
/* ===== SMTW 統合コメントフォーム（既存ポータルから移植・同一 GAS エンドポイント） ===== */
const SMTW_CMT_ENDPOINT = "https://script.google.com/macros/s/AKfycbwACdJ6Syy-lT0GpJWJ5InSa2t_QwTaIb7llj6pvh8LoiHtTMIo9FBzr8vqyB02_GMq/exec";
const SMTW_CMT_TEXT = {
    target: "対象", generalLabel: "全体・運営について",
    grpPaper: "図ごと", grpMelmaga: "メルマガ",
    name: "お名前", namePh: "お名前",
    email: "メールアドレス", emailPh: "メールアドレス（任意：控えをお送りします）",
    comment: "コメント", send: "川口先生に送る", sending: "送信中…",
    okMsg: "✓ 川口先生にお届けしました。ありがとうございます。",
    errMsg: "送信に失敗しました。時間をおいて再度お試しください。",
    notReady: "コメント機能は準備中です",
    jump: "✉️ この図についてコメントする",
    logTitle: "あなたのコメント（この端末のみに表示）",
    otherLabel: "その他", otherPh: "対象を自由にご記入ください",
    otherReq: "対象（その他）をご記入ください。"
};
(function () {
    const LOG_KEY = "smtw_cmt_log_all";
    function readProfile() { try { return JSON.parse(localStorage.getItem("smtw_cmt_profile")) || {}; } catch (e) { return {}; } }
    function saveProfile(name, email) { try { localStorage.setItem("smtw_cmt_profile", JSON.stringify({ name: name, email: email })); } catch (e) {} }
    function readLog() { try { return JSON.parse(localStorage.getItem(LOG_KEY)) || []; } catch (e) { return []; } }
    function appendLog(entry) { const log = readLog(); log.push(entry); try { localStorage.setItem(LOG_KEY, JSON.stringify(log)); } catch (e) {} return log; }
    function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
    function renderLog(logWrap) {
        const log = readLog();
        if (!log.length) { logWrap.innerHTML = ""; return; }
        let html = '<div class="smtw-cmt-log-title">' + esc(SMTW_CMT_TEXT.logTitle) + "</div>";
        for (let i = 0; i < log.length; i++) {
            html += '<div class="smtw-cmt-log-item"><span class="smtw-cmt-log-date">' +
                esc(log[i].date) + " ｜ " + esc(log[i].atitle || "") + "</span>" + esc(log[i].comment) + "</div>";
        }
        logWrap.innerHTML = html;
    }
    function buildTargetOptions() {
        let html = '<option value="general">' + esc(SMTW_CMT_TEXT.generalLabel) + "</option>";
        const papers = [], melmagas = [];
        const nodes = document.querySelectorAll(".smtw-cmt:not(.smtw-cmt-main)");
        for (let i = 0; i < nodes.length; i++) {
            const node = nodes[i];
            const aid = node.getAttribute("data-aid") || "";
            const atitle = node.getAttribute("data-atitle") || "";
            if (!aid) continue;
            const item = { aid: aid, atitle: atitle };
            if (node.closest(".melmaga")) { melmagas.push(item); } else { papers.push(item); }
        }
        function group(label, arr) {
            if (!arr.length) return "";
            let g = '<optgroup label="' + esc(label) + '">';
            for (let j = 0; j < arr.length; j++) { g += '<option value="' + esc(arr[j].aid) + '" data-atitle="' + esc(arr[j].atitle) + '">' + esc(arr[j].atitle) + "</option>"; }
            return g + "</optgroup>";
        }
        html += group(SMTW_CMT_TEXT.grpPaper, papers);
        html += group(SMTW_CMT_TEXT.grpMelmaga, melmagas);
        html += '<option value="other">' + esc(SMTW_CMT_TEXT.otherLabel) + "</option>";
        return { html: html, count: papers.length + melmagas.length + 2 };
    }
    function buildMainForm(box) {
        const prof = readProfile();
        const opts = buildTargetOptions();
        box.innerHTML =
            '<div class="smtw-cmt-row"><label>' + esc(SMTW_CMT_TEXT.target) + '</label><select class="smtw-cmt-target">' + opts.html + "</select></div>" +
            '<div class="smtw-cmt-row smtw-cmt-other-row" style="display:none;"><label>' + esc(SMTW_CMT_TEXT.otherLabel) + '</label><input type="text" class="smtw-cmt-other-input" placeholder="' + esc(SMTW_CMT_TEXT.otherPh) + '"></div>' +
            '<div class="smtw-cmt-row"><label>' + esc(SMTW_CMT_TEXT.name) + '</label><input type="text" class="smtw-cmt-name" placeholder="' + esc(SMTW_CMT_TEXT.namePh) + '" value="' + esc(prof.name || "") + '" required></div>' +
            '<div class="smtw-cmt-row"><label>' + esc(SMTW_CMT_TEXT.email) + '</label><input type="email" class="smtw-cmt-email" placeholder="' + esc(SMTW_CMT_TEXT.emailPh) + '" value="' + esc(prof.email || "") + '"></div>' +
            '<div class="smtw-cmt-row"><label>' + esc(SMTW_CMT_TEXT.comment) + '</label><textarea class="smtw-cmt-comment" rows="4" required></textarea></div>' +
            '<input type="text" class="smtw-cmt-hp" name="website" tabindex="-1" autocomplete="off">' +
            '<button type="button" class="smtw-cmt-send">' + esc(SMTW_CMT_TEXT.send) + "</button>" +
            '<div class="smtw-cmt-msg"></div><div class="smtw-cmt-log"></div>';
        const targetEl = box.querySelector(".smtw-cmt-target");
        const nameEl = box.querySelector(".smtw-cmt-name");
        const emailEl = box.querySelector(".smtw-cmt-email");
        const commentEl = box.querySelector(".smtw-cmt-comment");
        const hpEl = box.querySelector(".smtw-cmt-hp");
        const btn = box.querySelector(".smtw-cmt-send");
        const msg = box.querySelector(".smtw-cmt-msg");
        const logWrap = box.querySelector(".smtw-cmt-log");
        const otherRow = box.querySelector(".smtw-cmt-other-row");
        const otherInput = box.querySelector(".smtw-cmt-other-input");
        targetEl.addEventListener("change", function () { otherRow.style.display = (targetEl.value === "other") ? "" : "none"; if (targetEl.value === "other" && otherInput) { otherInput.focus(); } });
        renderLog(logWrap);
        function selectedTarget() {
            const opt = targetEl.options[targetEl.selectedIndex];
            const aid = targetEl.value;
            let atitle = opt ? (opt.getAttribute("data-atitle") || "") : "";
            if (aid === "general") { atitle = box.getAttribute("data-atitle") || "全体・運営"; }
            if (aid === "other") { atitle = (otherInput && otherInput.value.trim()) || SMTW_CMT_TEXT.otherLabel; }
            return { aid: aid, atitle: atitle };
        }
        btn.addEventListener("click", function () {
            const tgt = selectedTarget();
            const name = nameEl.value.trim(), email = emailEl.value.trim(), comment = commentEl.value.trim(), website = hpEl.value;
            msg.className = "smtw-cmt-msg";
            if (!name) { msg.className = "smtw-cmt-msg err"; msg.textContent = "お名前を入力してください。"; nameEl.focus(); return; }
            if (!comment) { msg.className = "smtw-cmt-msg err"; msg.textContent = "コメントを入力してください。"; commentEl.focus(); return; }
            if (tgt.aid === "other" && (!otherInput || !otherInput.value.trim())) { msg.className = "smtw-cmt-msg err"; msg.textContent = SMTW_CMT_TEXT.otherReq; if (otherInput) { otherInput.focus(); } return; }
            saveProfile(name, email);
            if (!SMTW_CMT_ENDPOINT || SMTW_CMT_ENDPOINT === "PASTE_GAS_WEBAPP_URL_HERE") { alert(SMTW_CMT_TEXT.notReady); return; }
            btn.disabled = true; const original = btn.textContent; btn.textContent = SMTW_CMT_TEXT.sending; msg.textContent = "";
            fetch(SMTW_CMT_ENDPOINT, { method: "POST", body: JSON.stringify({ aid: tgt.aid, atitle: tgt.atitle, name: name, email: email, comment: comment, page: location.pathname, website: website }) })
              .then(function (resp) {
                if (!resp.ok) { throw new Error("HTTP " + resp.status); }
                msg.className = "smtw-cmt-msg ok"; msg.textContent = SMTW_CMT_TEXT.okMsg;
                appendLog({ date: new Date().toLocaleString(), atitle: tgt.atitle, comment: comment });
                renderLog(logWrap); commentEl.value = ""; btn.disabled = false; btn.textContent = original;
              }).catch(function () { msg.className = "smtw-cmt-msg err"; msg.textContent = SMTW_CMT_TEXT.errMsg; btn.disabled = false; btn.textContent = original; });
        });
        return targetEl;
    }
    function buildJumpLink(box, mainForm) {
        const aid = box.getAttribute("data-aid") || "";
        box.className = "smtw-cmt-jump"; box.removeAttribute("style");
        box.innerHTML = '<a>' + esc(SMTW_CMT_TEXT.jump) + "</a>";
        const link = box.querySelector("a");
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const targetEl = mainForm.querySelector(".smtw-cmt-target");
            if (targetEl) { targetEl.value = aid; }
            const form = document.getElementById("smtw-cmt-form");
            if (form) { form.scrollIntoView({ behavior: "smooth", block: "start" }); }
        });
    }
    document.addEventListener("DOMContentLoaded", function () {
        const mainForm = document.querySelector(".smtw-cmt-main");
        let targetEl = null;
        if (mainForm) { targetEl = buildMainForm(mainForm); }
        const others = document.querySelectorAll(".smtw-cmt:not(.smtw-cmt-main)");
        for (let i = 0; i < others.length; i++) { buildJumpLink(others[i], mainForm); }
    });
})();
"""

# 解説本文の fetch描画 + #edit ブラウザ編集（GitHub Contents API 保存）
EDIT_JS = r"""
/* ===== 解説本文 fetch描画 + #edit ブラウザ編集モード ===== */
(function () {
    const RP_REPO = "__REPO_SLUG__";
    const RP_PATH = "docs/risk_premia_comments.json";
    const RP_TOKEN_KEY = "smtw_rp_edit_token";
    let RP_DATA = {};
    function utf8ToB64(s) { return btoa(unescape(encodeURIComponent(s))); }
    function render(data) {
        RP_DATA = data || {};
        const nodes = document.querySelectorAll("[data-cmt-key]");
        for (let i = 0; i < nodes.length; i++) {
            const k = nodes[i].getAttribute("data-cmt-key");
            if (RP_DATA[k] != null) { nodes[i].innerHTML = RP_DATA[k]; }
        }
    }
    const bust = (location.hash === "#edit") ? ("?_=" + new Date().getTime()) : "";
    fetch("risk_premia_comments.json" + bust)
        .then(function (r) { return r.ok ? r.json() : {}; })
        .then(render)
        .catch(function () {});

    function status(el, txt, ok) { el.textContent = txt; el.style.color = ok ? "#15803d" : "#b91c1c"; }
    function setEditing(on) {
        const nodes = document.querySelectorAll("[data-cmt-key]");
        for (let i = 0; i < nodes.length; i++) {
            nodes[i].contentEditable = on ? "true" : "false";
            nodes[i].classList.toggle("rp-editing", on);
        }
        document.getElementById("rp-edit-start").style.display = on ? "none" : "";
        document.getElementById("rp-edit-save").style.display = on ? "" : "none";
        document.getElementById("rp-edit-cancel").style.display = on ? "" : "none";
    }
    async function save(statusEl) {
        let token = localStorage.getItem(RP_TOKEN_KEY);
        if (!token) { token = prompt("GitHub Personal Access Token（fine-grained / smtw-notes / Contents: Read and write）:"); if (!token) return; localStorage.setItem(RP_TOKEN_KEY, token.trim()); token = token.trim(); }
        const updated = Object.assign({}, RP_DATA);
        const nodes = document.querySelectorAll("[data-cmt-key]");
        for (let i = 0; i < nodes.length; i++) { updated[nodes[i].getAttribute("data-cmt-key")] = nodes[i].innerHTML.trim(); }
        const body = JSON.stringify(updated, null, 2);
        const api = "https://api.github.com/repos/" + RP_REPO + "/contents/" + RP_PATH;
        const headers = { "Authorization": "Bearer " + token, "Accept": "application/vnd.github+json" };
        status(statusEl, "保存中…", true);
        try {
            const g = await fetch(api, { headers: headers });
            const sha = g.ok ? (await g.json()).sha : undefined;
            const put = await fetch(api, { method: "PUT", headers: headers, body: JSON.stringify({ message: "Update risk premia commentary", content: utf8ToB64(body), sha: sha }) });
            if (!put.ok) { const t = await put.text(); throw new Error("HTTP " + put.status + " " + t.slice(0, 120)); }
            RP_DATA = updated;
            status(statusEl, "✓ 保存しました（GitHub Pages 反映に約1分）", true);
            setEditing(false);
        } catch (e) {
            if (("" + e).indexOf("401") >= 0 || ("" + e).indexOf("403") >= 0) { localStorage.removeItem(RP_TOKEN_KEY); }
            status(statusEl, "✗ 保存失敗: " + e.message, false);
        }
    }
    document.addEventListener("DOMContentLoaded", function () {
        const bar = document.getElementById("rp-editbar");
        if (!bar) return;
        if (location.hash !== "#edit") { bar.style.display = "none"; return; }
        bar.style.display = "flex";
        const statusEl = document.getElementById("rp-edit-status");
        document.getElementById("rp-edit-start").addEventListener("click", function () { setEditing(true); status(statusEl, "編集中：解説枠を直接クリックして書き換え → 保存", true); });
        document.getElementById("rp-edit-save").addEventListener("click", function () { save(statusEl); });
        document.getElementById("rp-edit-cancel").addEventListener("click", function () { render(RP_DATA); setEditing(false); status(statusEl, "取り消しました", true); });
    });
})();
"""

# ---------------------------------------------------------------------------
# 4) レポート固有 CSS（ライト再スキン）
# ---------------------------------------------------------------------------
REPORT_CSS = """
        /* ===== レポート本体（ライト再スキン） ===== */
        .tldr { background:#fff; border:1px solid #e2e8f0; border-left:4px solid #2c5282; border-radius:10px; padding:0.6rem 1.2rem 1rem; margin:1.2rem 0 0.6rem; }
        .tldr h2 { margin:0.6rem 0 0.4rem; border:none; padding:0; font-size:1.1rem; color:#2c5282; }
        .tldr.concl { border-left-color:#15803d; }
        .tldr.concl h2 { color:#15803d; }
        .tldr ol { margin:0.4rem 0 0; padding-left:1.3rem; }
        .tldr li { margin:0.45rem 0; }
        .keytbl { width:100%; border-collapse:collapse; margin:0.8rem 0 0.3rem; font-size:0.9rem; }
        .keytbl th, .keytbl td { border:1px solid #e2e8f0; padding:0.4rem 0.7rem; text-align:left; }
        .keytbl th { background:#eef2f7; color:#1f3a5f; font-weight:600; }
        .keytbl td.num { text-align:right; font-variant-numeric:tabular-nums; }
        .keytbl tr.rank1 { background:#ecfdf5; font-weight:700; }
        .sec h2 { font-size:0.82rem; color:#b45309; letter-spacing:1.2px; border-left:none; border-bottom:1px solid #e2e8f0; padding:0 0 0.4rem; margin:2.2rem 0 0.2rem; }
        .page { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:1rem 1.2rem; margin:1rem 0; }
        .page h3 { margin:0 0 0.6rem; font-size:1.05rem; color:#1f3a5f; }
        .page h3 .pnum { display:inline-block; background:#2c5282; color:#fff; font-weight:800; border-radius:6px; padding:1px 9px; margin-right:0.6rem; font-size:0.85rem; vertical-align:middle; }
        .page img { width:100%; border-radius:8px; background:#fff; border:1px solid #e2e8f0; }
        .page .body { margin-top:0.7rem; }
        .page .body p { margin:0.5rem 0; }
        .tag { display:inline-block; font-size:0.68rem; padding:2px 9px; border-radius:20px; margin-left:0.5rem; vertical-align:middle; font-weight:700; }
        .t-mkt { background:#e0f2fe; color:#075985; border:1px solid #7dd3fc; }
        .t-diag { background:#f3e8ff; color:#6b21a8; border:1px solid #d8b4fe; }
        .t-fac { background:#fef3c7; color:#92400e; border:1px solid #fcd34d; }
        .lead { color:#2c5282; font-weight:600; }
        .num-pos { color:#15803d; } .num-neg { color:#b91c1c; }
        .callout { background:#fff8e1; border-left:4px solid #f59e0b; border-radius:6px; padding:0.7rem 1rem; margin:0.8rem 0; font-size:0.9rem; }
        .callout b { color:#1a1a1a; }
        .legend-tbl { width:100%; border-collapse:collapse; font-size:0.85rem; margin:0.6rem 0; }
        .legend-tbl th, .legend-tbl td { border:1px solid #e2e8f0; padding:0.3rem 0.55rem; text-align:left; vertical-align:top; }
        .legend-tbl th { background:#eef2f7; color:#1f3a5f; font-weight:600; }
        .legend-tbl td.no { text-align:right; color:#64748b; font-variant-numeric:tabular-nums; }
        .legend-note { font-size:0.8rem; color:#64748b; margin-top:0.3rem; }
        code { background:#eef2f7; padding:1px 6px; border-radius:5px; border:1px solid #e2e8f0; font-size:0.85rem; }
        /* 編集モード */
        #rp-editbar { position:sticky; top:0; z-index:50; display:none; align-items:center; gap:0.6rem; flex-wrap:wrap; background:#1f3a5f; color:#fff; padding:0.5rem 0.9rem; border-radius:8px; margin-bottom:1rem; font-size:0.85rem; }
        #rp-editbar button { font:inherit; font-size:0.82rem; font-weight:600; padding:0.35rem 0.9rem; border-radius:5px; border:none; cursor:pointer; background:#f59e0b; color:#1a1a1a; }
        #rp-editbar button:hover { background:#fbbf24; }
        #rp-edit-status { font-size:0.8rem; }
        [data-cmt-key].rp-editing { outline:2px dashed #f59e0b; outline-offset:3px; background:#fffbeb; border-radius:6px; }
"""

# ---------------------------------------------------------------------------
# 5) HTML 組み立て
# ---------------------------------------------------------------------------
FAVICON = ('<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,'
 'PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMiAzMiI+'
 'PHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiByeD0iNyIgZmlsbD0iIzFmM2E1ZiIvPjxwYXRoIGQ9'
 'Ik0yNCAzIEwyNSA1LjUgTDI3LjUgNiBMMjUgNi41IEwyNCA5IEwyMyA2LjUgTDIwLjUgNiBMMjMgNS41'
 'IFoiIGZpbGw9IiNmNTllMGIiLz48cGF0aCBkPSJNMyAxNCBMMTAgMTEgTDI2IDExIEwyNiAxNSBMMjIg'
 'MTUgTDIwIDE5IEwyNCAxOSBMMjQuNSAyMyBMNy41IDIzIEw4IDE5IEwxMiAxOSBMMTAgMTUgTDMgMTUg'
 'WiIgZmlsbD0iI2ZmZmZmZiIvPjwvc3ZnPg==">')

BASE_CSS = """
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:"Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif; background:#f8fafc; color:#1a1a1a; line-height:1.7; padding:2.5rem 1rem; }
        .container { max-width:820px; margin:0 auto; }
        h1 { font-size:1.6rem; color:#2c5282; margin-bottom:0.4rem; }
        .subtitle { color:#64748b; font-size:0.9rem; margin-bottom:1.2rem; padding-bottom:0.9rem; border-bottom:2px solid #2c5282; }
        a { color:#2c5282; } a:hover { text-decoration:underline; }
        .lang-toggle { position:fixed; top:1rem; right:1rem; z-index:100; display:inline-flex; align-items:center; gap:0.4rem; padding:0.5rem 0.9rem; background:#fff; border:1px solid #cbd5e1; border-radius:6px; color:#2c5282; font-size:0.85rem; font-weight:600; text-decoration:none; box-shadow:0 2px 6px rgba(0,0,0,0.08); }
        .lang-toggle:hover { background:#2c5282; color:#fff; text-decoration:none; }
        .page-nav { display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:1.6rem; }
        .page-nav a { flex:1 1 0; text-align:center; padding:0.6rem 0.7rem; background:#fff; border:1px solid #e2e8f0; border-radius:8px; color:#2c5282; text-decoration:none; font-size:0.9rem; font-weight:600; white-space:nowrap; }
        .page-nav a:hover { box-shadow:0 2px 8px rgba(0,0,0,0.08); text-decoration:none; }
        .page-nav a.active { background:#2c5282; color:#fff; border-color:#2c5282; }
        footer { margin-top:3rem; font-size:0.8rem; color:#94a3b8; text-align:center; border-top:1px solid #e2e8f0; padding-top:1.2rem; }
        @media (max-width:600px){ .lang-toggle{ top:0.5rem; right:0.5rem; padding:0.4rem 0.7rem; font-size:0.78rem; } }
"""

NAV_JP = """    <nav class="page-nav">
        <a href="Kawaguchi_seminar.html">第4回</a>
        <a href="Kawaguchi_seminar_papers.html">過去資料</a>
        <a href="Kawaguchi_seminar_melmaga.html">メルマガ</a>
        <a href="Kawaguchi_seminar_minutes.html">議事メモ</a>
        <a href="Kawaguchi_seminar_riskpremia.html" class="active">リスクプレミア</a>
    </nav>"""

def legend_html():
    rows = []
    for no, jp, en, note in LEGEND:
        rows.append('      <tr><td class="no">%d</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (no, jp, en, note))
    return ('  <div class="sec"><h2>東証33業種 番号⇄定義（凡例）</h2></div>\n'
            '  <p id="legend" style="font-size:0.9rem;color:#64748b;margin:0.4rem 0;">'
            'P5・P10〜P13 の業種番号はこの順序（<code>TS33_87-1_latest.csv</code> の列順と照合済み）。</p>\n'
            '  <table class="legend-tbl">\n'
            '      <tr><th class="no">No.</th><th>業種（日本語）</th><th>CSV列名</th><th>レポートでの所見</th></tr>\n'
            + "\n".join(rows) + "\n  </table>\n"
            '  <p class="legend-note">CSV列名（Grocery/Metallurgical/Gas/Telecom 等）は作成者の略称。正式英名は Foods / Metal Products / Electric Power &amp; Gas / Information &amp; Communication。</p>\n')

def figcards_html():
    out = []
    for sec_title, nums in SECTIONS:
        out.append('  <div class="sec"><h2>%s</h2></div>' % sec_title)
        for n in nums:
            title, tagcls, taglabel = FIGS[n]
            atitle = "リスクプレミア P%d：%s" % (n, re.sub("<[^>]+>", "", title))
            out.append(
              '  <div class="page">\n'
              '    <h3><span class="pnum">P%d</span>%s<span class="tag %s">%s</span></h3>\n'
              '    <img src="risk_premia_figs/%02d.png" alt="P%d %s">\n'
              '    <div class="body" data-cmt-key="p%d"></div>\n'
              '    <div class="smtw-cmt" data-aid="rp-p%d" data-atitle="%s"></div>\n'
              '  </div>' % (n, title, tagcls, taglabel, n, n, re.sub('"',"", re.sub("<[^>]+>","",title)), n, n, atitle))
    return "\n".join(out)

def build_jp():
    parts = []
    parts.append("<!DOCTYPE html>\n<html lang=\"ja\">\n<head>\n")
    parts.append('    <meta charset="utf-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1">\n')
    parts.append("    <title>リスクプレミア分析 — AIx知的鍛錬塾 特別セクション</title>\n")
    parts.append("    " + FAVICON + "\n")
    parts.append("    <style>" + BASE_CSS + REPORT_CSS + SMTW_CMT_CSS + "    </style>\n")
    parts.append("</head>\n<body>\n")
    parts.append('<a class="lang-toggle" href="Kawaguchi_seminar_riskpremia_en.html">🇬🇧 EN</a>\n')
    parts.append('<div class="container">\n')
    parts.append('    <h1>リスクプレミア分析 — 市場リターンの鍵リスクは何か</h1>\n')
    parts.append('    <p class="subtitle">特別セクション ／ 東証33業種 × マクロファクターAPT（Chen-Roll-Ross型）／ 全期間 1987-01 〜 2026-04（472ヶ月）／ 作成 松前 景一郎</p>\n')
    parts.append(NAV_JP + "\n")
    # 編集バー
    parts.append('    <div id="rp-editbar">\n'
                 '      <strong>✎ 編集モード</strong>\n'
                 '      <button id="rp-edit-start" type="button">編集開始</button>\n'
                 '      <button id="rp-edit-save" type="button">保存</button>\n'
                 '      <button id="rp-edit-cancel" type="button">キャンセル</button>\n'
                 '      <span id="rp-edit-status"></span>\n'
                 '    </div>\n')
    # データ期間の明記（独立バナー）
    parts.append('    <div style="background:#eef2f7;border:1px solid #cbd5e1;border-radius:8px;'
                 'padding:0.6rem 1rem;margin:0.4rem 0 0.2rem;font-size:0.92rem;color:#1f3a5f;">'
                 '<b>データ期間:</b> 1987年1月 〜 2026年4月（月次 <b>472ヶ月</b>）　｜　'
                 '<b>対象:</b> 東証33業種指数 ＋ 8マクロ系列（IIP・CPI・為替・JGB10・コール・TOPIX・原油 ほか）　｜　'
                 '一部の図は <span style="color:#c0392b;">赤線=TOPIX</span> を第2軸で重ね描き</div>\n')
    # 結論 TL;DR
    parts.append('    <div class="tldr">\n      <h2>結論：市場リターン（TOPIX）にとっての鍵リスク</h2>\n      <div data-cmt-key="tldr"></div>\n    </div>\n')
    # 市場相関 callout（静的・参照データ）
    parts.append('''    <div class="callout">
      <b>市場リターンと各マクロ変化の同時相関（強い順）</b>
      <table class="keytbl">
        <tr><th>順位</th><th>マクロ変数（月次変化）</th><th>市場リターン(TPX)との相関</th><th>解釈</th></tr>
        <tr class="rank1"><td>1</td><td>為替 USD/JPY</td><td class="num">+0.196</td><td>円安=株高、最大の連動</td></tr>
        <tr><td>2</td><td>原油 WTI</td><td class="num">+0.099</td><td>リスクオン代理</td></tr>
        <tr><td>3</td><td>CPI（物価）</td><td class="num">+0.046</td><td>ほぼ無相関</td></tr>
        <tr><td>4</td><td>IIP（生産）</td><td class="num">+0.037</td><td>ほぼ無相関</td></tr>
        <tr><td>5</td><td>TERM（長短金利差）</td><td class="num">−0.003</td><td>無相関</td></tr>
      </table>
    </div>\n''')
    # 33業種凡例
    parts.append(legend_html())
    # figカード
    parts.append(figcards_html() + "\n")
    # まとめ
    parts.append('    <div class="sec"><h2>まとめ：市場リターンの鍵リスク</h2></div>\n')
    parts.append('    <div class="tldr concl">\n      <h2>投資判断への含意</h2>\n      <div data-cmt-key="conclusion"></div>\n    </div>\n')
    # コメントフォーム（統合）
    parts.append('    <h2 style="color:#2c5282;font-size:1.15rem;margin-top:2.2rem;">コメント・質問フォーム</h2>\n')
    parts.append('    <p style="color:#64748b;font-size:0.9rem;">各図の「✉️ この図についてコメントする」から対象を選んで送れます。いただいた内容は議論の材料にさせていただきます（送信先：運営）。</p>\n')
    parts.append('    <div id="smtw-cmt-form" class="smtw-cmt smtw-cmt-main" data-aid="general" data-atitle="リスクプレミア・全体"></div>\n')
    # footer
    parts.append('''    <footer>
      データ: <code>Macro8_87-1_latest.csv</code>（無料ソース自動更新）＋ <code>TS33_87-1_latest.csv</code>（Bloomberg 33業種）。
      分析: <code>Risk premia_latest.R</code>。図は <code>output/Risk_premia_plots_latest.pdf</code> と同一。<br>
      リスクプレミアムのt値は素の平均/(SD/√n)による概算で、正式推論は要Newey-West。作成: 松前 景一郎 ／ 生成 %s ／ 参加者限定・転載禁止。
    </footer>\n''' % GEN_DATE)
    parts.append('</div>\n')
    # scripts
    parts.append("<script>" + EDIT_JS.replace("__REPO_SLUG__", REPO_SLUG) + "</script>\n")
    parts.append("<script>" + SMTW_CMT_JS + "</script>\n")
    parts.append("</body>\n</html>\n")
    return "".join(parts)

def build_en():
    nav = NAV_JP.replace('class="active"','').replace("Kawaguchi_seminar.html\">第4回","Kawaguchi_seminar_en.html\">3rd Mtg")
    nav = ('    <nav class="page-nav">\n'
           '        <a href="Kawaguchi_seminar_en.html">3rd Mtg</a>\n'
           '        <a href="Kawaguchi_seminar_papers_en.html">Archive</a>\n'
           '        <a href="Kawaguchi_seminar_melmaga_en.html">Newsletters</a>\n'
           '        <a href="Kawaguchi_seminar_minutes_en.html">Minutes</a>\n'
           '        <a href="Kawaguchi_seminar_riskpremia_en.html" class="active">Risk Premia</a>\n'
           '    </nav>')
    html = ("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
            '    <meta charset="utf-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "    <title>Risk Premia Analysis — AI x Intellectual Forging Academy</title>\n    " + FAVICON + "\n"
            "    <style>" + BASE_CSS + REPORT_CSS + "    </style>\n</head>\n<body>\n"
            '<a class="lang-toggle" href="Kawaguchi_seminar_riskpremia.html">🇯🇵 JP</a>\n'
            '<div class="container">\n'
            '    <h1>Risk Premia Analysis — Key Risks of Japanese Equity Returns</h1>\n'
            '    <p class="subtitle">Special section ／ TOPIX-33 industries × macro-factor APT (Chen-Roll-Ross) ／ 1987-01 – 2026-04 (472 months) ／ by Keiichiro Matsumae</p>\n'
            + nav + "\n"
            '    <div class="callout"><b>JP only for now.</b> This special section is currently available in Japanese. '
            'Please see the <a href="Kawaguchi_seminar_riskpremia.html">Japanese version</a>; an English summary can be provided on request.</div>\n'
            '    <h2 style="color:#2c5282;font-size:1.15rem;">Summary (3 points)</h2>\n'
            '    <ol style="margin-left:1.3rem;">\n'
            '      <li><b>FX (USD/JPY) is the single largest systematic driver</b> of TOPIX returns (contemporaneous corr +0.196; instantaneous causality χ²=16.3, p=0.00005). Co-moves within the month, but does not lead.</li>\n'
            '      <li><b>Volatility clusters in crises</b> — 1990-91 bubble burst and 2008 GFC (monthly vol ~9-11%). GARCH persistence α+β=0.88; unconditional annualized vol ~18.6%.</li>\n'
            '      <li><b>Textbook macro factors (IIP, CPI) are not priced</b> — Fama-MacBeth premia statistically insignificant (t≈−1.0 / −0.9).</li>\n'
            '    </ol>\n'
            '    <footer>Participants only ／ Not for redistribution ／ by Keiichiro Matsumae ／ generated ' + GEN_DATE + '.</footer>\n'
            '</div>\n</body>\n</html>\n')
    return html

def main():
    jp = build_jp()
    en = build_en()
    io.open(os.path.join(ROOT, "Kawaguchi_seminar_riskpremia.html"), "w", encoding="utf-8", newline="\n").write(jp)
    io.open(os.path.join(ROOT, "Kawaguchi_seminar_riskpremia_en.html"), "w", encoding="utf-8", newline="\n").write(en)
    if not os.path.isdir(DOCS): os.makedirs(DOCS)
    io.open(os.path.join(DOCS, "risk_premia_comments.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(COMMENTS, ensure_ascii=False, indent=2))
    # 整合チェック: data-cmt-key と JSON キーの照合
    keys_in_html = set(re.findall(r'data-cmt-key="([^"]+)"', jp))
    keys_in_json = set(COMMENTS.keys())
    missing = keys_in_html - keys_in_json
    extra = keys_in_json - keys_in_html
    print("JP bytes:", len(jp.encode("utf-8")), " EN bytes:", len(en.encode("utf-8")))
    print("data-cmt-key in HTML:", len(keys_in_html), " JSON keys:", len(keys_in_json))
    print("missing(JSONに無い):", sorted(missing), " extra(HTMLに無い):", sorted(extra))
    print("smtw-cmt blocks:", jp.count('class="smtw-cmt"'))
    print("img refs:", jp.count("risk_premia_figs/"))

if __name__ == "__main__":
    main()
