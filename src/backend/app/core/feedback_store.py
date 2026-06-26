"""
Feedback store — dual-write: JSONL append-only log + SQLite analytics DB.

JSONL (data/analytics/feedback.jsonl): raw log, human-readable, replay source.
SQLite (data/analytics/analytics.db):  queryable, JOIN-able with traces table.
"""
import json
from pathlib import Path
from typing import TYPE_CHECKING

from ..core.logger import logger

if TYPE_CHECKING:
    from ..models.feedback import FeedbackRecord
    from ..db.analytics_store import AnalyticsStore


class FeedbackStore:
    def __init__(
        self,
        path: str | None = None,
        analytics_store: "AnalyticsStore | None" = None,
    ) -> None:
        from ..core.config import settings
        self._path = Path(path or settings.feedback_file)
        self._analytics = analytics_store

    def append(self, record: "FeedbackRecord") -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as f:
                f.write(record.model_dump_json() + "\n")
        except Exception as exc:
            logger.warning("feedback_store.write_failed error=%s", exc)

        if self._analytics is not None:
            try:
                self._analytics.insert_feedback(record)
            except Exception as exc:
                logger.warning("analytics_store.feedback_write_failed error=%s", exc)
