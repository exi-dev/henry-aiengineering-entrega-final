# AGENTS.md — LegalMove Contract-Compare MVP

Implemented repo (not greenfield). Source of truth: `docs/` + `README.md` + `sdd/specs/001-contract-comparison/quickstart.md`. Don't invent APIs.

## Layout

- `backend/src/main.py` — FastAPI entrypoint, `POST /api/compare`. Run from `backend/` (imports are `src.*`).
- `backend/src/image_parser.py` — `parse_contract_image()` (validate → base64 → GPT-4o Vision).
- `backend/src/agents/contextualization_agent.py` — `build_context_map()`; `extraction_agent.py` — `extract_changes()`.
- `backend/src/models.py` — `ContractChangeOutput`. Fixtures: `backend/data/test_contracts/` (`original.jpg/.pdf`, `amendment.jpg/.pdf`).
- `frontend/src/pages/index.astro` — single view (Astro + `@astrojs/tailwind`, vanilla JS).

## Commands

```bash
cd backend && pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000 --env-file .env   # must run from backend/, --env-file required
cd frontend && npm install && npm run dev   # Astro default http://localhost:4321
```

No tests, lint, typecheck, or CI. Validation is manual per `sdd/.../quickstart.md` (form → loading → results → reset → corrupt-file `alert()` → multi-page PDF check). No `backend/.env.example` exists despite quickstart referencing it — required keys are `OPENAI_API_KEY` + Langfuse keys; never commit `backend/.env`.

## Backend pipeline — strict order, keep roles separate

1. `parse_contract_image()` ×2 (original + amendment): suffix check (`.jpg/.jpeg/.png/.pdf`) → content check (Pillow `verify()`+`load()`; PyMuPDF for PDFs) → `ValueError` on bad file. PDF rendered every page to PNG @200 DPI, all pages in one `gpt-4o` (`temperature=0`) Vision call via Langfuse `OpenAI` wrapper; truncated/empty transcription raises `RuntimeError`.
2. `build_context_map(original_text, amendment_text)` → structural map only. Must NOT extract changes (enforced in system prompt + module docstring).
3. `extract_changes(context_map, original_text, amendment_text)` → additions/deletions/modifications via `with_structured_output(ContractChangeOutput)` + `model_validate()`.
4. `main.py`: `compare_contracts` → `_validate_output()`; `ValueError` → 400 `{detail}`, any other exception → 500, missing field → FastAPI automatic 422.

LangChain chains built lazily in `_get_chain()` (`lru_cache`) so import/app start works without `OPENAI_API_KEY`; don't move LLM construction to module top level. Observability via `@observe` spans + `langfuse_context.get_current_langchain_handler()`.

## API contract — exact names (`docs/api-contract.md`)

- `POST /api/compare`, `multipart/form-data` (browser sets boundary; never hardcode `Content-Type`).
- Fields: `original_image`, `amendment_image` (jpeg/png/pdf). 200 → `ContractChangeOutput{sections_changed: List[str], topics_touched: List[str], summary_of_the_change: str}` exactly. Errors always `{detail: ...}`.

## Frontend contract (`docs/frontend-spec.md`)

- 3 mutually exclusive states via Tailwind `hidden`: `ui-form` → `ui-loading` (spinner `animate-spin` + "Procesando documentos con IA...") on `submit` → `ui-results`.
- Fixed IDs: `file-original` + `file-amendment` (`accept=".jpg,.jpeg,.png,.pdf"`, `required`), submit "Analizar Documentos", `res-summary` (`<p>`), `res-sections` (`<ul>`/`<li>`), `res-topics` (`<ul>`/`<li>` badges), `btn-reset` (hide results, show form, `form.reset()`).
- Script: `e.preventDefault()` → `FormData` keys `original_image`/`amendment_image` → `fetch('http://localhost:8000/api/compare', {method:'POST', body})` with no `Content-Type` → `textContent`/`createElement('li')`. `catch`: hide loading, show form, generic `alert()`.

## Gotchas

- Field-name mismatch (`file-original` vs `original_image`) is the #1 integration bug: input IDs stay frontend names, FormData keys must be API names.
- CORS in `main.py` allows only `http://localhost:4321` + `POST` — Astro must run on that origin or the browser blocks the call.
- `uvicorn` does NOT read `.env` — omit `--env-file .env` and keys are unset, failing at request time with `OpenAIError`.
- Don't merge the two agents into one prompt; contextualize-then-extract split is the core design.
- Don't send only the first PDF page — all pages go in a single Vision call.
