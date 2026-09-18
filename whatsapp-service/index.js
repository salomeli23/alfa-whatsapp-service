const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
} = require("@whiskeysockets/baileys");
const qrcode = require("qrcode");
const express = require("express");
const axios = require("axios");
const pino = require("pino");
const fs = require("fs");
const path = require("path");

const logger = pino({ level: "silent" });
let rawBackend = process.env.BACKEND_URL || process.env.BACKEND_INTERNAL_URL || "https://alfapolarizados.online";
if (rawBackend.startsWith("VALUE") || rawBackend.includes("${{") || (rawBackend.includes("localhost") && !process.env.BACKEND_INTERNAL_URL)) {
  rawBackend = "https://alfapolarizados.online";
}
const BACKEND = rawBackend.replace(/\/panel\/?$/i, "").replace(/\/+$/, "");
const AUTH_DIR = process.env.AUTH_DIR || path.join(__dirname, "auth");
const PORT = process.env.PORT || process.env.WA_PORT || 3001;
const WA_TOKEN = process.env.WA_TOKEN || "";

let sock = null;
let currentQR = null; // data URL
let connState = "connecting"; // connecting | qr | connected | disconnected
let meNumber = null;
let linkAt = 0; // timestamp (s) en que abrió la conexión actual
const seenIds = new Set(); // dedupe de mensajes ya procesados

const jidToContact = (jid) => (jid || "").split("@")[0].split(":")[0]; // normaliza a número

// WhatsApp puede identificar al mismo usuario como @s.whatsapp.net (número) o @lid.
// Preferimos SIEMPRE el JID de número para que la sesión del bot sea estable.
function resolveJid(msg) {
  const jid = msg.key.remoteJid || "";
  const alt = msg.key.remoteJidAlt || "";
  if (jid.endsWith("@s.whatsapp.net")) return jid;
  if (alt.endsWith("@s.whatsapp.net")) return alt;
  return jid;
}

async function startSock() {
  if (sock) {
    try {
      sock.ev.removeAllListeners("creds.update");
      sock.ev.removeAllListeners("connection.update");
      sock.ev.removeAllListeners("messages.upsert");
      sock.end();
    } catch (e) {}
  }
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const { version } = await fetchLatestBaileysVersion();
  const mySock = makeWASocket({ version, auth: state, logger, printQRInTerminal: false, syncFullHistory: false });
  sock = mySock;

  mySock.ev.on("creds.update", saveCreds);

  mySock.ev.on("connection.update", async (u) => {
    if (sock !== mySock) return; // socket viejo reconectando → ignorar
    const { connection, lastDisconnect, qr } = u;
    if (qr) {
      currentQR = await qrcode.toDataURL(qr);
      connState = "qr";
      console.log("QR actualizado");
    }
    if (connection === "open") {
      connState = "connected";
      currentQR = null;
      meNumber = (mySock.user && mySock.user.id) ? mySock.user.id.split(":")[0] : null;
      linkAt = Math.floor(Date.now() / 1000);
      console.log("WhatsApp conectado:", meNumber);
    }
    if (connection === "close") {
      const code = lastDisconnect && lastDisconnect.error && lastDisconnect.error.output
        ? lastDisconnect.error.output.statusCode : null;
      connState = "disconnected";
      console.log("Conexión cerrada. code:", code);
      if (code !== DisconnectReason.loggedOut) {
        setTimeout(startSock, 5000); // reconexión automática (con respiro)
      } else {
        try { fs.rmSync(AUTH_DIR, { recursive: true, force: true }); } catch (e) {}
        setTimeout(startSock, 2000); // nueva sesión → nuevo QR
      }
    }
  });

  mySock.ev.on("messages.upsert", async (up) => {
    if (sock !== mySock) return; // evita doble procesamiento de sockets anteriores
    if (up.type !== "notify") return;
    for (const msg of up.messages) {
      try {
        if (!msg.message || msg.key.fromMe) continue;
        const jid = resolveJid(msg);
        if (jid.endsWith("@g.us") || jid === "status@broadcast" || jid.endsWith("@newsletter")) continue;

        // Ignorar historial sincronizado al vincular el QR (mensajes viejos)
        const ts = Number(msg.messageTimestamp || 0);
        if (linkAt && ts && ts < linkAt - 30) continue;

        // Dedupe por ID de mensaje (WhatsApp puede re-entregar)
        const mid = msg.key.id || "";
        if (mid) {
          if (seenIds.has(mid)) continue;
          seenIds.add(mid);
          if (seenIds.size > 500) seenIds.delete(seenIds.values().next().value);
        }

        const m = msg.message;
        const text =
          m.conversation ||
          (m.extendedTextMessage && m.extendedTextMessage.text) ||
          (m.imageMessage && m.imageMessage.caption) ||
          (m.videoMessage && m.videoMessage.caption) ||
          (m.buttonsResponseMessage && m.buttonsResponseMessage.selectedDisplayText) ||
          (m.listResponseMessage && m.listResponseMessage.title) ||
          "";
        const isAudio = !!(m.audioMessage || m.pttMessage);
        const pushName = msg.pushName || "";
        const contact = jidToContact(jid);

        console.log(`[WA] Mensaje entrante de ${contact} (${pushName}): "${(text || (isAudio ? '[Audio]' : '')).slice(0, 60)}"`);
        const { data } = await axios.post(`${BACKEND}/api/bot/incoming`, {
          contact, name: pushName, text, is_audio: isAudio,
        }, { timeout: 20000 });

        if (data.paused) {
          console.log(`[WA] Conversación con ${contact} está en pausa por asesor`);
          continue;
        }
        const replyMsgs = data.messages || [];
        console.log(`[WA] Andrea generó ${replyMsgs.length} mensaje(s) de respuesta para ${contact}`);
        for (const mm of replyMsgs) {
          if (mm.delay) await new Promise((r) => setTimeout(r, mm.delay * 1000));
          await sendToJid(jid, mm.text || "", mm.media || []);
          await new Promise((r) => setTimeout(r, 400)); // pequeño respiro entre mensajes
        }
      } catch (e) {
        console.error(`[WA] Error enviando a ${BACKEND}/api/bot/incoming:`, e.message);
      }
    }
  });
}

async function sendToJid(jid, text, media) {
  if (media && media.length) {
    let caption = text || undefined;
    for (const url of media) {
      const isVideo = /\.(mp4|mov|webm|3gp)$/i.test(url);
      if (isVideo) await sock.sendMessage(jid, { video: { url }, caption });
      else await sock.sendMessage(jid, { image: { url }, caption });
      caption = undefined; // el texto va solo con el primer adjunto
    }
  } else if (text) {
    await sock.sendMessage(jid, { text });
  }
}

// ---------- API HTTP local ----------
const app = express();
app.use(express.json());

// Protección opcional por token (obligatoria si se define WA_TOKEN)
app.use((req, res, next) => {
  if (WA_TOKEN && req.headers["x-wa-token"] !== WA_TOKEN) {
    return res.status(401).json({ ok: false, error: "unauthorized" });
  }
  next();
});

app.get("/status", (req, res) => {
  res.json({ state: connState, qr: currentQR, me: meNumber });
});

app.post("/send", async (req, res) => {
  const { to, text, media } = req.body || {};
  if (!to) return res.status(400).json({ ok: false, error: "falta destino" });
  const jid = to.includes("@") ? to : `${to}@s.whatsapp.net`;
  try {
    await sendToJid(jid, text || "", media || []);
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

app.post("/logout", async (req, res) => {
  try { if (sock) await sock.logout(); } catch (e) {}
  try { fs.rmSync(AUTH_DIR, { recursive: true, force: true }); } catch (e) {}
  currentQR = null;
  connState = "disconnected";
  setTimeout(startSock, 1000);
  res.json({ ok: true });
});

app.listen(PORT, () => console.log(`WA service en puerto ${PORT} -> Backend conectado a: ${BACKEND}`));
startSock();
