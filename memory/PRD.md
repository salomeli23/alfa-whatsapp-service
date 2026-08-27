# PRD — Bot de WhatsApp "Andrea" · Alfa Polarizados

## Problema original
Construir un bot de WhatsApp para Alfa Polarizados usando Twilio. El bot ("Andrea")
atiende clientes que escriben al WhatsApp del negocio. Primer mensaje → bienvenida
exacta con menú de 5 servicios. Respuesta 1–5 → info detallada del servicio. Otra
entrada → repetir menú amablemente. Credenciales Twilio como variables de entorno.

## Decisiones del usuario
- Textos de servicio: genéricos/profesionales de ejemplo (editables).
- Sin dashboard de administración.
- Sin persistencia en base de datos.
- Tras mostrar un servicio: ofrecer hablar con un asesor humano / dejar datos.
- Twilio en modo Sandbox.

## Arquitectura
- Backend FastAPI (`/app/backend/server.py`) con rutas prefijadas `/api`.
- Lógica del bot en `/app/backend/bot_messages.py` (`build_reply`, WELCOME_MESSAGE, SERVICES).
- Webhook `POST /api/whatsapp/webhook` recibe Body/From de Twilio y responde TwiML XML.
- Estado en memoria `seen_contacts` para detectar el primer mensaje de cada número.
- Frontend React: landing branding + simulador de chat estilo WhatsApp (`/api/bot/preview`).
- Credenciales Twilio en `/app/backend/.env` (SID, AUTH_TOKEN, WHATSAPP_NUMBER).

## Endpoints
- GET  /api/                 estado del bot
- GET  /api/bot/info         datos del negocio + 5 servicios
- POST /api/bot/preview      simulador { message, contact, reset } → { reply }
- POST /api/whatsapp/webhook webhook Twilio (Body, From) → TwiML XML
- GET  /api/whatsapp/webhook health check

## Implementado (2026-06)
- ✅ Mensaje de bienvenida EXACTO en primer contacto.
- ✅ Nombre automático desde el perfil de WhatsApp (ProfileName); nunca se pregunta.
- ✅ Saludo con el nombre tras elegir opción del menú.
- ✅ Hint global "volver" para regresar al menú en cualquier momento.
- ✅ Opción 1: 3 planes (imágenes) + 3 videos y pregunta cuál plan gustó.
- ✅ Opción 2 (PPF): sin línea de precio; submenú (Protección Total, Pintura Completa, Piano Black, Partes Acrílicas) con catálogo Piano Black de 10 modelos (imagen + precio + piezas) y detección automática del modelo.
- ✅ Opción 3 y 5: info + marca/modelo + pase a asesor y agendar.
- ✅ Opción 4 (Arquitectónico): ciudad → lugar → medidas → resumen + agendar.
- ✅ Multimedia por WhatsApp (TwiML <Media>) y en el simulador web (img/video).
- ✅ Tests: backend 26/26 pytest, frontend 100%.

## Pendiente / Backlog
- P1: Validar firma X-Twilio-Signature en el webhook (seguridad producción).
- P1: Reemplazar textos genéricos por los precios/beneficios reales del negocio.
- P2: Persistir conversaciones/estado (Mongo/Redis) si se requiere historial o multi-worker.
- P2: Configurar el webhook en la consola de Twilio Sandbox apuntando a
      {REACT_APP_BACKEND_URL}/api/whatsapp/webhook.

## Notas de despliegue Twilio Sandbox
- En Twilio Console → Messaging → WhatsApp Sandbox, configurar "When a message comes in"
  a: https://andrea-polarizados.preview.emergentagent.com/api/whatsapp/webhook (POST).
- El usuario debe unirse al Sandbox enviando el código "join <palabra>" al número Sandbox.
