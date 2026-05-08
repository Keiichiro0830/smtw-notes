import { readFileSync, writeFileSync } from "node:fs";
import { webcrypto as crypto } from "node:crypto";

const file = "encrypted/260411_meeting_notes.html";
const password = "Kawaguchi";
const html = readFileSync(file, "utf8");

const m = html.match(/staticryptEncryptedMsgUniqueVariableName"\s*:\s*"([0-9a-f]+)"/);
const s = html.match(/staticryptSaltUniqueVariableName"\s*:\s*"([0-9a-f]+)"/);
if (!m || !s) throw new Error("payload/salt not found");
const signedMsg = m[1];
const saltHex = s[1];
console.error("salt:", saltHex, "payload bytes:", signedMsg.length / 2);

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

const salt = saltHex;  // staticrypt uses the salt hex string itself (not bytes) as the salt input — saltStr passed via UTF8Encoder.parse(salt)
// staticrypt passes the hex-string output of each round as the next round's password (via UTF8Encoder.parse)
let hp = await pbkdf2(utf8.encode(password), salt, 1000, "SHA-1");
hp = await pbkdf2(utf8.encode(hp), salt, 14000, "SHA-256");
hp = await pbkdf2(utf8.encode(hp), salt, 585000, "SHA-256");
console.error("hashedPassword:", hp);

// signedMsg = HMAC(64 hex) + encryptedMsg(iv 32 hex + ciphertext)
const hmacHex = signedMsg.substring(0, 64);
const encryptedMsg = signedMsg.substring(64);
const ivHex = encryptedMsg.substring(0, 32);
const ctHex = encryptedMsg.substring(32);

const key = await crypto.subtle.importKey("raw", fromHex(hp), { name: "AES-CBC" }, false, ["decrypt"]);
const plaintext = await crypto.subtle.decrypt({ name: "AES-CBC", iv: fromHex(ivHex) }, key, fromHex(ctHex));
const text = new TextDecoder().decode(plaintext);
writeFileSync("_src/decrypted_260411.html", text, "utf8");
console.error("OK", text.length, "chars written to _src/decrypted_260411.html");
