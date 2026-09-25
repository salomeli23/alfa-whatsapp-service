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

## Migración a Baileys / WhatsApp Web QR (Railway) — 2026-06
- ✅ Servicio Baileys hospedado en Railway: https://alfapola.up.railway.app (state=connected, operativo).
- ✅ yarn.lock y index.js TRACKEADOS en git.
- ✅ Backend .env producción: WA_SERVICE_URL=https://alfapola.up.railway.app, WA_TOKEN=camilo231.
- ✅ Error `ECONNREFUSED ::1:8001` resuelto: index.js ahora usa fallback directo `https://alfapolarizados.online` con sanitización automática de `/panel` y trailing slashes, más logs detallados por mensaje entrante.
- ✅ Bug "repite mensajes al vincular QR" + "No entendí tu mensaje" al enviar modelo: causa raíz = sockets Baileys duplicados tras reconexión (códigos 515/408) y replay de historial al vincular. Fix en index.js: (1) guard de socket único (handlers del socket viejo se ignoran + removeAllListeners + end), (2) ignorar mensajes con timestamp anterior a la vinculación (historial), (3) dedupe por message ID.
- ✅ Título del front y panel cambiado a "Chatbot Alfa" (index.html, login, sidebar, header del simulador).
- ✅ Opción 3 (Antiatraco): tras elegir plan, responde "una asesora continuará tu atención personalizada" y el bot se PAUSA para ese contacto (bot_paused=true en DB, handoff automático vía flag session["request_human"] en bot_incoming). Se reactiva desde el panel. Test: TestAntiatracoHandoff. 65/65 pytest OK.
- ✅ Opción 4 (Arquitectónico): tras enviar medidas, muestra resumen + "una asesora preparará tu cotización" y el bot se PAUSA igual que opción 3. Test: TestArchHandoff. 66/66 pytest OK.
- ✅ Opción 1: eliminado video "Prueba de seguridad" (quedan 2: instalación + visibilidad). Tras elegir plan y responder cuándo agendar → handoff a asesora + pausa del bot (nuevo step handoff_agendar).
- ✅ Opción 2 (PPF): eliminada la aclaración de marca ambigua — cualquier marca/modelo continúa el flujo al submenú. Tras cualquier sub-opción (Total, Pintura, Piano Black, Acrílicas) y responder cuándo agendar → handoff a asesora + pausa. Tests: TestScheduleHandoff (3 nuevos). 69/69 pytest OK.
- ✅ Continuidad garantizada con audio: si el cliente responde con nota de voz en CUALQUIER punto, Andrea pasa a asesora y pausa el bot (session["request_human"] en rama is_audio de bot_incoming). Mensaje AUDIO_HANDOFF actualizado. Test: TestAudioHandoff. 70/70 pytest OK.
- Nota continuidad de texto: los cortes vistos en capturas (ej. responder "1" y no recibir respuesta) son por el socket duplicado de Railway (código viejo). El fix ya está en index.js; requiere redeploy de Railway.
- ✅ Fallback amable: el bot NUNCA dice "No entendí". Ahora responde "¡Gracias por tu mensaje! 😊 Con gusto te ayudo. Estas son nuestras opciones 👇" + menú (INVALID_PREFIX cambiado).
- ✅ Opción 5 (Detailing): tras "Un asesor te ayudará a coordinar tu cita", cualquier respuesta (ej. "Ok") → handoff a asesora + pausa (step handoff_agendar).
- ✅ Opción 3 (Antiatraco) ya pasaba a asesora tras elegir plan (cualquier texto, ej. "Diamante"); el silencio visto en capturas era por el socket duplicado de Railway.
- Tests: TestKindFallback + TestAudioHandoff. 72/72 pytest OK.
- ✅ CAUSA RAÍZ menú repetido / modelo "se devuelve": WhatsApp entrega el mismo usuario con doble identidad (@s.whatsapp.net y @lid). Cada forma creaba una SESIÓN distinta en el backend → menú se repetía y pasos se perdían. Fix en index.js: resolveJid() prefiere siempre el JID de número (remoteJidAlt) → sesión estable. jidToContact ahora guarda solo el número.
- ⚠️ Contacto 256100427428012@lid quedó pausado en producción por handoffs de prueba → reactivado vía API (18 sep 2026).
- PENDIENTE USUARIO: Save to GitHub + redeploy Railway (aplica resolveJid + socket único + dedupe) + redeploy Emergent.
- ✅ Afirmaciones cortas ("Si", "Claro", "Ok", etc.) ya NO se citan como "Tomé nota: Si" — responde "¡Perfecto! 🙌" + handoff directo (AFFIRMATIONS en handoff_agendar). Fechas reales sí se citan. Test: test_affirmation_not_quoted. 73/73 pytest OK.
- ℹ️ Síntoma "hay que escribir 2 veces" = Railway sigue con código viejo (verificado: /status responde 200 sin token = middleware ausente). Además el LID llega en 2 formas ("id:5@lid" e "id@lid") generando 2 claves de sesión. Todo corregido en el código nuevo; requiere redeploy.
- ✅ CAUSA RAÍZ #2 (producción): el backend de Emergent corre con MÚLTIPLES WORKERS y las sesiones estaban en memoria por proceso → menú repetido, pasos perdidos, "escribir 2 veces". FIX DEFINITIVO: sesiones del bot persistidas en MongoDB (colección bot_sessions, helpers get_session/save_session, is_paused siempre fresco desde conversations). Verificado: el flujo sobrevive reinicio completo del backend. Loop de reenganche migrado a Mongo. 73/73 pytest OK.
- RESPUESTA a "¿backend con código viejo?": NO — producción ya tenía el código nuevo; el problema era multi-worker + sesiones en memoria.
- ✅ Ajustes 18-sep (2): Opción 1 re-incluye video Prueba de seguridad (3 videos). Opción 2: Protección Total y Pintura Completa ya NO hablan de cita → envían respuesta + info PPF + pasan directo a asesor (request_human, sin AGENDAR). Marca ambigua (Deepal/Tesla/Mazda/BYD) → menú con los modelos del catálogo piano black para que elija y siga el flujo (step ppf_clarify_model restaurado). Piano Black: piezas a cubrir entre paréntesis (helper _piezas_parentesis); precios actualizados Mazda CX-30 $950.000 y Ford Territory $1.300.000. Opción 4: quitada línea "Películas de seguridad y decorativas". Opción 5: "Restauración de faros y plásticos" → "Hidratación de partes plásticas". Tests actualizados (test_ppf_ambiguous_brand_shows_models, test_ppf_total_goes_to_advisor_no_cita). 73/73 pytest OK.
- ⚠️ Menú duplicado: causado por doble procesamiento de sockets Baileys (fix ya en index.js). Requiere Save to GitHub + redeploy Railway para aplicarse en producción.
- ✅ 64/64 pytest backend pasando.
- Pasos usuario: 1) Save to GitHub, 2) Redeploy Railway (para aplicar index.js blindado), 3) Probar mensaje desde otro número.
- ✅ Enrutador por palabras clave (_guess_service): texto libre o saludo largo con intención (polarizado/ppf/antiatraco/detailing/casa-ventana) entra DIRECTO al flujo del servicio en vez de reenviar el menú. Saludo corto puro (<=3 palabras) sigue mostrando el menú. Saludo largo sin intención → respuesta guiada corta ofreciendo Polarizado/PPF/Antiatraco (sin menú completo). Tests: test_free_text_routes_to_service. 74/74 pytest OK.
- ✅ Combo "1 y 2": responde "Primero te comparto la información de Polarizado y luego la de PPF" + ambas intros + pide vehículo una sola vez; tras el vehículo muestra planes de polarizado Y menú PPF juntos (session["combo_ppf"]). En el paso de elegir plan, palabras PPF (total/pintura/piano/acril/ppf) saltan al flujo PPF (recursión a ppf_protect). Nuevas keywords en _guess_service: pelicula/película → antiatraco(3), pernos/plásticos → detailing(5). Tests: TestComboAndKeywords. 77/77 pytest OK.
- ✅ Nuevo menú PPF (tras modelo): 1) Piezas Piano Black, 2) Piezas Acrílicas (espejos, farolas, stops), 3) Protección frontal o Full Front (nuevo: info + asesor, sin cita), 4) Protección completa o Full PPF (info + asesor, sin cita). Piano Black y Acrílicas mantienen continuidad con AGENDAR + handoff_agendar. Keywords actualizadas (frontal/front/completa/full). PPF_PINTURA_INFO eliminado. Tests actualizados al nuevo orden. 77/77 pytest OK.
- ✅ Opción 3 Antiatraco: reemplazada la imagen única (planes_bjx5xb.jpg) por las 5 nuevas imágenes de Cloudinary (ChatGPT_Image_22_sept...). Se envían como un solo mensaje con 5 adjuntos (sendToJid pone el texto como caption de la primera). 77/77 pytest OK.
