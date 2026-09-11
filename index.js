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
const BACKEND = process.env.BACKEND_INTERNAL_URL || process.env.BACKEND_URL || "http://localhost:8001";
const AUTH_DIR = process.env.AUTH_DIR || path.join(__dirname, "auth");
const PORT = process.env.PORT || process.env.WA_PORT || 3001;
const WA_TOKEN = process.env.WA_TOKEN || "";

let sock = null;
let currentQR = null; // data URL
let connState = "connecting"; // connecting | qr | connected | disconnected
let meNumber = null;

const jidToContact = (jid) => (jid || "").split(":")[0]; // normaliza

async function startSock() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const { version } = await fetchLatestBaileysVersion();
  sock = makeWASocket({ version, auth: state, logger, printQRInTerminal: false, syncFullHistory: false });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", async (u) => {
    const { connection, lastDisconnect, qr } = u;
    if (qr) {
      currentQR = await qrcode.toDataURL(qr);
      connState = "qr";
      console.log("QR actualizado");
    }
    if (connection === "open") {
      connState = "connected";
      currentQR = null;
      meNumber = (sock.user && sock.user.id) ? sock.user.id.split(":")[0] : null;
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

  sock.ev.on("messages.upsert", async (up) => {
    if (up.type !== "notify") return;
    for (const msg of up.messages) {
      try {
        if (!msg.message || msg.key.fromMe) continue;
        const jid = msg.key.remoteJid || "";
        if (jid.endsWith("@g.us") || jid === "status@broadcast" || jid.endsWith("@newsletter")) continue;

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

        const { data } = await axios.post(`${BACKEND}/api/bot/incoming`, {
          contact, name: pushName, text, is_audio: isAudio,
        }, { timeout: 20000 });

        if (data.paused) continue;
        for (const mm of data.messages || []) {
          if (mm.delay) await new Promise((r) => setTimeout(r, mm.delay * 1000));
          await sendToJid(jid, mm.text || "", mm.media || []);
          await new Promise((r) => setTimeout(r, 400)); // pequeño respiro entre mensajes
        }
      } catch (e) {
        console.error("Error procesando mensaje:", e.message);
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

app.listen(PORT, () => console.log(`WA service en puerto ${PORT}`));
startSock();
