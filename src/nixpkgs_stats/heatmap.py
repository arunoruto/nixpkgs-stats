import string

import numpy as np
import pandas as pd
import plotly.graph_objects as go


def _build_matrix(counts: dict[str, int]) -> pd.DataFrame:
    letters = list(string.ascii_lowercase)
    matrix = pd.DataFrame(0, index=letters, columns=letters, dtype=int)

    for prefix, count in counts.items():
        if len(prefix) == 2:
            row = prefix[1]
            col = prefix[0]
            if row in letters and col in letters:
                matrix.at[row, col] = count

    return matrix


def build_figure(
    counts: dict[str, int],
    title: str = "nixpkgs pkgs/by-name Package Distribution",
    log_scale: bool = False,
) -> go.Figure:
    matrix = _build_matrix(counts)
    letters = list(string.ascii_lowercase)
    values = matrix.values.astype(float)

    if log_scale:
        z = np.log1p(values)
        colorbar = dict(
            title="Count (log₁₀)",
            tickvals=[
                np.log1p(v) for v in [0, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000]
            ],
            ticktext=[
                "0",
                "1",
                "2",
                "5",
                "10",
                "20",
                "50",
                "100",
                "200",
                "500",
                "1k",
                "2k",
            ],
        )
    else:
        z = values
        colorbar = dict(title="Count")

    hover_template = "<b>%{x}%{y}</b><br>Count: %{customdata}<extra></extra>"

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=letters,
            y=letters,
            colorscale="Turbo",
            customdata=values,
            hovertemplate=hover_template,
            showscale=True,
            colorbar=colorbar,
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="First Letter",
        yaxis_title="Second Letter",
        xaxis=dict(
            side="top",
            tickmode="array",
            tickvals=letters,
        ),
        yaxis=dict(
            autorange="reversed",
            tickmode="array",
            tickvals=letters,
        ),
        width=750,
        height=750,
        margin=dict(t=150),
        # margin={"l": 40, "r": 40, "t": 100, "b": 40},
    )

    return fig
