# ⚖️ LegalMove MVP - Agente Autónomo de Comparación de Contratos

## 📌 El Problema
Actualmente, el equipo de Compliance invierte **más de 40 horas a la semana** comparando manualmente contratos originales con sus adendas para identificar cambios y evaluar impactos legales. Este proceso es lento, propenso a errores humanos y representa un cuello de botella crítico para la escalabilidad del negocio.

## 🚀 La Solución
Un **Agente Autónomo de Comparación de Contratos**. 
Este sistema recibe los documentos como imágenes escaneadas o PDF, extrae el texto mediante IA de visión y orquesta un equipo de **agentes virtuales** para entender el contexto y extraer de forma precisa las cláusulas modificadas.

El resultado es un **reporte estructurado y validado (JSON)**, con trazabilidad completa y listo para ser consumido por los sistemas de LegalMove.

---

## 🛠️ Stack Tecnológico

### Backend (Lógica y Agentes)
* **Framework:** FastAPI
* **Visión Multimodal:** OpenAI GPT-4o
* **Orquestación:** LangChain
* **Validación de Datos:** Pydantic
* **Observabilidad:** Langfuse

### Frontend (Interfaz de Usuario)
* **Framework:** Astro
* **Estilos:** Tailwind CSS
* **Lógica:** Vanilla JavaScript (SPA simulada en una única ruta)

---

## 🧠 Arquitectura del Sistema (Pipeline)

El núcleo del backend funciona a través de un flujo estructurado de procesamiento y análisis en 4 pasos:

1. **Parsing Multimodal (`image_parser.py`):**
   Recibe los documentos (original y adenda) como imagen o PDF. Si es PDF, renderiza cada página a imagen primero. Codifica en base64 y utiliza **GPT-4o (Vision)** para extraer el texto de forma fiel. Se registra la latencia y tokens en Langfuse.
2. **Agente de Contextualización (`contextualization_agent.py`):** 
   Analiza los textos extraídos para construir un mapa contextual. Identifica las secciones existentes y su correspondencia. *(Nota: Este agente NO extrae cambios, solo entiende la estructura).*
3. **Agente de Extracción (`extraction_agent.py`):** 
   Utiliza el mapa contextual y los textos para identificar, aislar y describir explícitamente cada cambio (adiciones, eliminaciones o modificaciones).
4. **Validación de Datos (`models.py`):** 
   Filtra y valida el output del Agente de Extracción asegurando que cumpla estrictamente con el esquema `ContractChangeOutput` requerido usando Pydantic.

---

## 🔌 API de Integración

El sistema expone un endpoint principal para el análisis.

* **Ruta:** `/api/compare`
* **Método:** `POST`
* **Content-Type:** `multipart/form-data`
* **Payload (Body):**
  * `original_image` (File - JPG/PNG/PDF): Contrato original.
  * `amendment_image` (File - JPG/PNG/PDF): Adenda.

### Respuesta Exitosa (200 OK)
Devuelve un JSON estrictamente validado:
```json
{
  "sections_changed": [
    "Cláusula 3.1: Términos de Pago",
    "Sección 5: Confidencialidad"
  ],
  "topics_touched": [
    "Financiero",
    "Privacidad de Datos"
  ],
  "summary_of_the_change": "Se modificó el plazo de pago de 30 a 60 días y se agregaron nuevas restricciones sobre el manejo de datos de terceros."
}
```

### Manejo de Errores
* **400 Bad Request:** Archivo no válido o corrupto.
* **422 Unprocessable Entity:** Faltan campos requeridos.
* **500 Internal Server Error:** Fallos en la IA, LangChain o validación de formato.

---

## 🖥️ Interfaz de Usuario (Frontend)

La interfaz construida en **Astro** (`index.astro`) funciona con tres estados visuales que otorgan una experiencia fluida:

* **📤 Estado 1 (Formulario - `ui-form`):** Inputs de carga para los dos documentos.
* **⏳ Estado 2 (Carga - `ui-loading`):** Spinner animado mientras la IA procesa los contratos.
* **✅ Estado 3 (Resultados - `ui-results`):** Visualización clara del resumen, lista de secciones modificadas y etiquetas (badges) de los temas afectados.

---

## ⚙️ Setup y Uso

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # completar OPENAI_API_KEY y credenciales de Langfuse
uvicorn src.main:app --reload --port 8000 --env-file .env
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Abre la URL que imprime el servidor de desarrollo de Astro y usa el formulario para subir un contrato original y su enmienda (JPG/PNG/PDF). El frontend llama a `http://localhost:8000/api/compare`, así que el backend debe estar corriendo primero.

No hay suite de tests ni linter configurados para este MVP; la validación es manual (ver `sdd/specs/001-contract-comparison/quickstart.md`).

---

