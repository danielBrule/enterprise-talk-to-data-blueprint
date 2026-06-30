# Phase 6 — Validation Summary

## Status

Partially demonstrated.

The implementation includes repository-level validation through tests, golden questions, SQL validation and evaluation runs. It does not claim independent enterprise assurance, formal security review or approval for pilot exposure.

## Validation decision

Proceed as a validated discovery MVP, not as a pilot-ready enterprise system.

The current evidence is sufficient to assess the implementation pattern and identify gaps. It is not sufficient to expose the system to real business users without further assurance.

## Phase 6 intent for this implementation

Phase 6 answers one practical question:

> Is the MVP safe, reliable and evidenced enough to justify controlled user testing?

For this implementation, the answer is partial: the technical pattern can be validated, but real pilot exposure would require stronger access, assurance and answer-quality evidence.

## Validation scope

| Area | Included |
|---|---|
| Domain | Le Figaro article analytics |
| Question set | Curated golden questions |
| Pipeline | Intent, view selection, metadata retrieval, SQL generation, SQL validation, execution and answer generation |
| SQL safety | Validation before execution |
| Evaluation | Fast and full evaluation modes |
| Observability | Traces, evaluation outputs and MLflow records |
| UI feedback | Basic feedback capture |

## Evaluation modes

| Mode | Purpose | Status |
|---|---|---|
| Fast mode | Test intent, view selection, SQL generation and SQL validation without database dependency | Demonstrated |
| Full mode | Test the complete pipeline with database execution where available | Partially demonstrated |
| Unit / integration tests | Check component behaviour and guardrails | Demonstrated |
| Manual UI/API testing | Review user-facing behaviour | Partially demonstrated |

## Validation controls

| Control | What it validates |
|---|---|
| Golden questions | Whether supported question patterns follow expected paths |
| Expected views | Whether the system selects the right approved analytics view |
| SQL validation | Whether generated SQL stays inside the safe execution boundary |
| Row limits | Whether result size remains bounded |
| Refusal / clarification paths | Whether unsupported or ambiguous requests avoid unsafe answering |
| Traces | Whether failures can be diagnosed by stage |
| Feedback capture | Whether answer review can be linked to future improvement |

## Assurance gaps

| Gap | Why it matters |
|---|---|
| Self-authored evaluation | Useful for regression, but not independent assurance |
| No second-party question set | Real users may ask questions outside expected patterns |
| No formal answer-quality scoring | Correctness, caveats and overreach are not yet systematically reviewed |
| Limited adversarial testing | Prompt injection, unsafe SQL and access-bypass cases need stronger coverage |
| Production identity not implemented | User access cannot be assured for enterprise pilot use |
| Full row-level security not claimed | Sensitive or restricted data would not be sufficiently protected |
| No formal security/privacy review | Required before real enterprise exposure |
| No residual-risk acceptance | No accountable owner has accepted remaining risks |

## Failure categories

| Failure category | Expected handling |
|---|---|
| Unsupported question | Refuse or redirect |
| Ambiguous question | Ask for clarification |
| No suitable view | Refuse rather than query unsupported data |
| Missing metadata | Fail safely or return a constrained answer |
| Unsafe SQL | Block before execution |
| Database execution error | Return controlled failure and log trace |
| Weak answer evidence | Caveat or avoid overstatement |
| Access uncertainty | Do not treat discovery role logic as production control |

## Phase 6 carry-forward gaps

| Gap | Next step |
|---|---|
| Independent validation missing | Add reviewer-authored questions and expected answers |
| Answer scoring incomplete | Score correctness, grounding, caveats and overreach |
| Access assurance incomplete | Add identity, role and denied-access tests |
| Adversarial testing limited | Add prompt-injection, unsafe SQL and unsupported-scope tests |
| Pilot boundary not approved | Define users, data, questions, usage limits and pause conditions |
| Residual risk not accepted | Create an explicit pilot risk decision before real users |

## Phase 6 exit view

The MVP has enough validation evidence for a discovery project and technical review.

It should not be treated as ready for enterprise pilot exposure without additional independent evaluation, access assurance, security review and residual-risk acceptance.

Suggested exit wording:

> Proceed as a validated discovery MVP. Do not proceed to real controlled pilot until independent questions, answer-quality scoring, access assurance, adversarial testing and pilot risk acceptance have been completed.