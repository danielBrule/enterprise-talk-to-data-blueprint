"""
Tests for AnalyticsStore (SQLite backend for traces + feedback).
All tests use tmp_path so no files are written to the working tree.
"""
import json
import sqlite3

from backend.app.db.analytics_store import AnalyticsStore
from backend.app.models.feedback import FeedbackRecord


def _store(tmp_path) -> AnalyticsStore:
    return AnalyticsStore(db_path=str(tmp_path / "analytics.db"))


def _raw_trace(trace_id: str = "t1", question: str = "top articles?", **overrides) -> dict:
    base = {
        "trace_id": trace_id,
        "timestamp": "2026-06-26T10:00:00+00:00",
        "question": question,
        "intent": "article_engagement",
        "execution_status": "success",
        "selected_views": ["analytics.vw_article_engagement"],
        "answer": "Article A leads.",
        "refusal_reason": None,
        "latency_ms": {"total_ms": 1000.0},
        "user_context": "role=analyst",
        "sql_retries": 0,
        "pipeline_env": "api",
    }
    base.update(overrides)
    return base


# ── insert_trace / get_recent_traces ─────────────────────────────────────────

def test_get_recent_traces_empty_db(tmp_path):
    store = _store(tmp_path)
    assert store.get_recent_traces(limit=10) == []


def test_insert_and_get_recent_traces(tmp_path):
    store = _store(tmp_path)
    store.insert_trace(_raw_trace("t1", timestamp="2026-06-26T10:00:00+00:00"))
    store.insert_trace(_raw_trace("t2", timestamp="2026-06-26T11:00:00+00:00"))
    store.insert_trace(_raw_trace("t3", timestamp="2026-06-26T12:00:00+00:00"))

    records = store.get_recent_traces(limit=10)
    assert len(records) == 3
    assert records[0]["trace_id"] == "t3"  # newest first
    assert records[1]["trace_id"] == "t2"
    assert records[2]["trace_id"] == "t1"


def test_get_recent_traces_respects_limit(tmp_path):
    store = _store(tmp_path)
    for i in range(5):
        store.insert_trace(_raw_trace(f"t{i}", timestamp=f"2026-06-26T{i:02d}:00:00+00:00"))

    records = store.get_recent_traces(limit=2)
    assert len(records) == 2
    assert records[0]["trace_id"] == "t4"
    assert records[1]["trace_id"] == "t3"


def test_insert_trace_selected_views_roundtrip(tmp_path):
    store = _store(tmp_path)
    views = ["analytics.vw_article_engagement", "analytics.vw_top_contributors"]
    store.insert_trace(_raw_trace("t1", selected_views=views))

    records = store.get_recent_traces(limit=1)
    stored = json.loads(records[0]["selected_views"])
    assert "analytics.vw_article_engagement" in stored
    assert "analytics.vw_top_contributors" in stored


def test_insert_trace_duplicate_ignored(tmp_path):
    store = _store(tmp_path)
    store.insert_trace(_raw_trace("t1"))
    store.insert_trace(_raw_trace("t1"))  # same trace_id — INSERT OR IGNORE

    assert len(store.get_recent_traces(limit=10)) == 1


def test_insert_trace_latency_stored(tmp_path):
    store = _store(tmp_path)
    store.insert_trace(_raw_trace("t1", latency_ms={"total_ms": 1234.5}))

    records = store.get_recent_traces(limit=1)
    assert records[0]["latency_total_ms"] == 1234.5


# ── insert_feedback ───────────────────────────────────────────────────────────

def test_insert_feedback(tmp_path):
    store = _store(tmp_path)
    store.insert_trace(_raw_trace("t1"))
    record = FeedbackRecord(
        trace_id="t1",
        rating=1,
        comment="Very helpful!",
        user_role="analyst",
    )
    store.insert_feedback(record)

    with sqlite3.connect(tmp_path / "analytics.db") as conn:
        row = conn.execute("SELECT * FROM feedback WHERE trace_id = 't1'").fetchone()
    assert row is not None
    assert row[3] == 1              # rating
    assert row[4] == "Very helpful!"  # comment
    assert row[5] == "analyst"      # user_role


def test_insert_feedback_negative_rating(tmp_path):
    store = _store(tmp_path)
    store.insert_trace(_raw_trace("t1"))
    record = FeedbackRecord(trace_id="t1", rating=-1, comment=None, user_role="editor")
    store.insert_feedback(record)

    with sqlite3.connect(tmp_path / "analytics.db") as conn:
        row = conn.execute("SELECT rating FROM feedback WHERE trace_id = 't1'").fetchone()
    assert row[0] == -1


def test_traces_and_feedback_joinable(tmp_path):
    store = _store(tmp_path)
    store.insert_trace(_raw_trace("t1", question="Which articles have the most comments?"))
    store.insert_feedback(FeedbackRecord(trace_id="t1", rating=-1, comment="Wrong answer", user_role="editor"))

    with sqlite3.connect(tmp_path / "analytics.db") as conn:
        row = conn.execute(
            """SELECT t.question, f.rating, f.comment
               FROM traces t JOIN feedback f ON t.trace_id = f.trace_id
               WHERE f.rating = -1"""
        ).fetchone()
    assert row is not None
    assert "articles" in row[0]
    assert row[1] == -1
    assert row[2] == "Wrong answer"
