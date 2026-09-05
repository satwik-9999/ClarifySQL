import os

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv


load_dotenv()


def get_db_connection():
    try:

        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        return connection

    except Error as e:

        print(
            f"Database connection error: {e}"
        )

        return None


def get_database_schema():

    connection = get_db_connection()

    if connection is None:
        return None

    cursor = None

    try:

        cursor = connection.cursor(
            dictionary=True
        )

        schema = {
            "tables": {},
            "relationships": []
        }

        cursor.execute(
            "SHOW TABLES"
        )

        tables_result = cursor.fetchall()

        table_names = []

        for row in tables_result:

            table_name = list(
                row.values()
            )[0]

            table_names.append(
                table_name
            )

        for table_name in table_names:

            cursor.execute(
                f"DESCRIBE `{table_name}`"
            )

            columns_result = cursor.fetchall()

            columns = []
            primary_keys = []

            for column in columns_result:

                column_info = {
                    "column": column["Field"],
                    "type": column["Type"],
                    "nullable": (
                        column["Null"] == "YES"
                    )
                }

                columns.append(
                    column_info
                )

                if column["Key"] == "PRI":

                    primary_keys.append(
                        column["Field"]
                    )

            schema["tables"][table_name] = {
                "columns": columns,
                "primary_keys": primary_keys
            }

        relationship_query = """
        SELECT
            TABLE_NAME,
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s
        AND REFERENCED_TABLE_NAME IS NOT NULL;
        """

        cursor.execute(
            relationship_query,
            (os.getenv("DB_NAME"),)
        )

        relationships = cursor.fetchall()

        for relationship in relationships:

            schema["relationships"].append(
                {
                    "table": relationship[
                        "TABLE_NAME"
                    ],
                    "column": relationship[
                        "COLUMN_NAME"
                    ],
                    "references_table": relationship[
                        "REFERENCED_TABLE_NAME"
                    ],
                    "references_column": relationship[
                        "REFERENCED_COLUMN_NAME"
                    ]
                }
            )

        return schema

    except Error as e:

        print(
            f"Schema extraction error: {e}"
        )

        return None

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


def execute_query(sql):

    connection = get_db_connection()

    if connection is None:
        return None

    cursor = None

    try:

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(sql)

        results = cursor.fetchall()

        return results

    except Error as e:

        print(
            f"Query execution error: {e}"
        )

        return None

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()