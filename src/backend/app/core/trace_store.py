import json
import pathlib
from typing import TYPE_CHECKING

from .config import settings
from .logger import logger
from .pii_filter import PiiFilter

if TYPE_CHECKING:
    from ..models.trace import TraceRecord
    from ..db.analytics_store import AnalyticsStore


class TraceStore:
    """
    Appends pipeline TraceRecords to data/analytics/traces.jsonl (JSONL) and,
    when an AnalyticsStore is provided, also inserts into data/analytics/analytics.db.

    JSONL: append-only raw log, human-readable, replay source.
    SQLite: queryable; supports JOIN with feedback table via trace_id.

    DEMO ONLY — in production:
    - Replace _write() with an Azure Application Insights / Log Analytics call for
      real-time operational monitoring and alerting.
    - Replace AnalyticsStore's SQLite connection with an Azure SQL pool so traces,
      feedback, and quality checks are all JOIN-able with the source analytics views
      in one database. AnalyticsStore uses standard SQL — only _get_conn() changes.
    Both backends are complementary, not alternatives: App Insights for ops,
    Azure SQL for analytical queries.
    """

    def __init__(
        self,
        path: str | None = None,
        anonymize: bool | None = None,
        analytics_store: "AnalyticsStore | None" = None,
    ) -> None:
        self._path = pathlib.Path(path or settings.trace_file)
        _anonymize = anonymize if anonymize is not None else settings.trace_anonymize
        self._filter = PiiFilter(enabled=_anonymize)
        self._analytics = analytics_store

    def append(self, trace: "TraceRecord") -> None:
        """
        Persist one trace record. Never raises — write failures are logged and
        swallowed so that a disk or network error never bubbles up to the user.
        The pipeline's primary job is answering questions, not storing telemetry.
        """
        raw = None
        try:
            raw = json.loads(trace.model_dump_json())
            raw["pipeline_env"] = settings.pipeline_env
            filtered = self._filter.apply(raw)
            self._write(json.dumps(filtered))
        except Exception as exc:
            logger.warning("trace_store.write_failed error=%s", exc)

        if self._analytics is not None and raw is not None:
            try:
                self._analytics.insert_trace(raw)
            except Exception as exc:
                logger.warning("analytics_store.write_failed error=%s", exc)

    def _write(self, line: str) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
