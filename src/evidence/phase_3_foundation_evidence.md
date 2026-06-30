# Phase 3 — Governed Foundation Evidence

## Status

Partially demonstrated.

The implementation demonstrates a governed query-surface pattern for a discovery MVP. It does not claim a production-grade governed data foundation with enterprise ownership, full access enforcement, formal data quality assurance or operational monitoring.

## Foundation decision

Proceed to orchestration design and MVP build using approved analytics views and repository metadata.

The assistant should not query raw tables directly. It should operate through a controlled analytical layer with explicit metadata, known caveats and validation rules.

## Phase 3 intent for this implementation

Phase 3 answers one practical question:

> Is there a controlled data foundation that the Talk-to-Data system can safely query for the scoped discovery questions?

For this implementation, the answer is yes for the Le Figaro discovery MVP, with production gaps made explicit.

## Foundation summary

| Area | Current implementation | Status |
|---|---|---|
| Queryable assets | Approved analytics views exposed to the assistant | Demonstrated |
| Raw data access | Raw tables are not intended as the assistant query surface | Demonstrated |
| Metrics | Repository metadata defines supported metrics and interpretation context | Partially demonstrated |
| Dimensions | Supported dimensions are limited to approved views and metadata | Partially demonstrated |
| Joins and grain | Encapsulated mainly through analytics views rather than left to the model | Partially demonstrated |
| Filters and caveats | Captured through metadata, prompts and answer constraints | Partially demonstrated |
| Access controls | Role-aware behaviour may be demonstrated, but production access enforcement is not claimed | Production gap |
| Quality controls | Discovery-level checks and caveats exist; production-grade DQ assurance is not claimed | Partially demonstrated |
| Foundation ownership | Repository owner acts as discovery owner | Partially demonstrated |

## Governed query surface

| Principle | Implementation decision |
|---|---|
| Use approved assets | The assistant is expected to query approved analytics views only |
| Avoid raw-table reasoning | Business logic should be pushed into views and metadata, not inferred freely by the model |
| Reduce unsafe joins | Joins and grain should be handled in the governed SQL layer where possible |
| Keep SQL bounded | Generated SQL is later checked by deterministic validation rules |
| Preserve caveats | Known limitations should remain available to answer generation and evaluation |

## Metadata foundation

The implementation uses repository metadata to ground the model before SQL generation.

| Metadata type | Purpose |
|---|---|
| Schema descriptions | Help the system understand available views and columns |
| Metrics metadata | Define supported measures and interpretation context |
| Glossary | Clarify domain terms and synonyms |
| Example questions | Provide expected question patterns and regression cases |
| SQL scripts | Define the queryable analytical layer |

Primary locations: `src/metadata/`, `src/sql/`, `src/metadata/example_questions/`.

## Access and exposure view

| Area | Discovery decision |
|---|---|
| Data sensitivity | Low-sensitivity discovery dataset |
| User roles | Role-aware behaviour may be demonstrated |
| Production identity | Out of scope |
| Row-level security | Not claimed as production-ready |
| Main exposure risk | Misleading interpretation rather than sensitive data leakage |
| Production requirement | Enterprise identity, RLS or equivalent access enforcement, audit and security review |

## Foundation risks

| Risk | Foundation response |
|---|---|
| Model chooses unsafe tables | Restrict query generation to approved analytics views |
| Model invents metric logic | Use metadata and view logic rather than free-form prompt inference |
| Ambiguous grain or joins | Encapsulate grain and joins in views where possible |
| Misleading caveats | Keep caveats available through metadata and answer generation |
| Weak production access | Treat identity and row-level security as explicit production gaps |
| Data quality uncertainty | Carry quality and coverage caveats into validation |

## Phase 3 carry-forward gaps

| Gap | Impact |
|---|---|
| No enterprise data owner | Foundation is suitable for discovery, not organisational approval |
| No independent metric owner | Metric semantics are self-authored |
| Limited data quality assurance | Good enough for discovery, not production assurance |
| Production access enforcement not complete | Blocks enterprise release |
| Monitoring of upstream change not implemented | Would be required for live operation |
| Foundation scope is narrow | Intentional, but limits generalisation |

## Handover to later phases

| Later phase | Phase 3 handover |
|---|---|
| Phase 4 — Orchestration | Approved views, metadata sources, caveats and query boundaries |
| Phase 5 — MVP build | Queryable foundation, metadata files and SQL scripts |
| Phase 6 — Validation | Foundation assumptions, metric caveats, access gaps and quality limitations |
| Phase 7 — Pilot | Supported data scope and exclusions |
| Phase 8 — Production readiness | Access, ownership, monitoring and data-quality gaps to resolve |

## Phase 3 exit view

The governed foundation is sufficient for a bounded discovery MVP.

It provides a controlled query surface, metadata grounding and a clear separation between what the model may infer and what must be encoded or validated. It is not a production governed data foundation.

Suggested exit wording:

> Proceed to orchestration and MVP build using the approved Le Figaro analytics views and repository metadata. Treat enterprise data ownership, independent semantic approval, production access enforcement and production-grade data quality controls as future gaps.