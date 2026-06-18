import time
from typing import Any

from sqlalchemy import text

from ..models.trace import TraceRecord, StageLatency, ValidationResult
from ..models.talk_to_data import AskRequest, AskResponse
from .intent_service import IntentService
from .view_selection_service import ViewSelectionService
from .metadata_service import get_context_for_views
from .sql_generation_service import SQLGenerationService
from .answer_service import AnswerService
from ..core.sql_safety import validate_query, SQLSafetyError
from ..db.connection import execute_query
from ..core.logger import logger


def _build_latency(latency: dict[str, float], pipeline_start: float) -> StageLatency:
    return StageLatency(
        intent_ms=latency.get("intent_ms"),
        view_selection_ms=latency.get("view_selection_ms"),
        metadata_ms=latency.get("metadata_ms"),
        sql_generation_ms=latency.get("sql_generation_ms"),
        sql_validation_ms=latency.get("sql_validation_ms"),
        execution_ms=latency.get("execution_ms"),
        answer_generation_ms=latency.get("answer_generation_ms"),
        total_ms=(time.perf_counter() - pipeline_start) * 1000,
    )


def _refuse(
    trace: TraceRecord,
    reason: str,
    latency: dict[str, float],
    pipeline_start: float,
) -> AskResponse:
    trace.refusal_reason = reason
    trace.execution_status = "refused"
    trace.latency_ms = _build_latency(latency, pipeline_start)
    logger.info("pipeline.refused trace_id=%s reason=%s", trace.trace_id, reason[:120])
    return AskResponse(refused=True, refusal_reason=reason, trace=trace)


class TalkToDataPipeline:
    def __init__(
        self,
        intent_service: IntentService | None = None,
        view_selection_service: ViewSelectionService | None = None,
        sql_generation_service: SQLGenerationService | None = None,
        answer_service: AnswerService | None = None,
    ):
        self.intent_service = intent_service or IntentService()
        self.view_selection_service = view_selection_service or ViewSelectionService()
        self.sql_generation_service = sql_generation_service or SQLGenerationService()
        self.answer_service = answer_service or AnswerService()

    async def run(self, request: AskRequest) -> AskResponse:
        pipeline_start = time.perf_counter()
        latency: dict[str, float] = {}
        trace = TraceRecord(question=request.question, user_context=request.user_context)

        result = await self._stage_intent(request.question, trace, latency, pipeline_start)
        if isinstance(result, AskResponse):
            return result

        result = await self._stage_view_selection(request.question, trace, latency, pipeline_start)
        if isinstance(result, AskResponse):
            return result
        selected_views: list[str] = result

        result = await self._stage_metadata(selected_views, trace, latency, pipeline_start)
        if isinstance(result, AskResponse):
            return result
        metadata_context: dict = result

        result = await self._stage_sql_generation(request.question, metadata_context, trace, latency, pipeline_start)
        if isinstance(result, AskResponse):
            return result
        sql: str = result

        result = self._stage_sql_validation(sql, trace, latency, pipeline_start)
        if isinstance(result, AskResponse):
            return result

        result = await self._stage_execution(sql, trace, latency, pipeline_start)
        if isinstance(result, AskResponse):
            return result
        rows: list = result

        return await self._stage_answer(
            request.question, sql, rows, metadata_context, trace, latency, pipeline_start
        )

    # ── Stage 1: Intent classification ────────────────────────────────────────

    async def _stage_intent(
        self,
        question: str,
        trace: TraceRecord,
        latency: dict[str, float],
        pipeline_start: float,
    ) -> AskResponse | None:
        t0 = time.perf_counter()
        intent_result = await self.intent_service.classify(question)
        latency["intent_ms"] = (time.perf_counter() - t0) * 1000

        trace.intent = intent_result.domain
        trace.answerable = intent_result.answerable
        trace.prompt_versions["intent"] = intent_result.prompt_version
        trace.model_deployments["intent"] = intent_result.model_deployment

        if not intent_result.answerable:
            return _refuse(trace, intent_result.reason, latency, pipeline_start)
        return None

    # ── Stage 2: View selection ────────────────────────────────────────────────

    async def _stage_view_selection(
        self,
        question: str,
        trace: TraceRecord,
        latency: dict[str, float],
        pipeline_start: float,
    ) -> AskResponse | list[str]:
        t0 = time.perf_counter()
        view_selection = await self.view_selection_service.select_views(question)
        latency["view_selection_ms"] = (time.perf_counter() - t0) * 1000

        selected_views: list[str] = view_selection.get("selected_views", [])
        confidence: float = view_selection.get("confidence") or 0.0
        trace.selected_views = selected_views
        trace.view_selection_confidence = confidence
        trace.view_selection_reason = view_selection.get("reason")

        if confidence < 0.4:
            return _refuse(
                trace,
                f"View selection confidence is too low ({confidence:.2f}) — the question may be ambiguous or out of scope.",
                latency,
                pipeline_start,
            )
        if not selected_views:
            return _refuse(
                trace,
                "No relevant views could be identified for this question.",
                latency,
                pipeline_start,
            )
        return selected_views

    # ── Stage 3: Metadata retrieval ────────────────────────────────────────────

    async def _stage_metadata(
        self,
        selected_views: list[str],
        trace: TraceRecord,
        latency: dict[str, float],
        pipeline_start: float,
    ) -> AskResponse | dict:
        t0 = time.perf_counter()
        metadata_context = await get_context_for_views(selected_views)
        latency["metadata_ms"] = (time.perf_counter() - t0) * 1000
        trace.metadata_used = list(metadata_context.keys())

        if not metadata_context:
            return _refuse(
                trace,
                f"No metadata found for selected views: {selected_views}",
                latency,
                pipeline_start,
            )
        return metadata_context

    # ── Stage 4: SQL generation ────────────────────────────────────────────────

    async def _stage_sql_generation(
        self,
        question: str,
        metadata_context: dict,
        trace: TraceRecord,
        latency: dict[str, float],
        pipeline_start: float,
    ) -> AskResponse | str:
        t0 = time.perf_counter()
        sql_result = await self.sql_generation_service.generate(question, metadata_context)
        latency["sql_generation_ms"] = (time.perf_counter() - t0) * 1000

        trace.generated_sql = sql_result.sql
        trace.prompt_versions["sql_generation"] = sql_result.prompt_version
        trace.model_deployments["sql_generation"] = sql_result.model_deployment

        if not sql_result.sql:
            return _refuse(
                trace,
                "SQL generation produced no query — cannot answer this question.",
                latency,
                pipeline_start,
            )
        return sql_result.sql

    # ── Stage 5: Deterministic SQL validation ─────────────────────────────────

    def _stage_sql_validation(
        self,
        sql: str,
        trace: TraceRecord,
        latency: dict[str, float],
        pipeline_start: float,
    ) -> AskResponse | None:
        t0 = time.perf_counter()
        try:
            validate_query(sql)
            validation_passed = True
            validation_reason = None
        except SQLSafetyError as e:
            validation_passed = False
            validation_reason = str(e)
        latency["sql_validation_ms"] = (time.perf_counter() - t0) * 1000

        trace.validation_result = ValidationResult(passed=validation_passed, reason=validation_reason)

        if not validation_passed:
            return _refuse(
                trace,
                f"SQL validation failed: {validation_reason}",
                latency,
                pipeline_start,
            )
        return None

    # ── Stage 6: Query execution ───────────────────────────────────────────────

    async def _stage_execution(
        self,
        sql: str,
        trace: TraceRecord,
        latency: dict[str, float],
        pipeline_start: float,
    ) -> AskResponse | list:
        t0 = time.perf_counter()
        try:
            rows = await execute_query(text(sql))
            latency["execution_ms"] = (time.perf_counter() - t0) * 1000
            trace.executed_sql = sql
            trace.execution_status = "success"
            trace.row_count = len(rows)
            trace.result_sample = rows[:3]
            return rows
        except Exception as exc:
            latency["execution_ms"] = (time.perf_counter() - t0) * 1000
            trace.execution_status = "failed"
            trace.error = str(exc)
            refusal = "Query execution failed — the database may be unavailable."
            trace.refusal_reason = refusal
            trace.latency_ms = _build_latency(latency, pipeline_start)
            logger.exception(
                "pipeline.execution_failed trace_id=%s sql=%s",
                trace.trace_id,
                sql[:80],
            )
            return AskResponse(refused=True, refusal_reason=refusal, trace=trace)

    # ── Stage 7: Answer generation ─────────────────────────────────────────────

    async def _stage_answer(
        self,
        question: str,
        sql: str,
        rows: list,
        metadata_context: dict,
        trace: TraceRecord,
        latency: dict[str, float],
        pipeline_start: float,
    ) -> AskResponse:
        t0 = time.perf_counter()
        answer_result = await self.answer_service.generate(
            question, sql, rows, metadata_context
        )
        latency["answer_generation_ms"] = (time.perf_counter() - t0) * 1000

        trace.answer = answer_result.answer
        trace.caveats = answer_result.caveats
        trace.prompt_versions["answer_generation"] = answer_result.prompt_version
        trace.model_deployments["answer_generation"] = answer_result.model_deployment
        trace.latency_ms = _build_latency(latency, pipeline_start)

        logger.info(
            "pipeline.complete trace_id=%s rows=%s total_ms=%.0f",
            trace.trace_id,
            trace.row_count,
            trace.latency_ms.total_ms or 0,
        )

        return AskResponse(
            answer=answer_result.answer,
            caveats=answer_result.caveats,
            refused=False,
            trace=trace,
        )
