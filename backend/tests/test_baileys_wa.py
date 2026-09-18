"""Backend tests for Baileys (WhatsApp Web) integration and /api/bot/incoming flow.

Cubre:
- GET /api/wa/status (auth requerido, estado qr/connecting)
- POST /api/bot/incoming (sin auth): bienvenida usa 'name', no pide nombre
- Flujos: opcion 1 (polarizado con saludo por nombre), opcion 3 (antiatraco con media),
  opcion 2 PPF (submenu proteger)
- Persistencia (mensajes in/out en /api/admin/conversations y /api/admin/messages)
- Pausa / control humano via /api/admin/toggle-bot
- /api/admin/reply: manejo controlado (200 ok:false) cuando Baileys no está vinculado,
  y NO pausa el bot en ese caso
- POST /api/wa/logout: proxy Ok o 503 controlado
"""
import os
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


@pytest.fixture(scope="module")
def client():
    return requests.Session()


@pytest.fixture(scope="module")
def auth_headers(client):
    r = client.post(f"{API}/auth/login",
                    json={"username": "alfa", "password": "Andrea2026*"},
                    timeout=15)
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _unique_contact():
    # Number-style contacts (Baileys jid sin '@s.whatsapp.net' es contact)
    return f"5730012{uuid.uuid4().hex[:5]}"


# ---------- /api/wa/status ----------
class TestWaStatus:
    def test_status_requires_auth(self, client):
        r = client.get(f"{API}/wa/status", timeout=15)
        assert r.status_code == 401

    def test_status_with_auth_returns_state(self, client, auth_headers):
        r = client.get(f"{API}/wa/status", headers=auth_headers, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert "state" in data
        # Baileys no vinculado: state debe ser qr | connecting | disconnected | offline
        assert data["state"] in ("qr", "connecting", "connected", "disconnected", "offline"), data
        assert "qr" in data
        # Si state == qr, qr debe ser un data URL
        if data["state"] == "qr" and data.get("qr"):
            assert data["qr"].startswith("data:image/"), data["qr"][:60]


# ---------- /api/wa/logout ----------
class TestWaLogout:
    def test_logout_requires_auth(self, client):
        r = client.post(f"{API}/wa/logout", timeout=15)
        assert r.status_code == 401

    def test_logout_with_auth(self, client, auth_headers):
        r = client.post(f"{API}/wa/logout", headers=auth_headers, timeout=20)
        # Servicio Node arriba: debería devolver 200 ok:true; si no está, 503 controlado
        assert r.status_code in (200, 503), r.text
        if r.status_code == 200:
            assert r.json().get("ok") is True


# ---------- /api/bot/incoming: bienvenida usa 'name' ----------
class TestBotIncomingWelcome:
    def test_new_contact_welcome_uses_name_no_ask(self, client):
        contact = _unique_contact()
        r = client.post(f"{API}/bot/incoming",
                        json={"contact": contact, "name": "Camila Perez", "text": "hola"},
                        timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["paused"] is False
        msgs = data["messages"]
        assert len(msgs) >= 1
        text = "\n".join(m["text"] for m in msgs)
        assert "Soy Andrea" in text
        # NUNCA debe preguntar el nombre
        assert "tu nombre" not in text.lower()
        assert "cuál es tu nombre" not in text.lower()

    def test_incoming_no_contact_returns_empty(self, client):
        r = client.post(f"{API}/bot/incoming", json={"text": "hola"}, timeout=10)
        assert r.status_code == 200
        assert r.json() == {"paused": False, "messages": []}


# ---------- Flujos con nombre (opciones) ----------
class TestBotIncomingFlows:
    def _send(self, client, contact, text, name="Camila"):
        r = client.post(f"{API}/bot/incoming",
                        json={"contact": contact, "name": name, "text": text},
                        timeout=15)
        assert r.status_code == 200, r.text
        return r.json()

    def test_option_1_polarizado_greets_by_name(self, client):
        c = _unique_contact()
        self._send(client, c, "hola", name="Camila Perez")
        data = self._send(client, c, "1", name="Camila Perez")
        text = "\n".join(m["text"] for m in data["messages"])
        assert "Camila" in text
        assert "marca y modelo" in text.lower()

    def test_option_3_antiatraco_has_media(self, client):
        c = _unique_contact()
        self._send(client, c, "hola", name="Ana Gomez")
        data = self._send(client, c, "3", name="Ana Gomez")
        # Tras elegir '3' debe pedir modelo o mostrar info con media
        # Enviamos modelo
        data2 = self._send(client, c, "Toyota Corolla", name="Ana Gomez")
        msgs = data2["messages"]
        media = []
        for m in msgs:
            media.extend(m.get("media") or [])
        text = "\n".join(m["text"] for m in msgs)
        assert media, f"Se esperaba media (imagen antiatraco). msgs={msgs}"
        # Debe preguntar por opciones (agendar/asesor/etc)
        assert "?" in text or "opción" in text.lower() or "cotiza" in text.lower() or "agendar" in text.lower()

    def test_option_2_ppf_submenu(self, client):
        c = _unique_contact()
        self._send(client, c, "hola", name="Luis")
        self._send(client, c, "2", name="Luis")
        data = self._send(client, c, "Mazda CX-5", name="Luis")
        text = "\n".join(m["text"] for m in data["messages"])
        assert "Protección Total" in text
        assert "Pintura Completa" in text
        assert "Piano Black" in text


# ---------- Persistencia ----------
class TestPersistenceIncoming:
    def test_incoming_persists_and_visible_in_admin(self, client, auth_headers):
        c = _unique_contact()
        r = client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Persist Tester", "text": "hola"},
                        timeout=15)
        assert r.status_code == 200
        # conversations
        rc = client.get(f"{API}/admin/conversations", headers=auth_headers, timeout=15)
        assert rc.status_code == 200
        conv = next((x for x in rc.json() if x["contact"] == c), None)
        assert conv is not None
        assert conv.get("name")
        assert conv.get("last_body")
        # messages
        rm = client.get(f"{API}/admin/messages", headers=auth_headers,
                        params={"contact": c}, timeout=15)
        assert rm.status_code == 200
        dirs = [m["direction"] for m in rm.json()]
        assert "in" in dirs and "out" in dirs
        assert rm.json()[0]["direction"] == "in"
        assert rm.json()[0]["body"] == "hola"


# ---------- Pausa (control humano) ----------
class TestPauseIncoming:
    def test_pause_and_resume_on_incoming(self, client, auth_headers):
        c = _unique_contact()
        # seed
        client.post(f"{API}/bot/incoming",
                    json={"contact": c, "name": "Pause Test", "text": "hola"}, timeout=15)
        # pause
        rp = client.post(f"{API}/admin/toggle-bot", headers=auth_headers,
                         json={"contact": c, "paused": True}, timeout=15)
        assert rp.status_code == 200
        assert rp.json()["bot_paused"] is True
        # next incoming -> paused:true, messages:[]
        r = client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Pause Test", "text": "1"},
                        timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert data["paused"] is True
        assert data["messages"] == []
        # resume
        rr = client.post(f"{API}/admin/toggle-bot", headers=auth_headers,
                         json={"contact": c, "paused": False}, timeout=15)
        assert rr.status_code == 200
        assert rr.json()["bot_paused"] is False
        r2 = client.post(f"{API}/bot/incoming",
                         json={"contact": c, "name": "Pause Test", "text": "hola"},
                         timeout=15)
        assert r2.status_code == 200
        assert r2.json()["paused"] is False
        assert len(r2.json()["messages"]) >= 1


# ---------- Fallback amable (nunca "No entendí") ----------
class TestKindFallback:
    def test_fallback_is_kind_not_confused(self, client):
        c = _unique_contact()
        client.post(f"{API}/bot/incoming",
                    json={"contact": c, "name": "Rosa", "text": "hola"}, timeout=15)
        r = client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Rosa", "text": "xyzabc"}, timeout=15)
        text = "\n".join(m["text"] for m in r.json()["messages"])
        assert "no entendí" not in text.lower()
        assert "😊" in text or "gusto" in text.lower()
        # sigue ofreciendo las opciones (continuidad)
        assert "opciones" in text.lower() or "servicio" in text.lower()

    def test_detailing_schedule_pauses_bot(self, client, auth_headers):
        c = _unique_contact()
        for txt in ["hola", "5", "Renault Duster"]:
            client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Rosa", "text": txt}, timeout=15)
        # Cualquier respuesta ("Ok") -> asesora + pausa
        r = client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Rosa", "text": "Ok"}, timeout=15)
        text = "\n".join(m["text"] for m in r.json()["messages"])
        assert "asesora" in text.lower()
        rc = client.get(f"{API}/admin/conversations", headers=auth_headers, timeout=15)
        conv = next((x for x in rc.json() if x["contact"] == c), None)
        assert conv is not None and conv.get("bot_paused") is True


# ---------- Continuidad con audio (siempre pasa a asesora) ----------
class TestAudioHandoff:
    def test_audio_pauses_bot_mid_flow(self, client, auth_headers):
        c = _unique_contact()
        client.post(f"{API}/bot/incoming",
                    json={"contact": c, "name": "Pedro", "text": "hola"}, timeout=15)
        client.post(f"{API}/bot/incoming",
                    json={"contact": c, "name": "Pedro", "text": "1"}, timeout=15)
        # Cliente responde con AUDIO en medio del flujo -> handoff + pausa
        r = client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Pedro", "text": "", "is_audio": True}, timeout=15)
        assert r.status_code == 200
        text = "\n".join(m["text"] for m in r.json()["messages"])
        assert "asesora" in text.lower() or "voz" in text.lower()
        rc = client.get(f"{API}/admin/conversations", headers=auth_headers, timeout=15)
        conv = next((x for x in rc.json() if x["contact"] == c), None)
        assert conv is not None and conv.get("bot_paused") is True
        r2 = client.post(f"{API}/bot/incoming",
                         json={"contact": c, "name": "Pedro", "text": "hola"}, timeout=15)
        assert r2.json()["paused"] is True and r2.json()["messages"] == []


# ---------- Handoff automático tras agendar (Opciones 1 y 2) ----------
class TestScheduleHandoff:
    def test_opt1_schedule_pauses_bot(self, client, auth_headers):
        c = _unique_contact()
        for txt in ["hola", "1", "Mazda 3", "cerámico"]:
            client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Ana", "text": txt}, timeout=15)
        r = client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Ana", "text": "mañana a las 10am"}, timeout=15)
        text = "\n".join(m["text"] for m in r.json()["messages"])
        assert "asesora" in text.lower()
        assert "mañana a las 10am" in text
        rc = client.get(f"{API}/admin/conversations", headers=auth_headers, timeout=15)
        conv = next((x for x in rc.json() if x["contact"] == c), None)
        assert conv is not None and conv.get("bot_paused") is True
        r2 = client.post(f"{API}/bot/incoming",
                         json={"contact": c, "name": "Ana", "text": "hola"}, timeout=15)
        assert r2.json()["paused"] is True and r2.json()["messages"] == []

    def test_ppf_ambiguous_brand_continues_flow(self, client):
        c = _unique_contact()
        client.post(f"{API}/bot/incoming",
                    json={"contact": c, "name": "Luis", "text": "hola"}, timeout=15)
        client.post(f"{API}/bot/incoming",
                    json={"contact": c, "name": "Luis", "text": "2"}, timeout=15)
        # Marca ambigua ("Mazda" sin modelo) -> debe continuar el flujo, sin pedir serie
        r = client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Luis", "text": "Mazda"}, timeout=15)
        text = "\n".join(m["text"] for m in r.json()["messages"])
        assert "Protección Total" in text and "Piano Black" in text

    def test_ppf_schedule_pauses_bot(self, client, auth_headers):
        c = _unique_contact()
        for txt in ["hola", "2", "Mazda", "1"]:
            client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Luis", "text": txt}, timeout=15)
        # Cualquier respuesta a "¿Agendamos?" -> asesora + pausa
        r = client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Luis", "text": "el lunes en la tarde"}, timeout=15)
        text = "\n".join(m["text"] for m in r.json()["messages"])
        assert "asesora" in text.lower()
        rc = client.get(f"{API}/admin/conversations", headers=auth_headers, timeout=15)
        conv = next((x for x in rc.json() if x["contact"] == c), None)
        assert conv is not None and conv.get("bot_paused") is True
        r2 = client.post(f"{API}/bot/incoming",
                         json={"contact": c, "name": "Luis", "text": "?"}, timeout=15)
        assert r2.json()["paused"] is True and r2.json()["messages"] == []


# ---------- Handoff automático (Opción 3) ----------
class TestAntiatracoHandoff:
    def test_antiatraco_preference_pauses_bot(self, client, auth_headers):
        c = _unique_contact()
        r = client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Sofia", "text": "hola"}, timeout=15)
        client.post(f"{API}/bot/incoming",
                    json={"contact": c, "name": "Sofia", "text": "3"}, timeout=15)
        client.post(f"{API}/bot/incoming",
                    json={"contact": c, "name": "Sofia", "text": "Renault Duster"}, timeout=15)
        # Preferencia -> mensaje de asesora + pausa del bot
        r = client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Sofia", "text": "Cerámico"}, timeout=15)
        assert r.status_code == 200
        text = "\n".join(m["text"] for m in r.json()["messages"])
        assert "asesora" in text.lower()
        # bot_paused en DB
        rc = client.get(f"{API}/admin/conversations", headers=auth_headers, timeout=15)
        conv = next((x for x in rc.json() if x["contact"] == c), None)
        assert conv is not None
        assert conv.get("bot_paused") is True
        # Siguiente mensaje -> pausado, sin respuesta automática
        r2 = client.post(f"{API}/bot/incoming",
                         json={"contact": c, "name": "Sofia", "text": "hola?"}, timeout=15)
        assert r2.json()["paused"] is True
        assert r2.json()["messages"] == []


# ---------- Handoff automático (Opción 4) ----------
class TestArchHandoff:
    def test_arch_measures_pauses_bot(self, client, auth_headers):
        c = _unique_contact()
        for txt in ["hola", "4", "Bogotá", "Apartamento"]:
            client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Maria", "text": txt}, timeout=15)
        r = client.post(f"{API}/bot/incoming",
                        json={"contact": c, "name": "Maria", "text": "3 m x 2 m"}, timeout=15)
        assert r.status_code == 200
        text = "\n".join(m["text"] for m in r.json()["messages"])
        assert "asesora" in text.lower()
        assert "Bogotá" in text and "Apartamento" in text and "3 m x 2 m" in text
        rc = client.get(f"{API}/admin/conversations", headers=auth_headers, timeout=15)
        conv = next((x for x in rc.json() if x["contact"] == c), None)
        assert conv is not None and conv.get("bot_paused") is True
        r2 = client.post(f"{API}/bot/incoming",
                         json={"contact": c, "name": "Maria", "text": "?"}, timeout=15)
        assert r2.json()["paused"] is True
        assert r2.json()["messages"] == []


# ---------- /api/admin/reply (Baileys no vinculado) ----------
class TestAdminReplyBaileys:
    def test_reply_controlled_when_not_linked(self, client, auth_headers):
        c = _unique_contact()
        client.post(f"{API}/bot/incoming",
                    json={"contact": c, "name": "Reply Test", "text": "hola"}, timeout=15)
        r = client.post(f"{API}/admin/reply", headers=auth_headers,
                        json={"contact": c, "body": "Hola desde panel"}, timeout=30)
        # NO debe crashear: 200 ok:false (Baileys sin vincular)
        assert r.status_code == 200, f"expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data.get("ok") is False
        assert data.get("error")
        # No debe pausar el bot cuando falla
        rc = client.get(f"{API}/admin/conversations", headers=auth_headers, timeout=15)
        conv = next((x for x in rc.json() if x["contact"] == c), None)
        assert conv is not None
        assert conv.get("bot_paused") is not True

    def test_reply_missing_fields_400(self, client, auth_headers):
        r = client.post(f"{API}/admin/reply", headers=auth_headers,
                        json={"contact": "", "body": ""}, timeout=15)
        assert r.status_code == 400
