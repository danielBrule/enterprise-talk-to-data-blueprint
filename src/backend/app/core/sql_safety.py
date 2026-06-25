"""
SQL safety validation using sqlglot AST parsing.

All checks operate on the parsed AST rather than regex so they are correct for
CTEs, subqueries, aliases, and string literals containing SQL keywords. On any
parse failure the query is rejected (fail closed).

Dialect: tsql — matches Azure SQL Server. sqlglot normalises SELECT TOP N to the
same Limit node as LIMIT N, so a single _check_row_limit covers both forms.
"""
from itertools import combinations

import sqlglot
import sqlglot.expressions as exp

from .config import settings
from .logger import logger


class SQLSafetyError(Exception):
    """Raised when a query violates SQL safety rules."""
    pass


MAX_LIMIT = 500
QUERY_TIMEOUT_SECONDS: int = settings.sql_query_timeout_seconds

_DIALECT = "tsql"

_FORBIDDEN_NODE_TYPES = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Create,
    exp.Alter,
    exp.TruncateTable,
    exp.Merge,
    exp.Execute,   # EXEC / EXECUTE
    exp.Grant,
)


# ── Parsing ────────────────────────────────────────────────────────────────────

def _parse(query: str) -> tuple[exp.Expression, list]:
    """Parse with tsql dialect. Raises SQLSafetyError on failure (fail closed)."""
    try:
        statements = sqlglot.parse(query, dialect=_DIALECT, error_level=sqlglot.ErrorLevel.RAISE)
    except sqlglot.errors.ParseError as e:
        raise SQLSafetyError(f"Query could not be parsed: {e}") from e
    if not statements or statements[0] is None:
        raise SQLSafetyError("Only SELECT statements are allowed")
    return statements[0], statements


# ── Rules ──────────────────────────────────────────────────────────────────────

def _check_single_select(statements: list) -> None:
    if len(statements) > 1:
        raise SQLSafetyError("Multi-statement queries are not allowed")
    if not isinstance(statements[0], exp.Select):
        raise SQLSafetyError("Only SELECT statements are allowed")


def _check_no_dangerous_nodes(tree: exp.Expression) -> None:
    for node_type in _FORBIDDEN_NODE_TYPES:
        if tree.find(node_type):
            raise SQLSafetyError(f"Statement type '{node_type.__name__}' is not allowed")


def _check_no_dbo_access(tree: exp.Expression) -> None:
    for table in tree.find_all(exp.Table):
        db = (table.args.get("db") or exp.Identifier(this="")).name.lower()
        if db == "dbo":
            raise SQLSafetyError(
                "Direct table access (dbo.*) is not allowed. Only analytics.* views are permitted."
            )


def _check_row_limit(tree: exp.Expression, params: dict | None) -> None:
    """Require TOP or LIMIT with a value in (0, MAX_LIMIT]. sqlglot normalises
    SELECT TOP N to the same Limit node as LIMIT N in tsql dialect."""
    limit = tree.find(exp.Limit)

    if not limit:
        raise SQLSafetyError(f"Query must include a LIMIT or TOP clause (max {MAX_LIMIT})")

    value_expr = limit.args.get("expression")
    if value_expr is None:
        raise SQLSafetyError("LIMIT/TOP clause has no value")

    # Negative literal: LIMIT -10 parses as Neg(Literal(10))
    if isinstance(value_expr, exp.Neg):
        raise SQLSafetyError("LIMIT/TOP value must be greater than 0")

    # Parameter placeholder (e.g. :row_limit)
    if isinstance(value_expr, (exp.Parameter, exp.Var)):
        param_name = str(value_expr).lstrip(":").lower()
        if not params or param_name not in params:
            raise SQLSafetyError(f"Missing parameter for LIMIT/TOP: :{param_name}")
        try:
            value = int(params[param_name])
        except (TypeError, ValueError):
            raise SQLSafetyError(f"LIMIT/TOP parameter :{param_name} must be an integer")
    else:
        try:
            value = int(value_expr.name)
        except (TypeError, ValueError, AttributeError):
            raise SQLSafetyError("LIMIT/TOP value could not be resolved to an integer")

    if value <= 0:
        raise SQLSafetyError("LIMIT/TOP value must be greater than 0")
    if value > MAX_LIMIT:
        raise SQLSafetyError(f"LIMIT/TOP value {value} exceeds maximum of {MAX_LIMIT}")


def _check_no_forbidden_joins(
    tree: exp.Expression, approved_pairs: set[frozenset]
) -> None:
    """
    Block any SQL that references more than one analytics view unless every
    view pair it touches is listed in the approved join register.

    Operates on the AST so CTE aliases and subquery references resolve to their
    source tables — regex scanning of the raw SQL string cannot do this.
    """
    views = {
        f"analytics.{table.name.lower()}"
        for table in tree.find_all(exp.Table)
        if (table.args.get("db") or exp.Identifier(this="")).name.lower() == "analytics"
    }
    if len(views) < 2:
        return
    for a, b in combinations(sorted(views), 2):
        if frozenset({a, b}) not in approved_pairs:
            raise SQLSafetyError(
                f"Cross-view query not allowed: {a} and {b} cannot be used together. "
                "Query each view independently."
            )


def _check_columns_exist(
    tree: exp.Expression,
    alias_to_view: dict[str, str],
    known_columns: dict[str, set[str]],
    all_known: set[str],
    select_aliases: set[str],
) -> None:
    for col in tree.find_all(exp.Column):
        col_name = col.name.lower()
        if not col_name or col_name == "*":
            continue
        # Column is a SELECT-list alias used downstream (e.g. in HAVING) — skip
        if col_name in select_aliases:
            continue

        table_part = col.args.get("table")
        table_qualifier = table_part.name.lower() if table_part else None

        if table_qualifier:
            view_key = alias_to_view.get(table_qualifier)
            if view_key is None:
                # Unresolvable qualifier (subquery alias, CTE name, etc.) — skip
                continue
            valid_cols = known_columns.get(view_key, all_known)
        else:
            valid_cols = all_known

        if col_name not in valid_cols:
            raise SQLSafetyError(
                f"Column '{col_name}' does not exist in the selected view. "
                f"Valid columns are: {', '.join(sorted(valid_cols))}."
            )


def _check_mandatory_filters(tree: exp.Expression, metadata_context: dict) -> None:
    where = tree.find(exp.Where)
    where_cols: set[str] = (
        {col.name.lower() for col in where.find_all(exp.Column)} if where else set()
    )
    for view_name, view_data in metadata_context.items():
        for required in (view_data.get("mandatory_filters") or []):
            if required.lower() not in where_cols:
                raise SQLSafetyError(
                    f"Mandatory filter '{required}' is missing from the WHERE clause "
                    f"(required by {view_name})."
                )


# ── Public API ─────────────────────────────────────────────────────────────────

def validate_sql_metadata(sql: str, metadata_context: dict) -> None:
    """
    Validate SQL column references and mandatory filters against view metadata.

    Should be called after validate_query() which guarantees the SQL is parseable.
    Two checks:
    - Every explicit column reference must exist in the view's declared column list.
      Skipped when SELECT * is used. Columns qualified by an unresolvable alias
      (subquery result, CTE) are skipped rather than rejected.
    - Every mandatory_filter declared in view YAML must appear in the WHERE clause.

    Raises SQLSafetyError with a precise, LLM-actionable message on failure so
    the error can be fed back to the SQL generation stage for self-correction.
    """
    if not sql or not metadata_context:
        return

    tree, _ = _parse(sql)

    # alias → full view name (e.g. "a" → "analytics.vw_article_engagement")
    alias_to_view: dict[str, str] = {}
    for table in tree.find_all(exp.Table):
        db = (table.args.get("db") or exp.Identifier(this="")).name.lower()
        full = f"{db}.{table.name.lower()}" if db else table.name.lower()
        if table.alias:
            alias_to_view[table.alias.lower()] = full

    # known columns per view, normalised to lowercase
    known_columns: dict[str, set[str]] = {
        vname.lower(): {c["name"].lower() for c in (vdata.get("columns") or [])}
        for vname, vdata in metadata_context.items()
    }
    all_known: set[str] = set().union(*known_columns.values()) if known_columns else set()

    # SELECT-list aliases (e.g. COUNT(*) AS cnt) — excluded from column validation
    select_aliases: set[str] = {
        node.alias.lower() for node in tree.find_all(exp.Alias) if node.alias
    }

    if not tree.find(exp.Star):
        _check_columns_exist(tree, alias_to_view, known_columns, all_known, select_aliases)

    _check_mandatory_filters(tree, metadata_context)


def validate_query(
    query: str,
    params: dict | None = None,
    approved_pairs: set[frozenset] | None = None,
) -> None:
    """
    Validate that a SQL query is safe to execute against the analytics views.

    Raises SQLSafetyError if any rule is violated:
    - Rule 1  : Must be a single SELECT statement (no DDL/DML, no multi-statement)
    - Rule 2  : No dangerous statement types inside the tree (Insert, Drop, Merge …)
    - Rule 3  : No direct dbo.* table access (analytics.* views only)
    - Rule 4/5: Must include SELECT TOP or LIMIT; value must be 1–MAX_LIMIT
    - Rule 6  : Cross-view references only allowed for approved pairs (skipped if
                approved_pairs is None — backward compat for callers without a policy)

    Fails closed: any parse error rejects the query.
    """
    if not query or not isinstance(query, str):
        raise SQLSafetyError("Query must be a non-empty string")

    tree, statements = _parse(query)

    _check_single_select(statements)
    _check_no_dangerous_nodes(tree)
    _check_no_dbo_access(tree)
    _check_row_limit(tree, params)
    if approved_pairs is not None:
        _check_no_forbidden_joins(tree, approved_pairs)

    logger.debug("sql_safety.passed query_preview=%s", query[:80])
