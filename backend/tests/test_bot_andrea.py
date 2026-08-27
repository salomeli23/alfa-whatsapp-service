"""Backend tests para el bot Andrea de Alfa Polarizados."""
import os
import re
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # fallback local
    BASE_URL = "http://localhost:8001"

API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    return s


# ---------- Health / info ----------
class TestHealth:
    def test_root_status(self, client):
        r = client.get(f"{API}/")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"
        assert "Andrea" in data.get("message", "")

    def test_bot_info(self, client):
        r = client.get(f"{API}/bot/info")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Andrea"
        assert "Cra. 49 #134A-41" in data["location"]
        assert "whatsapp_number" in data
        assert isinstance(data["services"], list)
        assert len(data["services"]) == 5
        ids = [s["id"] for s in data["services"]]
        assert ids == ["1", "2", "3", "4", "5"]
        # verifica que welcome contiene Andrea y opciones
        wm = data["welcome_message"]
        assert "Soy Andrea" in wm
        for n in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]:
            assert n in wm


# ---------- Webhook TwiML ----------
class TestWebhook:
    def _post(self, client, body, frm):
        return client.post(
            f"{API}/whatsapp/webhook",
            data={"Body": body, "From": frm},
        )

    def test_first_message_returns_welcome_twiml(self, client):
        frm = f"whatsapp:+57300{uuid.uuid4().hex[:7]}"
        r = self._post(client, "hola", frm)
        assert r.status_code == 200
        assert "xml" in r.headers.get("content-type", "").lower()
        body = r.text
        assert body.startswith("<?xml") or body.startswith("<Response")
        assert "<Response>" in body and "<Message>" in body
        assert "Soy Andrea" in body
        for n in ["1", "2", "3", "4", "5"]:
            assert f"{n}\ufe0f\u20e3" in body  # keycap emoji

    @pytest.mark.parametrize("opt", ["1", "2", "3", "4", "5"])
    def test_service_option_returns_detail_and_asesor(self, client, opt):
        frm = f"whatsapp:+57301{uuid.uuid4().hex[:7]}"
        # primer mensaje = welcome
        self._post(client, "hi", frm)
        r = self._post(client, opt, frm)
        assert r.status_code == 200
        body = r.text
        assert "<Response>" in body
        # texto de asesor humano presente
        assert "ASESOR" in body
        # verifica keywords específicos por opción
        markers = {
            "1": "Polarizado y Seguridad Vehicular",
            "2": "PPF",
            "3": "Antiatraco",
            "4": "Arquitectónico",
            "5": "Detailing",
        }
        assert markers[opt] in body

    def test_invalid_message_repeats_menu(self, client):
        frm = f"whatsapp:+57302{uuid.uuid4().hex[:7]}"
        self._post(client, "hi", frm)  # welcome
        r = self._post(client, "xyz", frm)
        assert r.status_code == 200
        body = r.text
        assert "No entendí" in body
        assert "Soy Andrea" in body

    def test_invalid_number_9_repeats_menu(self, client):
        frm = f"whatsapp:+57303{uuid.uuid4().hex[:7]}"
        self._post(client, "hi", frm)
        r = self._post(client, "9", frm)
        body = r.text
        assert "No entendí" in body

    def test_asesor_handoff(self, client):
        frm = f"whatsapp:+57304{uuid.uuid4().hex[:7]}"
        self._post(client, "hi", frm)
        r = self._post(client, "asesor", frm)
        body = r.text
        assert "asesor de Alfa Polarizados" in body or "un asesor" in body.lower()
        assert "Gracias por confiar" in body


# ---------- Preview endpoint ----------
class TestPreview:
    def test_preview_reset_returns_welcome(self, client):
        r = client.post(
            f"{API}/bot/preview",
            json={"message": "hola", "contact": f"prev-{uuid.uuid4().hex}", "reset": True},
        )
        assert r.status_code == 200
        data = r.json()
        assert "reply" in data
        assert "Soy Andrea" in data["reply"]

    def test_preview_new_contact_returns_welcome(self, client):
        r = client.post(
            f"{API}/bot/preview",
            json={"message": "1", "contact": f"prev-{uuid.uuid4().hex}"},
        )
        data = r.json()
        assert "Soy Andrea" in data["reply"]

    def test_preview_service_flow(self, client):
        c = f"prev-{uuid.uuid4().hex}"
        # reset welcome
        client.post(f"{API}/bot/preview", json={"message": "hi", "contact": c, "reset": True})
        r = client.post(f"{API}/bot/preview", json={"message": "2", "contact": c})
        data = r.json()
        assert "PPF" in data["reply"]
        assert "ASESOR" in data["reply"]

    def test_preview_invalid_after_seen(self, client):
        c = f"prev-{uuid.uuid4().hex}"
        client.post(f"{API}/bot/preview", json={"message": "hi", "contact": c, "reset": True})
        r = client.post(f"{API}/bot/preview", json={"message": "zzz", "contact": c})
        assert "No entendí" in r.json()["reply"]

    def test_preview_asesor(self, client):
        c = f"prev-{uuid.uuid4().hex}"
        client.post(f"{API}/bot/preview", json={"message": "hi", "contact": c, "reset": True})
        r = client.post(f"{API}/bot/preview", json={"message": "asesor", "contact": c})
        assert "Gracias por confiar" in r.json()["reply"]
