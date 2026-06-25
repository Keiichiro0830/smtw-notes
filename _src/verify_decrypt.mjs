import { readFileSync } from "node:fs";
import { webcrypto as crypto } from "node:crypto";

const file = process.argv[2];
const password = "Kawaguchi";
const html = readFileSync(file, "utf8");
const m = html.match(/staticryptEncryptedMsgUniqueVariableName"\s*:\s*"([0-9a-f]+)"/);
const s = html.match(/staticryptSaltUniqueVariableName"\s*:\s*"([0-9a-f]+)"/);
if (!m || !s) throw new Error("payload/salt not found");
const signedMsg = m[1], saltHex = s[1];
const utf8 = new TextEncoder();
const hex = (buf) => Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, "0")).join("");
const fromHex = (h) => Uint8Array.from(h.match(/.{2}/g).map(b => parseInt(b, 16)));
async function pbkdf2(pwBytes, saltStr, iter, hash) {
  const k = await crypto.subtle.importKey("raw", pwBytes, "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits({ name: "PBKDF2", hash, salt: utf8.encode(saltStr), iterations: iter }, k, 256);
  return hex(bits);
}
let hp = await pbkdf2(utf8.encode(password), saltHex, 1000, "SHA-1");
hp = await pbkdf2(utf8.encode(hp), saltHex, 14000, "SHA-256");
hp = await pbkdf2(utf8.encode(hp), saltHex, 585000, "SHA-256");
const encryptedMsg = signedMsg.substring(64);
const ivHex = encryptedMsg.substring(0, 32);
const ctHex = encryptedMsg.substring(32);
const key = await crypto.subtle.importKey("raw", fromHex(hp), { name: "AES-CBC" }, false, ["decrypt"]);
const plaintext = await crypto.subtle.decrypt({ name: "AES-CBC", iv: fromHex(ivHex) }, key, fromHex(ctHex));
const text = new TextDecoder().decode(plaintext);
const markers = process.argv.slice(3);
console.log("DECRYPT OK:", file, "| chars:", text.length);
for (const mk of markers) console.log("  marker [" + mk + "]:", text.includes(mk) ? "FOUND x" + text.split(mk).length : "MISSING", "(" + (text.split(mk).length - 1) + ")");
