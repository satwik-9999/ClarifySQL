# ClarifySQL

ClarifySQL turns natural language questions into schema-aware SQL queries and interactive results. It combines a Streamlit interface with a FastAPI backend, database schema discovery, clarification prompts, SQL validation, query history, and result visualizations.

## Features

- Natural language to SQL with schema context
- Clarification when a request is ambiguous
- SQL validation before query execution
- MySQL database integration
- Query history and session-based context
- Result analysis and visualizations
- Demo mode

## Architecture

```text
User → Streamlit UI → FastAPI → Query understanding → Clarification
     → SQL generation and validation → MySQL → Results and visualization
```

## Requirements

- Python 3.10 or newer
- MySQL
- A Gemini API key

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and set `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, and `GEMINI_API_KEY`. Keep the populated `.env` file private.
4. Start the API and interface in separate terminals:

   ```bash
   uvicorn main:app --reload
   streamlit run app.py
   ```

The API runs at `http://localhost:8000`. Interactive API documentation is available at `http://localhost:8000/docs`.
