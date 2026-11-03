# 🎯 Conti Clasificador

**Enlace a la app:** [https://ljchuello-ia.streamlit.app/](https://ljchuello-ia.streamlit.app/)  
**Autor/a:** Leonardo Chuello

## Pitch

En Sermatick Cia Ltda, el equipo de soporte técnico de primera línea pierde tiempo valioso clasificando manualmente decenas de incidencias diarias sin un criterio unificado de urgencia. Conti Clasificador es una aplicación web que conversa mediante chat o procesa correos pegados para identificar el incidente y asignarle de inmediato un semáforo operativo de atención. La inteligencia artificial aporta extracción automática de datos de contacto y una evaluación objetiva de criticidad con tiempos máximos de respuesta (SLA). Durante las pruebas aprendimos que ante la duda entre un fallo crítico y una lentitud operativa, el modelo requería una «regla de oro» explícita para priorizar siempre el caso crítico y no minimizar riesgos. Como siguiente paso, integraríamos el clasificador directamente vía webhooks con el sistema de tickets interno para atender el 100% de los casos bombero en menos de 15 minutos.

## El problema

El personal de soporte de Sermatick recibe a diario mensajes desordenados por correo y mensajería de clientes de su sistema de facturación electrónica. Hoy en día, cada operador clasifica según su intuición subjetiva y escala incidentes a Producción sin un criterio de urgencia unificado, saturando a los desarrolladores con dudas operativas. Resolver esto merece la pena porque un error al timbrar una factura con clientes esperando en caja no puede demorarse, mientras que una consulta informativa no debe interrumpir el flujo del equipo técnico.

## Qué hace la app

1. **Inicia la conversación o pega un correo:** En la pestaña *Chat agéntico*, conversas con Conti, quien te saluda y hace una pregunta a la vez (quién eres, cómo contactarte y qué ocurrió). También puedes usar la pestaña *Pegar correo* para procesar un mensaje completo en un solo paso.
2. **Obtén la clasificación automática:** La app analiza el texto y genera una ficha con el semáforo de prioridad (🔴 Bombero: 15 min, 🟡 Cotidiano: mismo día, 🟢 Consulta: 24-48 h), un resumen, el motivo de la elección y acciones recomendadas.
3. **Confirma y guarda:** Valida los datos identificados (nombre, contacto y descripción) y pulsa *Confirmar y guardar* para registrar el caso como abierto.
4. **Gestiona y notifica:** En la pestaña *Gestión*, busca casos por texto o fíltralos por estado y semáforo. Con un clic en *Notificar*, obtienes el mensaje formateado con emoji y SLA listo para avisar al equipo de Producción.

## La pieza de IA

- **Qué usa:** API de modelos LLM mediante el SDK de OpenAI, configurado por defecto con `deepseek/deepseek-v4.1-flash-1017` a través de OpenRouter (compatible con OpenAI, Groq u Ollama).
- **Por qué esa opción:** Ofrece respuestas rápidas, de muy bajo coste y estructuradas estrictamente en JSON, permitiendo cambiar de proveedor o modelo modificando solo las credenciales sin alterar una sola línea de código.
- **Qué pasa si falla:** Si no se configura la clave de API, la app muestra un aviso amistoso (`Falta configurar LLM_API_KEY en .streamlit/secrets.toml 🔑`) sin romperse; ante errores de conexión o respuestas no legibles, devuelve un estado seguro por defecto evitando que la interfaz falle.

## Cómo la he construido

- **Herramientas:** Antigravity IDE (asistente de código con modelos Gemini), Streamlit para la interfaz web, Python 3.12 y Git/GitHub para el control de versiones.
- **Fichero de contexto del agente:** [AGENTS.md](AGENTS.md), donde se definen la regla de oro, la prohibición de sobreingeniería, el tono en español neutro con trato de tú y las convenciones del proyecto.
- **Prompts clave:**
  1. *Prompt del semáforo con regla de oro:* Define las fronteras de criticidad y la regla «si dudas entre rojo y amarillo, elige rojo».
  2. *Prompt conversacional de Conti:* Guía el diálogo turno a turno para hacer una pregunta a la vez sin abrumar al usuario.
  3. *Esquema JSON estricto:* Restringe la salida del modelo a un JSON estructurado (`pregunta` o `clasificacion` con `semaforo`, `nombre`, `contacto`, `resumen`, `motivo`, `acciones`).
- **Qué delegué al agente y qué revisé a mano:**
  - *Delegado al agente:* Estructura inicial de la interfaz en Streamlit, maquetación del selector de temas claro/oscuro con CSS inyectado y lógica de filtrado dinámico en la pestaña de gestión.
  - *Revisado a mano:* Calibración de los prompts para garantizar respuestas en español neutro sin voseo, simplificación radical del código eliminando clases y dependencias innecesarias (cumpliendo AGENTS.md), y gestión segura de secretos.

## Prueba y mejora

| Quién la probó | Qué probó | Qué pasó | Qué cambié |
|---|---|---|---|
| Operador de soporte (yo como usuario) | Ingresó: *"El sistema va lento pero todavía puedo emitir comprobantes"* | El modelo dudó y lo clasificó como Bombero por la mención de comprobantes. | Ajusté el prompt aclarando que lentitud operativa sin detención de venta es 🟡 Cotidiano. |
| Operador de soporte | Pegó un correo con datos incompletos y sin teléfono de contacto | La app generaba valores nulos o campos en blanco poco claros. | Hice que nombre y contacto sean opcionales y muestren "Sin nombre" y "Sin contacto" por defecto. |
| Desarrollador de Producción | Notificación de caso crítico generado por la app | El mensaje de aviso era extenso y requería resumirse manualmente. | Simplifiqué la función `notificar()` para emitir una sola línea estandarizada con emoji, nivel y SLA. |

## Ejecutar en local (opcional)

```bash
pip install -r requirements.txt
# Ruta A: pon la clave en .streamlit/secrets.toml y ejecuta
streamlit run app.py
# Ruta B: exporta la clave y ejecuta
export LLM_API_KEY="…" && streamlit run app.py
```

## Capturas

> 💡 *Espacio reservado para las capturas de la entrega (sin claves de API ni datos sensibles a la vista):*

1. **App funcionando:** Diálogo en el chat con Conti realizando preguntas y entregando la ficha de confirmación.
2. **Caso límite (regla de oro):** Ejemplo donde una duda entre lentitud y paro en facturación se clasifica automáticamente como 🔴 Bombero.
3. **Trabajo con la IA:** Uso del asistente en Antigravity siguiendo las directrices de `AGENTS.md`.
4. **Prueba y gestión:** Tabla de casos en la pestaña *Gestión* con filtros aplicados y caso notificado a Producción.
