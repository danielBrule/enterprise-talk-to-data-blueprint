# Phase 1 — Framing Evidence

## Status

Partially demonstrated.

This implementation is framed as a discovery-style reference project. It is not a client-sponsored enterprise delivery, but it follows the logic of an early discovery that a company could run over a few weeks to assess Talk-to-Data value, feasibility, risks and production implications.

## Framing decision

Proceed to a bounded discovery MVP.

The objective is to test Talk-to-Data on a narrow, controlled analytical domain before attempting a broader implementation.

## Project context

| Area | Decision |
|---|---|
| Project type | Discovery / feasibility reference project |
| Domain | Le Figaro article analytics |
| Data source | Article and comment data collected through the companion project [lefigaro-harvester](https://github.com/danielBrule/lefigaro-harvester) |
| Delivery intent | Bounded discovery MVP |
| Primary objective | Assess how a governed Talk-to-Data capability behaves on a narrow analytical use case |
| Secondary objective | Identify implementation risks, controls, evidence needs and production gaps before scoping a larger project |
| Target users | Technical reviewer, data/AI practitioner, analyst-style user, business-style reviewer |
| Production intent | None at this stage |
| Success measure | Demonstrate a bounded question-to-answer flow with metadata grounding, SQL validation, evaluation, tracing and clear production gaps |

## Discovery questions

The project is designed to answer five practical questions:

1. Can a natural-language question be mapped to an approved analytical view?
2. Can metadata grounding reduce the risk of plausible but wrong SQL?
3. Can generated SQL be constrained and validated before execution?
4. What evidence is needed to evaluate answer quality and safe failure?
5. What would remain unresolved before pilot or production release?

## User and workflow hypothesis

| Area | Hypothesis |
|---|---|
| User need | Users want to explore article and comment performance without writing SQL or creating new fixed reports |
| Current workaround | Manual SQL, notebooks, static extracts or predefined dashboards |
| Main blocker | Flexible follow-up questions are slow to answer through fixed reporting |
| Expected value | Faster exploration of article analytics, with clearer evidence of where T2D needs semantic, validation and governance controls |
| Validation need | This remains a hypothesis until tested with real users in a controlled pilot |

## MVP boundary

| Boundary | In scope |
|---|---|
| Dataset | Le Figaro article and comment analytics |
| Question set | Curated golden questions and manual UI/API testing |
| Query surface | Approved analytics views only |
| Interaction | Natural-language question through API or UI |
| Pipeline | Intent, view selection, metadata retrieval, SQL generation, SQL validation, execution, answer generation |
| Evaluation | Golden-question evaluation and regression checks |
| Observability | Traces, feedback, evaluation outputs and MLflow records |

## Supported question types

Supported question types are defined through the golden question set in `src/metadata/example_questions/`.

They cover article analytics patterns such as article ranking, comment volume, publication trends, section comparison, period-based analysis, data-quality questions, follow-up questions and expected refusals or clarifications.

## Key assumptions and exclusions

| Area | Decision |
|---|---|
| Scope | Le Figaro article analytics only |
| Data sensitivity | Treated as low sensitivity and non-enterprise confidential |
| Query surface | Approved analytics views only, not unrestricted raw-table access |
| Metadata | Local repository metadata is sufficient for discovery |
| Identity | Production authentication is out of scope |
| Access control | Role-aware behaviour may be demonstrated, but production-grade access control and row-level security are not claimed |
| SQL safety | Generated SQL must be validated before execution |
| Evaluation | Repository-level golden-question evaluation; not independent assurance |
| Pilot | No real controlled pilot is claimed |
| Production | No production release, support model, monitoring dashboard or residual-risk sign-off is claimed |

## Framing risks

| Risk | Discovery response |
|---|---|
| Fluent but wrong answers | Use metadata grounding, approved views and SQL validation |
| Unsafe SQL | Validate generated SQL before execution |
| Scope creep | Restrict the project to one narrow analytical domain |
| Weak semantics | Use explicit metadata, glossary and metric definitions |
| Overclaiming readiness | Separate discovery evidence from pilot and production readiness |
| Poor transferability | Use findings to inform the scope of the next, broader project |

## Phase 1 exit-output coverage

| Required framing output | Current evidence | Status |
|---|---|---|
| Framing decision | Proceed to bounded discovery MVP | Demonstrated |
| MVP scope | Le Figaro article analytics, approved views, API/UI interaction | Demonstrated |
| Priority questions | Golden questions in `src/metadata/example_questions/` | Demonstrated |
| User/workflow hypothesis | Analyst-style exploration of article and comment performance | Partially demonstrated |
| Candidate source view | Le Figaro harvester data and approved analytics views | Partially demonstrated |
| Semantic risk view | Captured through metadata, glossary, metrics and caveats | Partially demonstrated |
| Security assumptions | Low-sensitivity discovery dataset; production auth/RLS excluded | Partially demonstrated |
| Architecture assumptions | API/UI, metadata grounding, SQL validation, Azure-oriented scaffolding | Demonstrated |
| Evaluation approach | Golden-question evaluation and regression checks | Demonstrated |
| Ownership view | Repository owner for discovery; no enterprise owner claimed | Partially demonstrated |
| Delivery plan | Discovery MVP built over a short, self-contained delivery cycle | Partially demonstrated |

## Evidence in repository

| Evidence | Location |
|---|---|
| Overall thesis and scope | `README.md` |
| Deliberate scope decisions | `README.md` |
| Implementation overview | `src/README.md` |
| Golden questions | `src/metadata/example_questions/` |
| Metadata assets | `src/metadata/` |
| SQL views and scripts | `src/sql/` |
| Backend pipeline | `src/backend/` |
| Frontend UI | `src/frontend/` |
| Evaluation outputs | `src/evaluation_results/` |
| MLflow evidence | `src/mlruns/`, `src/mlflow.db` |
| Infrastructure scaffold | `src/infra/` |

## Open gaps

| Gap | Why it remains open |
|---|---|
| Real sponsor | This is a reference discovery project |
| Real business owner | No enterprise organisation is attached |
| Real user cohort | No controlled pilot has been run |
| Independent validation | Evaluation is self-authored |
| Production risk appetite | No governance forum has approved risk tolerance |
| Support owner | Not applicable to a discovery MVP |

## Phase 1 exit view

The framing is sufficient to proceed to a bounded discovery MVP.

It establishes a clear domain, purpose, supported question boundary, delivery intent and explicit exclusions. It does not establish enterprise sponsorship, pilot readiness, production risk appetite or operational ownership.

Suggested exit wording:

> Proceed to a bounded discovery MVP on Le Figaro article analytics. The project is intended to assess Talk-to-Data feasibility, implementation risks, evidence needs and production gaps before scoping a broader or more realistic enterprise use case.