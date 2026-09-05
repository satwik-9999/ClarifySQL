import json

from database import get_db_connection


class QueryHistory:
    """
    Manages persistent query history using MySQL.
    """

    def add_query(
        self,
        session_id,
        question,
        sql,
        query_intent,
        results,
        result_analysis
    ):

        connection = get_db_connection()

        if connection is None:
            return False

        cursor = None

        try:

            cursor = connection.cursor()

            query = """
            INSERT INTO query_history (
                session_id,
                question,
                generated_sql,
                query_intent,
                execution_status,
                row_count
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """

            cursor.execute(
                query,
                (
                    session_id,
                    question,
                    sql,
                    json.dumps(query_intent),
                    "success",
                    len(results)
                )
            )

            connection.commit()

            return True

        except Exception as e:

            print(
                f"History insert error: {e}"
            )

            return False

        finally:

            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    def get_history(
        self,
        session_id=None
    ):

        connection = get_db_connection()

        if connection is None:
            return []

        cursor = None

        try:

            cursor = connection.cursor(
                dictionary=True
            )

            if session_id:

                query = """
                SELECT
                    history_id,
                    session_id,
                    question,
                    generated_sql,
                    query_intent,
                    execution_status,
                    row_count,
                    created_at
                FROM query_history
                WHERE session_id = %s
                ORDER BY created_at DESC
                """

                cursor.execute(
                    query,
                    (session_id,)
                )

            else:

                query = """
                SELECT
                    history_id,
                    session_id,
                    question,
                    generated_sql,
                    query_intent,
                    execution_status,
                    row_count,
                    created_at
                FROM query_history
                ORDER BY created_at DESC
                """

                cursor.execute(query)

            history = cursor.fetchall()

            for entry in history:

                if entry["query_intent"]:

                    try:

                        entry["query_intent"] = json.loads(
                            entry["query_intent"]
                        )

                    except Exception:

                        pass

                if entry["created_at"]:

                    entry["created_at"] = (
                        entry["created_at"].isoformat()
                    )

            return history

        except Exception as e:

            print(
                f"History retrieval error: {e}"
            )

            return []

        finally:

            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    def clear_history(
        self,
        session_id=None
    ):

        connection = get_db_connection()

        if connection is None:
            return False

        cursor = None

        try:

            cursor = connection.cursor()

            if session_id:

                query = """
                DELETE FROM query_history
                WHERE session_id = %s
                """

                cursor.execute(
                    query,
                    (session_id,)
                )

            else:

                query = """
                DELETE FROM query_history
                """

                cursor.execute(query)

            connection.commit()

            return True

        except Exception as e:

            print(
                f"History deletion error: {e}"
            )

            return False

        finally:

            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()


query_history = QueryHistory()