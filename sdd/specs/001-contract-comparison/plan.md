# Implementation Plan: Contract Comparison

**Branch**: `001-contract-comparison` | **Date**: 2026-09-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-contract-comparison/spec.md`

## Summary

Build the LegalMove MVP: a FastAPI backend running a 4-step pipeline (GPT-4o Vision
parsing → contextualization agent → extraction agent → Pydantic validation) behind
a single `POST /api/compare` endpoint, plus a single-page Astro frontend with the 3
states (`ui-form`, `ui-loading`, `ui-results`) that calls it. Scope, routes, field
names, and error shapes are already fixed by `docs/backend-spec.md`,
`docs/frontend-spec.md`, and `docs/api-contract.md` — this plan wires those already
-specified pieces together without adding anything beyond them.

## Technical Context

**Language/Version**: Python 3.11+ (backend); Node.js LTS + vanilla JavaScript (frontend via Astro)

**Primary Dependencies**: Backend — FastAPI, LangChain, Pydantic, Langfuse SDK, OpenAI SDK (GPT-4o Vision), Pillow (image validation), PyMuPDF (PDF-to-image rendering). Frontend — Astro, `@astrojs/tailwind`, no JS framework.

**Storage**: N/A — no persistence; each comparison is stateless, shown once (spec Assumptions).

**Testing**: None required for this MVP (per `AGENTS.md` and the constitution's Delivery Constraints); validated manually via `quickstart.md`.

**Target Platform**: Backend as a local/dev web server (uvicorn); frontend as a dev site in a desktop browser.

**Project Type**: Web application (existing `backend/` + `frontend/` split)

**Performance Goals**: None beyond covering the full wait with a processing indicator (FR-006); latency is dominated by GPT-4o Vision and is not optimized in this MVP.

**Constraints**: Exactly the 4-step pipeline, no extra agent/LLM calls (constitution III); contracts fixed field-for-field by `docs/api-contract.md` (constitution II); no test/CI tooling added (Delivery Constraints); secrets only via `.env.example`.

**Scale/Scope**: Single analyst, one comparison at a time, demo/delivery scale — not built for concurrent/production load.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
|---|---|---|
| I. MVP Simplicity First | Plan builds only the 3 UI states and 1 endpoint already specified; nothing speculative added | PASS |
| II. Docs Are the Source of Truth | Technical Context, data model, and contracts are taken verbatim from `docs/*.md`; no invented fields/routes | PASS |
| III. Token & Cost Efficiency | Pipeline stays at 4 steps, no added LLM calls; plan artifacts reference docs instead of duplicating them | PASS |
| IV. Strict Pipeline Separation | Structure keeps `image_parser.py`, both agents, and `models.py` separate; Langfuse spans required per step | PASS |
| Delivery Constraints | No test suite/CI introduced; `.env.example` only; existing stack and directories kept | PASS |

No violations — Complexity Tracking table is not needed.

**Post-Phase 1 re-check**: Design artifacts below (data-model.md, contracts/, quickstart.md) introduce no new entities, dependencies, or steps beyond what `docs/*.md` already define. All gates still PASS.

## Project Structure

### Documentation (this feature)

```text
specs/001-contract-comparison/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                          # FastAPI app + POST /api/compare
│   ├── image_parser.py                  # parse_contract_image() — GPT-4o Vision
│   ├── agents/
│   │   ├── contextualization_agent.py   # structure/context map only
│   │   └── extraction_agent.py          # change extraction only
│   └── models.py                        # ContractChangeOutput (Pydantic)
├── data/test_contracts/                 # sample images for manual testing
├── requirements.txt                     # pinned deps
└── .env.example                         # OpenAI + Langfuse keys (template)

frontend/
└── src/
    └── pages/
        └── index.astro                  # single view, 3 states, fetch to backend
```

**Structure Decision**: Web application option, matching the `backend/` and
`frontend/` directories that already exist (currently empty) and the exact file
layout mandated by `docs/backend-spec.md` ("Estructura de Entregables") and
`docs/frontend-spec.md` (§2). No `tests/` directory is added, per the
constitution's Delivery Constraints (no test suite required for this MVP).

## Complexity Tracking

*No violations — table omitted.*
