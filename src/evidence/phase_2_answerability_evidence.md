# Phase 2 — Answerability Evidence

## Status

Partially demonstrated.

The discovery project has enough data and semantic evidence to support a bounded MVP on Le Figaro article analytics. It does not claim enterprise-grade data ownership, independent semantic approval or production access readiness.

## Readiness decision

Proceed to governed foundation and MVP build for a narrow answerable question set.

The decision is based on curated Le Figaro article and comment data, approved analytics views, repository metadata and golden questions.

## Phase 2 intent for this implementation

Phase 2 answers one practical question:

> Can the scoped questions be answered safely enough from known data, definitions, views, filters and caveats to justify building a governed Talk-to-Data MVP?

For this discovery implementation, the answer is yes for the curated question set, with caveats.

## Answerability summary

| Area | Assessment | Status |
|---|---|---|
| Source readiness | Le Figaro article and comment data is available through the companion harvester project | Partially demonstrated |
| Question coverage | Golden questions define the supported analytical patterns | Demonstrated |
| Data model readiness | Approved analytics views provide a bounded query surface | Partially demonstrated |
| Metric readiness | Repository metadata supports interpretation | Partially demonstrated |
| Metadata readiness | Schema, metric and glossary files support grounding | Demonstrated |
| Access readiness | Role-aware behaviour may be demonstrated, but production access control is out of scope | Production gap |
| Overall MVP readiness | Sufficient for discovery MVP; not sufficient for enterprise pilot or production | Partially demonstrated |

## Candidate answerability matrix

| Question / pattern | Source route | MVP decision | Caveat |
|---|---|---|---|
| Article ranking | Approved article analytics views | Include | Ranking depends on available harvested data and selected metric |
| Comment volume | Approved comment analytics views | Include | Comment volume is not a full measure of readership or engagement |
| Publication trends | Approved article analytics views | Include | Date logic must remain explicit |
| Section comparison | Approved article and section views | Include with caveat | Section/category consistency depends on source data |
| Period-based analysis | Approved time-based views | Include with caveat | Published date, collected date and comment date may imply different answers |
| Data-quality or coverage questions | Metadata and available data-quality outputs | Include with caveat | Discovery-level checks only |
| Unsupported broad analysis | None | Exclude | Should trigger refusal or clarification |
| Sensitive or identity-level questions | None | Exclude | Not supported in this MVP |
| Forecasting / causal explanation | None | Exclude | Should not be inferred from descriptive analytics |

## Main semantic risks

| Risk | Discovery response |
|---|---|
| “Performance” is ambiguous | Clarify or map to supported metrics such as comment volume, publication count or ranking |
| Comment volume can be overinterpreted | Treat comments as one engagement signal, not full readership |
| Date fields can change the answer | Keep date logic explicit in views, SQL and answers |
| Section/category labels may be inconsistent | Use metadata and caveats rather than free interpretation |
| Missing harvested data may affect results | Treat coverage and freshness as caveats |
| Unsupported causal claims | Refuse or caveat; do not infer causality from descriptive outputs |

## Evidence used

Primary implementation evidence is in `src/metadata/example_questions/`, `src/metadata/`, `src/sql/`, `src/evaluation_results/` and `src/README.md`.

## Phase 2 carry-forward gaps

| Gap | Impact |
|---|---|
| Independent answerability review | Questions, metadata and assumptions are self-authored |
| Semantic approval | No business forum has approved metric definitions |
| Data quality assurance | Discovery checks are not production-grade |
| Production access model | Identity and row-level security are not implemented as enterprise controls |
| Broader domain coverage | Deliberately excluded to keep discovery focused |

## Handover to later phases

| Later phase | Phase 2 handover |
|---|---|
| Phase 3 — Governed foundation | Approved analytics views, metadata, caveats and known data risks |
| Phase 4 — Orchestration | Query boundaries, clarification needs, refusal cases and grounding requirements |
| Phase 5 — MVP build | MVP-ready question set, source mappings and known limitations |
| Phase 6 — Validation | Golden questions, expected-answer sources, caveat cases and failure categories |

## Phase 2 exit view

The scoped Le Figaro discovery use case is answerable enough to proceed to governed foundation and MVP build.

This does not mean the data and semantics are enterprise-ready. It means the remaining risks are understood, bounded and acceptable for a discovery MVP.

Suggested exit wording:

> Proceed with a narrow answerable question set for Le Figaro article analytics. The discovery MVP may use approved analytics views, repository metadata and golden questions, while treating independent semantic approval, production access control and enterprise data ownership as future gaps.