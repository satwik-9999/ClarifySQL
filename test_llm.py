from database import get_database_schema
from llm_service import generate_sql_with_llm


schema = get_database_schema()


question = "Which customers are from Hyderabad?"


sql = generate_sql_with_llm(
    question,
    schema
)


print("\nGenerated SQL:")
print(sql)