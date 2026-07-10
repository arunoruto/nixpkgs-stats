import plotly.graph_objects as go


def build_histogram(counts: dict[str, int], title: str = "") -> go.Figure:
    sorted_items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    prefixes = [p for p, _ in sorted_items]
    values = [c for _, c in sorted_items]

    fig = go.Figure(
        data=go.Bar(
            x=prefixes,
            y=values,
            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
            marker={"color": values, "colorscale": "Turbo", "showscale": False},
        )
    )

    fig.update_layout(
        title=title or "Package Count per Prefix (descending)",
        xaxis_title="Prefix",
        yaxis_title="Count",
        width=max(1200, len(prefixes) * 10),
        height=500,
        margin={"l": 50, "r": 20, "t": 60, "b": 80},
        xaxis={"tickangle": -90, "tickfont": {"size": 8}},
        bargap=0.05,
    )

    return fig
