import time

from sqlalchemy import text

from ..db.connection import execute_query
from ..core.logger import logger
from ..core.sql_safety import extract_views
from ..models.pipeline_context import PipelineContext
from .base import Stage, build_latency, Refusal


class ExecutionStage(Stage):
    async def run(self, ctx: PipelineContext) -> Refusal | None:
        t0 = time.perf_counter()

        # Access enforcement: refuse if the query touches a view the caller cannot see.
        # Skipped when ctx.user is None (evaluation runner, direct service calls).
        if ctx.user is not None:
            views_in_sql = extract_views(ctx.sql or "")
            allowed = {v.lower() for v in ctx.user.allowed_views}
            denied = sorted(views_in_sql - allowed)
            if denied:
                ctx.latency["execution_ms"] = (time.perf_counter() - t0) * 1000
                denied_str = ", ".join(denied)
                reason = (
                    f"Access denied: your role ('{ctx.user.role}') is not permitted "
                    f"to query {denied_str}."
                )
                logger.warning(
                    "security.access_denied trace_id=%s role=%s denied_views=%s",
                    ctx.trace.trace_id, ctx.user.role, denied_str,
                )
                ctx.trace.execution_status = "refused"
                ctx.trace.refusal_reason = reason
                ctx.trace.latency_ms = build_latency(ctx)
                return Refusal(reason=reason, trace=ctx.trace)

        try:
            rows = await execute_query(text(ctx.sql or ""))
            ctx.latency["execution_ms"] = (time.perf_counter() - t0) * 1000
            ctx.trace.executed_sql = ctx.sql
            ctx.trace.execution_status = "success"
            ctx.trace.row_count = len(rows)
            ctx.trace.result_sample = rows[:3]
            ctx.rows = rows
            return None
        except Exception as exc:
            ctx.latency["execution_ms"] = (time.perf_counter() - t0) * 1000
            # "failed" (infrastructure error) not "refused" (user-facing rejection) —
            # constructed directly rather than via refuse() to preserve this distinction.
            ctx.trace.execution_status = "failed"
            ctx.trace.error = str(exc)
            reason = "Query execution failed — the database may be unavailable."
            ctx.trace.refusal_reason = reason
            ctx.trace.latency_ms = build_latency(ctx)
            logger.exception(
                "pipeline.execution_failed trace_id=%s sql=%s",
                ctx.trace.trace_id,
                (ctx.sql or "")[:80],
            )
            return Refusal(reason=reason, trace=ctx.trace)
