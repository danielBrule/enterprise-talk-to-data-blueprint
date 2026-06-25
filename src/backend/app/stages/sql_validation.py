import time

from ..core.sql_safety import validate_query, validate_sql_metadata, SQLSafetyError
from ..models.pipeline_context import PipelineContext
from ..models.trace import ValidationResult
from ..services.metadata_service import get_approved_joins
from .base import Stage, Refusal, refuse


class SQLValidationStage(Stage):
    async def run(self, ctx: PipelineContext) -> Refusal | None:
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
        ctx.latency["sql_validation_ms"] = (time.perf_counter() - t0) * 1000

        ctx.trace.validation_result = ValidationResult(passed=passed, reason=reason)

        if not passed:
            return refuse(ctx, f"SQL validation failed: {reason}")
        return None
