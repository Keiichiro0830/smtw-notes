import { readFileSync } from "node:fs";
import { webcrypto as crypto } from "node:crypto";

const password = "Kawaguchi";
const utf8 = new TextEncoder();
const hex = (buf) => Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, "0")).join("");
const fromHex = (h) => Uint8Array.from(h.match(/.{2}/g).map(b => parseInt(b, 16)));

async function pbkdf2(pwBytes, saltStr, iter, hash) {
  const k = await crypto.subtle.importKey("raw", pwBytes, "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", hash, salt: utf8.encode(saltStr), iterations: iter },
    k, 256
  );
  return hex(bits);
}

async function decrypt(file) {
  const html = readFileSync(file, "utf8");
  const m = html.match(/staticryptEncryptedMsgUniqueVariableName"\s*:\s*"([0-9a-f]+)"/);
  const s = html.match(/staticryptSaltUniqueVariableName"\s*:\s*"([0-9a-f]+)"/);
  if (!m || !s) throw new Error("payload/salt not found in " + file);
  const salt = s[1];
  let hp = await pbkdf2(utf8.encode(password), salt, 1000, "SHA-1");
  hp = await pbkdf2(utf8.encode(hp), salt, 14000, "SHA-256");
  hp = await pbkdf2(utf8.encode(hp), salt, 585000, "SHA-256");
  const payload = m[1];
  // staticrypt --short: payload = hmac(64 hex) + iv(32 hex) + ciphertext(hex)
  const hmacHex = payload.slice(0, 64);
  const encrypted = payload.slice(64);
  const iv = fromHex(encrypted.slice(0, 32));
  const ct = fromHex(encrypted.slice(32));
  const key = await crypto.subtle.importKey("raw", fromHex(hp), "AES-CBC", false, ["decrypt"]);
  const pt = await crypto.subtle.decrypt({ name: "AES-CBC", iv }, key, ct);
  return new TextDecoder().decode(pt);
}

const checks = [
  ["docs/Kawaguchi_seminar.html", ["AIx知的鍛錬塾 ポータル", "hub-card", "第5回 研究会", "秋のシンポジウム", "第4回 — ループ・エンジニアリング演習", "Kawaguchi_seminar_0822.html", "Kawaguchi_seminar_1003.html", "Kawaguchi_seminar_prev.html", "配布BOX", "smtw-dist", "ファイル提出BOX", "smtw-upl-form", "SMTW_UPL_TEXT"]],
  ["docs/Kawaguchi_seminar_en.html", ["AI x Intellectual Forging Academy", "hub-card", "5th meeting", "Autumn symposium", "4th meeting", "Kawaguchi_seminar_0822_en.html", "Kawaguchi_seminar_1003_en.html", "Kawaguchi_seminar_prev_en.html", "Distribution box", "smtw-dist", "File submission box", "smtw-upl-form", "SMTW_UPL_TEXT"]],
  ["docs/Kawaguchi_seminar_0822.html", ["2026年8月22日", "1102会議室", "エージェンティック時空統計学入門チュートリアル", "R と RStudio", "2025年演習で用いた時空データ一覧", "pollutionhealthdata", "Kawaguchi_20260804_2025Seminar_Data_List.pdf", "Kawaguchi_20260801_Upstream_Experts.pdf", "https://otexts.com/fppjp/", "バイブ統計モデリング",
    // 上部の資料ボックス（2026-08-11 追加）
    "resource-box", "当日までにご覧いただきたい資料", "Kawaguchi_LLM_Mechanism_1_Embedding.docx", "Kawaguchi_LLM_Mechanism_2_NeuralLM.docx", "Kawaguchi_LLM_Mechanism_3_Attention.docx", "https://www.amazon.co.jp/dp/406527303X", "https://github.com/dmuraka/spbook_jp", "Chapter 列は、このテキストの章番号"]],
  ["docs/Kawaguchi_seminar_0822_en.html", ["August 22, 2026", "Room 1102", "agentic spatio-temporal statistics", "R and RStudio", "pollutionhealthdata", "Kawaguchi_20260804_2025Seminar_Data_List.pdf", "Kawaguchi_20260801_Upstream_Experts.pdf", "vibe statistical modeling",
    "resource-box", "Materials to look at before the day", "Kawaguchi_LLM_Mechanism_1_Embedding.docx", "Kawaguchi_LLM_Mechanism_3_Attention.docx", "https://www.amazon.co.jp/dp/406527303X", "https://github.com/dmuraka/spbook_jp"]],
  ["docs/Kawaguchi_seminar_1003.html", ["2026年10月3日", "今回は違うか？：ITブームとAIブームの違い", "計画資本（認知経済学）", "ゼミ会", "リアルオプションと計画資本"]],
  ["docs/Kawaguchi_seminar_1003_en.html", ["October 3, 2026", "Is This Time Different?", "planning capital (cognitive economics)", "zemi-kai", "Real Options and Planning Capital"]],
  ["docs/Kawaguchi_seminar_prev.html", ["第3回後アンケート結果", "時空統計合宿：時期の希望", "9月上旬", "chart-basho", "ループ・エンジニアリング", "第4回（7/18）事前資料", "paper-20260718-loop", "Lynch_202602_Claude_Code_Chief_of_Staff_JP.docx", "paper-20260718-theme", "paper-20260718-nikkei", "paper-20260718-tutorial", "paper-20260718-video", "paper-20260718-relink", "企業におけるAI活用", "paper-20260718-slides", "Kawaguchi_20260718_LLM_GenAI_Guide_Loop_Engineering_Ver2.pdf", "当日プレゼン資料"]],
  ["docs/Kawaguchi_seminar_prev_en.html", ["Post-3rd-meeting survey", "Retreat timing", "chart-basho", "loop engineering", "Pre-reads for the 4th meeting", "paper-20260718-loop", "paper-20260718-theme", "paper-20260718-relink", "AI adoption in the enterprise", "paper-20260718-slides", "Kawaguchi_20260718_LLM_GenAI_Guide_Loop_Engineering_Ver2.pdf"]],
  ["docs/Kawaguchi_seminar_minutes.html", ["10. 第5回 研究会 議事メモ（2026-08-22）", "グラム行列", "診断的不確実性", "第5回（最新・08-22）", "Kawaguchi_seminar_minutes4.html", "Belsley", "NVIDIA"]],
  ["docs/Kawaguchi_seminar_minutes4.html", ["9. 第4回ミーティング 議事メモ（2026-07-18）", "ループ・エンジニアリング演習 — 参加者の実践", "検証コストの安さ", "第5回（最新・08-22）", "Kawaguchi_seminar_minutes3.html", "昼食懇談"]],
  ["docs/Kawaguchi_seminar_minutes_en.html", ["9. 4th meeting summary (July 18, 2026)", "Loop-engineering exercise", "4th · latest (07-18)", "Kawaguchi_seminar_minutes3_en.html", "August 22, 2026"]],
  ["docs/Kawaguchi_seminar_minutes3.html", ["8. 第3回ミーティング 議事メモ（2026-06-20）", "第5回（最新・08-22）"]],
  ["docs/Kawaguchi_seminar_minutes3_en.html", ["3rd meeting summary", "4th · latest (07-18)"]],
  ["docs/Kawaguchi_seminar_minutes1.html", ["第5回（最新・08-22）", "第1回ミーティング 議事メモ"]],
  ["docs/Kawaguchi_seminar_minutes2.html", ["第5回（最新・08-22）", "第2回ミーティング 議事メモ"]],
  ["docs/Kawaguchi_seminar_minutes1_en.html", ["4th · latest (07-18)"]],
  ["docs/Kawaguchi_seminar_minutes2_en.html", ["4th · latest (07-18)"]],
  ["docs/Kawaguchi_seminar_video1.html", ["スライド 34", "講義ログ（自動文字起こし・全文）", "全体サマリー"]],
  ["docs/Kawaguchi_seminar_articles.html", ["バブルマネー争奪", "株式と債券の動きに矛盾", "日本経済新聞社に帰属"]],
];

let fail = 0;
for (const [file, needles] of checks) {
  try {
    const pt = await decrypt(file);
    const imgs = (pt.match(/data:image\/jpeg/g) || []).length;
    for (const n of needles) {
      const ok = pt.includes(n);
      if (!ok) fail++;
      console.log(`${ok ? "PASS" : "FAIL"}  ${file}  contains "${n}"`);
    }
    console.log(`INFO  ${file}  decrypted ${pt.length} chars, ${imgs} embedded jpeg(s)`);
  } catch (e) {
    fail++;
    console.log(`FAIL  ${file}  decrypt error: ${e.message}`);
  }
}
process.exit(fail ? 1 : 0);
