import requests
import streamlit as st
import plotly.express as px


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ClarifySQL",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #f8fafc;
    }

    /* Main content width */
    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    /* Main title */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    /* Section headings */
    h2, h3 {
        font-weight: 750 !important;
    }

    /* Text input */
    div[data-testid="stTextInput"] input {
        border-radius: 12px;
        border: 1px solid #d1d5db;
        padding: 14px;
        font-size: 16px;
        background-color: white;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15);
    }

    /* Primary button */
    div.stButton > button[kind="primary"] {
        border-radius: 12px;
        font-weight: 700;
        min-height: 48px;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        border: none;
    }

    /* Regular buttons */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    /* Cards */
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 12px;
    }

    /* Code blocks */
    pre {
        border-radius: 12px !important;
    }

    /* Divider */
    hr {
        border-color: #e5e7eb;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = "demo_session"

if "question" not in st.session_state:
    st.session_state.question = ""

if "pending_clarification" not in st.session_state:
    st.session_state.pending_clarification = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ============================================================
# DEMO DATA
# ============================================================

DEMO_RESPONSES = {

    # ========================================================
    # CUSTOMERS
    # ========================================================

    "show me all customers from hyderabad": {

        "question": "Show me all customers from Hyderabad",

        "sql": """SELECT customer_id, customer_name, email, phone, city
FROM customers
WHERE city = 'Hyderabad';""",

        "results": [
            {
                "customer_id": 1,
                "customer_name": "Rahul Sharma",
                "email": "rahul@example.com",
                "phone": "9876543210",
                "city": "Hyderabad"
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "filter",
            "operation": "customers_by_city",
            "table": "customers",
            "column": "city",
            "value": "Hyderabad"
        }
    },

    "show me all customers": {

        "question": "Show me all customers",

        "sql": """SELECT customer_id, customer_name, email, phone, city
FROM customers;""",

        "results": [
            {
                "customer_id": 1,
                "customer_name": "Rahul Sharma",
                "email": "rahul@example.com",
                "phone": "9876543210",
                "city": "Hyderabad"
            },
            {
                "customer_id": 2,
                "customer_name": "Priya Reddy",
                "email": "priya@example.com",
                "phone": "9876543211",
                "city": "Bangalore"
            },
            {
                "customer_id": 3,
                "customer_name": "Arjun Kumar",
                "email": "arjun@example.com",
                "phone": "9876543212",
                "city": "Chennai"
            },
            {
                "customer_id": 4,
                "customer_name": "Sneha Patel",
                "email": "sneha@example.com",
                "phone": "9876543213",
                "city": "Mumbai"
            },
            {
                "customer_id": 5,
                "customer_name": "Vikram Singh",
                "email": "vikram@example.com",
                "phone": "9876543214",
                "city": "Delhi"
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "list",
            "operation": "list_customers",
            "table": "customers"
        }
    },

    "show me each customer's total spending": {

        "question": "Show me each customer's total spending",

        "sql": """SELECT c.customer_name,
       SUM(o.total_amount) AS total_spending
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spending DESC;""",

        "results": [
            {
                "customer_name": "Rahul Sharma",
                "total_spending": 65000
            },
            {
                "customer_name": "Priya Reddy",
                "total_spending": 32000
            },
            {
                "customer_name": "Sneha Patel",
                "total_spending": 18000
            },
            {
                "customer_name": "Arjun Kumar",
                "total_spending": 5000
            },
            {
                "customer_name": "Vikram Singh",
                "total_spending": 2800
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "aggregation",
            "operation": "customer_total_spending",
            "group_by": "customer",
            "table": "orders",
            "calculation": "SUM(total_amount)",
            "alias": "total_spending"
        }
    },

    "show me customer names and their order amounts": {

        "question": "Show me customer names and their order amounts",

        "sql": """SELECT c.customer_name,
       o.total_amount
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id;""",

        "results": [
            {
                "customer_name": "Rahul Sharma",
                "total_amount": 65000
            },
            {
                "customer_name": "Priya Reddy",
                "total_amount": 32000
            },
            {
                "customer_name": "Arjun Kumar",
                "total_amount": 5000
            },
            {
                "customer_name": "Sneha Patel",
                "total_amount": 18000
            },
            {
                "customer_name": "Vikram Singh",
                "total_amount": 2800
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "join",
            "operation": "customer_order_amounts",
            "tables": [
                "customers",
                "orders"
            ],
            "columns": [
                "customer_name",
                "total_amount"
            ]
        }
    },


    # ========================================================
    # PRODUCTS
    # ========================================================

    "show me all products": {

        "question": "Show me all products",

        "sql": """SELECT product_id, product_name, category,
       price, stock_quantity
FROM products;""",

        "results": [
            {
                "product_id": 1,
                "product_name": "Laptop",
                "category": "Electronics",
                "price": 65000,
                "stock_quantity": 20
            },
            {
                "product_id": 2,
                "product_name": "Smartphone",
                "category": "Electronics",
                "price": 30000,
                "stock_quantity": 50
            },
            {
                "product_id": 3,
                "product_name": "Headphones",
                "category": "Accessories",
                "price": 2000,
                "stock_quantity": 100
            },
            {
                "product_id": 4,
                "product_name": "Keyboard",
                "category": "Accessories",
                "price": 1500,
                "stock_quantity": 75
            },
            {
                "product_id": 5,
                "product_name": "Mouse",
                "category": "Accessories",
                "price": 800,
                "stock_quantity": 120
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "list",
            "operation": "list_products",
            "table": "products"
        }
    },

    "show me products above 10000": {

        "question": "Show me products above 10000",

        "sql": """SELECT product_id, product_name, category,
       price, stock_quantity
FROM products
WHERE price > 10000;""",

        "results": [
            {
                "product_id": 1,
                "product_name": "Laptop",
                "category": "Electronics",
                "price": 65000,
                "stock_quantity": 20
            },
            {
                "product_id": 2,
                "product_name": "Smartphone",
                "category": "Electronics",
                "price": 30000,
                "stock_quantity": 50
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "filter",
            "operation": "products_above_price",
            "table": "products",
            "column": "price",
            "operator": ">",
            "value": 10000
        }
    },

    "which product generated the most revenue?": {

        "question": "Which product generated the most revenue?",

        "sql": """SELECT p.product_name,
       SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_revenue DESC
LIMIT 1;""",

        "results": [
            {
                "product_name": "Laptop",
                "total_revenue": 65000
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "ranking",
            "operation": "highest_product_revenue",
            "group_by": "product",
            "table": "order_items",
            "calculation": "quantity * unit_price",
            "alias": "total_revenue"
        }
    },

    "show me the products purchased by each customer": {

        "question": "Show me the products purchased by each customer",

        "sql": """SELECT c.customer_name,
       p.product_name
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
ORDER BY c.customer_name;""",

        "results": [
            {
                "customer_name": "Arjun Kumar",
                "product_name": "Headphones"
            },
            {
                "customer_name": "Priya Reddy",
                "product_name": "Laptop"
            },
            {
                "customer_name": "Rahul Sharma",
                "product_name": "Laptop"
            },
            {
                "customer_name": "Sneha Patel",
                "product_name": "Smartphone"
            },
            {
                "customer_name": "Vikram Singh",
                "product_name": "Keyboard"
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "multi_table_join",
            "operation": "customer_purchased_products",
            "tables": [
                "customers",
                "orders",
                "order_items",
                "products"
            ]
        }
    },


    # ========================================================
    # ORDERS
    # ========================================================

    "show me all orders": {

        "question": "Show me all orders",

        "sql": """SELECT order_id, customer_id, order_date,
       total_amount, order_status
FROM orders;""",

        "results": [
            {
                "order_id": 1,
                "customer_id": 1,
                "order_date": "2026-09-04 00:00:00",
                "total_amount": 65000,
                "order_status": "Completed"
            },
            {
                "order_id": 2,
                "customer_id": 2,
                "order_date": "2026-09-04 00:00:00",
                "total_amount": 32000,
                "order_status": "Pending"
            },
            {
                "order_id": 3,
                "customer_id": 3,
                "order_date": "2026-09-04 00:00:00",
                "total_amount": 5000,
                "order_status": "Processing"
            },
            {
                "order_id": 4,
                "customer_id": 4,
                "order_date": "2026-09-04 00:00:00",
                "total_amount": 18000,
                "order_status": "Completed"
            },
            {
                "order_id": 5,
                "customer_id": 5,
                "order_date": "2026-09-04 00:00:00",
                "total_amount": 2800,
                "order_status": "Pending"
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "list",
            "operation": "list_orders",
            "table": "orders"
        }
    },

    "show me all pending orders": {

        "question": "Show me all pending orders",

        "sql": """SELECT order_id, customer_id, order_date,
       total_amount, order_status
FROM orders
WHERE order_status = 'Pending';""",

        "results": [
            {
                "order_id": 2,
                "customer_id": 2,
                "order_date": "2026-09-04 00:00:00",
                "total_amount": 32000,
                "order_status": "Pending"
            },
            {
                "order_id": 5,
                "customer_id": 5,
                "order_date": "2026-09-04 00:00:00",
                "total_amount": 2800,
                "order_status": "Pending"
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "filter",
            "operation": "pending_orders",
            "table": "orders",
            "column": "order_status",
            "value": "Pending"
        }
    },

    "show me completed orders": {

        "question": "Show me completed orders",

        "sql": """SELECT order_id, customer_id, order_date,
       total_amount, order_status
FROM orders
WHERE order_status = 'Completed';""",

        "results": [
            {
                "order_id": 1,
                "customer_id": 1,
                "order_date": "2026-09-04 00:00:00",
                "total_amount": 65000,
                "order_status": "Completed"
            },
            {
                "order_id": 4,
                "customer_id": 4,
                "order_date": "2026-09-04 00:00:00",
                "total_amount": 18000,
                "order_status": "Completed"
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "filter",
            "operation": "completed_orders",
            "table": "orders",
            "column": "order_status",
            "value": "Completed"
        }
    },

    "show me processing orders": {

        "question": "Show me processing orders",

        "sql": """SELECT order_id, customer_id, order_date,
       total_amount, order_status
FROM orders
WHERE order_status = 'Processing';""",

        "results": [
            {
                "order_id": 3,
                "customer_id": 3,
                "order_date": "2026-09-04 00:00:00",
                "total_amount": 5000,
                "order_status": "Processing"
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "filter",
            "operation": "processing_orders",
            "table": "orders",
            "column": "order_status",
            "value": "Processing"
        }
    },


    # ========================================================
    # REVENUE
    # ========================================================

    "what is the total revenue?": {

        "question": "What is the total revenue?",

        "sql": """SELECT SUM(total_amount) AS total_revenue
FROM orders;""",

        "results": [
            {
                "total_revenue": 122800
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "aggregation",
            "operation": "total_revenue",
            "table": "orders",
            "calculation": "SUM(total_amount)",
            "alias": "total_revenue"
        }
    },

    "show me the highest spending customer": {

        "question": "Show me the highest spending customer",

        "sql": """SELECT c.customer_name,
       SUM(o.total_amount) AS total_spending
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spending DESC
LIMIT 1;""",

        "results": [
            {
                "customer_name": "Rahul Sharma",
                "total_spending": 65000
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "ranking",
            "operation": "highest_spending_customer",
            "group_by": "customer",
            "calculation": "SUM(total_amount)",
            "alias": "total_spending"
        }
    },


    # ========================================================
    # PAYMENTS
    # ========================================================

    "show me all payments": {

        "question": "Show me all payments",

        "sql": """SELECT payment_id, order_id, payment_date,
       payment_method, payment_status, amount
FROM payments;""",

        "results": [
            {
                "payment_id": 1,
                "order_id": 1,
                "payment_date": "2026-09-04 00:00:00",
                "payment_method": "UPI",
                "payment_status": "Completed",
                "amount": 65000
            },
            {
                "payment_id": 2,
                "order_id": 2,
                "payment_date": "2026-09-04 00:00:00",
                "payment_method": "Credit Card",
                "payment_status": "Completed",
                "amount": 32000
            },
            {
                "payment_id": 3,
                "order_id": 3,
                "payment_date": "2026-09-04 00:00:00",
                "payment_method": "Debit Card",
                "payment_status": "Completed",
                "amount": 5000
            },
            {
                "payment_id": 4,
                "order_id": 4,
                "payment_date": "2026-09-04 00:00:00",
                "payment_method": "UPI",
                "payment_status": "Completed",
                "amount": 18000
            },
            {
                "payment_id": 5,
                "order_id": 5,
                "payment_date": "2026-09-04 00:00:00",
                "payment_method": "Credit Card",
                "payment_status": "Pending",
                "amount": 2800
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "list",
            "operation": "list_payments",
            "table": "payments"
        }
    },

    "show me completed payments": {

        "question": "Show me completed payments",

        "sql": """SELECT payment_id, order_id, payment_date,
       payment_method, payment_status, amount
FROM payments
WHERE payment_status = 'Completed';""",

        "results": [
            {
                "payment_id": 1,
                "order_id": 1,
                "payment_date": "2026-09-04 00:00:00",
                "payment_method": "UPI",
                "payment_status": "Completed",
                "amount": 65000
            },
            {
                "payment_id": 2,
                "order_id": 2,
                "payment_date": "2026-09-04 00:00:00",
                "payment_method": "Credit Card",
                "payment_status": "Completed",
                "amount": 32000
            },
            {
                "payment_id": 3,
                "order_id": 3,
                "payment_date": "2026-09-04 00:00:00",
                "payment_method": "Debit Card",
                "payment_status": "Completed",
                "amount": 5000
            },
            {
                "payment_id": 4,
                "order_id": 4,
                "payment_date": "2026-09-04 00:00:00",
                "payment_method": "UPI",
                "payment_status": "Completed",
                "amount": 18000
            }
        ],

        "query_intent": {
            "success": True,
            "intent": "filter",
            "operation": "completed_payments",
            "table": "payments",
            "column": "payment_status",
            "value": "Completed"
        }
    }
}


# ============================================================
# DEMO RESULT ANALYSIS
# ============================================================

def create_demo_analysis(results):

    if not results:

        return {
            "result_type": "empty",
            "row_count": 0,
            "columns": [],
            "numeric_columns": [],
            "text_columns": [],
            "visualization": {
                "recommended": False,
                "chart_type": None,
                "x_axis": None,
                "y_axis": None
            }
        }

    columns = list(results[0].keys())

    numeric_columns = []
    text_columns = []

    for column in columns:

        values = [
            row.get(column)
            for row in results
            if row.get(column) is not None
        ]

        if values and all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            for value in values
        ):

            numeric_columns.append(column)

        else:

            text_columns.append(column)

    metric_keywords = [
        "amount",
        "revenue",
        "sales",
        "spending",
        "price",
        "quantity",
        "count",
        "total",
        "average",
        "avg",
        "sum"
    ]

    metric_columns = [
        column
        for column in numeric_columns
        if any(
            keyword in column.lower()
            for keyword in metric_keywords
        )
    ]

    if metric_columns:

        y_axis = metric_columns[0]

    elif numeric_columns:

        y_axis = numeric_columns[0]

    else:

        y_axis = None

    preferred_text_columns = [
        column
        for column in text_columns
        if any(
            keyword in column.lower()
            for keyword in [
                "name",
                "category",
                "city",
                "status",
                "method"
            ]
        )
    ]

    if preferred_text_columns:

        x_axis = preferred_text_columns[0]

    elif text_columns:

        x_axis = text_columns[0]

    else:

        x_axis = None

    recommended = (
        len(results) > 1
        and x_axis is not None
        and y_axis is not None
    )

    return {
        "result_type": "table",
        "row_count": len(results),
        "columns": columns,
        "numeric_columns": numeric_columns,
        "text_columns": text_columns,
        "visualization": {
            "recommended": recommended,
            "chart_type": "bar" if recommended else None,
            "x_axis": x_axis if recommended else None,
            "y_axis": y_axis if recommended else None
        }
    }


# ============================================================
# DEMO RESPONSE
# ============================================================

def make_demo_response(question):

    normalized = question.lower().strip()

    if normalized == "who is the best customer?":

        return {
            "success": True,
            "status": "clarification_needed",
            "question": question,
            "clarification": (
                "How should 'best customer' be measured?"
            ),
            "options": [
                {
                    "id": "total_spending",
                    "label": "Total spending"
                },
                {
                    "id": "order_count",
                    "label": "Number of orders"
                }
            ]
        }

    if normalized in DEMO_RESPONSES:

        data = DEMO_RESPONSES[normalized]

        results = data["results"]

        return {
            "success": True,
            "status": "query_executed",
            "question": data["question"],
            "session_id": st.session_state.session_id,
            "query_intent": data["query_intent"],
            "conversation_context": None,
            "sql": data["sql"],
            "safety": "SQL passed security validation.",
            "schema_validation": {
                "tables": "All referenced tables exist.",
                "columns": "All referenced columns exist."
            },
            "result_analysis": create_demo_analysis(
                results
            ),
            "visualization": {
                "available": False,
                "figure": None
            },
            "history_saved": True,
            "results": results
        }

    return {
        "success": False,
        "status": "demo_question_not_available",
        "message": (
            "This question is not included in Demo Mode. "
            "Switch to Live AI Mode when Gemini is available."
        )
    }


# ============================================================
# LIVE API REQUEST
# ============================================================

def send_live_query(question):

    response = requests.post(
        f"{API_URL}/query",
        json={
            "question": question,
            "session_id": st.session_state.session_id
        },
        timeout=120
    )

    return response.json()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🧠 ClarifySQL")

    st.caption(
        "Natural Language Data Assistant"
    )

    st.divider()

    st.subheader("⚙️ Workspace")

    mode = st.radio(
        "Execution Mode",
        [
            "Demo Mode",
            "Live AI Mode"
        ],
        label_visibility="collapsed"
    )

    if mode == "Demo Mode":

        st.success(
            "● Demo Mode"
        )

        st.caption(
            "Works without Gemini API calls."
        )

    else:

        st.info(
            "● Live AI Mode"
        )

        st.caption(
            "Uses the real FastAPI + Gemini pipeline."
        )

    st.divider()

    st.subheader("💡 Try asking")

    examples = [
        "Show me each customer's total spending",
        "Which product generated the most revenue?",
        "What is the total revenue?",
        "Show me all customers",
        "Show me all products",
        "Show me products above 10000",
        "Show me all orders",
        "Show me all pending orders",
        "Show me completed orders",
        "Show me processing orders",
        "Show me all payments",
        "Show me completed payments",
        "Show me customer names and their order amounts",
        "Show me the products purchased by each customer",
        "Show me all customers from Hyderabad",
        "Show me the highest spending customer",
        "Who is the best customer?"
    ]

    for example in examples:

        if st.button(
            example,
            key=f"example_{example}",
            use_container_width=True
        ):

            st.session_state.question = example
            st.rerun()

    st.divider()

    st.caption("Session")

    st.code(
        st.session_state.session_id
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.title("Ask your data anything.")

st.markdown(
    """
    Turn natural language questions into
    **secure SQL, database results, and insights.**
    """
)

st.divider()


# ============================================================
# QUESTION INPUT
# ============================================================

st.subheader(
    "💬 What would you like to know?"
)

question = st.text_input(
    "Question",
    value=st.session_state.question,
    placeholder=(
        "e.g. Which product generated the most revenue?"
    ),
    label_visibility="collapsed"
)

ask_clicked = st.button(
    "🚀 Ask ClarifySQL",
    type="primary",
    use_container_width=True
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if ask_clicked:

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        st.session_state.question = question

        with st.spinner(
            "ClarifySQL is understanding your question..."
        ):

            try:

                if mode == "Demo Mode":

                    response_data = make_demo_response(
                        question
                    )

                else:

                    response_data = send_live_query(
                        question
                    )

                st.session_state.last_result = (
                    response_data
                )

                if response_data.get(
                    "status"
                ) == "clarification_needed":

                    st.session_state.pending_clarification = (
                        response_data
                    )

                else:

                    st.session_state.pending_clarification = None

            except requests.exceptions.ConnectionError:

                st.error(
                    "Unable to connect to the ClarifySQL backend."
                )

                st.info(
                    "Make sure FastAPI is running with "
                    "`python -m uvicorn main:app --reload`."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out."
                )

            except Exception as e:

                st.error(
                    f"Unexpected error: {str(e)}"
                )


# ============================================================
# CLARIFICATION
# ============================================================

pending = st.session_state.pending_clarification

if pending:

    st.divider()

    st.subheader(
        "🤔 Clarification needed"
    )

    st.info(
        pending.get(
            "clarification",
            "Please provide more information."
        )
    )

    options = pending.get(
        "options",
        []
    )

    option_columns = st.columns(
        len(options)
        if options
        else 1
    )

    for index, option in enumerate(options):

        label = option.get(
            "label",
            "Option"
        )

        option_id = option.get(
            "id",
            label
        )

        with option_columns[index]:

            if st.button(
                f"✓ {label}",
                key=f"clarification_{option_id}",
                use_container_width=True
            ):

                with st.spinner(
                    "Finding your answer..."
                ):

                    try:

                        if mode == "Demo Mode":

                            if option_id == "total_spending":

                                response_data = {
                                    "success": True,
                                    "status": "query_executed",
                                    "question": (
                                        "Who is the best customer? "
                                        "Measure it using Total spending."
                                    ),
                                    "session_id": (
                                        st.session_state.session_id
                                    ),
                                    "query_intent": {
                                        "success": True,
                                        "intent": "ranking",
                                        "operation": (
                                            "highest_spending_customer"
                                        ),
                                        "group_by": "customer",
                                        "calculation": (
                                            "SUM(total_amount)"
                                        ),
                                        "alias": "total_spending"
                                    },
                                    "conversation_context": {
                                        "clarification_id": (
                                            "customer_metric"
                                        ),
                                        "selected_option": option
                                    },
                                    "sql": """SELECT c.customer_name,
       SUM(o.total_amount) AS total_spending
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spending DESC
LIMIT 1;""",
                                    "safety": (
                                        "SQL passed security validation."
                                    ),
                                    "schema_validation": {
                                        "tables": (
                                            "All referenced tables exist."
                                        ),
                                        "columns": (
                                            "All referenced columns exist."
                                        )
                                    },
                                    "results": [
                                        {
                                            "customer_name": (
                                                "Rahul Sharma"
                                            ),
                                            "total_spending": 65000
                                        }
                                    ],
                                    "result_analysis": {
                                        "result_type": "single_row",
                                        "row_count": 1,
                                        "columns": [
                                            "customer_name",
                                            "total_spending"
                                        ],
                                        "numeric_columns": [
                                            "total_spending"
                                        ],
                                        "text_columns": [
                                            "customer_name"
                                        ],
                                        "visualization": {
                                            "recommended": False,
                                            "chart_type": None,
                                            "x_axis": None,
                                            "y_axis": None
                                        }
                                    },
                                    "visualization": {
                                        "available": False,
                                        "figure": None
                                    },
                                    "history_saved": True
                                }

                            else:

                                response_data = {
                                    "success": True,
                                    "status": "query_executed",
                                    "question": (
                                        "Who is the best customer? "
                                        "Measure it using Number of orders."
                                    ),
                                    "session_id": (
                                        st.session_state.session_id
                                    ),
                                    "query_intent": {
                                        "success": True,
                                        "intent": "ranking",
                                        "operation": (
                                            "highest_order_count_customer"
                                        ),
                                        "group_by": "customer",
                                        "calculation": (
                                            "COUNT(order_id)"
                                        ),
                                        "alias": "order_count"
                                    },
                                    "conversation_context": {
                                        "clarification_id": (
                                            "customer_metric"
                                        ),
                                        "selected_option": option
                                    },
                                    "sql": """SELECT c.customer_name,
       COUNT(o.order_id) AS order_count
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY order_count DESC
LIMIT 1;""",
                                    "safety": (
                                        "SQL passed security validation."
                                    ),
                                    "schema_validation": {
                                        "tables": (
                                            "All referenced tables exist."
                                        ),
                                        "columns": (
                                            "All referenced columns exist."
                                        )
                                    },
                                    "results": [
                                        {
                                            "customer_name": (
                                                "Rahul Sharma"
                                            ),
                                            "order_count": 1
                                        }
                                    ],
                                    "result_analysis": {
                                        "result_type": "single_row",
                                        "row_count": 1,
                                        "columns": [
                                            "customer_name",
                                            "order_count"
                                        ],
                                        "numeric_columns": [
                                            "order_count"
                                        ],
                                        "text_columns": [
                                            "customer_name"
                                        ],
                                        "visualization": {
                                            "recommended": False,
                                            "chart_type": None,
                                            "x_axis": None,
                                            "y_axis": None
                                        }
                                    },
                                    "visualization": {
                                        "available": False,
                                        "figure": None
                                    },
                                    "history_saved": True
                                }

                        else:

                            response_data = send_live_query(
                                label
                            )

                        st.session_state.last_result = (
                            response_data
                        )

                        st.session_state.pending_clarification = None

                        st.rerun()

                    except requests.exceptions.ConnectionError:

                        st.error(
                            "Unable to connect to the backend."
                        )

                    except requests.exceptions.Timeout:

                        st.error(
                            "The request timed out."
                        )

                    except Exception as e:

                        st.error(
                            f"Unexpected error: {str(e)}"
                        )


# ============================================================
# DISPLAY RESULTS
# ============================================================

result = st.session_state.last_result

if result:

    status = result.get(
        "status"
    )

    success = result.get(
        "success",
        False
    )

    # ========================================================
    # SUCCESSFUL QUERY
    # ========================================================

    if status == "query_executed" and success:

        st.divider()

        st.success(
            "Query completed successfully."
        )

        final_question = result.get(
            "question"
        )

        if final_question:

            st.subheader(
                f"💬 {final_question}"
            )

        results = result.get(
            "results",
            []
        )

        analysis = result.get(
            "result_analysis",
            {}
        )

        columns = analysis.get(
            "columns",
            []
        )

        result_type = analysis.get(
            "result_type",
            "table"
        )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        metric_columns = st.columns(3)

        with metric_columns[0]:

            st.metric(
                "Result Rows",
                len(results)
            )

        with metric_columns[1]:

            st.metric(
                "Columns",
                len(columns)
            )

        with metric_columns[2]:

            st.metric(
                "Result Type",
                result_type.replace(
                    "_",
                    " "
                ).title()
            )

        # ----------------------------------------------------
        # RESULTS
        # ----------------------------------------------------

        st.subheader(
            "📊 Results"
        )

        if results:

            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "The query executed successfully, "
                "but no records were found."
            )

        # ----------------------------------------------------
        # VISUALIZATION
        # ----------------------------------------------------

        visualization = result.get(
            "visualization",
            {}
        )

        if visualization.get(
            "available"
        ):

            figure = visualization.get(
                "figure"
            )

            if figure:

                st.subheader(
                    "📈 Visualization"
                )

                st.plotly_chart(
                    figure,
                    use_container_width=True,
                    config={
                        "displayModeBar": False
                    }
                )

        elif mode == "Demo Mode":

            visualization_info = analysis.get(
                "visualization",
                {}
            )

            if (
                visualization_info.get(
                    "recommended"
                )
                and results
            ):

                x_axis = visualization_info.get(
                    "x_axis"
                )

                y_axis = visualization_info.get(
                    "y_axis"
                )

                if x_axis and y_axis:

                    st.subheader(
                        "📈 Visualization"
                    )

                    figure = px.bar(
                        results,
                        x=x_axis,
                        y=y_axis,
                        title=(
                            f"{y_axis.replace('_', ' ').title()} by "
                            f"{x_axis.replace('_', ' ').title()}"
                        )
                    )

                    figure.update_layout(
                        plot_bgcolor="white",
                        paper_bgcolor="white",
                        margin={
                            "l": 20,
                            "r": 20,
                            "t": 60,
                            "b": 20
                        }
                    )

                    st.plotly_chart(
                        figure,
                        use_container_width=True,
                        config={
                            "displayModeBar": False
                        }
                    )

        # ----------------------------------------------------
        # GENERATED SQL
        # ----------------------------------------------------

        sql = result.get(
            "sql"
        )

        if sql:

            with st.expander(
                "🧠 View Generated SQL"
            ):

                st.code(
                    sql,
                    language="sql"
                )

        # ----------------------------------------------------
        # TECHNICAL DETAILS
        # ----------------------------------------------------

        with st.expander(
            "🔍 View Technical Details"
        ):

            query_intent = result.get(
                "query_intent"
            )

            if query_intent:

                st.write(
                    "Query Understanding"
                )

                st.json(
                    query_intent
                )

            if analysis:

                st.write(
                    "Result Analysis"
                )

                st.json(
                    analysis
                )

        # ----------------------------------------------------
        # HISTORY
        # ----------------------------------------------------

        if result.get(
            "history_saved"
        ):

            st.caption(
                "✓ Query saved to history"
            )

    # ========================================================
    # ERROR
    # ========================================================

    elif not success:

        st.divider()

        error_status = result.get(
            "status"
        )

        if error_status == "llm_generation_failed":

            st.error(
                "⚠️ AI service temporarily unavailable."
            )

            st.info(
                "Gemini has reached its current API quota. "
                "Switch to Demo Mode to continue using ClarifySQL."
            )

        elif error_status == "demo_question_not_available":

            st.warning(
                result.get(
                    "message",
                    "This question is not available in Demo Mode."
                )
            )

        else:

            st.error(
                result.get(
                    "message",
                    "Something went wrong."
                )
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ClarifySQL • Natural Language Data Intelligence"
)