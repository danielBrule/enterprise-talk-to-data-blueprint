"""
Entry point for the golden question evaluation runner.

Usage:
    make eval                                          # fast mode, print summary
    make eval MODE=full OUTPUT=report.json             # full mode, save JSON report
    make eval LIMIT=10                                 # only first 10 positive questions
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
import json
import subprocess
import sys
from pathlib import Path

from backend.app.evaluation.golden_runner import GoldenRunner


async def _run(mode: str, output: Path | None, limit: int | None) -> int:
    runner = GoldenRunner()
    report = await runner.run_all(mode=mode, limit=limit)
    report.print_summary()

    if output:
        try:
            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
            ).decode().strip()
        except Exception:
            commit = "unknown"
        data = {"git_commit": commit, **report.to_dict()}
        output.write_text(json.dumps(data, indent=2, default=str))
        print(f"\nReport written to {output} (commit {commit[:8]})")

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
    args = parser.parse_args()
    sys.exit(asyncio.run(_run(args.mode, args.output, args.limit)))


if __name__ == "__main__":
    main()
