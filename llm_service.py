import os
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")


if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured. "
        "Please add it to the .env file."
    )


client = genai.Client(
    api_key=api_key
)


MODEL = "gemini-3.6-flash"


def generate_sql_with_llm(
    question,
    schema,
    query_intent=None
):
    """
    Generates MySQL SQL from a natural-language question
    using Google Gemini.

    The database schema and structured query intent are
    provided to Gemini so that the generated SQL uses the
    actual database structure and understood intent.
    """

    schema_text = json.dumps(
        schema,
        indent=2,
        default=str
    )

    intent_text = json.dumps(
        query_intent,
        indent=2,
        default=str
    )

    prompt = f"""
You are the SQL generation engine for ClarifySQL.

Convert the user's natural-language question into ONE
read-only MySQL SQL query.

STRICT RULES:

1. Generate ONLY SELECT or WITH queries.
2. Never generate INSERT.
3. Never generate UPDATE.
4. Never generate DELETE.
5. Never generate DROP.
6. Never generate ALTER.
7. Never generate CREATE.
8. Never generate TRUNCATE.
9. Never generate REPLACE.
10. Never generate GRANT.
11. Never generate REVOKE.
12. Use ONLY tables that exist in the provided schema.
13. Use ONLY columns that exist in the provided schema.
14. Respect the relationships in the schema.
15. Use proper JOIN conditions when multiple tables are required.
16. Never invent tables or columns.
17. Never modify database data.
18. Return ONLY SQL.
19. Do NOT use markdown code fences.
20. The database is MySQL.
21. Use the structured query intent as additional guidance.
22. If the structured intent identifies a relative time period such
    as today, yesterday, this_month, or last_month, translate it
    into the appropriate MySQL date condition.
23. Do not hardcode today's date. Use MySQL date functions such as
    CURDATE(), CURRENT_DATE, DATE_SUB(), YEAR(), MONTH(), etc.
24. The final SQL must answer the user's original question.

DATABASE SCHEMA:

{schema_text}

STRUCTURED QUERY INTENT:

{intent_text}

USER QUESTION:

{question}

Return only the SQL query.
"""

    interaction = client.interactions.create(
        model=MODEL,
        input=prompt
    )

    sql = interaction.output_text.strip()

    if sql.startswith("```sql"):
        sql = sql[6:]

    elif sql.startswith("```"):
        sql = sql[3:]

    if sql.endswith("```"):
        sql = sql[:-3]

    return sql.strip()