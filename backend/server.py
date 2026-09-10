from fastapi import FastAPI, APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import Response, PlainTextResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import time
import asyncio
import logging
import httpx
from pathlib import Path
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client as TwilioClient

from bot_messages import build_reply, WELCOME_MESSAGE, SERVICES, AUDIO_HANDOFF
from auth import hash_password, verify_password, create_access_token, require_admin

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', '')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'alfa')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Andrea2026*')

# Servicio Baileys (WhatsApp Web vía QR) — sin Twilio
# En preview corre localmente en :3001. En PRODUCCIÓN, hospédalo externamente
# (Railway/Render/VPS) y define WA_SERVICE_URL con esa URL pública.
WA_SERVICE_URL = os.environ.get('WA_SERVICE_URL', 'http://localhost:3001')
WA_TOKEN = os.environ.get('WA_TOKEN', '')


def _wa_headers():
    return {"x-wa-token": WA_TOKEN} if WA_TOKEN else {}

# Reenganche si el cliente no responde en más de 3 horas
REENGAGE_AFTER_SECONDS = 3 * 60 * 60
REENGAGE_CHECK_INTERVAL = 10 * 60

twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# MongoDB
mongo_client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = mongo_client[os.environ['DB_NAME']]

app = FastAPI(title="Alfa Polarizados - Bot Andrea")
api_router = APIRouter(prefix="/api")

# Estado en memoria: sesión por contacto (saludo, servicio, esperando vehículo, human)
sessions: dict[str, dict] = {}


# ---------- Persistencia de mensajes ----------
async def log_message(contact: str, direction: str, body: str, media=None, name=None, channel_from=None):
    now = datetime.now(timezone.utc).isoformat()
    await db.messages.insert_one({
        "contact": contact,
        "direction": direction,  # "in" | "out"
        "body": body or "",
        "media": media or [],
        "timestamp": now,
    })
    update = {
        "contact": contact,
        "last_body": (body or ("📎 Multimedia" if media else "")),
        "last_direction": direction,
        "last_time": now,
        "updated_at": now,
    }
    if name:
        update["name"] = name
    if channel_from:
        update["channel_from"] = channel_from
    await db.conversations.update_one(
        {"contact": contact},
        {"$set": update, "$setOnInsert": {"created_at": now, "bot_paused": False}},
        upsert=True,
    )


async def wa_send(to: str, text: str = "", media=None) -> dict:
    """Envía un mensaje por el servicio Baileys (WhatsApp Web)."""
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{WA_SERVICE_URL}/send", json={"to": to, "text": text, "media": media or []}, headers=_wa_headers(), timeout=30)
        return r.json()


@api_router.post("/bot/incoming")
async def bot_incoming(payload: dict):
    """Recibe un mensaje entrante desde el servicio Baileys, aplica la lógica del bot y persiste."""
    contact = payload.get("contact")
    name = payload.get("name")
    text = payload.get("text", "")
    is_audio = payload.get("is_audio", False)
    if not contact:
        return {"paused": False, "messages": []}

    session = sessions.setdefault(contact, {})
    if name and not session.get("name"):
        session["name"] = name.split()[0] if name.split() else name
    session["last_activity"] = time.time()
    session["reengaged"] = False

    await log_message(contact, "in", text, name=session.get("name"))

    # Respetar pausa (control humano desde el panel)
    if "human" not in session:
        conv = await db.conversations.find_one({"contact": contact})
        session["human"] = bool(conv and conv.get("bot_paused"))
    if session.get("human"):
        return {"paused": True, "messages": []}

    if is_audio:
        messages = [{"text": AUDIO_HANDOFF, "media": [], "delay": 0}]
    else:
        messages = build_reply(text, session)

    for m in messages:
        await log_message(contact, "out", m.get("text", ""), media=m.get("media") or [])
    return {"paused": False, "messages": messages}


@api_router.get("/wa/status")
async def wa_status(admin: str = Depends(require_admin)):
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{WA_SERVICE_URL}/status", headers=_wa_headers(), timeout=10)
            return r.json()
    except Exception as exc:
        return {"state": "offline", "qr": None, "me": None, "error": str(exc)}


@api_router.post("/wa/logout")
async def wa_logout(admin: str = Depends(require_admin)):
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{WA_SERVICE_URL}/logout", headers=_wa_headers(), timeout=15)
            return r.json()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Servicio WhatsApp no disponible: {exc}")


# ---------- Endpoints públicos ----------
@api_router.get("/")
async def root():
    return {"message": "Bot Andrea de Alfa Polarizados está activo", "status": "ok"}


@api_router.get("/bot/info")
async def bot_info():
    return {
        "name": "Andrea",
        "business": "Alfa Polarizados",
        "location": "Cra. 49 #134A-41 – Barrio Spring, Bogotá",
        "whatsapp_number": TWILIO_WHATSAPP_NUMBER,
        "welcome_message": WELCOME_MESSAGE,
        "services": [
            {"id": "1", "title": "Polarizado y seguridad vehicular", "detail": SERVICES["1"]},
            {"id": "2", "title": "PPF (Protección de pintura)", "detail": SERVICES["2"]},
            {"id": "3", "title": "Película Antiatraco", "detail": SERVICES["3"]},
            {"id": "4", "title": "Polarizado Arquitectónico", "detail": SERVICES["4"]},
            {"id": "5", "title": "Detailing Profesional", "detail": SERVICES["5"]},
        ],
    }


@api_router.post("/bot/preview")
async def bot_preview(payload: dict):
    message = payload.get("message", "")
    reset = payload.get("reset", False)
    contact = payload.get("contact", "preview-user")
    name = payload.get("name")
    if reset or contact not in sessions:
        sessions[contact] = {}
    if name and not sessions[contact].get("name"):
        sessions[contact]["name"] = name
    messages = build_reply(message, sessions[contact])
    return {"messages": messages}


@api_router.post("/whatsapp/webhook")
async def whatsapp_webhook(
    Body: str = Form(default=""),
    From: str = Form(default=""),
    ProfileName: str = Form(default=""),
    NumMedia: str = Form(default="0"),
    MediaContentType0: str = Form(default=""),
    MediaUrl0: str = Form(default=""),
    To: str = Form(default=""),
):
    logger.info("WhatsApp entrante de %s (%s) -> %s: %s [media=%s %s]", From, ProfileName, To, Body, NumMedia, MediaContentType0)

    has_media = NumMedia.isdigit() and int(NumMedia) > 0
    # Ignorar eventos no accionables (ecos de salientes / callbacks de estado sin contenido)
    if not From or (not (Body or "").strip() and not has_media):
        return Response(content=str(MessagingResponse()), media_type="application/xml")

    session = sessions.setdefault(From, {})
    if ProfileName and not session.get("name"):
        session["name"] = ProfileName.split()[0] if ProfileName.split() else ProfileName
    if To:
        session["channel_from"] = To

    session["last_activity"] = time.time()
    session["reengaged"] = False
    session["pending_delayed"] = False

    # Registrar el mensaje entrante
    in_media = [MediaUrl0] if (has_media and MediaUrl0) else []
    await log_message(From, "in", Body, media=in_media, name=session.get("name"), channel_from=To)

    # Si el bot está en pausa (un asesor tomó la conversación), no responder automáticamente
    if "human" not in session:
        conv = await db.conversations.find_one({"contact": From})
        session["human"] = bool(conv and conv.get("bot_paused"))
    if session.get("human"):
        return Response(content=str(MessagingResponse()), media_type="application/xml")

    # Audio → remitir a la asesora
    if has_media and MediaContentType0.startswith("audio"):
        messages = [{"text": AUDIO_HANDOFF, "media": [], "delay": 0}]
    else:
        messages = build_reply(Body, session)

    immediate = [m for m in messages if not m.get("delay")]
    delayed = [m for m in messages if m.get("delay")]

    if delayed and twilio_client and From.startswith("whatsapp:"):
        session["pending_delayed"] = True
        asyncio.create_task(_send_delayed(From, delayed, session))
    elif delayed:
        immediate = immediate + delayed

    twiml = MessagingResponse()
    for m in immediate:
        msg = twiml.message(m.get("text", ""))
        for url in m.get("media") or []:
            msg.media(url)
        await log_message(From, "out", m.get("text", ""), media=m.get("media") or [])
    return Response(content=str(twiml), media_type="application/xml")


async def _send_delayed(contact: str, messages: list, session: dict):
    sender = session.get("channel_from") or f"whatsapp:{TWILIO_WHATSAPP_NUMBER}"
    for m in messages:
        await asyncio.sleep(m.get("delay", 0))
        if not session.get("pending_delayed"):
            return
        try:
            twilio_client.messages.create(
                from_=sender, to=contact, body=m.get("text", ""), media_url=(m.get("media") or None),
            )
            await log_message(contact, "out", m.get("text", ""), media=m.get("media") or [])
        except Exception as exc:
            logger.error("Error enviando mensaje diferido a %s: %s", contact, exc)
    session["pending_delayed"] = False


@api_router.get("/whatsapp/webhook")
async def whatsapp_webhook_health():
    return PlainTextResponse("Webhook de WhatsApp de Andrea activo ✅")


async def _reengagement_loop():
    while True:
        await asyncio.sleep(REENGAGE_CHECK_INTERVAL)
        now = time.time()
        for contact, s in list(sessions.items()):
            if contact.startswith("preview-"):
                continue
            la = s.get("last_activity")
            if not la or s.get("reengaged") or not s.get("greeted") or s.get("human"):
                continue
            if now - la > REENGAGE_AFTER_SECONDS:
                name = s.get("name", "")
                saludo = f"¡Hola de nuevo, {name}! 👋" if name else "¡Hola de nuevo! 👋"
                body = (
                    f"{saludo} Soy Andrea de Alfa Polarizados 🙋‍♀️. Vi que quedó pendiente nuestra "
                    "conversación. ¿Continuamos? 😊 Escribe *volver* para ver el menú o cuéntame en qué te ayudo."
                )
                try:
                    await wa_send(contact, body)
                    s["reengaged"] = True
                    await log_message(contact, "out", body)
                    logger.info("Reenganche enviado a %s", contact)
                except Exception as exc:
                    logger.error("Error reenganchando %s: %s", contact, exc)


# ---------- Autenticación ----------
@api_router.post("/auth/login")
async def login(payload: dict):
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    user = await db.users.find_one({"username": username})
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    token = create_access_token(username)
    return {"token": token, "username": username}


@api_router.get("/auth/me")
async def me(admin: str = Depends(require_admin)):
    return {"username": admin}


# ---------- Panel (protegido) ----------
@api_router.get("/admin/conversations")
async def list_conversations(admin: str = Depends(require_admin)):
    convs = await db.conversations.find({}, {"_id": 0}).sort("updated_at", -1).to_list(500)
    return convs


@api_router.get("/admin/messages")
async def get_messages(contact: str, admin: str = Depends(require_admin)):
    msgs = await db.messages.find({"contact": contact}, {"_id": 0}).sort("timestamp", 1).to_list(2000)
    return msgs


@api_router.post("/admin/reply")
async def admin_reply(payload: dict, admin: str = Depends(require_admin)):
    contact = payload.get("contact")
    body = (payload.get("body") or "").strip()
    if not contact or not body:
        raise HTTPException(status_code=400, detail="Falta contacto o mensaje")

    try:
        result = await wa_send(contact, body)
    except Exception as exc:
        logger.error("Error enviando respuesta manual a %s: %s", contact, exc)
        return {"ok": False, "error": f"No se pudo enviar (WhatsApp no vinculado): {exc}"}

    if not result.get("ok"):
        return {"ok": False, "error": result.get("error") or "No se pudo enviar el mensaje"}

    # Envío exitoso → un asesor toma la conversación (bot en pausa)
    sessions.setdefault(contact, {})["human"] = True
    await db.conversations.update_one({"contact": contact}, {"$set": {"bot_paused": True}})
    await log_message(contact, "out", body)
    return {"ok": True}


@api_router.post("/admin/toggle-bot")
async def toggle_bot(payload: dict, admin: str = Depends(require_admin)):
    contact = payload.get("contact")
    paused = bool(payload.get("paused"))
    if not contact:
        raise HTTPException(status_code=400, detail="Falta contacto")
    sessions.setdefault(contact, {})["human"] = paused
    await db.conversations.update_one({"contact": contact}, {"$set": {"bot_paused": paused}}, upsert=True)
    return {"ok": True, "bot_paused": paused}


# ---------- Startup ----------
async def seed_admin():
    existing = await db.users.find_one({"username": ADMIN_USERNAME})
    if existing is None:
        await db.users.insert_one({
            "username": ADMIN_USERNAME,
            "password_hash": hash_password(ADMIN_PASSWORD),
            "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        logger.info("Admin '%s' creado", ADMIN_USERNAME)
    elif not verify_password(ADMIN_PASSWORD, existing["password_hash"]):
        await db.users.update_one(
            {"username": ADMIN_USERNAME},
            {"$set": {"password_hash": hash_password(ADMIN_PASSWORD)}},
        )
        logger.info("Contraseña del admin '%s' actualizada", ADMIN_USERNAME)


@app.on_event("startup")
async def _on_startup():
    await db.users.create_index("username", unique=True)
    await db.conversations.create_index("contact", unique=True)
    await db.messages.create_index("contact")
    await seed_admin()
    asyncio.create_task(_reengagement_loop())


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
