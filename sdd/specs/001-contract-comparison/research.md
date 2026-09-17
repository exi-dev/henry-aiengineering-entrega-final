# Phase 0 Research: Contract Comparison

All technical unknowns are already resolved by the existing project docs — there
are no open `NEEDS CLARIFICATION` items in the Technical Context.

## Decisions

### Backend framework & pipeline
- **Decision**: FastAPI app exposing `POST /api/compare`; strict 4-step pipeline
  (image parsing → contextualization agent → extraction agent → Pydantic validation).
- **Rationale**: Mandated by `docs/backend-spec.md` and constitution Principle IV
  (Strict Pipeline Separation).
- **Alternatives considered**: None — the stack and flow are fixed by prior specs;
  re-deriving them would violate constitution Principle II (Docs Are the Source of Truth).

### Vision/text extraction
- **Decision**: GPT-4o Vision via the OpenAI SDK, called once per image (original,
  amendment), base64-encoded input.
- **Rationale**: `docs/backend-spec.md` Paso 1.
- **Alternatives considered**: Traditional OCR (e.g., Tesseract) — rejected; the
  spec requires GPT-4o Vision specifically for faithful transcription of scanned
  legal text.

### Agent orchestration
- **Decision**: LangChain implements the two agents (contextualization, extraction)
  as separate, single-purpose calls.
- **Rationale**: `docs/backend-spec.md` Pasos 2–3; constitution Principle IV forbids
  merging them.
- **Alternatives considered**: A single combined prompt — explicitly rejected by
  both the spec and the constitution.

### Output validation
- **Decision**: Pydantic model `ContractChangeOutput` (`sections_changed`,
  `topics_touched`, `summary_of_the_change`), validated via `model_validate()` or
  `response_format`.
- **Rationale**: `docs/backend-spec.md` Paso 4 and `docs/api-contract.md` §3.3.
- **Alternatives considered**: Manual JSON parsing — rejected, no schema guarantee.

### Observability
- **Decision**: A Langfuse span around every pipeline step (inputs, outputs,
  latency, tokens).
- **Rationale**: Explicitly required by `docs/backend-spec.md`; constitution
  Principle IV makes it non-negotiable, not optional polish.
- **Alternatives considered**: No tracing — rejected, it's a spec requirement.

### Frontend
- **Decision**: Astro single page (`index.astro`) with Tailwind, vanilla JS, and 3
  mutually-exclusive states toggled via the Tailwind `hidden` class.
- **Rationale**: `docs/frontend-spec.md` §1–4.
- **Alternatives considered**: A JS framework (React/Vue) — rejected; the spec
  calls for vanilla JS to keep the MVP simple (constitution Principle I).

### Testing approach
- **Decision**: No automated test suite; validation is manual via `quickstart.md`.
- **Rationale**: `AGENTS.md` states no toolchain/tests/CI exist yet; the
  constitution's Delivery Constraints only require documenting commands if tooling
  is *added*, and none is being added for this MVP.
- **Alternatives considered**: A pytest suite — rejected as scope creep for a
  delivery-focused MVP (constitution Principles I and III).
