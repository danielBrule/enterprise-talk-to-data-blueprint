# Phase 5 — MVP Evidence

## Status

Demonstrated for discovery MVP.

The implementation builds a bounded Talk-to-Data MVP for Le Figaro article analytics. It is observable, testable and structured around evidence, but it is not a production service.

## MVP decision

Proceed to repository-level validation.

The MVP is complete enough to test the end-to-end pattern: natural-language question, metadata grounding, SQL generation, SQL validation, execution, answer generation, traces and feedback.

## Phase 5 intent for this implementation

Phase 5 answers one practical question:

> Can the designed Talk-to-Data flow be built as a working, bounded MVP that generates enough evidence for validation?

For this implementation, the answer is yes.

## Built scope

| Area | Implemented |
|---|---|
| Backend | FastAPI service exposing the Talk-to-Data pipeline |
| Frontend | Lightweight React/Vite UI for asking questions and capturing feedback |
| Domain | Le Figaro article and comment analytics |
| Query surface | Approved analytics views |
| Metadata | Schema, metric, glossary and example-question files |
| Model use | Intent, view selection support, SQL drafting and answer generation |
| Validation | Deterministic SQL checks before execution |
| Evaluation | Golden-question evaluation runner |
| Observability | Traces, feedback, evaluation results and MLflow records |
| Deployment | Local/dev setup with Azure-oriented infrastructure scaffolding |

## Implemented pipeline

| Stage | Implemented behaviour |
|---|---|
| Intent | Classifies the user question and can stop unsupported requests early |
| View selection | Selects candidate approved analytics views |
| Metadata retrieval | Loads relevant schema, metric, glossary and example context |
| SQL generation | Drafts SQL from bounded metadata context |
| SQL validation | Blocks unsafe or unsupported SQL before execution |
| SQL execution | Executes validated SQL against the configured database |
| Answer generation | Produces a user-facing answer from query results and context |

## MVP controls

| Control | Purpose |
|---|---|
| Approved views | Avoid unrestricted querying over raw tables |
| Metadata grounding | Reduce unsupported SQL and semantic guessing |
| SQL validation | Treat model-generated SQL as untrusted until checked |
| Row limits | Keep query outputs bounded |
| Refusal / clarification | Avoid forcing answers for unsupported or ambiguous questions |
| Evaluation runner | Re-test the pipeline against known question patterns |
| Feedback capture | Support review and improvement |
| Traces | Support debugging and failure analysis |

## Evidence generated

| Evidence | Purpose |
|---|---|
| Golden-question runs | Check expected pipeline behaviour |
| Fast evaluation mode | Test intent, view selection, SQL generation and validation without database dependency |
| Full evaluation mode | Test the full pipeline when database access is available |
| Unit and integration tests | Check implementation behaviour and guardrails |
| MLflow records | Track evaluation runs and results |
| UI feedback | Capture reviewer judgement against answers |
| Traces | Diagnose failures by pipeline stage |

## Known MVP limitations

| Limitation | Impact |
|---|---|
| Discovery dataset only | Does not prove enterprise domain scalability |
| Self-authored evaluation | Useful for regression, not independent assurance |
| No real pilot users | User value and workflow fit are not yet evidenced |
| Production identity out of scope | Blocks enterprise release |
| Full row-level security not claimed | Blocks production use with sensitive data |
| Limited monitoring | Traces exist, but live operational monitoring is not implemented |
| Limited support model | No live service operation or incident process |
| Limited model comparison | Model choices are suitable for discovery, not fully benchmarked |

## Phase 5 carry-forward gaps

| Gap | Next phase impact |
|---|---|
| Validation needs independent evidence | Phase 6 should add stronger question and failure testing |
| Access controls need hardening | Phase 6/8 must validate identity and authorisation before real users |
| Answer quality needs scoring | Phase 6 should assess correctness, caveats and overreach |
| Real usage is missing | Phase 7 would need controlled user testing |
| Operational controls are incomplete | Phase 8/9 would need monitoring, support, ownership and risk acceptance |

## Phase 5 exit view

The MVP is sufficient to proceed to validation.

It demonstrates the core governed Talk-to-Data implementation pattern: bounded scope, metadata grounding, staged orchestration, deterministic SQL validation, evaluation, traces and feedback.

It does not demonstrate pilot readiness, production readiness or live operation.

Suggested exit wording:

> Proceed to Phase 6 validation for the Le Figaro discovery MVP. The implementation is complete enough to test the core Talk-to-Data flow, while treating independent assurance, production access control, real user testing and operational readiness as future gaps.