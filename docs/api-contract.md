# Contrato de API - LegalMove MVP

Este documento define la interfaz de comunicación entre el frontend (Astro) y el backend (FastAPI) para el procesamiento y comparación de contratos mediante agentes de IA.

---

## 1. Información general del endpoint

- **Ruta:** `/api/compare`
- **Método:** `POST`
- **Descripción:** Recibe dos documentos (contrato original y adenda), como imagen escaneada o PDF, orquesta los agentes de IA para su análisis y devuelve un JSON estructurado con los cambios identificados.

---

## 2. Petición (Request)

### 2.1 Headers

- `Content-Type`: `multipart/form-data`

> El navegador o cliente debe generar el boundary automáticamente; no debe fijarse manualmente.

### 2.2 Body (Form-Data)

La petición debe incluir obligatoriamente los siguientes campos como archivos binarios:

| Clave | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `original_image` | `File` | `image/jpeg`, `image/png`, `application/pdf` | Contrato original, como imagen escaneada o PDF. |
| `amendment_image` | `File` | `image/jpeg`, `image/png`, `application/pdf` | Adenda o enmienda, como imagen escaneada o PDF. |

> Un PDF con varias páginas se procesa completo (todas las páginas se transcriben como un solo documento).

---

## 3. Respuesta exitosa (Response 200 OK)

### 3.1 Headers

- `Content-Type`: `application/json`

### 3.2 Body (JSON Schema)

La respuesta exitosa siempre devolverá un objeto JSON validado por Pydantic (`ContractChangeOutput`), con la siguiente estructura estricta:

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

### 3.3 Tipos de datos (Pydantic model)

- `sections_changed` (`List[str]`): Lista de identificadores o títulos de las secciones que sufrieron modificaciones.
- `topics_touched` (`List[str]`): Lista de categorías comerciales o legales afectadas (por ejemplo: Riesgo, Financiero, SLA).
- `summary_of_the_change` (`str`): Párrafo descriptivo que explica exactamente qué cambió entre ambos documentos.

---

## 4. Manejo de errores (Error Responses)

El backend debe responder con los siguientes códigos HTTP en caso de falla, devolviendo siempre un JSON con el detalle del error en la clave `detail`.

### 4.1 `400 Bad Request`

Cuando el archivo enviado no es una imagen/PDF válido o está corrupto.

```json
{
  "detail": "El archivo debe ser formato JPEG, PNG o PDF (.jpg, .jpeg, .png, .pdf)."
}
```

### 4.2 `422 Unprocessable Entity`

Validación de FastAPI cuando faltan los campos requeridos en el `multipart/form-data`.

```json
{
  "detail": [
    {
      "loc": ["body", "amendment_image"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 4.3 `500 Internal Server Error`

Cuando ocurre un fallo en el procesamiento de OpenAI, en el pipeline de LangChain o en la validación de Pydantic post-extracción.

```json
{
  "detail": "Error en el agente de extracción: fallo al generar el formato JSON requerido."
}
```
