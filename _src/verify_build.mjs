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
  ["docs/Kawaguchi_seminar.html", ["第3回後アンケート結果", "時空統計合宿：時期の希望", "9月上旬", "chart-basho", "ループ・エンジニアリング", "第4回（7/18）事前資料", "paper-20260718-loop", "ループ・エンジニアリング演習</strong>（川口先生より・7/14）", "Lynch_202602_Claude_Code_Chief_of_Staff_JP.docx", "paper-20260718-theme", "paper-20260718-nikkei", "paper-20260718-tutorial", "paper-20260718-video", "paper-20260718-relink", "企業におけるAI活用", "事前資料 公開中", "paper-20260718-slides", "Kawaguchi_20260718_LLM_GenAI_Guide_Loop_Engineering_Ver2.pdf", "当日プレゼン資料", "ファイル提出BOX", "smtw-upl-form", "SMTW_UPL_TEXT"]],
  ["docs/Kawaguchi_seminar_en.html", ["Post-3rd-meeting survey", "Retreat timing", "chart-basho", "loop engineering", "Pre-reads for the 4th meeting", "paper-20260718-loop", "Loop-engineering exercise</strong> (proposed by Prof. Kawaguchi, July 14)", "paper-20260718-theme", "paper-20260718-relink", "AI adoption in the enterprise", "paper-20260718-slides", "Kawaguchi_20260718_LLM_GenAI_Guide_Loop_Engineering_Ver2.pdf", "File submission box", "smtw-upl-form", "SMTW_UPL_TEXT"]],
  ["docs/Kawaguchi_seminar_video1.html", ["スライド 34", "講義ログ（自動文字起こし・全文）", "全体サマリー"]],
  ["docs/Kawaguchi_seminar_articles.html", ["バブルマネー争奪", "株式と債券の動きに矛盾", "日本経済新聞社に帰属"]],
  ["docs/Kawaguchi_seminar_boj.html", ["日銀"]],
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
