import pytest

from backend.app.core.sql_safety import validate_query, validate_sql_metadata, SQLSafetyError, MAX_LIMIT


# Valid queries
def test_validate_query_simple_select_with_limit():
    """Valid: Simple SELECT with LIMIT"""
    validate_query("SELECT * FROM analytics.vw_article_engagement LIMIT 50")


def test_validate_query_with_where_clause():
    """Valid: SELECT with WHERE and LIMIT"""
    validate_query(
        "SELECT id, title FROM analytics.vw_article_engagement WHERE article_id = 1 LIMIT 100"
    )


def test_validate_query_max_limit():
    """Valid: SELECT with max LIMIT"""
    validate_query(f"SELECT * FROM analytics.vw_keyword_engagement LIMIT {MAX_LIMIT}")


def test_validate_query_multiple_views():
    """Valid: JOIN across analytics views"""
    validate_query("""
        SELECT a.article_id, k.keyword_id 
        FROM analytics.vw_article_engagement a
        JOIN analytics.vw_keyword_engagement k ON a.article_id = k.article_id
        LIMIT 50
    """)


def test_validate_query_with_aggregation():
    """Valid: SELECT with GROUP BY and aggregation"""
    validate_query("""
        SELECT article_id, COUNT(*) as count
        FROM analytics.vw_article_engagement
        GROUP BY article_id
        LIMIT 10
    """)


# Invalid queries - wrong statement type
def test_validate_query_insert_rejected():
    """Invalid: INSERT is not allowed"""
    with pytest.raises(SQLSafetyError, match="Only SELECT statements"):
        validate_query("INSERT INTO analytics.vw_article_engagement VALUES (1)")


def test_validate_query_update_rejected():
    """Invalid: UPDATE is not allowed"""
    with pytest.raises(SQLSafetyError, match="Only SELECT statements"):
        validate_query("UPDATE analytics.vw_article_engagement SET title = 'foo'")


def test_validate_query_delete_rejected():
    """Invalid: DELETE is not allowed"""
    with pytest.raises(SQLSafetyError, match="Only SELECT statements"):
        validate_query("DELETE FROM analytics.vw_article_engagement")


def test_validate_query_drop_rejected():
    """Invalid: DROP is not allowed"""
    with pytest.raises(SQLSafetyError, match="Only SELECT statements"):
        validate_query("DROP TABLE analytics.vw_article_engagement")


def test_validate_query_create_rejected():
    """Invalid: CREATE is not allowed"""
    with pytest.raises(SQLSafetyError, match="Only SELECT statements"):
        validate_query(
            "CREATE VIEW test AS SELECT * FROM analytics.vw_article_engagement"
        )


def test_validate_query_execute_rejected():
    """Invalid: EXECUTE is not allowed"""
    with pytest.raises(SQLSafetyError, match="Only SELECT statements"):
        validate_query("EXECUTE sp_test")


def test_validate_query_grant_rejected():
    """Invalid: GRANT is not allowed"""
    with pytest.raises(SQLSafetyError, match="Only SELECT statements"):
        validate_query("GRANT SELECT ON analytics.vw_article_engagement")


# Invalid queries - schema restrictions
def test_validate_query_dbo_table_rejected():
    """Invalid: Direct dbo.* table access is not allowed"""
    with pytest.raises(SQLSafetyError, match="Direct table access"):
        validate_query("SELECT * FROM dbo.articles LIMIT 50")


def test_validate_query_dbo_join_rejected():
    """Invalid: JOIN with dbo.* table is not allowed"""
    with pytest.raises(SQLSafetyError, match="Direct table access"):
        validate_query("""
            SELECT a.id, c.comment
            FROM analytics.vw_article_engagement a
            JOIN dbo.comments c ON a.article_id = c.article_id
            LIMIT 50
        """)


# Invalid queries - missing or invalid LIMIT
def test_validate_query_no_limit_rejected():
    """Invalid: Missing LIMIT clause"""
    with pytest.raises(SQLSafetyError, match="must include a LIMIT or TOP clause"):
        validate_query("SELECT * FROM analytics.vw_article_engagement")


def test_validate_query_limit_exceeds_max():
    """Invalid: LIMIT exceeds maximum"""
    with pytest.raises(SQLSafetyError, match="exceeds maximum"):
        validate_query(
            f"SELECT * FROM analytics.vw_article_engagement LIMIT {MAX_LIMIT + 1}"
        )


def test_validate_query_limit_zero():
    """Invalid: LIMIT is zero"""
    with pytest.raises(SQLSafetyError, match="must be greater than 0"):
        validate_query("SELECT * FROM analytics.vw_article_engagement LIMIT 0")


def test_validate_query_limit_negative():
    """Invalid: LIMIT is negative"""
    with pytest.raises(SQLSafetyError, match="must be greater than 0"):
        validate_query("SELECT * FROM analytics.vw_article_engagement LIMIT -10")


# Edge cases
def test_validate_query_empty_string():
    """Invalid: Empty query"""
    with pytest.raises(SQLSafetyError, match="non-empty string"):
        validate_query("")


def test_validate_query_none():
    """Invalid: None query"""
    with pytest.raises(SQLSafetyError, match="non-empty string"):
        validate_query(None)


def test_validate_query_whitespace_only():
    """Invalid: Whitespace only"""
    with pytest.raises(SQLSafetyError, match="Only SELECT"):
        validate_query("   \n\t   ")


def test_validate_query_case_insensitive_keywords():
    """Valid: Keywords are case-insensitive"""
    validate_query("select * from analytics.vw_article_engagement limit 50")
    validate_query("SeLeCt * FrOm analytics.vw_article_engagement LiMiT 50")


def test_validate_query_dangerous_keyword_in_string_literal():
    """Valid: SQL keywords inside string literals are not treated as dangerous (AST parsing)"""
    validate_query("SELECT 'INSERT' FROM analytics.vw_article_engagement LIMIT 50")


def test_validate_query_merge_rejected():
    """Invalid: MERGE is not allowed (caught by SELECT or keyword check)"""
    with pytest.raises(SQLSafetyError):
        validate_query(
            "MERGE analytics.vw_article_engagement USING (SELECT 1) AS src ON 1=0 "
            "WHEN NOT MATCHED THEN INSERT VALUES (1)"
        )


def test_validate_query_multi_statement_rejected():
    """Invalid: Multi-statement queries (semicolon before end) are blocked"""
    with pytest.raises(SQLSafetyError, match="Multi-statement"):
        validate_query(
            "SELECT TOP 10 article_id FROM analytics.vw_article_engagement; "
            "SELECT TOP 5 keyword_id FROM analytics.vw_keyword_engagement"
        )


def test_validate_query_trailing_semicolon_allowed():
    """Valid: A lone trailing semicolon is permitted (not a multi-statement)"""
    validate_query("SELECT TOP 10 article_id FROM analytics.vw_article_engagement;")


# ── Join register (Rule 6) ──────────────────────────────────────────────────────

_AE = "analytics.vw_article_engagement"
_KE = "analytics.vw_keyword_engagement"
_TC = "analytics.vw_top_contributors"

_APPROVED_AE_KE: set[frozenset] = {frozenset({_AE, _KE})}
_EMPTY_REGISTER: set[frozenset] = set()


def test_join_policy_single_view_passes():
    """Valid: single view always passes even with an empty register"""
    validate_query(
        "SELECT TOP 10 article_id FROM analytics.vw_article_engagement",
        approved_pairs=_EMPTY_REGISTER,
    )


def test_join_policy_cross_view_blocked_by_empty_register():
    """Invalid: explicit JOIN blocked when pair not in approved list"""
    with pytest.raises(SQLSafetyError, match="Cross-view query not allowed"):
        validate_query(
            f"SELECT TOP 50 a.article_id FROM {_AE} a JOIN {_KE} k ON a.id = k.id",
            approved_pairs=_EMPTY_REGISTER,
        )


def test_join_policy_cross_view_allowed_by_register():
    """Valid: JOIN passes when pair is explicitly approved"""
    validate_query(
        f"SELECT TOP 50 a.article_id FROM {_AE} a JOIN {_KE} k ON a.id = k.id",
        approved_pairs=_APPROVED_AE_KE,
    )


def test_join_policy_subquery_cross_view_blocked():
    """Invalid: cross-view reference inside a subquery is also blocked"""
    with pytest.raises(SQLSafetyError, match="Cross-view query not allowed"):
        validate_query(
            f"SELECT TOP 50 article_id FROM {_AE} "
            f"WHERE article_id IN (SELECT article_id FROM {_KE})",
            approved_pairs=_EMPTY_REGISTER,
        )


def test_join_policy_three_views_partial_approval_blocked():
    """Invalid: three views where only one pair is approved — second pair still blocked"""
    with pytest.raises(SQLSafetyError, match="Cross-view query not allowed"):
        validate_query(
            f"SELECT TOP 50 a.article_id FROM {_AE} a "
            f"JOIN {_KE} k ON a.id = k.id "
            f"JOIN {_TC} t ON t.id = a.id",
            approved_pairs=_APPROVED_AE_KE,
        )


def test_join_policy_skipped_when_no_policy_provided():
    """Valid: cross-view JOIN passes when approved_pairs=None (backward compat)"""
    validate_query(
        f"SELECT TOP 50 a.article_id FROM {_AE} a JOIN {_KE} k ON a.id = k.id"
    )


# ── Metadata validation (validate_sql_metadata) ────────────────────────────────

_META_AE = {
    "analytics.vw_article_engagement": {
        "columns": [
            {"name": "article_id"},
            {"name": "title"},
            {"name": "publication_date"},
            {"name": "insert_date"},
            {"name": "comment_count"},
            {"name": "avg_comment_sentiment"},
            {"name": "total_replies"},
            {"name": "keyword_count"},
        ],
        "mandatory_filters": [],
    }
}

_META_WITH_FILTER = {
    "analytics.vw_article_engagement": {
        "columns": [{"name": "article_id"}, {"name": "tenant_id"}, {"name": "comment_count"}],
        "mandatory_filters": ["tenant_id"],
    }
}


def test_metadata_valid_columns_pass():
    """Valid: all columns exist in the view metadata"""
    validate_sql_metadata(
        "SELECT TOP 10 article_id, title, comment_count FROM analytics.vw_article_engagement",
        _META_AE,
    )


def test_metadata_unknown_column_blocked():
    """Invalid: hallucinated column name rejected with the valid list"""
    with pytest.raises(SQLSafetyError, match="article_sentiment"):
        validate_sql_metadata(
            "SELECT TOP 10 article_id, article_sentiment FROM analytics.vw_article_engagement",
            _META_AE,
        )


def test_metadata_error_message_includes_valid_list():
    """Invalid: error message lists all valid column names for LLM self-correction"""
    with pytest.raises(SQLSafetyError, match="article_id"):
        validate_sql_metadata(
            "SELECT TOP 10 bad_col FROM analytics.vw_article_engagement",
            _META_AE,
        )


def test_metadata_select_star_skips_column_check():
    """Valid: SELECT * bypasses column validation"""
    validate_sql_metadata(
        "SELECT TOP 10 * FROM analytics.vw_article_engagement",
        _META_AE,
    )


def test_metadata_alias_qualified_column_validated():
    """Valid: table alias resolved to view — column checked against correct view"""
    validate_sql_metadata(
        "SELECT TOP 10 a.article_id, a.comment_count FROM analytics.vw_article_engagement a",
        _META_AE,
    )


def test_metadata_alias_qualified_unknown_column_blocked():
    """Invalid: alias-qualified column that doesn't exist in the view"""
    with pytest.raises(SQLSafetyError, match="ghost_col"):
        validate_sql_metadata(
            "SELECT TOP 10 a.ghost_col FROM analytics.vw_article_engagement a",
            _META_AE,
        )


def test_metadata_subquery_alias_column_skipped():
    """Valid: column qualified by a subquery alias is not validated (unresolvable)"""
    validate_sql_metadata(
        "SELECT TOP 10 sub.article_id FROM "
        "(SELECT TOP 100 article_id FROM analytics.vw_article_engagement) sub",
        _META_AE,
    )


def test_metadata_select_alias_in_having_skipped():
    """Valid: column name that matches a SELECT-list alias is not rejected"""
    validate_sql_metadata(
        "SELECT TOP 10 comment_count, COUNT(*) AS cnt "
        "FROM analytics.vw_article_engagement "
        "GROUP BY comment_count HAVING cnt > 5",
        _META_AE,
    )


def test_metadata_column_in_where_validated():
    """Invalid: unknown column in WHERE clause is caught"""
    with pytest.raises(SQLSafetyError, match="mystery_filter"):
        validate_sql_metadata(
            "SELECT TOP 10 article_id FROM analytics.vw_article_engagement "
            "WHERE mystery_filter = 1",
            _META_AE,
        )


def test_metadata_column_in_function_validated():
    """Invalid: column inside a function call is still validated"""
    with pytest.raises(SQLSafetyError, match="bad_date_col"):
        validate_sql_metadata(
            "SELECT TOP 10 article_id FROM analytics.vw_article_engagement "
            "WHERE YEAR(bad_date_col) = 2025",
            _META_AE,
        )


def test_metadata_mandatory_filter_present_passes():
    """Valid: mandatory filter column appears in WHERE clause"""
    validate_sql_metadata(
        "SELECT TOP 10 article_id FROM analytics.vw_article_engagement WHERE tenant_id = 1",
        _META_WITH_FILTER,
    )


def test_metadata_mandatory_filter_missing_blocked():
    """Invalid: mandatory filter absent from WHERE clause"""
    with pytest.raises(SQLSafetyError, match="tenant_id"):
        validate_sql_metadata(
            "SELECT TOP 10 article_id, comment_count FROM analytics.vw_article_engagement",
            _META_WITH_FILTER,
        )


def test_metadata_no_mandatory_filters_passes():
    """Valid: view with empty mandatory_filters always passes the filter check"""
    validate_sql_metadata(
        "SELECT TOP 10 article_id FROM analytics.vw_article_engagement",
        _META_AE,
    )


def test_metadata_empty_context_skipped():
    """Valid: no metadata context — check is skipped entirely"""
    validate_sql_metadata(
        "SELECT TOP 10 article_id FROM analytics.vw_article_engagement",
        {},
    )
