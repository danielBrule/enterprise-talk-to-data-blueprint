# Talk-to-Data: an enterprise delivery blueprint

> Talk-to-Data is not a chatbot connected to a database. It is a governed decision
> interface over trusted data — and the hard part was never making a model produce an
> answer. It is making sure every answer is grounded in the right definition, the right
> data, the right permissions, and the right level of confidence.

This repository is a practitioner's blueprint for delivering enterprise Talk-to-Data (T2D)
as a *governed analytics product*, together with a working reference implementation of the
patterns it describes.

The failure mode it is built to prevent is specific: a system that returns **fluent, plausible
and wrong** answers. In an enterprise context that is not a minor limitation — it is a trust,
governance and adoption failure. Fluency is not evidence of correctness, and most of the
delivery work in T2D sits *around* the model, not in it.

## The reference implementation

The blueprint is not only prose. <!-- TODO: link your code repo --> **[`t2d-engine`](https://github.com/your-handle/t2d-engine)**
implements the core patterns the documents argue for:

- **Deterministic query validation** — writes, drops, unrestricted joins, missing row limits and
  forbidden tables are blocked *before* any query reaches execution, not reviewed after.
- **Metadata grounding** — queries are constrained to approved metric definitions, not inferred
  from the user's wording.
- **Safe failure** — the system clarifies, caveats, refuses or escalates rather than guessing.
- **Evaluation harness** — golden questions with expected answers and safe-failure cases, scored
  and reproducible.

<!-- TODO: replace with your real command + a one-line result, e.g. -->
```bash
make eval        # runs the golden-question suite and prints a scorecard
```

Each claim in the blueprint maps to where it is implemented — see
[`t2d-engine/README`](https://github.com/your-handle/t2d-engine) for the claim-to-code table.

## What "governed" means in practice

Every metric the system can answer is defined once — with its calculation, grain, mandatory
filters, access rules and caveats — and the model queries *that definition* rather than
reconstructing one:

| Field | Example |
|---|---|
| Metric | Net revenue |
| Definition | Revenue after discounts, credits and refunds |
| Calculation | `SUM(gross_revenue - discount_amount - refund_amount)` |
| Grain | Order line |
| Mandatory filters | Completed orders only; test orders excluded |
| Access | Restricted by region and legal entity |
| Caveat | Current month provisional; refunds may lag up to 48h |

A user asking *"net revenue last month by region"* gets the approved definition, their permitted
regions only, and the provisional-month caveat — or a refusal if they ask for something outside
approved scope. That control surface, not the language model, is the product.

## How to read this

| You have | Read | You'll get |
|---|---|---|
| 3 minutes | this README | the thesis and the shape of the work |
| 15 minutes | [`docs/master.md`](docs/master.md) | delivery logic, risks, decision gates, operating model |
| Going deep | [`docs/phases/`](docs/phases) | the nine-phase delivery journey, end to end |
| Building one | [`docs/annexes/`](docs/annexes) | templates, scorecards, registers, worked examples to adapt |

The phase model is delivery *logic*, not a fixed waterfall — phases run light for a POC, deepen
for an MVP, and formalise before pilot or production. The discipline is to avoid carrying POC
assumptions into production without revalidating them.

## The nine phases

| Phase | Focus | What it decides |
|---|---|---|
| 1 | Framing | Is T2D the right response to a real business need, and is it bounded and owned? |
| 2 | Data & semantic readiness | Which questions can be answered safely, and which need remediation, caveats or deferral? |
| 3 | Governed data foundation | The approved queryable layer: metric logic, joins, filters, access controls, caveats, quality checks |
| 4 | Design architecture | How a question becomes a governed answer: grounding, model use, tool boundaries, validation, safe failure |
| 5 | Prototype / MVP build | A bounded, observable, testable build that generates evidence before formal validation |
| 6 | Validation, assurance & remediation | Is it safe, reliable and evidenced enough for controlled user testing? |
| 7 | Controlled pilot & user testing | Does it hold up with real users, real questions and real operating conditions? |
| 8 | Production readiness & release | Resilience, support, monitoring, access, governance, ownership — and the release decision |
| 9 | Operate, adopt & improve | Run it as a live product: feedback, regression testing, cost control, semantic updates |

Each phase has a main guide (delivery logic, decisions, risks, required outputs, handover) and an
annex pack (practical material to adapt, not follow mechanically).

> **Status:** <!-- TODO: set this to what you are actually publishing. You have all nine; if you
> are staging the release, say "Phases 1–5 published; 6–9 in review" and remove the rows you are
> not shipping yet. Do not claim "coming soon" for material that exists. -->

## Repository structure

```text
docs/
  master.md            Strategic overview: logic, risks, gates, operating model
  phases/              The nine phase guides
  annexes/             Templates, checklists, registers, worked examples
```

## Who wrote this

<!-- TODO: one or two real sentences in your own voice. State an opinion you'd defend. Example: -->
**[Your name].** I wrote this after seeing T2D initiatives stall for reasons that had nothing to
do with the model. My view is that most should be stopped — or sent back to a dashboard — at the
framing stage, and that the willingness *not* to proceed is the most underrated delivery skill in
this space. Feedback and disagreement welcome.

## Scope and status

This is a delivery blueprint, not a technical design, security policy, compliance review or vendor
selection framework. Cost, effort and timeline figures are illustrative planning aids, not
benchmarks. Security, privacy and regulatory requirements should be reviewed by the appropriate
specialists for each organisation.

<!-- TODO: add a LICENSE file and reference it here, e.g. "Licensed under CC BY 4.0." -->