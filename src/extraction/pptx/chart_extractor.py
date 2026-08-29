"""
extraction/pptx/chart_extractor.py

Pulls the underlying data table a chart is visualizing (categories +
per-series values), plus the chart title if set. This is usually the
highest-value content on a data-heavy slide, and was previously lost
entirely by extractors that only flagged `has_chart=True`.
"""

from __future__ import annotations


def extract_chart(shape) -> dict | None:
    if not shape.has_chart:
        return None

    chart = shape.chart

    try:
        plot = chart.plots[0]
        categories = [str(c) for c in plot.categories]
    except Exception:
        categories = []

    series_data = []
    for s in chart.series:
        try:
            values = list(s.values)
        except Exception:
            values = []
        series_data.append({"name": s.name, "values": values})

    title = None
    try:
        if chart.has_title:
            title = chart.chart_title.text_frame.text
    except Exception:
        pass

    return {
        "chart_type": str(chart.chart_type),
        "title": title,
        "categories": categories,
        "series": series_data,
    }
