# Phase 7 — Pilot Simulation

## Status

Not yet evidenced.

No real controlled pilot has been run. This file defines how the discovery MVP could be tested with real users in a controlled setting, and what evidence would be needed before moving toward production-readiness assessment.

## Pilot decision

Do not claim Phase 7 completion.

The implementation can support a small controlled pilot, but pilot evidence would require real users, trace-linked feedback, issue triage and an explicit pilot decision.

## Phase 7 intent for this implementation

Phase 7 answers one practical question:

> Can real users use the validated MVP safely, usefully and with the right level of trust inside a controlled boundary?

For this implementation, the answer is not yet evidenced.

## Proposed pilot boundary

| Area | Proposed boundary |
|---|---|
| Pilot type | Controlled discovery pilot |
| Users | 3–5 technical, analyst-style or business-style reviewers |
| Domain | Le Figaro article analytics |
| Data | Approved article and comment analytics views |
| Question types | Article ranking, comment volume, publication trends, section comparison, data-quality questions, supported follow-ups |
| Unsupported questions | Sensitive data, raw-table access, unrestricted SQL, forecasting, causal claims, external data |
| Environment | Local/dev or controlled review environment |
| Usage | Learning and evaluation only; not business decision support |
| Duration | Short review cycle, e.g. a few days to two weeks |
| Success measure | Users can ask supported questions, understand caveats, and identify where the system helps or fails |

## Pilot evidence required

| Evidence | Purpose |
|---|---|
| User cohort | Confirm who tested the MVP and which role they represented |
| Pilot question log | Capture real user questions, not only golden questions |
| Trace linkage | Link each question, answer, refusal or failure to a trace |
| Feedback record | Capture user judgement on usefulness, correctness and clarity |
| Caveat review | Check whether users understood limitations |
| Refusal review | Check whether unsupported questions were handled clearly |
| Access behaviour | Check whether role-aware behaviour worked as expected |
| Issue triage | Classify issues as fix, constrain, defer, monitor or stop |
| Pilot decision | Decide whether to proceed, narrow, remediate, extend or stop |

## Current implementation readiness

| Area | Current state |
|---|---|
| UI for user testing | Available |
| API for controlled testing | Available |
| Golden questions | Available |
| Traces | Available |
| Feedback capture | Available |
| SQL validation | Available |
| Pilot users | Not yet available |
| Pilot operating plan | Not yet executed |
| Support process | Not yet defined |
| Pilot decision record | Not yet available |

## Signals to review

| Signal | Why it matters |
|---|---|
| Supported-question success | Shows whether the MVP works inside the intended scope |
| Unsupported-question refusal | Shows whether the system avoids unsafe overreach |
| Clarification quality | Shows whether ambiguity is handled usefully |
| Trust calibration | Shows whether users rely on answers at the right level |
| Caveat understanding | Shows whether limitations are visible and understood |
| Latency | Shows whether the interaction is usable |
| Cost | Shows whether usage could scale economically |
| Feedback quality | Shows whether user feedback can improve the system |
| Support need | Shows whether the system can be used without constant builder explanation |

## Pilot issue categories

| Category | Example |
|---|---|
| Answer quality | Wrong, incomplete or unclear answer |
| Semantic ambiguity | User intent or metric meaning unclear |
| View selection | Wrong or weakly justified view selected |
| SQL validation | Valid question blocked, or unsafe query not blocked |
| UX | User cannot understand response, caveat or refusal |
| Access | Role behaviour unclear or insufficient |
| Performance | Response too slow |
| Scope | User asks for unsupported domain or analysis type |

## Phase 7 carry-forward gaps

| Gap | Impact |
|---|---|
| No real users | Workflow fit and trust cannot be assessed |
| No real question behaviour | Golden questions may not reflect how users actually ask |
| No monitored sessions | User interpretation and confusion are not observed |
| No support process | Supportability cannot be assessed |
| No issue triage record | Pilot findings cannot be converted into production-readiness backlog |
| No pilot decision | Cannot credibly proceed to Phase 8 as a real release path |

## Phase 7 exit view

Phase 7 is not complete.

The implementation is ready for a small controlled review, but not enough evidence exists to claim pilot success or move to production readiness.

Suggested exit wording:

> Do not proceed to Phase 8 as a real production-readiness gate. The discovery MVP can be used for a small controlled pilot, but Phase 7 evidence still needs real users, real questions, trace-linked feedback, issue triage and an explicit pilot decision.