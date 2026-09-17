<!--
Sync Impact Report
- Version change: 1.0.1 → 1.0.2 (clarification, no principles added/removed)
- Modified principles: II. Docs Are the Source of Truth (400 now covers invalid/
  corrupt JPEG/PNG/PDF, not just images); IV. Strict Pipeline Separation (clarified
  that image_parser.py accepts PDF, rendering every page to an image before the
  single GPT-4o Vision call) — reflects the PDF-support feature added on top of
  docs/backend-spec.md, docs/frontend-spec.md, docs/api-contract.md
- Added sections: none
- Removed sections: none
- Deferred/TODO items: RATIFICATION_DATE unknown (original adoption date not provided)
- Templates checked: plan-template.md, spec-template.md, tasks-template.md, checklist-template.md
  read for compatibility; no updates required (they reference the constitution generically).
-->

# LegalMove MVP Constitution

## Core Principles

### I. MVP Simplicity First
Build only what `docs/backend-spec.md`, `docs/frontend-spec.md`, and `docs/api-contract.md`
require to demonstrate the contract-comparison flow end to end. No speculative
abstractions, config options, extra endpoints, or UI states beyond the 3 defined
(`ui-form`, `ui-loading`, `ui-results`). If a feature isn't needed to ship the MVP,
it does not get built.
**Rationale**: This is a scoped MVP for delivery, not a platform. Every extra layer
is time and tokens spent on something the evaluator won't ask for.

### II. Docs Are the Source of Truth
`README.md` and `docs/*.md` define the API shapes, field names, and pipeline steps.
Code MUST match them exactly: endpoint `POST /api/compare`, form fields
`original_image`/`amendment_image`, fixed frontend IDs (`file-original`,
`file-amendment`, `res-summary`, `res-sections`, `res-topics`, `btn-reset`), and
error responses always shaped `{"detail": ...}` with `400` (invalid/corrupt file —
JPEG/PNG/PDF), `422` (missing field, FastAPI default), `500` (OpenAI/LangChain/Pydantic failure).
Do not invent or "improve" contracts mid-implementation; if a doc is wrong or
incomplete, fix the doc first, then the code.
**Rationale**: Frontend and backend are built independently against these docs;
drift between them is the single biggest integration risk (see `AGENTS.md` gotchas).

### III. Token & Cost Efficiency
Minimize LLM calls and tokens both in the running system and in the development
process. In the product: don't add extra GPT-4o Vision calls or agent round-trips
beyond the required 4-step pipeline (parse → contextualize → extract → validate).
In development: prefer small, targeted changes over broad rewrites, and avoid
generating unnecessary documentation, boilerplate, or exploratory scaffolding.
**Rationale**: Vision/LLM calls cost real money per token, and the team explicitly
wants a lean delivery process, not gold-plating.

### IV. Strict Pipeline Separation
The four backend steps stay separate and single-purpose: `image_parser.py` only
transcribes (run once per document, original and amendment — a PDF is rendered
page-by-page to images first, all pages sent in that one call); the contextualization
agent only maps structure (it MUST NOT extract changes); the extraction agent only
identifies changes (additions/deletions/modifications); `models.py` only validates
against `ContractChangeOutput` (`sections_changed: List[str]`,
`topics_touched: List[str]`, `summary_of_the_change: str`) via `model_validate()`
or `response_format`. Do not merge agent responsibilities into one prompt or
function. Every step MUST emit a Langfuse span (inputs, outputs, latency, tokens).
**Rationale**: The contextualize-then-extract split is the core design decision of
this system (per `README.md`); merging steps degrades accuracy and traceability.
Tracing is required by `docs/backend-spec.md`, not optional polish.

## Delivery Constraints

No test suite, linter, or CI is required for this MVP (per `AGENTS.md`). If any
tooling is added, the exact commands MUST be documented in `AGENTS.md` at the same
time. Secrets (OpenAI, Langfuse keys) are provided via `.env.example` only; `.env`
is never committed. Backend and frontend remain in their existing `backend/` and
`frontend/` directories with the stack already chosen (FastAPI/LangChain/Pydantic/
Langfuse; Astro/Tailwind/vanilla JS) — do not swap frameworks mid-project.

## Governance

This constitution governs how work on the LegalMove MVP is planned and built; it
takes precedence over ad hoc preferences when the two conflict. Amendments happen
by editing this file directly, bumping the version per semantic rules (MAJOR: a
principle is removed or reversed; MINOR: a principle or section is added; PATCH:
wording/clarification only), and updating `Last Amended`. Any plan, spec, or task
list produced by Spec Kit commands MUST stay consistent with these principles —
where a conflict is found, simplify the plan rather than amend the constitution,
unless the user explicitly requests a scope change.

**Version**: 1.0.2 | **Ratified**: TODO(RATIFICATION_DATE): original adoption date not provided | **Last Amended**: 2026-09-17
