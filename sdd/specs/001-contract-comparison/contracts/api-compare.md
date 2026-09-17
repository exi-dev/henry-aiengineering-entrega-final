# API Contract: POST /api/compare

Canonical source: `docs/api-contract.md` — do not duplicate or redefine field
shapes here (constitution Principle II: Docs Are the Source of Truth). This file
is a short recap for implementation reference only.

## Recap

- **Route**: `POST /api/compare`, `multipart/form-data` (browser-set boundary;
  never hardcode `Content-Type`).
- **Request fields** (both required): `original_image` (File, `image/jpeg` |
  `image/png` | `application/pdf`), `amendment_image` (File, `image/jpeg` |
  `image/png` | `application/pdf`). A multi-page PDF is read in full (every page).
- **Success (200)**: `ContractChangeOutput` JSON —
  `sections_changed: string[]`, `topics_touched: string[]`,
  `summary_of_the_change: string`.
- **Errors**: always shaped `{"detail": ...}` —
  - `400` invalid/corrupt image or PDF
  - `422` missing required field (FastAPI default)
  - `500` OpenAI/LangChain/Pydantic failure

Full request/response examples and exact error payload shapes:
see `docs/api-contract.md` §2–4.
