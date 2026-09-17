# Especificación frontend

## 1. Contexto y stack

- Proyecto: Frontend MVP para LegalMove (Comparador de Contratos con IA).
- Framework: Astro (versión más reciente, inicialización básica).
- Estilos: Tailwind CSS (integración oficial de `@astrojs/tailwind`).
- Lógica de cliente: JavaScript vanilla con etiqueta `<script>` en Astro.
- Arquitectura: SPA simulada en una única ruta estática.

---

## 2. Estructura de archivos requerida

- `src/pages/index.astro`: única vista de la aplicación. Debe contener el HTML, las clases de Tailwind y el script del cliente.

---

## 3. Interfaz de usuario (estados)

La vista `index.astro` debe implementar un único contenedor principal con 3 secciones mutuamente excluyentes, controladas mediante la clase `hidden` de Tailwind.

### Estado 1: Formulario (`ui-form`)

Inputs:

- Input tipo file para "Contrato Original" con id `file-original`, `accept: .jpg, .jpeg, .png, .pdf` y `required`.
- Input tipo file para "Enmienda" con id `file-amendment`, `accept: .jpg, .jpeg, .png, .pdf` y `required`.

Acción:

- Botón de tipo submit con texto: "Analizar Documentos".

### Estado 2: Carga (`ui-loading`)

- Indicador: spinner animado con Tailwind `animate-spin`.
- Texto descriptivo: "Procesando documentos con IA...".
- Condición: se muestra inmediatamente al disparar el evento `submit` del formulario y oculta el Estado 1.

### Estado 3: Resultados (`ui-results`)

Elementos a renderizar a partir de la respuesta del backend:

- Resumen: etiqueta `<p>` con id `res-summary`, mostrando `summary_of_the_change`.
- Secciones modificadas: etiqueta `<ul>` con id `res-sections`, renderizando elementos `<li>` por cada valor de `sections_changed`.
- Temas afectados: etiqueta `<ul>` con id `res-topics`, renderizando elementos `<li>` con estilo de badges/etiquetas visuales por cada valor de `topics_touched`.
- Acción: botón con id `btn-reset` para reiniciar la aplicación, ocultando el Estado 3, mostrando el Estado 1 y limpiando el formulario.

---

## 4. Lógica de cliente (script en Astro)

El `<script>` dentro de `index.astro` debe implementar el siguiente flujo:

### Captura del DOM

Obtener referencias a:

- formulario
- contenedores de estado
- nodos de resultados

### Event listener `submit`

1. Prevenir el comportamiento por defecto con `e.preventDefault()`.
2. Ocultar `ui-form` y mostrar `ui-loading`.
3. Instanciar `FormData`.
4. Agregar `file-original` bajo la clave `original_image`.
5. Agregar `file-amendment` bajo la clave `amendment_image`.

### Petición HTTP (`fetch`)

- Endpoint: `http://localhost:8000/api/compare`
- Método: `POST`
- Body: instancia de `FormData`
- Importante: no setear `Content-Type`; dejar que el navegador asigne el boundary `multipart`.

### Manejo de respuesta

- Parsear JSON.
- Ocultar `ui-loading` y mostrar `ui-results`.
- Inyectar los datos en el DOM con `textContent` e `innerHTML` según corresponda.

### Manejo de errores

- En el bloque `catch`:
  - ocultar `ui-loading`
  - mostrar `ui-form`
  - lanzar un `alert()` genérico de error de procesamiento.

### Reset

- Añadir un event listener al botón de reset para volver al estado inicial.

---

## 5. Esquema de datos esperado del backend

El frontend debe asumir que el backend devolverá un JSON estricto validado por Pydantic con la siguiente estructura exacta:

```json
{
  "sections_changed": ["string"],
  "topics_touched": ["string"],
  "summary_of_the_change": "string"
}
```