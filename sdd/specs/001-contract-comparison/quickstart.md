# Quickstart: Validate Contract Comparison

## Prerequisites

- Python 3.11+, Node.js LTS
- OpenAI API key and Langfuse keys (copy `backend/.env.example` → `.env` and fill in)
- Two sample contract documents, JPEG/PNG or PDF: one "original", one "amendment"
  (see `backend/data/test_contracts/`)

## 1. Run the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000 --env-file .env
```

`--env-file .env` is required — uvicorn does not read `.env` on its own, and the
app will fail with an `OpenAIError` at request time if the keys aren't loaded.

## 2. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open the local URL the Astro dev server prints.

## 3. Validate User Story 1 — compare and get the changes

1. On the form (`ui-form`), select an original contract document and an amendment
   document (image or PDF, can mix formats), then submit.
2. Confirm the loading state (`ui-loading`: spinner + "Procesando documentos con
   IA...") appears immediately and hides the form (User Story 2 / FR-006).
3. Confirm the results view (`ui-results`) shows a summary (`res-summary`), a list
   of changed sections (`res-sections`), and topic badges (`res-topics`) (FR-005 /
   SC-002).

## 4. Validate reset — User Story 3

1. From `ui-results`, click reset (`btn-reset`).
2. Confirm the form reappears empty and `ui-results` is hidden (FR-009 / SC-004).

## 5. Validate error handling — edge cases

1. Submit a non-image/non-PDF file (e.g., a `.txt` renamed to `.jpg`) → expect a
   generic `alert()` and a return to `ui-form` (FR-008).
2. Try to submit with only one file selected → the browser's `required` attribute
   should block submission before it reaches the backend.
3. Submit a multi-page PDF as one of the documents → confirm the report reflects
   content from pages beyond the first (not just page 1).
4. (Optional, backend-only) confirm a `400` with `{"detail": ...}` on a corrupt file:

   ```bash
   curl -X POST http://localhost:8000/api/compare \
     -F "original_image=@bad.txt" -F "amendment_image=@bad.txt"
   ```

Full field names, IDs, and error shapes: `docs/api-contract.md`,
`docs/frontend-spec.md`, and this feature's `contracts/api-compare.md` /
`data-model.md`.
