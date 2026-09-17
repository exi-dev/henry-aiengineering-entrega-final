# 📄 Especificaciones del Backend: Comparador Autónomo de Contratos (LegalMove)

## 🎯 Objetivo Principal
Construir un **sistema multi-agente autónomo** que procese un contrato original y su adenda, entregados como **imágenes escaneadas (JPG/PNG) o PDF**.
El sistema extraerá el texto usando IA de visión y utilizará dos agentes especializados para **identificar, extraer y resumir los cambios legales**, devolviendo un reporte estructurado y validado.

---

## 🛠️ Stack Tecnológico
* **Framework Backend:** FastAPI (orquestación de la API)
* **Visión Multimodal:** OpenAI GPT-4o (procesamiento de imágenes a texto)
* **Orquestación de Agentes:** LangChain
* **Validación de Datos:** Pydantic
* **Observabilidad y Trazabilidad:** Langfuse

---

## 🏗️ Flujo de Ejecución (Pipeline)

### Paso 0: Scaffolding del Backend
* **Acción:** Inicialización de la aplicación **FastAPI**.
* **Detalle:** Configuración de rutas (endpoints) estructuradas para recibir las cargas de documentos (contrato original y adenda) e iniciar el proceso.

### Paso 1: Parsing Multimodal de Documentos
* **Archivo encargado:** `src/image_parser.py`
* **Función:** `parse_contract_image()`
* **Formatos aceptados:** JPEG, PNG o PDF.
* **Mecánica:**
  1. Recibe el archivo (imagen o PDF).
  2. Si es PDF, renderiza **cada página** como imagen (una sola llamada al modelo con todas las páginas, para no perder contenido en contratos multi-página); si ya es una imagen, se usa tal cual.
  3. Codifica la(s) imagen(es) en **base64**.
  4. Llama a **GPT-4o (Vision)** con todas las imágenes del documento en un solo mensaje.
* **Prompt:** Instruir al modelo para extraer el texto completo de la forma más fiel posible, tratando varias páginas como un único documento.
* **Ejecución:** Se corre dos veces (Original y Adenda).
* **Observabilidad:** Registrar inputs, outputs, latencia y tokens mediante **spans de Langfuse** en el pipeline principal.

### Paso 2: Agente 1 - Contextualización
* **Archivo encargado:** `src/agents/contextualization_agent.py`
* **Input:** Textos parseados de ambos documentos.
* **Responsabilidad:** Construir un mapa contextual. Identificar qué secciones existen, cómo se corresponden entre sí y el propósito general de cada bloque.
* **Output:** Análisis de estructura comparada (texto estructurado, funciona como contexto). 
* ⚠️ *Nota crítica: Este agente NO extrae cambios.*

### Paso 3: Agente 2 - Extracción de Cambios
* **Archivo encargado:** `src/agents/extraction_agent.py`
* **Input:** Mapa contextual del Agente 1 **+** Textos parseados de ambos documentos.
* **Responsabilidad exclusiva:** Identificar, aislar y describir cada cambio (adiciones, eliminaciones, modificaciones).
* **Output:** Formato listo para ser estructurado como JSON.

### Paso 4: Validación de Datos (Pydantic)
* **Archivo encargado:** `src/models.py`
* **Modelo:** `ContractChangeOutput`
* **Esquema Requerido:**
  * `sections_changed` (`List[str]`): Identificadores de secciones modificadas.
  * `topics_touched` (`List[str]`): Categorías legales/comerciales afectadas.
  * `summary_of_the_change` (`str`): Descripción detallada de los cambios.
* **Mecánica:** Validar el output del Agente 2 explícitamente con `model_validate()` o utilizando `response_format=ContractChangeOutput` en la llamada al LLM.

---

## 📂 Estructura de Entregables (Repositorio Público)

| Entregable | Archivo | Descripción |
| :--- | :--- | :--- |
| **Script principal** | `src/main.py` | Entry point que inicializa el pipeline completo. Integra FastAPI para recibir los inputs e iniciar el flujo. |
| **Agente 1** | `src/agents/contextualization_agent.py` | Agente de contextualización con system prompt y lógica propios. |
| **Agente 2** | `src/agents/extraction_agent.py` | Agente de extracción con system prompt y lógica propios. |
| **Utilidades de documento** | `src/image_parser.py` | Funciones de validación (imagen o PDF), render de páginas PDF, encoding base64 y llamadas multimodales (GPT-4o). |
| **Modelos Pydantic** | `src/models.py` | Modelo `ContractChangeOutput` con los tres campos requeridos. |
| **Documentos de prueba** | `data/test_contracts/` | Carpeta para almacenar imágenes/PDFs de ejemplo. |
| **Documentación** | `README.md` | Documentación completa (diagramas, arquitectura, setup, uso, decisiones técnicas). |
| **Dependencias** | `requirements.txt` + `.env.example` | Dependencias con versiones fijadas y template de variables de entorno. |