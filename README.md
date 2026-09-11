# Alfa Polarizados — Servicio WhatsApp (Baileys)

Microservicio Node.js que vincula WhatsApp Web por **QR** y conecta el bot "Andrea".
Debe correr como un **proceso persistente** (mantiene el socket de WhatsApp).

⚠️ El deploy de Emergent NO ejecuta este servicio (solo corre FastAPI + React + Mongo).
En **producción** hospédalo aparte (Railway / Render / Fly.io / VPS) y apunta el backend a él.

## Variables de entorno
| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `PORT` | Puerto HTTP (Railway/Render lo inyectan) | `3001` |
| `BACKEND_URL` | URL pública del backend FastAPI de Emergent | `https://alfapolarizados.online` |
| `WA_TOKEN` | Token secreto compartido con el backend (recomendado) | `un-token-largo` |
| `AUTH_DIR` | Carpeta persistente para la sesión de WhatsApp | `/data/auth` |

## Endpoints
- `GET /status` → `{ state, qr, me }` (state: connecting|qr|connected|disconnected)
- `POST /send` → `{ to, text, media[] }`
- `POST /logout` → cierra sesión y regenera QR

Si defines `WA_TOKEN`, todas las peticiones requieren el header `x-wa-token: <WA_TOKEN>`.

## Correr local
```bash
yarn install
BACKEND_URL=http://localhost:8001 node index.js
```

## Desplegar en Railway/Render
1. Sube esta carpeta a un repo (o subcarpeta).
2. Servicio Node: build `yarn install`, start `node index.js`.
3. Configura variables: `BACKEND_URL` (tu backend de Emergent), `WA_TOKEN`.
4. Añade un **volumen persistente** montado en `AUTH_DIR` (para no reescanear el QR).
5. Copia la URL pública del servicio.

## Conectar con el backend (Emergent)
En `backend/.env` define:
```
WA_SERVICE_URL=https://TU-SERVICIO-BAILEYS.up.railway.app
WA_TOKEN=el-mismo-token
```
Reinicia el backend. En el panel → "Vincular WhatsApp (QR)" verás el QR del servicio externo.
