import { useEffect, useRef, useState, useCallback } from "react";
import axios from "axios";
import { toast, Toaster } from "sonner";
import {
  MessageCircle, Send, LogOut, Search, Bot, User, RefreshCw, Pause, Play, Lock, QrCode, X,
} from "lucide-react";
import "@/Panel.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const TOKEN_KEY = "alfa_admin_token";

const api = axios.create({ baseURL: API });
api.interceptors.request.use((cfg) => {
  const t = localStorage.getItem(TOKEN_KEY);
  if (t) cfg.headers.Authorization = `Bearer ${t}`;
  return cfg;
});

function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const { data } = await api.post("/auth/login", { username, password });
      localStorage.setItem(TOKEN_KEY, data.token);
      onLogin(data.username);
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo iniciar sesión");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-wrap" data-testid="login-page">
      <form className="login-card" onSubmit={submit}>
        <div className="login-logo"><span className="brand-mark">α</span></div>
        <h1 className="login-title">Panel Andrea</h1>
        <p className="login-sub">Alfa Polarizados · Mensajes de WhatsApp</p>
        <div className="login-field">
          <User size={16} />
          <input data-testid="login-username" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Usuario" autoFocus />
        </div>
        <div className="login-field">
          <Lock size={16} />
          <input data-testid="login-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Contraseña" />
        </div>
        {error && <div className="login-error" data-testid="login-error">{error}</div>}
        <button data-testid="login-submit" className="login-btn" disabled={loading}>
          {loading ? "Ingresando…" : "Ingresar"}
        </button>
      </form>
    </div>
  );
}

function displayName(c) {
  return c.name || (c.contact || "").replace("whatsapp:", "").replace("@s.whatsapp.net", "").replace("@c.us", "");
}

function QRLinkModal({ onClose }) {
  const [status, setStatus] = useState({ state: "connecting", qr: null, me: null });
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    try {
      const { data } = await api.get("/wa/status");
      setStatus(data);
    } catch (e) { /* ignore */ }
  }, []);

  useEffect(() => { load(); const i = setInterval(load, 3000); return () => clearInterval(i); }, [load]);

  const logout = async () => {
    setLoading(true);
    try { await api.post("/wa/logout"); toast.success("Sesión cerrada, escanea el nuevo QR"); await load(); }
    catch (e) { toast.error("No se pudo desvincular"); }
    finally { setLoading(false); }
  };

  const connected = status.state === "connected";

  return (
    <div className="qr-overlay" data-testid="qr-modal" onClick={onClose}>
      <div className="qr-card" onClick={(e) => e.stopPropagation()}>
        <button className="qr-close" onClick={onClose} data-testid="qr-close"><X size={18} /></button>
        <h2 className="qr-title"><QrCode size={20} /> Vincular WhatsApp</h2>

        {connected ? (
          <div className="qr-connected" data-testid="qr-connected">
            <div className="qr-dot-ok" />
            <p>Conectado ✅</p>
            <p className="qr-num">{status.me}</p>
            <button className="qr-logout" onClick={logout} disabled={loading} data-testid="qr-logout">
              {loading ? "…" : "Desvincular"}
            </button>
          </div>
        ) : status.qr ? (
          <>
            <p className="qr-help">Abre WhatsApp en tu teléfono → <b>Dispositivos vinculados</b> → <b>Vincular un dispositivo</b> y escanea:</p>
            <img src={status.qr} alt="QR de WhatsApp" className="qr-img" data-testid="qr-image" />
            <p className="qr-state">Esperando escaneo… (el QR se actualiza solo)</p>
          </>
        ) : (
          <div className="qr-loading" data-testid="qr-loading">
            <RefreshCw className="spin" size={26} />
            <p>{status.state === "offline" ? "Servicio de WhatsApp iniciando…" : "Generando código QR…"}</p>
          </div>
        )}
      </div>
    </div>
  );
}

function Dashboard({ onLogout }) {
  const [convs, setConvs] = useState([]);
  const [active, setActive] = useState(null);
  const [messages, setMessages] = useState([]);
  const [reply, setReply] = useState("");
  const [query, setQuery] = useState("");
  const [sending, setSending] = useState(false);
  const [showQR, setShowQR] = useState(false);
  const scrollRef = useRef(null);

  const loadConvs = useCallback(async () => {
    try {
      const { data } = await api.get("/admin/conversations");
      setConvs(data);
    } catch (e) {
      if (e.response?.status === 401) onLogout();
    }
  }, [onLogout]);

  const loadMessages = useCallback(async (contact) => {
    if (!contact) return;
    try {
      const { data } = await api.get("/admin/messages", { params: { contact } });
      setMessages(data);
      setTimeout(() => scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight }), 50);
    } catch (e) {
      if (e.response?.status === 401) onLogout();
    }
  }, [onLogout]);

  useEffect(() => { loadConvs(); const i = setInterval(loadConvs, 5000); return () => clearInterval(i); }, [loadConvs]);
  useEffect(() => {
    if (!active) return;
    loadMessages(active);
    const i = setInterval(() => loadMessages(active), 4000);
    return () => clearInterval(i);
  }, [active, loadMessages]);

  const activeConv = convs.find((c) => c.contact === active);

  const sendReply = async (e) => {
    e.preventDefault();
    if (!reply.trim() || !active) return;
    setSending(true);
    try {
      const { data } = await api.post("/admin/reply", { contact: active, body: reply });
      if (data.ok) {
        setReply("");
        await loadMessages(active);
        await loadConvs();
        toast.success("Mensaje enviado");
      } else {
        toast.error(data.error || "No se pudo enviar");
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "No se pudo enviar");
    } finally {
      setSending(false);
    }
  };

  const toggleBot = async () => {
    if (!active) return;
    const paused = !(activeConv?.bot_paused);
    try {
      await api.post("/admin/toggle-bot", { contact: active, paused });
      await loadConvs();
      toast.success(paused ? "Bot en pausa — respondes tú" : "Bot reactivado");
    } catch (err) {
      toast.error("No se pudo cambiar el estado del bot");
    }
  };

  const filtered = convs.filter((c) => displayName(c).toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="panel" data-testid="dashboard">
      <aside className="sidebar">
        <div className="side-head">
          <div className="brand"><span className="brand-mark sm">α</span><span className="side-title">Andrea · Chats</span></div>
          <div className="flex items-center gap-1">
            <button className="icon-btn" onClick={() => setShowQR(true)} title="Vincular WhatsApp (QR)" data-testid="open-qr-btn"><QrCode size={16} /></button>
            <button className="icon-btn" onClick={onLogout} title="Salir" data-testid="logout-btn"><LogOut size={16} /></button>
          </div>
        </div>
        <button className="link-wa-btn" onClick={() => setShowQR(true)} data-testid="link-wa-btn">
          <QrCode size={15} /> Vincular WhatsApp (QR)
        </button>
        <div className="search-box">
          <Search size={15} />
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Buscar cliente…" data-testid="search-input" />
        </div>
        <div className="conv-list" data-testid="conversation-list">
          {filtered.length === 0 && <div className="empty-hint">Aún no hay conversaciones.</div>}
          {filtered.map((c) => (
            <button key={c.contact} className={`conv-item ${active === c.contact ? "active" : ""}`} onClick={() => setActive(c.contact)} data-testid={`conv-${c.contact}`}>
              <div className="conv-avatar">{displayName(c).charAt(0).toUpperCase()}</div>
              <div className="conv-body">
                <div className="conv-top">
                  <span className="conv-name">{displayName(c)}</span>
                  {c.bot_paused && <span className="badge-human" title="Bot en pausa">👤</span>}
                </div>
                <div className="conv-last">{c.last_direction === "out" ? "↩ " : ""}{c.last_body}</div>
              </div>
            </button>
          ))}
        </div>
      </aside>

      <main className="chat-pane">
        {!active ? (
          <div className="no-chat"><MessageCircle size={44} /><p>Selecciona una conversación para ver los mensajes</p></div>
        ) : (
          <>
            <header className="chat-head">
              <div className="conv-avatar lg">{displayName(activeConv || {}).charAt(0).toUpperCase()}</div>
              <div className="flex-1">
                <div className="chat-name">{displayName(activeConv || {})}</div>
                <div className="chat-num">{(active || "").replace("whatsapp:", "")}</div>
              </div>
              <button className={`bot-toggle ${activeConv?.bot_paused ? "paused" : ""}`} onClick={toggleBot} data-testid="toggle-bot-btn">
                {activeConv?.bot_paused ? <><Play size={14} /> Reactivar bot</> : <><Pause size={14} /> Pausar bot</>}
              </button>
              <button className="icon-btn" onClick={() => loadMessages(active)} title="Actualizar"><RefreshCw size={15} /></button>
            </header>

            <div className="msgs" ref={scrollRef} data-testid="messages">
              {messages.map((m, i) => (
                <div key={i} className={`msg-row ${m.direction === "in" ? "in" : "out"}`}>
                  <div className="msg-bubble">
                    {(m.media || []).map((url, j) =>
                      /\.(mp4|mov|webm)$/i.test(url) ? (
                        <video key={j} src={url} controls className="msg-media" />
                      ) : /\.(ogg|oga|mp3|amr|wav|m4a|aac)$/i.test(url) ? (
                        <audio key={j} src={url} controls className="msg-media" />
                      ) : (
                        <img key={j} src={url} alt="media" className="msg-media" />
                      )
                    )}
                    {m.body && <div className="msg-text">{m.body}</div>}
                    <div className="msg-meta">
                      {m.direction === "out" ? <Bot size={11} /> : <User size={11} />}
                      {new Date(m.timestamp).toLocaleString("es-CO", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "2-digit" })}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <form className="reply-bar" onSubmit={sendReply}>
              <input value={reply} onChange={(e) => setReply(e.target.value)} placeholder="Escribe una respuesta…" data-testid="reply-input" />
              <button className="reply-send" disabled={sending} data-testid="reply-send"><Send size={18} /></button>
            </form>
          </>
        )}
      </main>
      <Toaster position="top-right" richColors />
      {showQR && <QRLinkModal onClose={() => setShowQR(false)} />}
    </div>
  );
}

export default function Panel() {
  const [authed, setAuthed] = useState(!!localStorage.getItem(TOKEN_KEY));

  const logout = () => { localStorage.removeItem(TOKEN_KEY); setAuthed(false); };

  useEffect(() => {
    if (!localStorage.getItem(TOKEN_KEY)) return;
    api.get("/auth/me").catch(() => logout());
  }, []);

  return authed ? <Dashboard onLogout={logout} /> : <Login onLogin={() => setAuthed(true)} />;
}
