import plotly.express as px


def create_visualization(results, result_analysis):
    """
    Creates a Plotly visualization from SQL query results
    and result analysis metadata.

    Returns a Plotly Figure or None when visualization
    is not appropriate.
    """

    if not results:
        return None

    if not result_analysis:
        return None

    visualization = result_analysis.get(
        "visualization",
        {}
    )

    if not visualization.get("recommended"):
        return None

    chart_type = visualization.get("chart_type")

    x_axis = visualization.get("x_axis")

    y_axis = visualization.get("y_axis")

    if not x_axis or not y_axis:
        return None

    if x_axis not in results[0]:
        return None

    if y_axis not in results[0]:
        return None

    # ============================================================
    # BAR CHART
    # ============================================================

    if chart_type == "bar":

        figure = px.bar(
            results,
            x=x_axis,
            y=y_axis,
            title=f"{y_axis.replace('_', ' ').title()} by "
                  f"{x_axis.replace('_', ' ').title()}"
        )

        return figure

    # ============================================================
    # LINE CHART
    # ============================================================

    if chart_type == "line":

        figure = px.line(
            results,
            x=x_axis,
            y=y_axis,
            title=f"{y_axis.replace('_', ' ').title()} over "
                  f"{x_axis.replace('_', ' ').title()}"
        )

        return figure

    # ============================================================
    # PIE CHART
    # ============================================================

    if chart_type == "pie":

        figure = px.pie(
            results,
            names=x_axis,
            values=y_axis,
            title=f"{y_axis.replace('_', ' ').title()} by "
                  f"{x_axis.replace('_', ' ').title()}"
        )

        return figure

    return None


def serialize_visualization(figure):
    """
    Converts a Plotly Figure into a JSON-compatible
    dictionary that can be returned by FastAPI.
    """

    if figure is None:

        return None

    return figure.to_plotly_json()