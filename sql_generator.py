import re

import sqlglot
from sqlglot import exp


FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "REPLACE",
    "GRANT",
    "REVOKE",
    "MERGE"
}


DESTRUCTIVE_PATTERNS = [
    r"\bdelete\b",
    r"\bremove\b",
    r"\berase\b",
    r"\bdestroy\b",
    r"\btruncate\b",
    r"\bdrop\b",
    r"\bupdate\b",
    r"\bmodify\b",
    r"\bchange\b",
    r"\binsert\b",
    r"\bcreate\b",
    r"\balter\b"
]


def validate_user_request(question):
    """
    Determines whether the user's request is asking for a
    potentially destructive database operation.

    ClarifySQL is currently read-only.
    """

    if not question or not question.strip():

        return {
            "allowed": False,
            "message": "Question is empty."
        }

    question_lower = question.lower().strip()

    for pattern in DESTRUCTIVE_PATTERNS:

        if re.search(pattern, question_lower):

            return {
                "allowed": False,
                "message": (
                    "This request appears to modify or delete "
                    "database data. ClarifySQL currently supports "
                    "read-only database queries."
                )
            }

    return {
        "allowed": True,
        "message": "User request is read-only."
    }


def validate_sql(sql):
    """
    Performs security validation on generated SQL.

    Only a single read-only SELECT or WITH statement is allowed.
    """

    if not sql or not sql.strip():

        return {
            "safe": False,
            "message": "SQL query is empty."
        }

    cleaned_sql = sql.strip()

    sql_without_trailing_semicolon = (
        cleaned_sql.rstrip(";").strip()
    )

    try:

        statements = sqlglot.parse(
            sql_without_trailing_semicolon,
            read="mysql"
        )

    except Exception as e:

        return {
            "safe": False,
            "message": f"Invalid SQL syntax: {str(e)}"
        }

    if len(statements) != 1:

        return {
            "safe": False,
            "message": "Multiple SQL statements are not allowed."
        }

    parsed_sql = statements[0]

    # Only SELECT statements are allowed.
    if not isinstance(parsed_sql, exp.Select):

        return {
            "safe": False,
            "message": "Only read-only SELECT queries are allowed."
        }

    dangerous_expression_types = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Create,
        exp.Alter,
        exp.Merge
    )

    for expression in parsed_sql.walk():

        if isinstance(
            expression,
            dangerous_expression_types
        ):

            return {
                "safe": False,
                "message": (
                    "Unsafe SQL operation detected. "
                    "Only read-only queries are allowed."
                )
            }

    sql_upper = cleaned_sql.upper()

    for keyword in FORBIDDEN_KEYWORDS:

        pattern = r"\b" + re.escape(keyword) + r"\b"

        if re.search(pattern, sql_upper):

            return {
                "safe": False,
                "message": (
                    f"Unsafe SQL detected: "
                    f"{keyword} is not allowed."
                )
            }

    first_word_match = re.match(
        r"^\s*([A-Z]+)",
        sql_upper
    )

    if not first_word_match:

        return {
            "safe": False,
            "message": "Could not determine SQL statement type."
        }

    first_word = first_word_match.group(1)

    if first_word != "SELECT":

        return {
            "safe": False,
            "message": "Only SELECT queries are allowed."
        }

    return {
        "safe": True,
        "message": "SQL query is safe."
    }


def validate_schema_tables(sql, schema):
    """
    Ensures every table referenced by the generated SQL exists
    in the actual database schema.
    """

    if not schema:

        return {
            "valid": False,
            "message": "Database schema is unavailable."
        }

    available_tables = set(
        schema.get("tables", {}).keys()
    )

    try:

        parsed_sql = sqlglot.parse_one(
            sql,
            read="mysql"
        )

    except Exception as e:

        return {
            "valid": False,
            "message": f"Could not parse SQL: {str(e)}"
        }

    referenced_tables = set()

    for table in parsed_sql.find_all(exp.Table):

        table_name = table.name

        if table_name:

            referenced_tables.add(table_name)

    for table_name in referenced_tables:

        if table_name not in available_tables:

            return {
                "valid": False,
                "message": (
                    f"Table '{table_name}' does not exist "
                    f"in the database schema."
                )
            }

    return {
        "valid": True,
        "message": (
            "All referenced tables exist "
            "in the database schema."
        )
    }


def validate_schema_columns(sql, schema):
    """
    Validates explicitly qualified columns against the
    database schema.

    Unqualified columns are left to MySQL because they may
    depend on joins, aliases, expressions, and aggregation.
    """

    if not schema:

        return {
            "valid": False,
            "message": "Database schema is unavailable."
        }

    try:

        parsed_sql = sqlglot.parse_one(
            sql,
            read="mysql"
        )

    except Exception as e:

        return {
            "valid": False,
            "message": f"Could not parse SQL: {str(e)}"
        }

    table_map = {}

    for table in parsed_sql.find_all(exp.Table):

        table_name = table.name
        alias = table.alias_or_name

        if table_name:

            table_map[alias] = table_name

    for column in parsed_sql.find_all(exp.Column):

        column_name = column.name
        table_alias = column.table

        if column_name == "*":

            continue

        if table_alias:

            actual_table = table_map.get(table_alias)

            if not actual_table:

                continue

            table_info = schema["tables"].get(
                actual_table
            )

            if not table_info:

                return {
                    "valid": False,
                    "message": (
                        f"Table '{actual_table}' does not "
                        f"exist in the database schema."
                    )
                }

            available_columns = {
                column_info["column"]
                for column_info in table_info.get(
                    "columns",
                    []
                )
            }

            if column_name not in available_columns:

                return {
                    "valid": False,
                    "message": (
                        f"Column '{column_name}' does not exist "
                        f"in table '{actual_table}'."
                    )
                }

    return {
        "valid": True,
        "message": "Qualified columns are valid."
    }