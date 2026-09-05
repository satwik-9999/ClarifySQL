def analyze_results(results):
    """
    Analyzes SQL query results and determines the result type
    and whether the data is suitable for visualization.
    """

    if results is None:

        return {
            "result_type": "error",
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

    if len(results) == 0:

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

    # ============================================================
    # IDENTIFY COLUMN TYPES
    # ============================================================

    numeric_columns = []
    text_columns = []

    for column in columns:

        values = [
            row.get(column)
            for row in results
            if row.get(column) is not None
        ]

        if not values:
            continue

        if all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            for value in values
        ):

            numeric_columns.append(column)

        else:

            text_columns.append(column)

    # ============================================================
    # SINGLE VALUE
    # ============================================================

    if len(results) == 1 and len(columns) == 1:

        return {
            "result_type": "single_value",
            "row_count": len(results),
            "columns": columns,
            "numeric_columns": numeric_columns,
            "text_columns": text_columns,
            "visualization": {
                "recommended": False,
                "chart_type": None,
                "x_axis": None,
                "y_axis": None
            }
        }

    # ============================================================
    # SINGLE ROW
    # ============================================================

    if len(results) == 1:

        return {
            "result_type": "single_row",
            "row_count": len(results),
            "columns": columns,
            "numeric_columns": numeric_columns,
            "text_columns": text_columns,
            "visualization": {
                "recommended": False,
                "chart_type": None,
                "x_axis": None,
                "y_axis": None
            }
        }

    # ============================================================
    # CHOOSE BEST NUMERIC COLUMN
    # ============================================================

    identifier_keywords = [
        "id",
        "code",
        "number"
    ]

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
        "sum",
        "profit",
        "cost"
    ]

    metric_columns = []

    for column in numeric_columns:

        column_lower = column.lower()

        is_identifier = any(
            keyword in column_lower
            for keyword in identifier_keywords
        )

        is_metric = any(
            keyword in column_lower
            for keyword in metric_keywords
        )

        if is_metric and not is_identifier:

            metric_columns.append(column)

    # Prefer meaningful metric columns over IDs

    if metric_columns:

        selected_y_axis = metric_columns[0]

    elif numeric_columns:

        selected_y_axis = numeric_columns[0]

    else:

        selected_y_axis = None

    # ============================================================
    # CHOOSE BEST TEXT COLUMN
    # ============================================================

    preferred_text_keywords = [
        "name",
        "category",
        "city",
        "status",
        "method"
    ]

    preferred_text_columns = []

    for column in text_columns:

        column_lower = column.lower()

        if any(
            keyword in column_lower
            for keyword in preferred_text_keywords
        ):

            preferred_text_columns.append(column)

    if preferred_text_columns:

        selected_x_axis = preferred_text_columns[0]

    elif text_columns:

        selected_x_axis = text_columns[0]

    else:

        selected_x_axis = None

    # ============================================================
    # VISUALIZATION
    # ============================================================

    visualization = {
        "recommended": False,
        "chart_type": None,
        "x_axis": None,
        "y_axis": None
    }

    if selected_x_axis and selected_y_axis:

        visualization = {
            "recommended": True,
            "chart_type": "bar",
            "x_axis": selected_x_axis,
            "y_axis": selected_y_axis
        }

    # ============================================================
    # FINAL RESULT
    # ============================================================

    return {
        "result_type": "table",
        "row_count": len(results),
        "columns": columns,
        "numeric_columns": numeric_columns,
        "text_columns": text_columns,
        "visualization": visualization
    }