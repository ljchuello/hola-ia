# 🎯 Conti Clasificador

Este proyecto se llama **Conti Clasificador**. Siempre nos referimos a él así, nunca como "hola-ia".

## 🚫 Regla número uno: prohibida la sobreingeniería

Este proyecto es una **muestra didáctica**, no un sistema real. No va a producción y no necesita comportarse como si fuera a hacerlo.

- ❌ Nada de arquitecturas por capas, factories, interfaces, inyección de dependencias ni patrones de diseño.
- ❌ Nada de validaciones, reintentos, fallbacks, manejo de excepciones ni logs.
- ❌ Nada de Pydantic, bases de datos, ORM, Docker, CI/CD, autenticación ni tests.
- ❌ Nada de archivos nuevos si el código cabe en los que ya existen.
- ❌ Nada de optimizar, cachear ni escalar.
- ✅ Menos es más: si una función se entiende en 10 líneas, que dure 10 líneas.
- ✅ El código se lee de arriba abajo como un tutorial.
- ✅ Los nombres deben ser obvios y en español.
- ✅ Si dudas entre agregar algo o no agregarlo: **no lo agregues**.

## 🎓 Propósito

Mostrar lo simple que es conectar un LLM a Streamlit para clasificar casos de soporte.

## 🚦 El semáforo

| Color | Nombre | Qué significa | SLA |
| --- | --- | --- | --- |
| 🔴 | Bombero | Algo está caído, bloqueado o se pierde información | 15 minutos |
| 🟡 | Cotidiano | Solicitud normal de operación | Mismo día |
| 🟢 | Consulta | Duda o petición de información | 24-48 horas |

**Regla de oro:** ante la duda entre 🔴 y 🟡, siempre 🔴. Nunca se minimiza un posible incendio.

## 🎨 Emojis

Los emojis son parte del estilo del proyecto. Úsalos con naturalidad, sin saturar.

- ✅ En títulos, textos de la interfaz, comentarios de bloque, docstrings, README, commits y respuestas.
- ❌ En nombres de variables, funciones, archivos, rutas, claves de diccionarios o JSON.
- 📏 Máximo uno por bloque o encabezado, y nunca dos seguidos.

## 🧱 Stack

- Python 3.10+
- Streamlit para la interfaz
- SDK de OpenAI apuntando a cualquier API compatible

## ▶️ Comandos

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📐 Convenciones

- `snake_case` para variables y funciones.
- Español para todo lo que ve el usuario.
- Commits con un emoji al inicio: `✨ feat:`, `🐛 fix:`, `📝 docs:`.
