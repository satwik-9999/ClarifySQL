def check_clarification(question):
    """
    Checks whether the user's question is ambiguous
    and requires clarification before SQL generation.

    Returns structured clarification information
    that can be stored by the conversation manager.
    """

    if not question or not question.strip():

        return {
            "needs_clarification": True,
            "clarification_id": "empty_question",
            "message": "Please enter a question.",
            "options": []
        }

    question_lower = question.lower().strip()

    # ============================================================
    # BEST CUSTOMER
    # ============================================================

    if (
        "best customer" in question_lower
        or "top customer" in question_lower
    ):

        return {
            "needs_clarification": True,
            "clarification_id": "customer_metric",
            "message": "How should 'best customer' be measured?",
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

    # ============================================================
    # BEST PRODUCT
    # ============================================================

    if (
        "best product" in question_lower
        or "top product" in question_lower
    ):

        return {
            "needs_clarification": True,
            "clarification_id": "product_metric",
            "message": "How should 'best product' be measured?",
            "options": [
                {
                    "id": "sales_revenue",
                    "label": "Highest sales revenue"
                },
                {
                    "id": "quantity_sold",
                    "label": "Highest quantity sold"
                }
            ]
        }

    # ============================================================
    # NO CLARIFICATION REQUIRED
    # ============================================================

    return {
        "needs_clarification": False,
        "clarification_id": None,
        "message": None,
        "options": []
    }