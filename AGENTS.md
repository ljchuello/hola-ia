# AGENTS.md · Conti Clasificador

## Qué es este proyecto

Una aplicación web interactiva que ayuda al personal de soporte técnico de primera línea en Sermatick a clasificar incidencias de su sistema de facturación electrónica mediante un semáforo operativo (🔴 Bombero, 🟡 Cotidiano, 🟢 Consulta) para ordenar el escalamiento a Producción.

## Cómo está hecho

- Python 3.12.
- Interfaz: Streamlit (Ruta A).
- IA: API compatible con OpenAI mediante el SDK `openai`. El modelo por defecto es `deepseek/deepseek-v4.1-flash-1017` servido a través de OpenRouter (configurable a Gemini u OpenAI mediante `LLM_BASE_URL` y `LLM_MODEL`). La lógica del modelo y los prompts residen en `conti.py`.
- Archivos: `app.py` (interfaz y flujo de usuario), `conti.py` (prompts y llamadas a la IA), `casos.json` (almacén local), `requirements.txt` (dependencias), `README.md` y `AGENTS.md`.
- La especificación completa está en [especificacion.md](especificacion.md).

## Reglas

- La clave de la API va SIEMPRE en secretos (`st.secrets` en `.streamlit/secrets.toml` para la ruta A, variable de entorno `LLM_API_KEY` para la ruta B). Nunca en el código, en el README, en este archivo ni en el chat.
- Cada llamada a la API va dentro de `try/except` y muestra un mensaje claro para el usuario sin romper la aplicación.
- Textos de la interfaz y respuestas en español neutro, con trato de **tú** (prohibido voseo como `vos`, `tenés`, `hacé` y regionalismos), pensados para alguien sin conocimientos técnicos. *Contexto:* en una fase de pruebas el modelo empezó a responder en tono argentino/rioplatense (*"fijate que tenés..."*), por lo que se añadió explícitamente en el prompt y en estas reglas la exigencia de español neutro y tuteo sin excepciones.
- **Prohibida la sobreingeniería:** Es una muestra didáctica y minimalista. Nada de arquitecturas multicapa, factories, interfaces, Pydantic, bases de datos relacionales, Docker, CI/CD ni patrones de diseño complejos. Si una función se entiende en 10 líneas, que dure 10 líneas.
- **El semáforo y la regla de oro:**
  - 🔴 **Bombero (15 min):** Proceso crítico detenido y cliente esperando (no guarda factura, no cierra venta, pérdida de datos).
  - 🟡 **Cotidiano (mismo día):** El sistema funciona pero algo lo traba (lentitud, error no bloqueante, impresora).
  - 🟢 **Consulta (24-48 h):** Dudas o temas con terceros que no frenan la operación.
  - *Regla de oro:* ante la duda entre 🔴 y 🟡, siempre 🔴. Nunca se minimiza un posible incendio.
- Cambios pequeños: uno por petición. Al terminar, explica qué has cambiado y por qué.
- Si añades una librería, añádela también a `requirements.txt` y dilo.
- No uses datos personales reales. Para probar, inventa ejemplos.
- Uso moderado de emojis: máximo uno por bloque o encabezado, nunca dos seguidos ni en variables o identificadores de código.

## Cómo comprobar que funciona

- Ruta A: `streamlit run app.py` en local (con `.streamlit/secrets.toml`), o haz push y revisa la app en Streamlit Cloud ([https://ljchuello-ia.streamlit.app/](https://ljchuello-ia.streamlit.app/)).
- Ruta B: `export LLM_API_KEY="…"` y ejecuta `streamlit run app.py`.
- Casos de prueba (entrada → lo que esperamos):
  1. *"No puedo timbrar una factura de venta y el comprador está en caja"* → Clasifica como 🔴 Bombero (SLA: 15 minutos) e identifica el bloqueo crítico.
  2. *"La pantalla de reportes tarda en cargar, pero podemos emitir documentos"* → Clasifica como 🟡 Cotidiano (SLA: mismo día), explicando que la operación no está detenida.
  3. *"¿Cuál es la receta de una pizza napolitana?"* (entrada fuera de tema) → Conti responde amablemente que es el asistente de soporte técnico y pide describir la incidencia con el sistema.

## Qué no hacer

- No borres ni reescribas el README sin preguntar.
- No cambies el modelo ni la arquitectura sin preguntar.
- No hagas push ni despliegues sin que yo lo haya revisado.
- No agregues capas de abstracción, validadores complejos, ORMs ni dependencias adicionales innecesarias.
- No uses voseo (`vos`, `podés`, `revisá`) ni regionalismos en ningún texto visible ni en respuestas del agente.
