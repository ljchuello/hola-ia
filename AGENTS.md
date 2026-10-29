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
- ✅ Única excepción: leer `st.secrets` sin romper la app cuando no existe el archivo de secretos.

## 🔐 Secretos

- La clave real vive en `.streamlit/secrets.toml`, ignorado por git.
- La plantilla pública es `.streamlit/secrets.example.toml`.
- Nunca escribas claves reales en el código, en este archivo ni en el README.

## 🎓 Propósito

Mostrar lo simple que es conectar un LLM a Streamlit para clasificar casos de soporte.

## 🚦 El semáforo

| Color | Nombre | Qué significa | SLA |
| --- | --- | --- | --- |
| 🔴 | Bombero | Un proceso crítico está detenido y hay un cliente esperando: no se puede guardar una factura o una nota de crédito, no se puede cerrar una venta, el sistema no responde o se pierde información | 15 minutos |
| 🟡 | Cotidiano | El sistema funciona, pero algo lo traba: la impresora no imprime, va lento o una pantalla da error, y se puede seguir trabajando por otro lado | Mismo día |
| 🟢 | Consulta | Una duda, una solicitud de información o un tema con un tercero (proveedor, banco, internet) que no frena la operación | 24-48 horas |

**Regla de oro:** ante la duda entre 🔴 y 🟡, siempre 🔴. Nunca se minimiza un posible incendio.

## 🎨 Emojis

Los emojis son parte del estilo del proyecto. Úsalos con naturalidad, sin saturar.

- ✅ En títulos, textos de la interfaz, comentarios de bloque, docstrings, README, commits y respuestas.
- ❌ En nombres de variables, funciones, archivos, rutas, claves de diccionarios o JSON.
- 📏 Máximo uno por bloque o encabezado, y nunca dos seguidos.

## 🗣️ Idioma

Todo el texto se escribe en **español neutro**, dentro y fuera del proyecto.

- ✅ Trato con **tú** en toda la interfaz, los prompts, el README y las respuestas del agente.
- ❌ Nada de voseo: `vos`, `tenés`, `podés`, `hacé`, `escribí`, `revisá`, `confirmalo`.
- ❌ Nada de regionalismos: `al toque`, `planilla`, `alícuota`, `che`, `laburo`.
- ✅ Las respuestas del agente también son en español neutro, incluso fuera del proyecto.

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
- Español neutro para todo lo que ve el usuario y para las respuestas del agente.
- Commits con un emoji al inicio: `✨ feat:`, `🐛 fix:`, `📝 docs:`.
