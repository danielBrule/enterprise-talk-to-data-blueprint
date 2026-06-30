# Phase 8 — Release Readiness

## Status

Production gap.

The implementation demonstrates several production-relevant patterns, but it is not a controlled production release and should not be presented as production-ready.

## Release decision

Do not release to production.

The discovery MVP is suitable for technical review, validation and controlled learning. It is not ready for real enterprise users, sensitive data or decision-critical use.

## Phase 8 intent for this implementation

Phase 8 answers one practical question:

> What would be required to move this MVP from validated discovery build to controlled production release?

For this implementation, the answer is clear: the core pattern is demonstrated, but production controls, ownership, monitoring, support and risk acceptance are missing.

## Current release boundary

| Area | Current boundary |
|---|---|
| Release type | Discovery MVP / reference implementation |
| Users | Repository owner, technical reviewers, controlled testers |
| Domain | Le Figaro article analytics |
| Data | Approved article and comment analytics views |
| Usage | Learning, technical assessment and portfolio review |
| Not allowed | Enterprise decision support, regulated reporting, broad user access or sensitive data use |

## Production-relevant controls demonstrated

| Control | Current evidence |
|---|---|
| Bounded scope | Le Figaro article analytics only |
| Approved query surface | Assistant queries approved analytics views |
| Metadata grounding | Schema, metric, glossary and example metadata are used |
| SQL validation | Generated SQL is checked before execution |
| Safe failure | Unsupported or ambiguous questions can refuse or clarify |
| Evaluation | Golden-question evaluation and regression checks exist |
| Traceability | Pipeline traces and evaluation records support diagnosis |
| Feedback | UI feedback can support review and improvement |
| Deployment scaffolding | Azure-oriented infrastructure artefacts exist |

## Release blockers

| Blocker | Why it blocks release |
|---|---|
| No production identity | Users are not authenticated through enterprise identity |
| No full row-level security | Access control is not production-grade |
| No real pilot evidence | Workflow fit, trust and user behaviour are not proven |
| No independent assurance | Evaluation is self-authored |
| No formal security review | Security and privacy risks are not independently assessed |
| No production monitoring | Live quality, latency, cost and failure signals are not operationalised |
| No support model | Users would not have a defined support or escalation route |
| No residual-risk sign-off | No accountable owner has accepted remaining risk |
| No run-cost approval | Production cost and capacity are not funded or approved |

## Required before controlled release

| Area | Required next evidence |
|---|---|
| Identity and access | Enterprise authentication, role mapping, RLS/access tests |
| Security | Security, privacy, retention and audit review |
| Evaluation | Independent question set, adversarial tests and answer-quality scoring |
| Pilot | Real user pilot with trace-linked feedback and issue triage |
| Monitoring | Dashboard for usage, errors, refusals, latency, cost and feedback |
| Support | Runbook, support owner, escalation route and incident process |
| Governance | Release owner, change approval, residual-risk acceptance |
| Cost | Usage forecast, model/query cost estimate and capacity plan |

## Phase 8 exit view

Phase 8 is not complete.

The implementation demonstrates a credible path toward controlled release, but it lacks the enterprise evidence and operating controls required to release safely.

Suggested exit wording:

> Do not proceed to production release. The discovery MVP demonstrates the governed Talk-to-Data pattern, but controlled release would require production identity, access enforcement, independent assurance, real pilot evidence, monitoring, support, cost approval and residual-risk acceptance.