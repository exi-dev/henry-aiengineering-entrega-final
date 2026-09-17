# Feature Specification: Contract Comparison

**Feature Branch**: `001-contract-comparison`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "revisa los documentos, estamos creando un mvp por lo que no debe ser algo muy elaborado ni de sobreingenieria, que mantenga solo la funcionalidad" — build the LegalMove MVP as described in README.md / docs/*.md: compare a scanned original contract against its amendment and return a structured summary of what changed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Compare two contracts and get the changes (Priority: P1)

A Compliance analyst has an original contract and its amendment, each as a scanned
image or a PDF. They submit both documents and receive a structured report
describing what changed, so they don't have to compare the documents clause by
clause by hand.

**Why this priority**: This is the entire value of the product. Without it there is
no MVP — everything else is presentation around this single capability.

**Independent Test**: Submit one original contract image and one amendment image;
verify a report is returned listing the changed sections, the topics affected, and
a plain-language summary.

**Acceptance Scenarios**:

1. **Given** valid scanned images of an original contract and its amendment, **When**
   the analyst submits both, **Then** the system returns a report with the changed
   sections, affected topics, and a summary of what changed.
2. **Given** a report has been returned, **When** the analyst reads it, **Then** the
   summary accurately reflects the substantive differences between the two documents
   (no unrelated or fabricated changes).

---

### User Story 2 - Know the system is working (Priority: P2)

While the comparison is running, the analyst sees a clear indication that the system
is processing their documents, so they don't resubmit or think the tool is broken.

**Why this priority**: Comparison takes noticeable time (multiple AI steps). Without
feedback, users abandon or double-submit.

**Independent Test**: Submit a valid pair of documents and confirm a processing
indicator appears immediately and remains visible until the report (or an error) is
shown.

**Acceptance Scenarios**:

1. **Given** the analyst has submitted both documents, **When** processing starts,
   **Then** a processing indicator is shown and the submission form is hidden.
2. **Given** processing finishes (success or failure), **When** the result is ready,
   **Then** the processing indicator disappears and is replaced by the report or an
   error message.

---

### User Story 3 - Start a new comparison (Priority: P3)

After reviewing a report, the analyst wants to compare another pair of documents
right away, without reloading the page.

**Why this priority**: Analysts process many contracts in a session; this removes
friction but the product is still usable without it (manual page reload).

**Independent Test**: From the results view, trigger "start over" and verify the
submission form reappears empty and ready for new files.

**Acceptance Scenarios**:

1. **Given** a report is displayed, **When** the analyst chooses to start over,
   **Then** the report is hidden, the submission form is shown, and any previously
   selected files are cleared.

---

### Edge Cases

- Submitting a file that is not a JPEG/PNG/PDF, or a corrupted file → user sees a
  clear error and can retry; the system does not crash.
- Submitting a multi-page PDF → all pages are read as one document, not just the
  first page.
- Submitting with one or both documents missing → user is told the documents are
  required.
- The comparison fails partway through (extraction/analysis error) → user sees a
  generic failure message and can retry; no partial or malformed report is shown.
- Documents contain no detectable differences → report still returns, with an empty
  or minimal set of changes rather than an error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST let a user submit exactly two documents per comparison:
  one "original contract" and one "amendment".
- **FR-002**: System MUST only accept JPEG, PNG, or PDF for both documents, and
  both MUST be provided before a comparison can run.
- **FR-003**: System MUST extract the readable text content from each submitted
  document, including every page when the document is a multi-page PDF.
- **FR-004**: System MUST compare the two documents' content and identify which
  sections/clauses changed between the original and the amendment.
- **FR-005**: System MUST return a structured report containing: the list of
  changed sections, the list of topics/categories affected, and a plain-language
  summary of the changes.
- **FR-006**: System MUST show a visible processing indicator for the entire
  duration between submission and result (success or failure).
- **FR-007**: System MUST display the report to the user once the comparison
  completes successfully.
- **FR-008**: System MUST show a clear, non-technical error message — and return to
  a submittable state — if the documents are invalid, missing, or the comparison
  fails for any reason.
- **FR-009**: Users MUST be able to reset the interface after viewing a report (or
  an error) to submit a new pair of documents without reloading the page.
- **FR-010**: System MUST NOT require user accounts, login, or any identity
  information to perform a comparison.

### Key Entities

- **Contract Document**: A single uploaded file (image or PDF) representing either
  the "original" contract or the "amendment"; relevant attributes are its role
  (original vs. amendment), its format, and its extracted text content.
- **Comparison Report**: The structured result of comparing two Contract Documents;
  made up of the changed sections, the topics touched, and a summary of the change.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time user can obtain a comparison report from two contract
  documents (image or PDF) without any training or outside help.
- **SC-002**: 100% of successful comparisons return a report containing all three
  expected elements: changed sections, topics touched, and a summary.
- **SC-003**: 100% of invalid submissions or processing failures result in a clear,
  visible message — never a blank screen or an unhandled crash.
- **SC-004**: A user can go from viewing one report to submitting the next
  comparison in under 10 seconds, without reloading the page.

## Assumptions

- Single-user, no-login MVP: no accounts, roles, or permissions are required — this
  matches the constitution's MVP Simplicity First principle and nothing in the
  source docs mentions authentication.
- Exactly one original and one amendment are compared at a time; multi-document or
  batch comparison is out of scope for this MVP.
- Uploaded documents and generated reports are not persisted or retrievable later;
  each comparison is a one-off, shown once in the browser session.
- Users work from a desktop browser; mobile-specific layout is out of scope.
