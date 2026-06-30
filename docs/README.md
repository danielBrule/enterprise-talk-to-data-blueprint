# Talk-to-Data Delivery Blueprint — Documents

The full blueprint. Start with the [master](master.md) for the strategic overview, then go deeper
by phase. Formatted PDF versions of every document are in [`pdf/`](pdf).

## Master

[master.md](master.md) — delivery logic, risks, principles, decision gates and operating model.

## Phases

| Phase | Guide | Annex pack | Evidence |
|---|---|---|---|
| 1 | [Framing](phases/phase_1_framing.md) | [annex](annexes/phase_1_framing_annexes.md) | [evidence](../src/evidence/phase_1_framing_evidence.md) |
| 2 | [Data & semantic readiness](phases/phase_2_data_semantic_readiness.md) | [annex](annexes/phase_2_data_semantic_readiness_annexes.md) | [evidence](../src/evidence/phase_2_answerability_evidence.md) |
| 3 | [Governed data foundation](phases/phase_3_governed_data_foundation.md) | [annex](annexes/phase_3_governed_data_foundation_annexes.md) | [evidence](../src/evidence/phase_3_foundation_evidence.md) |
| 4 | [Design architecture](phases/phase_4_design_architecture.md) | [annex](annexes/phase_4_design_architecture_annexes.md) | [evidence](../src/evidence/phase_4_orchestration_evidence.md) |
| 5 | [Prototype / MVP build](phases/phase_5_prototype_mvp_build.md) | [annex](annexes/phase_5_prototype_mvp_build_annexes.md) | [evidence](../src/evidence/phase_5_mvp_evidence.md) |
| 6 | [Validation, assurance & remediation](phases/phase_6_validation_assurance_remediation.md) | [annex](annexes/phase_6_validation_assurance_remediation_annexes.md) | [evidence](../src/evidence/phase_6_validation_summary.md) |
| 7 | [Controlled pilot & user testing](phases/phase_7_controlled_pilot.md) | [annex](annexes/phase_7_controlled_pilot_annexes.md) | [evidence](../src/evidence/phase_7_pilot_simulation.md) |
| 8 | [Production readiness & release](phases/phase_8_production_readiness.md) | [annex](annexes/phase_8_production_readiness_annexes.md) | [evidence](../src/evidence/phase_8_release_readiness.md) |
| 9 | [Operate, adopt & improve](phases/phase_9_operate_adopt_improve.md) | [annex](annexes/phase_9_operate_adopt_improve_annexes.md) | [evidence](../src/evidence/phase_9_operating_gap.md) |

Each main guide covers delivery logic, decisions, risks, required outputs and handover. Each annex
pack holds templates, checklists, registers, scorecards and worked examples to adapt, not follow
mechanically. Each evidence file maps that phase's required exit outputs against what the
[reference implementation](../src/evidence/README.md) in `src/` actually produced — see
[`src/evidence/phase_exit_evidence.md`](../src/evidence/phase_exit_evidence.md) for the
consolidated, phase-by-phase view.

## PDFs

[`pdf/`](pdf) holds a formatted version of every document above. They are generated from the
Markdown — regenerate them after any edit, from the repository root:

```bash
make pdf
```
