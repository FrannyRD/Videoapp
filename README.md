# Generador de Videos — Enigma Diario

App que genera videos verticales (1080x1920) listos para Reels/Shorts a partir de un guion
(texto + palabra clave por escena). Busca clips en Pexels, genera voz con Edge-TTS, e incrusta
texto animado con FFmpeg.

**Importante:** la subida a Facebook/YouTube se hace manual — esta app solo genera el .mp4 final
para que lo descargues y subas tú.

---

## 1. Consigue tu API Key gratis de Pexels

1. Entra a https://www.pexels.com/api/
2. Crea una cuenta gratis
3. Copia tu API Key (la necesitas en el paso 4)

---

## 2. Sube el código a GitHub

```bash
cd videoapp
git init
git add .
git commit -m "Primera versión del generador de videos"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

---

## 3. Despliega en Render

1. Entra a https://render.com y crea cuenta (gratis)
2. Click en **"New +"** → **"Web Service"**
3. Conecta tu repositorio de GitHub
4. Render detectará el `Dockerfile` automáticamente — déjalo como "Docker"
5. Plan: **Free**
6. En **"Environment Variables"** agrega:
   - `PEXELS_API_KEY` = (tu clave del paso 1)
7. Click **"Create Web Service"**

El primer deploy tarda 3-5 minutos (instala FFmpeg + dependencias). Cuando termine, te da una URL pública (ej: `https://enigma-video-generator.onrender.com`).

**Nota sobre el plan gratis de Render:** el servicio "se duerme" tras 15 min de inactividad. La primera petición después de eso tarda ~30-60 segundos extra en despertar — es normal, no es un error.

---

## 4. Usar la app

1. Abre la URL que te dio Render
2. Escribe cada escena: el texto (lo que se va a decir y mostrar) + una palabra clave en inglés (para buscar el video de fondo, ej: `dark cave`, `treasure map`)
3. Elige la voz
4. Click "Generar video"
5. Espera 1-3 minutos (depende de cuántas escenas)
6. Descarga el .mp4 y súbelo manualmente a Facebook/YouTube

---

## Estructura del proyecto

```
videoapp/
├── app.py              # Servidor web (Flask)
├── pipeline.py          # Orquesta todo el proceso
├── pexels_client.py      # Busca y descarga videos de Pexels
├── tts_client.py         # Genera la voz (Edge-TTS, gratis)
├── video_builder.py      # Ensambla el video final con FFmpeg
├── templates/index.html  # Interfaz web
├── requirements.txt
├── Dockerfile
└── render.yaml
```

---

## Probado y verificado localmente

- ✅ Texto largo hace salto de línea automático sin cortarse en pantalla
- ✅ Caracteres especiales (comillas, dos puntos, %, tildes) no rompen el video
- ✅ Duración de cada escena se ajusta automáticamente a la duración de la voz
- ✅ Video final en formato correcto: H.264, 1080x1920, audio AAC
- ✅ Mezcla de voz + música de fondo a bajo volumen

## Pendiente de probar en Render (requiere internet, no disponible en este entorno de prueba)

- Búsqueda y descarga real de clips desde Pexels
- Generación de voz real con Edge-TTS

Si al usar la app en Render un clip no se encuentra para una palabra clave, el error te lo dirá
explícitamente (no se rompe en silencio) — prueba con una palabra clave más genérica.

## Limitaciones conocidas

- El plan gratis de Pexels tiene límite de 200 peticiones/hora — suficiente para uso normal
- Edge-TTS es un servicio no oficial de Microsoft; en raras ocasiones puede fallar temporalmente
- Videos muy largos (10+ escenas) pueden tardar varios minutos en generarse en el plan free de Render (CPU limitada)
