import { useEffect, useRef, useState } from "react";
import "@/App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Panel from "@/Panel";
import {
  Car,
  Shield,
  Siren,
  Building2,
  Sparkles,
  MapPin,
  Send,
  RotateCcw,
  MessageCircle,
  CheckCircle2,
  LayoutDashboard,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SERVICE_META = [
  { id: "1", icon: Car, title: "Polarizado y Seguridad Vehicular", tag: "Rechazo de calor · UV · Privacidad" },
  { id: "2", icon: Shield, title: "PPF · Protección de Pintura", tag: "Piano Black · Autorreparable" },
  { id: "3", icon: Siren, title: "Película Antiatraco", tag: "Seguridad · Anti-impacto" },
  { id: "4", icon: Building2, title: "Polarizado Arquitectónico", tag: "Hogar · Oficina · Fachadas" },
  { id: "5", icon: Sparkles, title: "Detailing Profesional", tag: "Cerámico · Pulido · Interiores" },
];

const CONTACT_ID = "web-preview-" + Math.random().toString(36).slice(2, 8);

function ChatSimulator() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const [userName, setUserName] = useState("");
  const scrollRef = useRef(null);

  const scrollToBottom = () => {
    setTimeout(() => {
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }, 60);
  };

  const sendMessage = async (text, reset = false) => {
    if (!text.trim() && !reset) return;
    if (!reset) {
      setMessages((m) => [...m, { role: "user", text }]);
    }
    setInput("");
    setLoading(true);
    scrollToBottom();
    try {
      const res = await axios.post(`${API}/bot/preview`, {
        message: text,
        contact: CONTACT_ID,
        reset,
        name: userName || "Cliente",
      });
      const botMsgs = (res.data.messages || []).map((m) => ({
        role: "bot",
        text: m.text,
        media: m.media || [],
        delay: m.delay || 0,
      }));
      const immediate = botMsgs.filter((m) => !m.delay);
      const delayed = botMsgs.filter((m) => m.delay);
      setMessages((m) => [...m, ...immediate]);
      if (delayed.length > 0) {
        // Simula el envío diferido de la pregunta tras cargar/ver el video
        let acc = 0;
        delayed.forEach((dm, idx) => {
          const uiDelay = Math.min(dm.delay, 4); // acortado para la demo
          acc += uiDelay;
          setTimeout(() => {
            setMessages((m) => [...m, dm]);
            if (idx === delayed.length - 1) setLoading(false);
            scrollToBottom();
          }, acc * 1000);
        });
      } else {
        setLoading(false);
      }
    } catch (e) {
      setMessages((m) => [...m, { role: "bot", text: "⚠️ Error de conexión con el bot." }]);
      setLoading(false);
    } finally {
      scrollToBottom();
    }
  };

  const startChat = async () => {
    setMessages([]);
    setStarted(true);
    await sendMessage("Hola", true);
  };

  const resetChat = () => {
    setMessages([]);
    setStarted(false);
  };

  useEffect(scrollToBottom, [messages, loading]);

  return (
    <div className="phone-frame" data-testid="chat-simulator">
      <div className="phone-topbar">
        <div className="avatar-a">A</div>
        <div className="flex-1">
          <div className="text-white font-semibold leading-tight">Andrea · Alfa Polarizados</div>
          <div className="text-[11px] text-emerald-300 flex items-center gap-1">
            <span className="dot-online" /> en línea
          </div>
        </div>
        <button data-testid="reset-chat-btn" onClick={resetChat} className="icon-btn" title="Reiniciar">
          <RotateCcw size={16} />
        </button>
      </div>

      <div ref={scrollRef} className="chat-body" data-testid="chat-body">
        {!started && (
          <div className="h-full flex flex-col items-center justify-center text-center px-6 gap-4">
            <MessageCircle className="text-emerald-400" size={40} />
            <p className="text-zinc-300 text-sm">
              Prueba la conversación real del bot. En WhatsApp, Andrea toma tu nombre automáticamente;
              aquí escríbelo para simularlo.
            </p>
            <input
              data-testid="name-input"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              placeholder="Tu nombre (ej. Camila)"
              className="wa-input !bg-white/5 !rounded-full text-center max-w-[220px]"
            />
            <button data-testid="start-chat-btn" onClick={startChat} className="wa-btn">
              Iniciar chat
            </button>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "bubble-row end" : "bubble-row start"}>
            <div className={m.role === "user" ? "bubble user" : "bubble bot"} data-testid={`msg-${m.role}-${i}`}>
              {m.media && m.media.length > 0 && (
                <div className="bubble-media">
                  {m.media.map((url, j) =>
                    /\.(mp4|mov|webm)$/i.test(url) ? (
                      <video key={j} src={url} controls playsInline className="media-el" data-testid={`media-video-${i}-${j}`} />
                    ) : (
                      <img key={j} src={url} alt="media" className="media-el" data-testid={`media-img-${i}-${j}`} />
                    )
                  )}
                </div>
              )}
              {m.text}
            </div>
          </div>
        ))}

        {loading && (
          <div className="bubble-row start">
            <div className="bubble bot typing">
              <span /><span /><span />
            </div>
          </div>
        )}
      </div>

      {started && (
        <div className="chat-input">
          <div className="quick-replies">
            {["1", "2", "3", "4", "5", "asesor", "volver"].map((q) => (
              <button
                key={q}
                data-testid={`quick-${q}`}
                onClick={() => sendMessage(q)}
                className="chip"
                disabled={loading}
              >
                {q}
              </button>
            ))}
          </div>
          <form
            className="flex items-center gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              sendMessage(input);
            }}
          >
            <input
              data-testid="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Escribe un mensaje…"
              className="wa-input"
            />
            <button data-testid="send-btn" type="submit" className="send-btn" disabled={loading}>
              <Send size={18} />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

function Home() {
  const [info, setInfo] = useState(null);

  useEffect(() => {
    axios
      .get(`${API}/bot/info`)
      .then((r) => setInfo(r.data))
      .catch((e) => console.error(e));
  }, []);

  return (
    <div className="page" data-testid="home-page">
      {/* Ambient glow */}
      <div className="glow glow-1" />
      <div className="glow glow-2" />

      <header className="nav">
        <div className="brand" data-testid="brand-logo">
          <span className="brand-mark">α</span>
          <div className="leading-none">
            <div className="brand-name">ALFA</div>
            <div className="brand-sub">POLARIZADOS</div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Link className="wa-cta panel-cta" to="/panel" data-testid="nav-panel-btn">
            <LayoutDashboard size={16} /> Panel
          </Link>
          <a
            className="wa-cta"
            href={`https://wa.me/${(info?.whatsapp_number || "").replace(/[^\d]/g, "")}`}
            target="_blank"
            rel="noopener noreferrer"
            data-testid="nav-whatsapp-btn"
          >
            <MessageCircle size={16} /> WhatsApp
          </a>
        </div>
      </header>

      <section className="hero">
        <div className="hero-left">
          <div className="pill" data-testid="hero-pill">
            <span className="dot-online" /> Bot Andrea · Atención automática 24/7
          </div>
          <h1 className="hero-title">
            Protección y estilo <span className="accent">de otro nivel</span> para tu vehículo.
          </h1>
          <p className="hero-desc">
            Soy <b>Andrea</b> 🙋‍♀️, tu asesora virtual de Alfa Polarizados. Escríbeme por WhatsApp y te
            ayudo a elegir el servicio perfecto: polarizado, PPF, película antiatraco, arquitectónico y
            detailing profesional.
          </p>
          <div className="hero-loc" data-testid="hero-location">
            <MapPin size={16} className="text-emerald-400" />
            Cra. 49 #134A-41 – Barrio Spring, Bogotá
          </div>
          <div className="hero-actions">
            <a
              className="btn-primary"
              href={`https://wa.me/${(info?.whatsapp_number || "").replace(/[^\d]/g, "")}`}
              target="_blank"
              rel="noopener noreferrer"
              data-testid="hero-whatsapp-btn"
            >
              <MessageCircle size={18} /> Escribir a Andrea
            </a>
            <a className="btn-ghost" href="#servicios" data-testid="hero-services-btn">
              Ver servicios
            </a>
          </div>
          <div className="trust">
            {["Materiales de alta calidad", "Procesos profesionales", "Garantía certificada"].map((t) => (
              <div key={t} className="trust-item">
                <CheckCircle2 size={15} className="text-emerald-400" /> {t}
              </div>
            ))}
          </div>
        </div>

        <div className="hero-right">
          <ChatSimulator />
        </div>
      </section>

      <section id="servicios" className="services" data-testid="services-section">
        <div className="section-head">
          <span className="eyebrow">NUESTROS SERVICIOS</span>
          <h2 className="section-title">Cinco formas de elevar tu vehículo</h2>
        </div>
        <div className="services-grid">
          {SERVICE_META.map((s, i) => {
            const Icon = s.icon;
            return (
              <div key={s.id} className="service-card" data-testid={`service-card-${s.id}`} style={{ animationDelay: `${i * 80}ms` }}>
                <div className="service-num">{s.id}</div>
                <Icon size={26} className="service-icon" />
                <h3 className="service-title">{s.title}</h3>
                <p className="service-tag">{s.tag}</p>
              </div>
            );
          })}
        </div>
      </section>

      <footer className="footer" data-testid="footer">
        <div className="footer-inner">
          <div className="brand">
            <span className="brand-mark">α</span>
            <div className="leading-none">
              <div className="brand-name">ALFA POLARIZADOS</div>
              <div className="brand-sub">Bogotá · Barrio Spring</div>
            </div>
          </div>
          <div className="footer-meta">
            <div className="flex items-center gap-2">
              <MapPin size={14} className="text-emerald-400" /> Cra. 49 #134A-41 – Barrio Spring, Bogotá
            </div>
            <div className="opacity-60 mt-2 text-xs">Bot Andrea impulsado por Twilio WhatsApp</div>
          </div>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/panel" element={<Panel />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
