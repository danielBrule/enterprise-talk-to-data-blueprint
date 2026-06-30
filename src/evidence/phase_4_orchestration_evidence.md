# Phase 4 — Orchestration Evidence

## Status

Demonstrated for discovery MVP.

The implementation defines and builds a bounded question-to-answer flow. It does not claim production-grade orchestration governance, model-risk approval, full monitoring or release change control.

## Orchestration decision

Proceed to MVP build using a staged pipeline with deterministic controls around model output.

The model may help classify intent, select context, draft SQL and generate an answer. It should not decide access, invent metric logic, bypass validation or execute unrestricted queries.

## Phase 4 intent for this implementation

Phase 4 answers one practical question:

> Can the system turn a user question into a governed answer using bounded metadata, model calls, tool boundaries and validation?

For this implementation, the answer is yes for the scoped Le Figaro discovery use case.

## Implemented flow

| Stage | Purpose | Control point |
|---|---|---|
| Intent classification | Decide whether the question is supported, ambiguous, system-related or out of scope | Unsupported or unclear requests can stop early |
| View selection | Select relevant approved analytics views | Only approved views should be considered |
| Metadata retrieval | Load schema, metric, glossary and example context | SQL generation is grounded in repository metadata |
| SQL generation | Draft SQL for the selected view and question | Model output is treated as untrusted |
| SQL validation | Check generated SQL before execution | Unsafe SQL is rejected before database access |
| SQL execution | Execute validated SQL | Execution only happens after validation |
| Answer generation | Convert result into a user-facing answer | Answer should stay within evidence and caveats |

## Model and tool boundaries

| Area | Boundary |
|---|---|
| Model use | Intent, view selection support, SQL drafting, answer generation |
| Deterministic controls | SQL validation, scope checks, row limits and unsafe-query rejection |
| Metadata | Repository files provide the grounding context |
| Query execution | SQL execution is a tool call, not a model decision |
| Access | Role-aware behaviour may be demonstrated, but production access enforcement is not claimed |
| Refusal | Unsupported or unsafe questions should refuse or clarify rather than guess |

## Validation design

| Control | Purpose |
|---|---|
| Golden questions | Test supported question patterns and expected paths |
| Fast evaluation mode | Validate intent, view selection, SQL generation and SQL validation without database dependency |
| Full evaluation mode | Test the complete pipeline where database access is available |
| SQL safety checks | Prevent unsafe or unsupported query execution |
| Traces | Support debugging and failure classification |
| Feedback capture | Link user review to implementation behaviour |

## Orchestration risks

| Risk | Response |
|---|---|
| Model invents unsupported SQL | Use approved metadata and deterministic SQL validation |
| Wrong view selected | Evaluate against golden questions and expected views |
| Ambiguous user intent | Clarify or refuse rather than force an answer |
| Overconfident answer | Ground the answer in query results and caveats |
| Follow-up context drift | Keep follow-up handling bounded to supported scope |
| Production drift | Treat monitoring, regression and change control as future production gaps |

## Evidence used

Primary implementation evidence is in `src/backend/`, `src/backend/stages/`, `src/backend/prompts/`, `src/metadata/`, `src/sql/`, `src/evaluation_results/` and `src/README.md`.

## Phase 4 carry-forward gaps

| Gap | Impact |
|---|---|
| Limited model comparison | Model choice is sufficient for discovery but not fully benchmarked |
| No production model-risk approval | Required before regulated or enterprise release |
| Limited monitoring thresholds | Traces exist, but production alerting is not defined |
| Limited follow-up assurance | Multi-turn behaviour needs stronger testing before pilot |
| No formal change-control process | Prompt, model and validation changes would need governance before production |

## Phase 4 exit view

The orchestration design is sufficient for MVP build.

It defines a staged runtime flow, clear model/tool boundaries, metadata grounding, deterministic SQL validation and repeatable evaluation. It is not yet a production orchestration control model.

Suggested exit wording:

> Proceed to MVP build using the staged Le Figaro Talk-to-Data orchestration. Treat model comparison, monitoring thresholds, follow-up assurance and orchestration change control as future validation and production-readiness gaps.