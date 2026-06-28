# Generador de Videos — Multi Página Facebook

App Flask para generar videos verticales 1080x1920 listos para Reels/Shorts. Usa Pexels para clips, Edge-TTS para voz, FFmpeg para render y una biblioteca separada por página para mantener orden de producción.

## Qué incluye esta versión

- Biblioteca por página: Casos Sin Resolver, Mundo Animal Salvaje, Historia Prohibida, Mente Profunda, Enigma Diario y Biblia Cinemática.
- 28 videos cargados por página: 4 videos por día durante 7 días.
- Checklist persistente para marcar cada video como listo y saber cuál sigue.
- Botón para cargar el siguiente video pendiente de cada página.
- Opciones de subtítulos: meme, cinemático, limpio, amarillo impacto y minimal.
- Música recomendada por nicho/página, además de opciones generales y sin música.
- Historial local de clips usados de Pexels por página para reducir repeticiones y evitar usar el mismo clip en videos relacionados.
- Mantiene el modo manual original: puedes seguir pegando escenas o historias propias.

## Variables de entorno

En Render o tu servidor agrega:

- `PEXELS_API_KEY`: clave gratis de Pexels API.

## Ejecutar local

```bash
pip install -r requirements.txt
python app.py
```

Abre: `http://localhost:5000`

## Desplegar en Render

Este repo incluye `Dockerfile` y `render.yaml`. En Render crea un Web Service con Docker y agrega `PEXELS_API_KEY` en Environment Variables.

## Archivos nuevos importantes

- `content_library.py`: banco inicial de contenido por página.
- `content_state.py`: guarda los checks de videos listos en `data/video_status.json`.
- `pexels_client.py`: ahora guarda historial de clips usados en `data/used_pexels_clips.json`.
- `caption_builder.py`: estilos de subtítulos.
- `templates/index.html`: interfaz multi página.

## Nota importante sobre clips

La app intenta evitar repeticiones guardando los IDs de Pexels usados por página. Aun así, si Pexels devuelve pocos resultados para una keyword muy específica, puede reutilizar un clip como último recurso para no romper la generación. Para reducir ese riesgo, usa keywords variadas y no demasiado limitadas.
