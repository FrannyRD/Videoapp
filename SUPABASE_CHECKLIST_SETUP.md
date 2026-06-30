# Configuración de Supabase para guardar el checklist

Este cambio guarda los videos marcados como listos/vistos en Supabase para que no se pierdan cuando Render se duerma o reinicie.

## 1. Crear tabla en Supabase

Entra a Supabase > SQL Editor y ejecuta el archivo:

```sql
supabase_video_status_setup.sql
```

## 2. Variables de entorno en Render

En Render > Environment agrega:

```text
SUPABASE_URL=https://TU-PROYECTO.supabase.co
SUPABASE_SERVICE_ROLE_KEY=TU_SERVICE_ROLE_KEY
```

Opcional:

```text
SUPABASE_VIDEO_STATUS_TABLE=video_status
```

## 3. Deploy

Haz redeploy de la app en Render.

Si las variables no están configuradas, la app seguirá funcionando con el JSON local como antes, pero Render puede perder esos datos al dormir/reiniciar.
