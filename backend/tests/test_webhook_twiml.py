"""Confirm que el webhook Twilio de Andrea opera correctamente en la preview.

Escenario reportado por el usuario: su dominio de producción está offline y
Twilio está apuntando al dominio de producción. Aquí validamos contra la URL
publica de la preview (REACT_APP_BACKEND_URL) que:
 1) GET /api/whatsapp/webhook -> 200 con mensaje de salud
 2) POST welcome (con ProfileName) -> TwiML XML válido con WELCOME_MESSAGE
    y NUNCA pregunta el nombre.
 3) POST '1' -> TwiML con info del servicio de Polarizado + pregunta marca/modelo.
 4) POST '3' + modelo -> TwiML con imagen (Media) del plan Antiatraco y
    pregunta por la opción preferida.
 5) Persistencia: /api/admin/conversations y /api/admin/messages retornan los
    mensajes registrados (in/out) con token admin.
"""
import os
import re
import uuid
import pytest
import requests


def _load_frontend_url():
    path = "/app/frontend/.env"
    if os.path.exists(path):
        for line in open(path):
            if line.startswith("REACT_APP_BACKEND_URL="):
                return line.split("=", 1)[1].strip()
    return ""


BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or _load_frontend_url()).rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL debe estar configurado"
API = f"{BASE_URL}/api"

ADMIN_USER = "alfa"
ADMIN_PASS = "Andrea2026*"
TWILIO_TO = "whatsapp:+14155238886"


@pytest.fixture(scope="module")
def client():
    return requests.Session()


@pytest.fixture(scope="module")
def admin_token(client):
    r = client.post(f"{API}/auth/login", json={"username": ADMIN_USER, "password": ADMIN_PASS}, timeout=15)
    assert r.status_code == 200, f"login fallo: {r.status_code} {r.text}"
    return r.json()["token"]


@pytest.fixture(scope="module")
def new_contact(client):
    """Contacto único con al menos 1 in + 1 out ya persistidos.

    Idempotente para que funcione bajo xdist (workers separados): siempre
    envía el welcome antes de exponerlo, sin depender del orden de tests.
    """
    contact = f"whatsapp:+57300{uuid.uuid4().hex[:7]}"
    _post_webhook(client, "hola", contact, profile_name="Camila Perez")
    return contact


def _post_webhook(client, body, frm, profile_name="Camila Perez"):
    return client.post(
        f"{API}/whatsapp/webhook",
        data={"Body": body, "From": frm, "To": TWILIO_TO, "ProfileName": profile_name},
        timeout=15,
    )


# ---------- 1) GET health ----------
class TestWebhookHealth:
    def test_get_returns_200_with_health_text(self, client):
        r = client.get(f"{API}/whatsapp/webhook", timeout=15)
        assert r.status_code == 200
        assert "Webhook de WhatsApp de Andrea activo" in r.text


# ---------- 2/3/4) Flujo TwiML end-to-end con mismo contacto ----------
class TestWebhookFlow:
    def test_2_first_message_returns_welcome_twiml(self, client, new_contact):
        r = _post_webhook(client, "hola", new_contact, profile_name="Camila Perez")
        assert r.status_code == 200
        assert "xml" in r.headers.get("content-type", "").lower()
        body = r.text
        assert "<Response>" in body and "<Message>" in body
        # Bienvenida exacta (fragmentos claves)
        assert "Soy Andrea" in body
        assert "Alfa Polarizados" in body
        assert "Cra. 49 #134A-41" in body
        # No debe pedir nombre en ningún paso
        assert "tu nombre" not in body.lower()
        assert "cuál es tu nombre" not in body.lower()

    def test_3_option1_returns_polarizado_info_and_asks_vehicle(self, client, new_contact):
        r = _post_webhook(client, "1", new_contact)
        assert r.status_code == 200
        body = r.text
        assert "<Response>" in body and "<Message>" in body
        # Info del servicio de Polarizado
        assert "Polarizado" in body
        # Debe usar el ProfileName (Camila)
        assert "Camila" in body
        # Pregunta por marca y modelo
        assert "marca y modelo" in body.lower()

    def test_4_option3_antiatraco_after_model_returns_media_and_prompt(self, client):
        # Nuevo contacto para no contaminar el flujo anterior
        contact = f"whatsapp:+57301{uuid.uuid4().hex[:7]}"
        # welcome
        r = _post_webhook(client, "hola", contact, profile_name="Ana Torres")
        assert r.status_code == 200
        # Selecciona 3 (Antiatraco) -> pedirá vehicle
        r = _post_webhook(client, "3", contact, profile_name="Ana Torres")
        assert r.status_code == 200
        assert "marca y modelo" in r.text.lower() or "vehículo" in r.text.lower()
        # Enviar modelo -> debe responder con imagen (Media) del catálogo y pedir opción
        r = _post_webhook(client, "Mazda 3", contact, profile_name="Ana Torres")
        assert r.status_code == 200
        body = r.text
        assert "<Response>" in body and "<Message>" in body
        # TwiML debe contener <Media> con URL de la imagen de planes antiatraco
        assert "<Media>" in body, f"Esperaba <Media> en TwiML: {body[:400]}"
        media_urls = re.findall(r"<Media>([^<]+)</Media>", body)
        assert any("planes" in u.lower() or "cloudinary" in u.lower() for u in media_urls), media_urls
        # Debe preguntar cuál opción prefiere el usuario
        assert "opción" in body.lower() or "prefieres" in body.lower() or "gusta" in body.lower()


# ---------- 5) ProfileName se toma automáticamente ----------
class TestProfileName:
    def test_profile_name_used_never_asks(self, client):
        contact = f"whatsapp:+57302{uuid.uuid4().hex[:7]}"
        r = _post_webhook(client, "hola", contact, profile_name="Sofia Lopez")
        assert r.status_code == 200
        r = _post_webhook(client, "1", contact, profile_name="Sofia Lopez")
        assert "Sofia" in r.text
        assert "tu nombre" not in r.text.lower()


# ---------- 6) Persistencia en Mongo vía panel admin ----------
class TestPersistence:
    def test_admin_conversations_contains_contact(self, client, admin_token, new_contact):
        headers = {"Authorization": f"Bearer {admin_token}"}
        r = client.get(f"{API}/admin/conversations", headers=headers, timeout=15)
        assert r.status_code == 200
        data = r.json()
        # Puede venir como {conversations:[...]} o lista directa
        convs = data.get("conversations") if isinstance(data, dict) else data
        assert isinstance(convs, list)
        contacts = [c.get("contact") for c in convs]
        assert new_contact in contacts, f"El contacto {new_contact} no está en conversations. Muestra: {contacts[:5]}"

    def test_admin_messages_contains_in_and_out(self, client, admin_token, new_contact):
        headers = {"Authorization": f"Bearer {admin_token}"}
        r = client.get(f"{API}/admin/messages", params={"contact": new_contact}, headers=headers, timeout=15)
        assert r.status_code == 200
        data = r.json()
        msgs = data.get("messages") if isinstance(data, dict) else data
        assert isinstance(msgs, list) and len(msgs) > 0
        directions = {m.get("direction") for m in msgs}
        assert "in" in directions, f"No hay mensajes 'in'. dirs={directions}"
        assert "out" in directions, f"No hay mensajes 'out'. dirs={directions}"
        # Debe existir el primer mensaje entrante "hola" y el welcome saliente
        in_bodies = [m.get("body", "") for m in msgs if m.get("direction") == "in"]
        out_bodies = [m.get("body", "") for m in msgs if m.get("direction") == "out"]
        assert any("hola" in b.lower() for b in in_bodies)
        assert any("Soy Andrea" in b for b in out_bodies)
        # Verifica que el _id de Mongo NO se filtra en la respuesta
        for m in msgs:
            assert "_id" not in m, "Mongo _id no debe estar en la respuesta"
