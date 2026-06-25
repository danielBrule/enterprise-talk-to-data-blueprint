import time

from ..core.sql_safety import validate_query, validate_sql_metadata, SQLSafetyError
from ..models.pipeline_context import PipelineContext
from ..models.trace import ValidationResult
from ..services.metadata_service import get_approved_joins
from .base import Stage


class SQLValidationStage(Stage):
    async def run(self, ctx: PipelineContext) -> None:
        """
        Validate the generated SQL and store the result in context.

        Does NOT refuse directly — the pipeline orchestrator reads ctx.sql_validation_error
        and decides whether to retry SQL generation or surface a refusal to the user.
        This allows the retry loop in TalkToDataPipeline to feed the error back to the
        SQL generation stage as a correction hint before giving up.
        """
        t0 = time.perf_counter()

        joins_config = await get_approved_joins()
        approved_pairs: set[frozenset] = {
            frozenset(entry["views"])
            for entry in joins_config.get("approved_joins", [])
        }

        try:
            validate_query(ctx.sql or "", approved_pairs=approved_pairs)
            validate_sql_metadata(ctx.sql or "", ctx.metadata_context or {})
            passed, reason = True, None
        except SQLSafetyError as e:
            passed, reason = False, str(e)
        ctx.latency["sql_validation_ms"] = ctx.latency.get("sql_validation_ms", 0) + (time.perf_counter() - t0) * 1000

        ctx.trace.validation_result = ValidationResult(passed=passed, reason=reason)
        ctx.sql_validation_error = reason  # None on pass, error string on fail
