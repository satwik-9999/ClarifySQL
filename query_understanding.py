import re


def understand_query(question):
    """
    Converts a natural-language question into structured intent.

    This is currently a rule-based query understanding layer.
    It will later be enhanced with an LLM-based understanding system.
    """

    if not question or not question.strip():

        return {
            "success": False,
            "message": "Question is empty.",
            "intent": None
        }

    original_question = question.strip()
    question_lower = original_question.lower().strip()

    # ============================================================
    # 1. CUSTOMER CITY FILTER
    # ============================================================

    customer_city_patterns = [

        r"(?:show|list|get|give\s+me)\s+"
        r"(?:all\s+)?(?:the\s+)?"
        r"(?!me\b)"
        r"([a-zA-Z]+)\s+customers?\b",

        r"(?:show|list|get|give\s+me)\s+"
        r"(?:all\s+)?customers?\s+"
        r"(?:from|in|located\s+in|living\s+in)\s+"
        r"([a-zA-Z]+)\b",

        r"(?:which|what)\s+customers?\s+"
        r"(?:are\s+)?"
        r"(?:from|in|located\s+in|living\s+in)\s+"
        r"([a-zA-Z]+)\b",

        r"customers?\s+"
        r"(?:from|in|located\s+in|living\s+in)\s+"
        r"([a-zA-Z]+)\b"
    ]

    for pattern in customer_city_patterns:

        city_match = re.search(
            pattern,
            question_lower
        )

        if city_match:

            city = city_match.group(1).strip()

            return {
                "success": True,
                "intent": "filter",
                "table": "customers",
                "column": "city",
                "operator": "=",
                "value": city.title(),
                "original_question": original_question
            }

    # ============================================================
    # 2. JOIN: CUSTOMER NAMES + ORDER AMOUNTS
    # ============================================================

    customer_order_patterns = [

        r"customer\s+names?.*order\s+amounts?",

        r"customer\s+names?.*order\s+total",

        r"customer.*order\s+amount",

        r"customers?.*orders?.*amount"
    ]

    for pattern in customer_order_patterns:

        if re.search(
            pattern,
            question_lower
        ):

            return {
                "success": True,
                "intent": "join",
                "tables": [
                    "customers",
                    "orders"
                ],
                "relationship": {
                    "left_table": "customers",
                    "left_column": "customer_id",
                    "right_table": "orders",
                    "right_column": "customer_id"
                },
                "columns": [
                    "customer_name",
                    "total_amount"
                ],
                "original_question": original_question
            }

    # ============================================================
    # 3. CUSTOMER TOTAL SPENDING
    # ============================================================

    customer_spending_patterns = [

        r"(?:show|list|get|give\s+me)\s+"
        r"(?:each|every)\s+customer'?s?\s+"
        r"(?:total\s+)?spending",

        r"(?:show|list|get|give\s+me)\s+"
        r"(?:the\s+)?total\s+spending\s+"
        r"(?:for|by|of)\s+(?:each|every)\s+customer",

        r"total\s+spending\s+(?:for|by|of)\s+(?:each|every)\s+customer",

        r"how\s+much\s+(?:has|have)\s+each\s+customer\s+spent",

        r"customer'?s?\s+total\s+spending"
    ]

    for pattern in customer_spending_patterns:

        if re.search(
            pattern,
            question_lower
        ):

            return {
                "success": True,
                "intent": "grouping",
                "operation": "sum",
                "group_by": "customer",
                "table": "orders",
                "column": "total_amount",
                "alias": "total_spending",
                "join": {
                    "table": "customers",
                    "left_column": "customer_id",
                    "right_column": "customer_id"
                },
                "original_question": original_question
            }

    # ============================================================
    # 4. PRODUCT WITH HIGHEST REVENUE
    # ============================================================

    product_revenue_patterns = [

        r"(?:which|what)\s+product\s+"
        r"(?:generated|made|brought|produced)\s+"
        r"(?:the\s+)?most\s+revenue",

        r"(?:which|what)\s+product\s+"
        r"(?:has|had|generated|made)\s+"
        r"(?:the\s+)?highest\s+(?:sales\s+)?revenue",

        r"(?:which|what)\s+product\s+"
        r"(?:generated|made)\s+"
        r"(?:the\s+)?highest\s+sales",

        r"(?:best|top)\s+product\s+"
        r"(?:by|in\s+terms\s+of)\s+revenue",

        r"product\s+with\s+(?:the\s+)?highest\s+revenue",

        r"highest\s+revenue\s+product"
    ]

    for pattern in product_revenue_patterns:

        if re.search(
            pattern,
            question_lower
        ):

            return {
                "success": True,
                "intent": "ranking",
                "operation": "highest_product_revenue",
                "group_by": "product",
                "table": "order_items",
                "calculation": "quantity * unit_price",
                "alias": "total_revenue",
                "join": {
                    "table": "products",
                    "left_column": "product_id",
                    "right_column": "product_id"
                },
                "original_question": original_question
            }

    # ============================================================
    # 5. PRODUCTS PURCHASED BY EACH CUSTOMER
    # ============================================================

    customer_product_patterns = [

        r"(?:show|list|get|give\s+me)\s+"
        r"(?:the\s+)?products?\s+"
        r"(?:purchased|bought|ordered)\s+"
        r"(?:by|from)\s+(?:each|every)\s+customer",

        r"(?:show|list|get|give\s+me)\s+"
        r"(?:each|every)\s+customer'?s?\s+"
        r"(?:purchased|bought|ordered)\s+products?",

        r"(?:what|which)\s+products?\s+"
        r"(?:did|has|have)\s+each\s+customer\s+"
        r"(?:purchase|purchased|buy|bought|order|ordered)",

        r"products?\s+(?:purchased|bought|ordered)\s+"
        r"by\s+each\s+customer"
    ]

    for pattern in customer_product_patterns:

        if re.search(
            pattern,
            question_lower
        ):

            return {
                "success": True,
                "intent": "multi_table_join",
                "operation": "customer_purchased_products",
                "tables": [
                    "customers",
                    "orders",
                    "order_items",
                    "products"
                ],
                "relationships": [
                    {
                        "left_table": "customers",
                        "left_column": "customer_id",
                        "right_table": "orders",
                        "right_column": "customer_id"
                    },
                    {
                        "left_table": "orders",
                        "left_column": "order_id",
                        "right_table": "order_items",
                        "right_column": "order_id"
                    },
                    {
                        "left_table": "order_items",
                        "left_column": "product_id",
                        "right_table": "products",
                        "right_column": "product_id"
                    }
                ],
                "columns": [
                    "customer_name",
                    "product_name"
                ],
                "original_question": original_question
            }

    # ============================================================
    # 6. SHOW ALL CUSTOMERS
    # ============================================================

    customer_patterns = [
        r"show\s+(?:all\s+)?customers?\b",
        r"list\s+(?:all\s+)?customers?\b",
        r"give\s+me\s+(?:all\s+)?customers?\b",
        r"get\s+(?:all\s+)?customers?\b",
        r"which\s+customers?\b"
    ]

    for pattern in customer_patterns:

        if re.search(
            pattern,
            question_lower
        ):

            return {
                "success": True,
                "intent": "list",
                "table": "customers",
                "original_question": original_question
            }

    # ============================================================
    # 7. PRODUCTS ABOVE / GREATER THAN PRICE
    # ============================================================

    price_match = re.search(
        r"(?:products?|items?).*?"
        r"(?:above|over|greater\s+than|more\s+than|higher\s+than)\s*"
        r"(?:₹|rs\.?|inr)?\s*"
        r"([0-9]+(?:\.[0-9]+)?)",
        question_lower
    )

    if price_match:

        price = price_match.group(1)

        return {
            "success": True,
            "intent": "filter",
            "table": "products",
            "column": "price",
            "operator": ">",
            "value": float(price),
            "original_question": original_question
        }

    # ============================================================
    # 8. PRODUCTS BELOW / LESS THAN PRICE
    # ============================================================

    price_match = re.search(
        r"(?:products?|items?).*?"
        r"(?:below|under|less\s+than|lower\s+than)\s*"
        r"(?:₹|rs\.?|inr)?\s*"
        r"([0-9]+(?:\.[0-9]+)?)",
        question_lower
    )

    if price_match:

        price = price_match.group(1)

        return {
            "success": True,
            "intent": "filter",
            "table": "products",
            "column": "price",
            "operator": "<",
            "value": float(price),
            "original_question": original_question
        }

    # ============================================================
    # 9. SHOW ALL PRODUCTS
    # ============================================================

    product_patterns = [
        r"show\s+(?:all\s+)?products?\b",
        r"list\s+(?:all\s+)?products?\b",
        r"give\s+me\s+(?:all\s+)?products?\b",
        r"get\s+(?:all\s+)?products?\b"
    ]

    for pattern in product_patterns:

        if re.search(
            pattern,
            question_lower
        ):

            return {
                "success": True,
                "intent": "list",
                "table": "products",
                "original_question": original_question
            }

    # ============================================================
    # 10. PENDING ORDERS
    # ============================================================

    if re.search(
        r"\bpending\s+orders?\b",
        question_lower
    ):

        return {
            "success": True,
            "intent": "filter",
            "table": "orders",
            "column": "order_status",
            "operator": "=",
            "value": "Pending",
            "original_question": original_question
        }

    # ============================================================
    # 11. COMPLETED ORDERS
    # ============================================================

    if re.search(
        r"\bcompleted\s+orders?\b",
        question_lower
    ):

        return {
            "success": True,
            "intent": "filter",
            "table": "orders",
            "column": "order_status",
            "operator": "=",
            "value": "Completed",
            "original_question": original_question
        }

    # ============================================================
    # 12. PROCESSING ORDERS
    # ============================================================

    if re.search(
        r"\bprocessing\s+orders?\b",
        question_lower
    ):

        return {
            "success": True,
            "intent": "filter",
            "table": "orders",
            "column": "order_status",
            "operator": "=",
            "value": "Processing",
            "original_question": original_question
        }

    # ============================================================
    # 13. SHOW ALL ORDERS
    # ============================================================

    order_patterns = [
        r"show\s+(?:all\s+)?orders?\b",
        r"list\s+(?:all\s+)?orders?\b",
        r"give\s+me\s+(?:all\s+)?orders?\b",
        r"get\s+(?:all\s+)?orders?\b"
    ]

    for pattern in order_patterns:

        if re.search(
            pattern,
            question_lower
        ):

            return {
                "success": True,
                "intent": "list",
                "table": "orders",
                "original_question": original_question
            }

    # ============================================================
    # 14. SHOW ALL PAYMENTS
    # ============================================================

    payment_patterns = [
        r"show\s+(?:all\s+)?payments?\b",
        r"list\s+(?:all\s+)?payments?\b",
        r"give\s+me\s+(?:all\s+)?payments?\b",
        r"get\s+(?:all\s+)?payments?\b"
    ]

    for pattern in payment_patterns:

        if re.search(
            pattern,
            question_lower
        ):

            return {
                "success": True,
                "intent": "list",
                "table": "payments",
                "original_question": original_question
            }

    # ============================================================
    # 15. REVENUE BY CUSTOMER / GROUPING
    # ============================================================

    revenue_customer_patterns = [

        r"revenue\s+(?:for|by|from)\s+(?:each\s+)?customer",

        r"total\s+revenue\s+(?:for|by|from)\s+(?:each\s+)?customer",

        r"sales\s+(?:for|by|from)\s+(?:each\s+)?customer",

        r"show\s+sales\s+by\s+customer",

        r"show\s+(?:the\s+)?revenue\s+by\s+customer",

        r"show\s+(?:the\s+)?total\s+revenue\s+by\s+customer"
    ]

    for pattern in revenue_customer_patterns:

        if re.search(
            pattern,
            question_lower
        ):

            return {
                "success": True,
                "intent": "grouping",
                "operation": "sum",
                "group_by": "customer",
                "table": "orders",
                "column": "total_amount",
                "alias": "total_revenue",
                "original_question": original_question
            }

    # ============================================================
    # 16. TODAY
    # ============================================================

    if re.search(
        r"\btoday\b",
        question_lower
    ):

        return {
            "success": True,
            "intent": "time_filter",
            "table": "orders",
            "date_column": "order_date",
            "time_period": "today",
            "original_question": original_question
        }

    # ============================================================
    # 17. YESTERDAY
    # ============================================================

    if re.search(
        r"\byesterday\b",
        question_lower
    ):

        return {
            "success": True,
            "intent": "time_filter",
            "table": "orders",
            "date_column": "order_date",
            "time_period": "yesterday",
            "original_question": original_question
        }

    # ============================================================
    # 18. THIS MONTH
    # ============================================================

    if re.search(
        r"\bthis\s+month\b",
        question_lower
    ):

        return {
            "success": True,
            "intent": "time_filter",
            "table": "orders",
            "date_column": "order_date",
            "time_period": "this_month",
            "original_question": original_question
        }

    # ============================================================
    # 19. LAST MONTH
    # ============================================================

    if re.search(
        r"\blast\s+month\b",
        question_lower
    ):

        return {
            "success": True,
            "intent": "time_filter",
            "table": "orders",
            "date_column": "order_date",
            "time_period": "last_month",
            "original_question": original_question
        }

    # ============================================================
    # 20. ORDERS BY MONTH + YEAR
    # ============================================================

    month_names = (
        "january|february|march|april|may|june|"
        "july|august|september|october|november|december"
    )

    month_year_match = re.search(
        rf"(?:orders?|sales?).*?"
        rf"\b(?:from|in|during)\s+"
        rf"({month_names})\s+"
        rf"(20[0-9]{{2}})\b",
        question_lower
    )

    if month_year_match:

        month = month_year_match.group(1)

        year = int(
            month_year_match.group(2)
        )

        return {
            "success": True,
            "intent": "time_filter",
            "table": "orders",
            "date_column": "order_date",
            "time_period": "month",
            "month": month.title(),
            "year": year,
            "original_question": original_question
        }

    # ============================================================
    # 21. ORDERS BY MONTH
    # ============================================================

    month_match = re.search(
        rf"(?:orders?|sales?).*?"
        rf"\b(?:from|in|during)\s+"
        rf"({month_names})\b",
        question_lower
    )

    if month_match:

        month = month_match.group(1)

        return {
            "success": True,
            "intent": "time_filter",
            "table": "orders",
            "date_column": "order_date",
            "time_period": "month",
            "month": month.title(),
            "original_question": original_question
        }

    # ============================================================
    # 22. ORDERS BY YEAR
    # ============================================================

    year_match = re.search(
        r"(?:orders?|sales?).*?"
        r"\b(?:from|in|during)\s+"
        r"(20[0-9]{2})\b",
        question_lower
    )

    if year_match:

        year = int(
            year_match.group(1)
        )

        return {
            "success": True,
            "intent": "time_filter",
            "table": "orders",
            "date_column": "order_date",
            "time_period": "year",
            "value": year,
            "original_question": original_question
        }

    # ============================================================
    # 23. TOTAL REVENUE
    # ============================================================

    revenue_patterns = [
        r"total\s+revenue",
        r"\brevenue\b",
        r"total\s+sales",
        r"overall\s+sales"
    ]

    for pattern in revenue_patterns:

        if re.search(
            pattern,
            question_lower
        ):

            return {
                "success": True,
                "intent": "aggregation",
                "operation": "sum",
                "table": "orders",
                "column": "total_amount",
                "alias": "total_revenue",
                "original_question": original_question
            }

    # ============================================================
    # 24. HIGHEST SPENDING CUSTOMER
    # ============================================================

    highest_customer_patterns = [
        r"highest\s+spending\s+customer",
        r"top\s+spending\s+customer",
        r"best\s+customer",
        r"customer\s+who\s+spent\s+the\s+most",
        r"customer\s+with\s+highest\s+spending"
    ]

    for pattern in highest_customer_patterns:

        if re.search(
            pattern,
            question_lower
        ):

            return {
                "success": True,
                "intent": "ranking",
                "operation": "highest_spending_customer",
                "original_question": original_question
            }

    # ============================================================
    # 25. UNKNOWN QUERY
    # ============================================================

    return {
        "success": False,
        "intent": "unknown",
        "message": (
            "I could not understand the requested "
            "operation yet."
        ),
        "original_question": original_question
    }