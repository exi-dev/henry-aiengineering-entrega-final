---

description: "Task list for the Contract Comparison MVP"
---

# Tasks: Contract Comparison

**Input**: Design documents from `/specs/001-contract-comparison/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-compare.md, quickstart.md

**Tests**: Not requested for this MVP (per constitution Delivery Constraints — no test suite required); validation is manual via `quickstart.md`.

**Organization**: Tasks are grouped by user story, and within each story by track —
**Backend**, **LangChain** (the two agents), and **Frontend** — so each track can be
handed to a different agent/developer and run in parallel. Tasks on the same file
are sequential within their track; tracks touch different files and can proceed
concurrently once Phase 2 (Foundational) is done.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- File paths are exact and match `plan.md` / `docs/*.md`

## Path Conventions

- Backend: `backend/src/...` (FastAPI app, image parsing, Pydantic models)
- LangChain agents: `backend/src/agents/...` (contextualization + extraction agents)
- Frontend: `frontend/src/pages/index.astro` (single page, all 3 UI states)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create the project directory structure per plan.md: `backend/src/agents/`, `backend/data/test_contracts/`, `frontend/src/pages/`
- [X] T002 [P] Backend: create `backend/requirements.txt` with pinned versions for `fastapi`, `uvicorn`, `python-multipart`, `langchain`, `langchain-openai`, `openai`, `pydantic`, `langfuse` (also added `Pillow`, needed to detect corrupt images before calling the vision model)
- [X] T003 [P] Backend: create `backend/.env.example` with `OPENAI_API_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` placeholders (never commit a real `.env`)
- [X] T004 [P] Frontend: initialize the Astro project with `@astrojs/tailwind` in `frontend/` (`package.json`, `astro.config.mjs`, Tailwind config)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before any user story is implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Backend: create the `ContractChangeOutput` Pydantic model in `backend/src/models.py` with fields `sections_changed: List[str]`, `topics_touched: List[str]`, `summary_of_the_change: str` — per data-model.md, no field is optional, and an empty `sections_changed` list is valid
- [X] T006 [P] Backend: scaffold the FastAPI app instance in `backend/src/main.py` (per backend-spec Paso 0), with routing ready to receive multipart uploads
- [X] T007 [P] Backend: add a shared Langfuse client/tracer setup — implemented via `@observe` decorators (langfuse.decorators) plus the `langfuse.openai` client wrapper in `image_parser.py`/`main.py`, reading keys from `.env` — required because constitution Principle IV mandates a Langfuse span on every pipeline step
- [X] T008 [P] Frontend: create `frontend/src/pages/index.astro` skeleton with one container and three empty sections with ids `ui-form`, `ui-loading`, `ui-results`; only `ui-form` visible by default (Tailwind `hidden` class on the other two)

**Checkpoint**: Foundation ready — Backend, LangChain, and Frontend tracks can now proceed in parallel.

---

## Phase 3: User Story 1 - Compare two contracts and get the changes (Priority: P1) 🎯 MVP

**Goal**: Full 4-step backend pipeline plus a minimal working UI so an analyst can submit two contract images and see a structured comparison report.

**Independent Test**: Per `quickstart.md` — `curl -X POST http://localhost:8000/api/compare -F original_image=@... -F amendment_image=@...` returns a `ContractChangeOutput` JSON; or the same flow through the browser form.

### Backend track

- [X] T009 [P] [US1] Implement `parse_contract_image()` in `backend/src/image_parser.py`: validate JPEG/PNG, base64-encode, call GPT-4o Vision to transcribe the text faithfully, run once per image (original and amendment), wrapped in a Langfuse span (inputs, outputs, latency, tokens)
- [X] T012 [US1] Implement `POST /api/compare` in `backend/src/main.py`: accept multipart fields `original_image`/`amendment_image` (both required), run image_parser → contextualization_agent → extraction_agent → validate with `ContractChangeOutput.model_validate()` (or `response_format`), return 200 with the JSON (depends on T005, T009, T010, T011)
- [X] T013 [US1] Add error handling in `backend/src/main.py`: `400` with `{"detail": "..."}` for an invalid/corrupt image (per data-model.md ContractDocument rule "an invalid or corrupt file → 400"), rely on FastAPI's default `422` for a missing required field, `500` with `{"detail": "..."}` for an OpenAI/LangChain/Pydantic failure (depends on T012)

### LangChain track

- [X] T010 [P] [US1] Implement the contextualization agent in `backend/src/agents/contextualization_agent.py`: input is both parsed texts, output is a structural/context map only — it MUST NOT extract changes (constitution Principle IV) — wrapped in a Langfuse span
- [X] T011 [US1] Implement the extraction agent in `backend/src/agents/extraction_agent.py`: input is the context map (T010) plus both parsed texts (T009), output is additions/deletions/modifications ready for JSON, wrapped in a Langfuse span (depends on T009, T010 for their output shapes)

### Frontend track

- [X] T014 [US1] Build the `ui-form` section in `frontend/src/pages/index.astro`: file inputs `file-original` and `file-amendment` (`accept=".jpg,.jpeg,.png"`, `required`), submit button labeled "Analizar Documentos" (depends on T008)
- [X] T015 [US1] Build the `ui-results` section in `frontend/src/pages/index.astro`: `<p id="res-summary">`, `<ul id="res-sections">`, `<ul id="res-topics">` rendered as badges (depends on T008; same file as T014, sequential)
- [X] T016 [US1] Implement the submit handler script in `frontend/src/pages/index.astro`: `e.preventDefault()`, build `FormData` with keys `original_image`/`amendment_image`, `fetch('http://localhost:8000/api/compare', {method:'POST', body})` with no manual `Content-Type`, on success hide `ui-form`/show `ui-results` and inject `summary_of_the_change`/`sections_changed`/`topics_touched` via `textContent`/`innerHTML` (depends on T014, T015)

**Checkpoint**: User Story 1 is fully functional and independently testable — an analyst can get a comparison report end-to-end.

---

## Phase 4: User Story 2 - Know the system is working (Priority: P2)

**Goal**: A visible processing indicator covers the entire wait between submission and result.

**Independent Test**: Submit valid documents; confirm `ui-loading` appears immediately and hides `ui-form`, and disappears when the result (success or failure) is ready.

### Frontend track

- [X] T017 [US2] Build the `ui-loading` section in `frontend/src/pages/index.astro`: spinner using Tailwind `animate-spin` plus the text "Procesando documentos con IA..." (depends on T008)
- [X] T018 [US2] Wire the loading state into the submit handler in `frontend/src/pages/index.astro`: hide `ui-form`/show `ui-loading` immediately on submit; on a successful response hide `ui-loading` (depends on T016, T017)
- [X] T019 [US2] Implement the `catch` handler in the same submit script in `frontend/src/pages/index.astro`: on fetch failure, hide `ui-loading`, show `ui-form`, and trigger a generic `alert()` (FR-008) (depends on T018)

**Checkpoint**: User Stories 1 and 2 both work together.

---

## Phase 5: User Story 3 - Start a new comparison (Priority: P3)

**Goal**: The analyst can immediately start a new comparison after viewing a report.

**Independent Test**: From `ui-results`, trigger reset and confirm the form reappears empty and ready for new files.

### Frontend track

- [X] T020 [US3] Add the reset button `btn-reset` inside the `ui-results` section in `frontend/src/pages/index.astro` (depends on T015)
- [X] T021 [US3] Implement the reset click handler in `frontend/src/pages/index.astro`: hide `ui-results`, show `ui-form`, call the form's `reset()` to clear selected files (depends on T016, T020)

**Checkpoint**: All three user stories are independently functional together — the MVP is complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T022 [P] Add sample scanned contract images to `backend/data/test_contracts/` for manual validation — added synthetic `original.jpg`/`amendment.jpg` and `original.pdf`/`amendment.pdf` (not real scanned legal documents, but functional test fixtures with a deliberate clause change)
- [~] T023 Run the full `quickstart.md` validation (all 3 user stories + edge cases) end to end — backend verified for real: US1 success path (200 + correct report), 422 missing field, 400 corrupt image, 400 corrupt PDF, all against the live OpenAI API. Frontend (US2 loading state, US3 reset) was verified by code review only, not by driving a real browser — still needs a manual pass per `quickstart.md` §3–4
- [X] T024 [P] Document setup/run commands (`uvicorn`, `npm run dev`) in the root `README.md`, per the "setup, uso" deliverable already promised there

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational only
- **User Story 2 (Phase 4)**: Depends on Foundational + T016 (extends the same `index.astro` submit handler)
- **User Story 3 (Phase 5)**: Depends on Foundational + T015/T016 (extends the same `index.astro` results section)
- **Polish (Phase 6)**: Depends on the user stories being complete

### Within User Story 1 (the only phase with cross-track dependencies)

- T012 (endpoint wiring) depends on T005 (model), T009 (image parser), T010 (context agent), T011 (extraction agent)
- T013 (error handling) depends on T012
- T011 (extraction agent) depends on T009/T010 only for their agreed input shape, not on their code being merged — can be written in parallel and integrated at T012

### Parallel Opportunities — 3-agent orchestration

Once Phase 2 (Foundational) is checkpointed, hand off three parallel tracks:

```text
# Backend Agent (sequential within itself)
T009 → T012 → T013

# LangChain Agent (sequential within itself)
T010 → T011

# Frontend Agent (sequential within itself, covers US1 + US2 + US3)
T014 → T015 → T016 → T017 → T018 → T019 → T020 → T021
```

The Backend Agent and LangChain Agent must sync once (T009 and T010's output
shapes agreed) before the Backend Agent writes T012. The Frontend Agent has no
dependency on Backend/LangChain code — it only needs the contract in
`docs/api-contract.md` / `contracts/api-compare.md` — so it can run fully
concurrently with the other two tracks.

Within Setup and Foundational: T002/T003/T004 are parallel; T005/T006/T007/T008
are parallel (four different files).

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1 (Setup) → Phase 2 (Foundational)
2. Phase 3 (User Story 1) across the three tracks in parallel
3. **STOP and VALIDATE**: run `quickstart.md` §3 (and the `curl` check in §5.3)
4. This is already a demoable MVP

### Incremental Delivery

1. Foundation ready → hand off Backend/LangChain/Frontend agents for US1
2. US1 done → validate → demo (MVP)
3. Frontend Agent adds US2 (loading feedback) → validate → demo
4. Frontend Agent adds US3 (reset) → validate → demo
5. Phase 6 polish (sample data, quickstart run, README) → deliver

---

## Phase 7: Amendment — PDF Support (post-MVP-delivery)

**Reason**: User requested the ability to upload PDF, not just JPEG/PNG, for both
documents. Extends FR-002/FR-003 and `ContractDocument` (data-model.md); docs
(`docs/backend-spec.md`, `docs/frontend-spec.md`, `docs/api-contract.md`,
`README.md`, `AGENTS.md`) and the constitution (v1.0.1 → v1.0.2) were updated to
match before/alongside this code change, per constitution Principle II.

- [X] Backend: extend `backend/src/image_parser.py` to accept `.pdf` — render every
  PDF page to a PNG (via `pymupdf`) and send all pages in one GPT-4o Vision call;
  reject non-JPEG/PNG/PDF and corrupt PDFs with the same `ValueError` → `400` path
- [X] Backend: add `pymupdf==1.28.2` to `backend/requirements.txt`
- [X] Frontend: update both file inputs' `accept` in `frontend/src/pages/index.astro`
  to `.jpg,.jpeg,.png,.pdf`
- [X] Verified end-to-end with the real OpenAI API: single-page PDF comparison
  (200, correct diff), multi-page PDF (2 pages, both read), corrupt PDF (400)

**Bugs found and fixed while testing this feature** (kept here since they're not
separately tracked elsewhere):
- `pydantic==2.11.4` had no prebuilt wheel for the project's Python 3.14 venv →
  bumped to `pydantic==2.13.5` in `backend/requirements.txt`
- `contextualization_agent.py`/`extraction_agent.py` built `ChatOpenAI` at import
  time, crashing app startup without `OPENAI_API_KEY` — made lazy (`@lru_cache`)
- `uvicorn` needs `--env-file .env` to load the `.env` file at all — documented in
  `README.md`, `AGENTS.md`, and `quickstart.md`
