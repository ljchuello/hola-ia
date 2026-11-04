# Entrega final · Conti Clasificador

**Nombre y apellidos:** Leonardo Chuello

## 1. Enlaces

- **App desplegada:** [https://ljchuello-ia.streamlit.app/](https://ljchuello-ia.streamlit.app/)
- **Repositorio:** [https://github.com/ljchuello/hola-ia](https://github.com/ljchuello/hola-ia)

## 2. Problema y usuario

El personal de soporte técnico de primera línea en Sermatick Cia Ltda recibe a diario decenas de incidencias desordenadas por correo y mensajería de clientes de su sistema de facturación electrónica. Actualmente, cada operador clasifica según su intuición subjetiva y escala incidencias a Producción sin un criterio de urgencia unificado, demorando casos críticos o saturando a desarrollo con dudas operativas. La IA resuelve la extracción interactiva de datos de contacto y la clasificación objetiva de criticidad mediante un semáforo operativo con tiempos de atención definidos (SLA). Quedan fuera de la solución la corrección del código de facturación en Producción, la redacción de la respuesta final al cliente y la integración transaccional directa con las bases de datos del sistema.

## 3. Especificación

Enlace al documento completo en el repositorio: [especificacion.md](https://github.com/ljchuello/hola-ia/blob/main/especificacion.md)

### Funcionalidades principales
1. **Captura conversacional y extracción directa:** Modo de chat interactivo donde Conti formula una sola pregunta a la vez para identificar al cliente, su contacto y el problema, además de una pestaña alternativa para analizar correos completos pegados en un área de texto.
2. **Clasificación objetiva con semáforo y SLA:** Categorización automática en tres niveles de atención:
   - 🔴 **Bombero (SLA: 15 minutos):** Proceso crítico detenido con cliente en espera (no guarda facturas, no cierra ventas, pérdida de datos).
   - 🟡 **Cotidiano (SLA: mismo día):** El sistema opera con dificultad pero no está detenido (lentitud general, fallo de impresora, errores en reportes secundarios).
   - 🟢 **Consulta (SLA: 24-48 horas):** Dudas operativas, solicitudes de información o temas de terceros que no frenan la operación.
   - **Regla de oro:** Ante la duda entre 🔴 y 🟡, siempre se clasifica como 🔴 para no minimizar incidentes graves.
3. **Panel de gestión y aviso a Producción:** Visualización de tickets registrados en almacenamiento local (`casos.json`), filtrado dinámico por estado (abierto/cerrado) o semáforo, y generación con un clic de la notificación formateada con emoji y SLA para el equipo de desarrollo.

### Entradas y salidas

| El usuario da… | La app devuelve… | Ejemplo |
|---|---|---|
| Mensajes en lenguaje natural respondiendo a las preguntas de Conti en el chat | Pregunta de seguimiento para completar datos faltantes o tarjeta final de clasificación para confirmar | Usuario: *"Soy Carlos de Farmacia Central (0991234567). No puedo emitir facturas y tengo clientes en mostrador"* → Conti clasifica directamente como 🔴 Bombero (SLA: 15 min), resume el caso y sugiere revisar la cola de comprobantes. |
| Un correo electrónico completo pegado en el área de texto | Ficha estructurada con semáforo, motivo de la elección, datos de contacto identificados y pasos de acción sugeridos | Correo: *"Estimados, ¿podrían confirmarme si el reporte contable incluye retenciones del mes anterior? Saludos, Laura."* → Clasificación 🟢 Consulta (SLA: 24-48 h), motivo: duda informativa que no detiene la facturación. |
| Clic en *Notificar* en la pestaña de Gestión | Mensaje listo para copiar o enviar al equipo de Producción con los detalles clave del incidente | Mensaje: *"🔴 Caso Bombero notificado a Producción · SLA: 15 minutos"* |

### Criterios de aceptación y casos límite

| Entrada / Situación | Resultado esperado |
|---|---|
| *"No puedo timbrar una factura de venta y el comprador está en caja"* (Caso normal 🔴) | Clasifica como 🔴 Bombero con SLA de 15 minutos e identifica el bloqueo operativo crítico. |
| *"La pantalla de reportes tarda en cargar, pero podemos emitir documentos"* (Caso normal 🟡) | Clasifica como 🟡 Cotidiano con SLA del mismo día, explicando que el trabajo continúa con lentitud. |
| *"¿Cómo cambio el logotipo de mi empresa en las facturas?"* (Caso normal 🟢) | Clasifica como 🟢 Consulta con SLA de 24 a 48 horas, detallando que es una duda de configuración. |
| Caso ambiguo con duda entre lentitud severa y paro parcial (Caso límite) | Aplica la regla de oro clasificando automáticamente como 🔴 Bombero para proteger la operación crítica. |
| Entrada fuera de tema (e.g., *"¿Cuál es la receta de una pizza?"*) (Caso límite) | Conti responde amablemente recordando que es el asistente de soporte técnico e invita a reportar una incidencia del sistema. |
| Campo de texto vacío o sin datos suficientes (Caso límite) | En el chat, Conti solicita cordialmente los datos faltantes; en la pestaña de correos, emite un aviso solicitando ingresar texto. |
| Clave de API no configurada o corte de conexión (Caso límite) | La app captura el error mediante `try/except` y muestra un mensaje informativo claro en la interfaz sin romperse ni interrumpir la sesión. |

## 4. La pieza de IA

- **Qué usa:** API compatible con OpenAI mediante el SDK oficial `openai` en Python, configurada por defecto con el modelo `deepseek/deepseek-v4.1-flash-1017` a través de OpenRouter (fácilmente adaptable a OpenAI, Groq u Ollama mediante `LLM_BASE_URL` y `LLM_MODEL`).
- **Por qué esa opción:** Permite respuestas rápidas a un coste prácticamente nulo, fuerza una salida estructurada estricta en JSON (`response_format={"type": "json_object"}`) y desacopla por completo el proveedor del código fuente.
- **Qué pasa si falla:** Todas las llamadas a la API residen dentro de bloques `try/except` controlados. Si falta la clave de API o se agota la cuota, la interfaz muestra una advertencia visual amistosa (`st.warning` pidiendo configurar `.streamlit/secrets.toml`) y retorna un estado seguro por defecto sin que la aplicación se caiga ni muestre errores técnicos al usuario.
- **Dónde está la clave:** La clave de autenticación se gestiona exclusivamente a través de secretos (`st.secrets` en `.streamlit/secrets.toml` para Streamlit Cloud o la variable de entorno `LLM_API_KEY` para ejecución local). Jamás se incluye en el código fuente, en el historial de Git ni en ningún documento público.

## 5. Proceso con IA

- **Herramientas:** Antigravity IDE (asistente de código con modelos Gemini), Streamlit para la interfaz web, Python 3.12 y Git/GitHub para el control de versiones.
- **Fichero de contexto del agente:** [AGENTS.md](https://github.com/ljchuello/hola-ia/blob/main/AGENTS.md) en la raíz del repositorio, donde se instruyen las directrices del proyecto: la regla de oro del semáforo, la redacción en español neutro con trato de tú y la prohibición estricta de sobreingeniería.
- **Prompts clave:**
  1. *Prompt del semáforo con regla de oro (clasificación directa):*
     ```text
     Eres Conti, el clasificador de casos de soporte del equipo de Producción.
     Escribe en español neutro, sin voseo ni regionalismos.

     Clasifica cada caso en uno de estos tres niveles:
     🔴 rojo — Bombero: un proceso crítico está detenido y hay un cliente esperando.
     🟡 amarillo — Cotidiano: el sistema funciona, pero algo lo traba y hay que resolverlo hoy.
     🟢 verde — Consulta: no hay nada roto de tu lado. Es una duda, una solicitud de información o un tema con un tercero.

     La frontera entre rojo y amarillo es simple: si el trabajo se detiene, es rojo; si solo se hace más lento, es amarillo.
     Regla de oro: si dudas entre rojo y amarillo, elige rojo.

     Identifica siempre al usuario: nombre y contacto. Si no aparecen, déjalos vacíos.
     Responde SOLO con este JSON: {"semaforo": "rojo | amarillo | verde", "nombre": "...", "contacto": "...", "resumen": "...", "motivo": "...", "acciones": ["..."]}
     ```
  2. *Prompt conversacional de Conti (chat interactivo):*
     ```text
     Eres Conti, el asistente de soporte del equipo de Producción. Escribe en español neutro, sin voseo ni regionalismos.
     Tu trabajo es conversar con la persona para entender su caso y, cuando tengas lo necesario, clasificarlo con el semáforo.
     Habla natural, como un humano: saluda, haz UNA pregunta a la vez y espera la respuesta.
     Pregunta lo que falte, pero sin molestar: con saber quién es, cómo contactarlo y qué pasó ya puedes clasificar.
     Responde SOLO con JSON en uno de estos dos formatos:
     1. Si falta información: {"tipo": "pregunta", "mensaje": "..."}
     2. Si ya puedes clasificar: {"tipo": "clasificacion", "semaforo": "...", "nombre": "...", "contacto": "...", "resumen": "...", "motivo": "...", "acciones": ["..."]}
     ```
  3. *Prompt de contención de alcance (fuera de tema):*
     Instrucción incorporada para declinar amablemente peticiones no vinculadas con soporte técnico (como recetas o consultas generales) y orientar al usuario a describir su incidencia con el sistema de facturación.
- **Qué delegué al agente y qué revisé a mano:**
  - *Delegado al agente:* Esqueleto inicial de la interfaz en Streamlit, maquetación de pestañas, inyección de estilos CSS para selector de temas claro/oscuro y lógica de filtrado dinámico en la tabla de gestión.
  - *Revisado a mano:* Calibración minuciosa de los prompts para exigir español neutro con trato de tú (después de que el modelo tendiera al voseo rioplatense en pruebas preliminares), eliminación de sobreingeniería (descartando clases complejas, Pydantic y validadores innecesarios para mantener el código minimalista) y saneamiento de la lectura/escritura del archivo local `casos.json`.

## 6. Prueba y mejora

| Quién la probó | Qué probó | Qué pasó | Qué cambié |
|---|---|---|---|
| Andres (compañero) | La aplicación completa (flujo conversacional y pestaña de correos) | Validó el funcionamiento general indicando que la app clasificaba los incidentes como él esperaba | Mantuve el flujo y la estructura visual validada sin introducir cambios disruptivos |
| Victor (compañero) | Interfaz visual y respuestas del modelo | Tuvo inquietudes iniciales sobre la ubicación de algunos elementos en pantalla | Le expliqué el criterio de diseño minimalista para personal de soporte en mostrador; comprendió la decisión y validó que no requería cambios |
| Leonardo (yo, autor) | Toda la aplicación, casos extremos y persistencia | Noté que ante casos dudosos el modelo a veces minimizaba la urgencia, respondía con modismos no neutros y fallaba al sincronizar `casos.json` | Introduje la «regla de oro» en el prompt del sistema, fijé el tuteo neutro en `AGENTS.md` y corregí el manejo de excepciones en la persistencia JSON |

- **Feedback que he dado a un compañero:** En el debate del hito en Blackboard, revisé la propuesta de un compañero enfocada en atención al cliente y le sugerí implementar una regla de desempate explícita para incidencias ambiguas (similar a nuestra regla de oro), así como blindar los campos de entrada frente a textos vacíos para evitar llamadas innecesarias a la API.

## 7. Pitch escrito

1. **El problema y quién lo tiene:** En Sermatick Cia Ltda, los operadores de soporte de primera línea reciben a diario un aluvión desordenado de correos y mensajes sobre el sistema de facturación electrónica, clasificando por intuición y escalando a ciegas sin un criterio común de urgencia.
2. **Qué hace la app:** Conti Clasificador es un asistente web interactivo que conversa mediante chat o analiza correos pegados para identificar quién reporta, sus datos de contacto y la gravedad del incidente, asignándole al instante un semáforo operativo de atención (🔴 Bombero, 🟡 Cotidiano, 🟢 Consulta) y facilitando su notificación directa a Producción.
3. **Qué aporta la IA, que no se conseguiría sin ella:** Comprende el lenguaje natural caótico y fragmentado de clientes con problemas urgentes, abstrayendo de inmediato la intención, resumiendo el incidente y determinando objetivamente la criticidad operativa sin obligar al usuario a llenar formularios extensos y rígidos.
4. **Qué aprendí de la prueba y qué cambié:** Durante las pruebas comprobé que el modelo tendía a subestimar fallos que combinaban lentitud con procesos de venta; aprendí que requería una «regla de oro» explícita en el prompt para que, ante cualquier duda razonable, clasifique preventivamente como 🔴 Bombero y proteja la facturación de los clientes.
5. **Qué haría después, con un dato o un ejemplo concreto que lo respalde:** Como siguiente paso, conectaría Conti Clasificador mediante webhooks directamente con el sistema de tickets interno de Sermatick, con el objetivo de garantizar que el 100% de los casos 🔴 Bombero notifiquen al equipo de guardia en menos de 60 segundos y se atiendan antes del límite de SLA de 15 minutos, reduciendo a cero las pérdidas de venta por paros en caja de cobro.
