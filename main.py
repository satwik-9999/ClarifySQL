from fastapi import FastAPI
from pydantic import BaseModel

from database import get_database_schema, execute_query
from clarification import check_clarification

from conversation_manager import conversation_manager

from query_understanding import understand_query

from sql_generator import (
    validate_user_request,
    validate_sql,
    validate_schema_tables,
    validate_schema_columns
)

from llm_service import generate_sql_with_llm

from result_analyzer import analyze_results

from visualization import (
    create_visualization,
    serialize_visualization
)

from query_history import query_history


app = FastAPI(
    title="ClarifySQL API",
    description="Enterprise Natural Language Data Assistant",
    version="1.0.0"
)


class QueryRequest(BaseModel):

    question: str

    session_id: str = "default"


@app.get("/")
def home():

    return {
        "message": "Welcome to ClarifySQL API",
        "status": "running"
    }


@app.get("/schema")
def get_schema():

    schema = get_database_schema()

    if schema is None:

        return {
            "success": False,
            "message": "Could not retrieve database schema."
        }

    return {
        "success": True,
        "schema": schema
    }


@app.get("/history")
def get_query_history(
    session_id: str = None
):

    history = query_history.get_history(
        session_id
    )

    return {
        "success": True,
        "count": len(history),
        "history": history
    }


@app.delete("/history")
def clear_query_history(
    session_id: str = None
):

    success = query_history.clear_history(
        session_id
    )

    if not success:

        return {
            "success": False,
            "message": "Could not clear query history."
        }

    return {
        "success": True,
        "message": "Query history cleared."
    }


@app.get("/conversation")
def get_conversation_context(
    session_id: str = "default"
):

    context = conversation_manager.get_context(
        session_id
    )

    return {
        "success": True,
        "session_id": session_id,
        "context": context
    }


@app.delete("/conversation")
def clear_conversation_context(
    session_id: str = "default"
):

    conversation_manager.clear_context(
        session_id
    )

    return {
        "success": True,
        "message": "Conversation context cleared.",
        "session_id": session_id
    }


@app.post("/query")
def process_query(request: QueryRequest):

    question = request.question

    session_id = request.session_id

    # ============================================================
    # STEP 1: USER REQUEST SAFETY CHECK
    # ============================================================

    request_safety = validate_user_request(
        question
    )

    if not request_safety["allowed"]:

        return {
            "success": False,
            "status": "request_not_allowed",
            "question": question,
            "message": request_safety["message"]
        }

    # ============================================================
    # STEP 2: CHECK FOR PENDING CONVERSATION
    # ============================================================

    clarification_resolved = False

    if conversation_manager.has_pending_clarification(
        session_id
    ):

        resolution = conversation_manager.resolve_clarification(
            session_id,
            question
        )

        if resolution["resolved"]:

            question = resolution["question"]

            clarification_resolved = True

        else:

            return {
                "success": True,
                "status": "clarification_needed",
                "question": question,
                "clarification": resolution["message"],
                "options": resolution["options"]
            }

    # ============================================================
    # STEP 3: CHECK NEW QUESTION FOR CLARIFICATION
    # ============================================================

    if not clarification_resolved:

        clarification_result = check_clarification(
            question
        )

        if clarification_result["needs_clarification"]:

            conversation_manager.store_clarification(
                session_id=session_id,
                original_question=question,
                clarification_id=clarification_result[
                    "clarification_id"
                ],
                clarification=clarification_result[
                    "message"
                ],
                options=clarification_result[
                    "options"
                ]
            )

            return {
                "success": True,
                "status": "clarification_needed",
                "question": question,
                "clarification": clarification_result[
                    "message"
                ],
                "options": clarification_result[
                    "options"
                ]
            }

    # ============================================================
    # STEP 4: GET CONVERSATION CONTEXT
    # ============================================================

    conversation_context = (
        conversation_manager.get_context(
            session_id
        )
    )

    # ============================================================
    # STEP 5: QUERY UNDERSTANDING
    # ============================================================

    query_intent = understand_query(
        question
    )

    # ============================================================
    # STEP 6: GET DATABASE SCHEMA
    # ============================================================

    schema = get_database_schema()

    if schema is None:

        return {
            "success": False,
            "status": "schema_retrieval_failed",
            "question": question,
            "message": "Could not retrieve database schema."
        }

    # ============================================================
    # STEP 7: GENERATE SQL USING GEMINI
    # ============================================================

    try:

        sql = generate_sql_with_llm(
            question,
            schema,
            query_intent
        )

    except Exception as e:

        return {
            "success": False,
            "status": "llm_generation_failed",
            "question": question,
            "query_intent": query_intent,
            "conversation_context": conversation_context,
            "message": (
                f"LLM SQL generation failed: {str(e)}"
            )
        }

    if not sql:

        return {
            "success": False,
            "status": "sql_generation_failed",
            "question": question,
            "query_intent": query_intent,
            "conversation_context": conversation_context,
            "message": (
                "The LLM returned an empty SQL query."
            )
        }

    # ============================================================
    # STEP 8: SQL SECURITY VALIDATION
    # ============================================================

    safety_result = validate_sql(
        sql
    )

    if not safety_result["safe"]:

        return {
            "success": False,
            "status": "unsafe_sql",
            "question": question,
            "query_intent": query_intent,
            "conversation_context": conversation_context,
            "sql": sql,
            "message": safety_result["message"]
        }

    # ============================================================
    # STEP 9: TABLE SCHEMA VALIDATION
    # ============================================================

    table_validation = validate_schema_tables(
        sql,
        schema
    )

    if not table_validation["valid"]:

        return {
            "success": False,
            "status": "invalid_schema_reference",
            "question": question,
            "query_intent": query_intent,
            "conversation_context": conversation_context,
            "sql": sql,
            "message": table_validation["message"]
        }

    # ============================================================
    # STEP 10: COLUMN SCHEMA VALIDATION
    # ============================================================

    column_validation = validate_schema_columns(
        sql,
        schema
    )

    if not column_validation["valid"]:

        return {
            "success": False,
            "status": "invalid_schema_reference",
            "question": question,
            "query_intent": query_intent,
            "conversation_context": conversation_context,
            "sql": sql,
            "message": column_validation["message"]
        }

    # ============================================================
    # STEP 11: EXECUTE SQL
    # ============================================================

    results = execute_query(
        sql
    )

    if results is None:

        return {
            "success": False,
            "status": "query_execution_failed",
            "question": question,
            "query_intent": query_intent,
            "conversation_context": conversation_context,
            "sql": sql,
            "safety": safety_result["message"],
            "schema_validation": {
                "tables": table_validation["message"],
                "columns": column_validation["message"]
            },
            "message": (
                "SQL passed validation but "
                "could not be executed."
            )
        }

    # ============================================================
    # STEP 12: ANALYZE RESULTS
    # ============================================================

    result_analysis = analyze_results(
        results
    )

    # ============================================================
    # STEP 13: CREATE VISUALIZATION
    # ============================================================

    visualization_figure = create_visualization(
        results,
        result_analysis
    )

    visualization_data = serialize_visualization(
        visualization_figure
    )

    # ============================================================
    # STEP 14: SAVE QUERY HISTORY
    # ============================================================

    history_saved = query_history.add_query(
        session_id=session_id,
        question=question,
        sql=sql,
        query_intent=query_intent,
        results=results,
        result_analysis=result_analysis
    )

    # ============================================================
    # STEP 15: RETURN RESULTS
    # ============================================================

    return {
        "success": True,
        "status": "query_executed",
        "question": question,
        "session_id": session_id,
        "query_intent": query_intent,
        "conversation_context": conversation_context,
        "sql": sql,
        "safety": safety_result["message"],
        "schema_validation": {
            "tables": table_validation["message"],
            "columns": column_validation["message"]
        },
        "result_analysis": result_analysis,
        "visualization": {
            "available": visualization_data is not None,
            "figure": visualization_data
        },
        "history_saved": history_saved,
        "results": results
    }