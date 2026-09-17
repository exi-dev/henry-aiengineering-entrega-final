# Phase 1 Data Model: Contract Comparison

No entity here is persisted — everything lives only for the duration of one
`POST /api/compare` request (spec Assumptions: no persistence).

## ContractDocument (transient)

Represents one uploaded file (image or PDF) during a single request.

| Field | Type | Notes |
|---|---|---|
| role | enum(`original`, `amendment`) | Which side of the comparison |
| file | binary (JPEG/PNG/PDF) | Raw upload; validated by content-type/extension |
| page_images | List[binary] | For a PDF, each page rendered to a PNG before parsing; for an image, a single-element list holding the image itself |
| extracted_text | string | Output of GPT-4o Vision parsing across all `page_images` in one call (backend-spec Paso 1) |

Validation rules (FR-002; `docs/api-contract.md` §2.2):
- Both `original` and `amendment` are required; a request missing either is
  rejected with `422`.
- Only `image/jpeg` / `image/png` / `application/pdf` accepted; an invalid or
  corrupt file (including a PDF that fails to open or has zero pages) → `400`.

## ContextMap (internal, agent-to-agent only)

Intermediate output of the contextualization agent; consumed only by the
extraction agent. Never exposed in any contract or response.

| Field | Type | Notes |
|---|---|---|
| structure | structured text | Section correspondence between the two documents; contains no change data — the contextualization agent MUST NOT extract changes (constitution Principle IV) |

## ContractChangeOutput (a.k.a. Comparison Report)

The structured, validated result returned to the client. Matches
`docs/api-contract.md` §3.2 exactly.

| Field | Type | Notes |
|---|---|---|
| sections_changed | List[str] | Section/clause identifiers that changed (FR-004, FR-005) |
| topics_touched | List[str] | Affected categories (e.g., "Financiero", "Privacidad de Datos") |
| summary_of_the_change | str | Plain-language description of the change |

Validation rules:
- Produced only by `models.py::ContractChangeOutput`, via `model_validate()` or
  `response_format` (constitution Principle IV).
- No field is optional; an empty `sections_changed` list is valid (edge case: no
  detected differences).

There are no state transitions — each request is a one-shot pipeline run.
