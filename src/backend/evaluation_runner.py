"""
Entry point for the golden question evaluation runner.

Usage:
    make eval                                          # fast mode, print summary
    make eval MODE=full OUTPUT=report.json             # full mode, save JSON report
    make eval LIMIT=10                                 # only first 10 positive questions
    make mlflow-ui                                     # open MLflow UI
    poetry run python -m backend.evaluation_runner --mode fast
    poetry run python -m backend.evaluation_runner --mode fast --limit 10
    poetry run python -m backend.evaluation_runner --mode full --output report.json

Modes:
    fast (default)  Stages 1-5 only. No database required.
                    Checks intent classification, view selection, SQL generation,
                    and SQL validation against golden questions.

    full            All 7 stages. Requires live Azure SQL and Azure OpenAI credentials.
                    Adds database execution and answer quality checks on top of fast mode.

Exit code: 0 if pass rate >= 80%, 1 otherwise.
"""
import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import mlflow

from backend.app.evaluation.golden_runner import GoldenRunner, _GOLDEN_QUESTIONS_PATH
from backend.app.prompts.intent import PROMPT_VERSION as INTENT_VERSION
from backend.app.prompts.sql_generation import PROMPT_VERSION as SQL_GEN_VERSION

MLFLOW_EXPERIMENT = "talk-to-data-eval"
MLFLOW_TRACKING_URI = "sqlite:///mlflow.db"


def _golden_questions_hash() -> str:
    content = _GOLDEN_QUESTIONS_PATH.read_bytes()
    return hashlib.md5(content).hexdigest()[:8]


def _log_to_mlflow(report, mode: str, commit: str, eval_run: str, duration_s: float) -> None:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT)
    with mlflow.start_run(run_name=f"{eval_run}-{mode}-{commit[:8]}"):
        mlflow.log_params({
            "mode": mode,
            "git_commit": commit[:8],
            "intent_version": INTENT_VERSION,
            "sql_gen_version": SQL_GEN_VERSION,
            "golden_questions_hash": _golden_questions_hash(),
            "eval_run": eval_run,
        })
        mlflow.log_metrics({
            "pass_rate": round(report.pass_rate, 4),
            "passed": report.passed,
            "partial": report.partial,
            "failed": report.failed,
            "total": report.total,
            "partial_rate": round(report.partial / report.total, 4) if report.total else 0,
            "eval_duration_s": round(duration_s, 1),
        })
        rows = ["question,status,failure_reasons"]
        for r in report.records:
            reasons = "; ".join(r.failure_reasons or [])
            question = r.question.replace(",", " ")
            rows.append(f"{question},{r.status},{reasons}")
        mlflow.log_text("\n".join(rows), "question_results.csv")


async def _run(mode: str, output: Path | None, limit: int | None, eval_run: str) -> int:
    t0 = time.monotonic()
    runner = GoldenRunner()
    report = await runner.run_all(mode=mode, limit=limit)
    duration_s = time.monotonic() - t0
    report.print_summary()

    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        commit = "unknown"

    if output:
        data = {"git_commit": commit, "eval_run": eval_run, **report.to_dict()}
        output.write_text(json.dumps(data, indent=2, default=str))
        print(f"\nReport written to {output} (commit {commit[:8]})")

    _log_to_mlflow(report, mode, commit, eval_run, duration_s)
    print(f"MLflow run logged to experiment '{MLFLOW_EXPERIMENT}' — run: mlflow ui")

    return 0 if report.pass_rate >= 0.8 else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run golden question evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["fast", "full"],
        default="fast",
        help="fast: stages 1-5, no DB (default); full: all 7 stages with DB and LLM",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        metavar="FILE",
        help="Write JSON report to FILE",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Run only the first N positive questions (useful when rate-limited)",
    )
    parser.add_argument(
        "--eval-run",
        default="",
        metavar="LABEL",
        help="Short label for this run logged to MLflow (e.g. v12, post-prompt-fix)",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(_run(args.mode, args.output, args.limit, args.eval_run)))


if __name__ == "__main__":
    main()
