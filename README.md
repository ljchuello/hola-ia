# 🎯 Conti Clasificador

Una muestra mínima de cómo usar un LLM para clasificar casos de soporte **conversando con un chatbot** y avisar al equipo de Producción con un semáforo.

> ⚠️ Proyecto demostrativo. No es para producción: guarda los casos en un JSON local, no valida errores y no envía notificaciones reales.

## 🏢 ¿Para quién es?

Conti Clasificador es la demo de una propuesta para **Sermatick Cia Ltda**, empresa de desarrollo de software que ofrece un sistema de facturación electrónica como servicio.

- 🎯 **Objetivo:** servir de MVP para presentar la propuesta e implementarla después en producción.
- 🧑‍💻 **Quién lo usa:** el personal de soporte, la primera línea frente al cliente.
- 🗂️ **Qué resuelve:** ordena y prioriza los casos antes de que escalen al departamento de Producción.

## 🚦 El semáforo

| Color | Nombre | Qué significa | SLA |
| --- | --- | --- | --- |
| 🔴 | Bombero | Un proceso crítico está detenido y hay un cliente esperando: no se puede guardar una factura o una nota de crédito, no se puede cerrar una venta, el sistema no responde o se pierde información | 15 minutos |
| 🟡 | Cotidiano | El sistema funciona, pero algo lo traba: la impresora no imprime, va lento o una pantalla da error, y se puede seguir trabajando por otro lado | Mismo día |
| 🟢 | Consulta | Una duda, una solicitud de información o un tema con un tercero (proveedor, banco, internet) que no frena la operación | 24-48 horas |

**La frontera:** si el trabajo se detiene es 🔴; si solo se hace más lento es 🟡; si es de un tercero y no frena la operación es 🟢.

**Regla de oro:** ante la duda entre 🔴 y 🟡, siempre 🔴.

## ▶️ Cómo correrlo

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🔐 Secretos (recomendado)

Para que quien use la app no tenga que pegar ninguna clave:

1. Copia la plantilla:
   ```bash
   cp .streamlit/secrets.example.toml .streamlit/secrets.toml
   ```
2. Abre `.streamlit/secrets.toml` y pon tu clave real:
   ```toml
   LLM_API_KEY = "sk-..."
   ```
3. Reinicia Streamlit.

Con la clave configurada, la app la usa directamente: no hay campos de configuración en la barra lateral. El archivo `secrets.toml` está ignorado por git y nunca se sube.

En Streamlit Cloud, pega los mismos valores en **App settings → Secrets**.

## 🔑 Configuración

El orden de prioridad es: `secrets.toml` → variable de entorno. Si no hay clave, la app avisa al intentar clasificar:

| Variable | Por defecto |
| --- | --- |
| `LLM_API_KEY` | vacío |
| `LLM_BASE_URL` | `https://openrouter.ai/api/v1` |
| `LLM_MODEL` | `deepseek/deepseek-v4.1-flash-1017` |

Funciona con cualquier API compatible con OpenAI 🤝:

- OpenAI: `https://api.openai.com/v1`
- Groq: `https://api.groq.com/openai/v1`
- OpenRouter: `https://openrouter.ai/api/v1`
- Ollama: `http://localhost:11434/v1` (la API key puede ser cualquier texto)

## 💬 Chat agéntico

La pestaña **Chat agéntico** reemplaza al formulario de "Nuevo caso":

1. Conti saluda y te va preguntando una cosa a la vez: quién eres, cómo contactarte y qué pasó.
2. Le respondes con lenguaje natural, como en un chat normal. Nada de formatos.
3. Cuando Conti cree que ya tiene lo necesario, clasifica el caso con el semáforo.
4. Antes de guardar, te muestra el resumen y pides confirmación. Si no quedó bien, sigues hablando.
5. Al confirmar, el caso se guarda como abierto y queda en Gestión.

También puedes pegar un correo completo en la pestaña **📋 Pegar correo** y Conti lo clasifica de inmediato.

## 🗂️ Gestión de casos

La pestaña **Gestión** permite:

- 🔍 Buscar por nombre de la empresa o persona, teléfono, correo o motivo.
- 🎚️ Filtrar por estado: abiertos, cerrados o todos.
- 🚦 Filtrar por semáforo.
- ✅ Cerrar un caso abierto o 🔓 reabrirlo.
- 📣 Notificar a Producción.

Los casos se guardan en `casos.json`, así que sobreviven a una recarga del navegador. Ese archivo es local y está ignorado por git.

## 🧠 Cómo funciona

1. Hablas con Conti en el chat (o pegas un correo completo).
2. `conti.py` le manda el historial al modelo con un prompt que define el semáforo.
3. En cada turno el modelo responde un JSON: o hace una pregunta, o entrega la clasificación.
4. Cuando clasifica, la app te muestra el resumen para confirmar antes de guardar.
5. El caso se guarda como **abierto**, aparece un aviso y queda en **Gestión**.
6. En **Gestión** puedes buscarlo, cerrarlo, reabrirlo o notificarlo.

### 🛠️ ¿Cómo está construido?

- 🧠 **Prompt:** un texto en `conti.py` le dice al modelo cómo clasificar; no hay reglas escondidas en el código.
- 🤝 **SDK:** las llamadas se hacen con el **SDK de OpenAI**, así funciona con cualquier API compatible.
- 🌐 **Proveedor:** el modelo es **DeepSeek V4 Flash** (`deepseek/deepseek-v4.1-flash-1017`), servido a través de **OpenRouter**.
- 🔐 **Secretos:** la API key y la dirección del proveedor viven en `.streamlit/secrets.toml`, ignorado por git. La plantilla pública es `secrets.example.toml`.

Cambiar de proveedor o de modelo es cambiar esas dos líneas de secretos, sin tocar el código.

## 📁 Archivos

- `app.py` — interfaz de Streamlit.
- `conti.py` — prompts, llamada al modelo y mensaje de notificación.
- `casos.json` — casos guardados localmente (ignorado por git).
- `.streamlit/secrets.example.toml` — plantilla de secretos.
- `.streamlit/secrets.toml` — tu clave real (ignorado por git).
- `AGENTS.md` — reglas del proyecto (incluida la prohibición de sobreingeniería).
- `requirements.txt` — dependencias.
