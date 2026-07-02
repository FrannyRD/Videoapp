# Meta AI Video Beta

Esta sección fue agregada aparte del generador principal. No cambia el flujo actual de Pexels, contenidos por página, checklist, música ni subtítulos.

## Ruta nueva

Abre:

```text
/meta-ai
```

También aparece un enlace en la pantalla principal.

## Variables necesarias en Render

Agrega estas variables privadas en tu servicio de Render:

```text
META_AI_DATR=valor_cookie_datr
META_AI_ECTO_1_SESS=valor_cookie_ecto_1_sess
```

Opcional:

```text
META_AI_ABRA_SESS=valor_cookie_abra_sess
META_AI_ACCESS_TOKEN=valor_access_token_si_lo_tienes
```

## Cómo obtener las cookies

1. Abre `https://www.meta.ai` en una computadora.
2. Inicia sesión.
3. Abre herramientas de desarrollador.
4. Ve a Application/Storage → Cookies → `https://www.meta.ai`.
5. Copia los valores de `datr` y `ecto_1_sess`.
6. Pégalos en Render como variables de entorno.
7. Haz redeploy.

## Importante

Este SDK no es una API oficial de Meta Developers. Puede dejar de funcionar si Meta cambia su web o invalida cookies. Por eso quedó aislado en una subpágina y no se mezcla con el generador principal.

No compartas tus cookies públicamente ni las pegues en el código.
