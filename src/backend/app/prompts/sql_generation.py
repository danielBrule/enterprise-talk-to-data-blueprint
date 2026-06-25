PROMPT_VERSION = "sql_gen_v4"


def build_sql_generation_prompt(question: str, views_context: str) -> list[dict]:
    """
    Build the SQL generation prompt.

    Expects:
        question:      the user's natural language question
        views_context: pre-formatted string produced by _build_views_context —
                       one block per view with purpose, available columns, and limitations

    Returns a two-message list (system + user) instructing the model to produce
    a single JSON object {"sql": "<T-SQL SELECT TOP N statement>"}.
    """
    system = (
        "You generate T-SQL SELECT statements for Azure SQL Server. "
        "You must only query the analytics views provided. "
        "Every query must use SELECT TOP N where N is between 1 and 500. "
        "Never use LIMIT, FETCH FIRST, or OFFSET — this is T-SQL, not standard SQL. "
        "Never query any table outside the analytics schema. "
        "Respond only with valid JSON containing a single key 'sql'. "
        "No markdown fences, no explanation outside the JSON."
    )
    user = f"""Generate a T-SQL SELECT statement to answer this question:
"{question}"

Approved views and columns:
{views_context}

Rules:
- Query only analytics.* views listed above.
- Use SELECT TOP N (1 <= N <= 500). Do not use LIMIT or FETCH FIRST.
- No DDL, DML, EXEC, subqueries outside analytics schema, or multi-statement queries.
- Include only columns that exist in the view definitions above.
- For ranking questions, use ORDER BY with SELECT TOP 10 (or another appropriate N).
- For scalar aggregate questions (a single SUM/AVG/COUNT/MAX/MIN with no GROUP BY), \
use SELECT TOP 1 — the result is always one row.
- For grouped aggregate questions (aggregate + GROUP BY), use SELECT TOP 10 for \
"top N by metric" questions, or SELECT TOP 500 when all groups are needed.
- For filter-only questions where all matching rows are needed, use SELECT TOP 500.
- When returning multiple rows, always include the primary identifier column of the view \
(article_id for vw_article_engagement, keyword_id for vw_keyword_engagement, \
contributor_id for vw_top_contributors, error_id for vw_ingestion_errors).
- Use descriptive aliases for aggregate results that reflect the metric, \
e.g. total_comment_count, avg_sentiment, max_comment_count, error_count.
- Respect grain: each view already has one row per its stated unit (article, keyword, contributor, error). \
Do not re-aggregate a column if the grain context shows rows are already atomic.
- Respect allowed aggregations: only apply the aggregate functions listed for each column. \
Never SUM a column listed as [AVG, MIN, MAX] only (e.g. avg_comment_sentiment, avg_sentiment).
- GROUP BY only columns listed as valid dimensions for the view. \
If no dimensions are listed, the view is already at grain level — do not add GROUP BY.

Respond with exactly this JSON:
{{
  "sql": "<SELECT TOP N col1, col2 FROM analytics.vw_name [WHERE ...] [ORDER BY ...]>"
}}"""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
