import argparse
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from nixpkgs_stats.heatmap import build_figure
from nixpkgs_stats.histogram import build_histogram
from nixpkgs_stats.scanner import get_repo_info, scan


def build_table(counts: dict[str, int]) -> go.Figure:
    df = (
        pd.DataFrame(counts.items(), columns=["Prefix", "Count"])
        .sort_values("Count", ascending=False)
        .reset_index(drop=True)
    )
    df.index += 1
    df.index.name = "#"

    top5 = df.head(5)
    bottom5 = df.tail(5)
    sep = pd.DataFrame([["...", "..."]], columns=["Prefix", "Count"], index=["..."])
    sep.index.name = "#"
    table = pd.concat([top5, sep, bottom5])

    cell_values = [
        [str(i) for i in table.index],
        table["Prefix"].tolist(),
        [str(c) for c in table["Count"].tolist()],
    ]

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=["#", "Prefix", "Count"],
                    align="center",
                    font=dict(size=14),
                ),
                cells=dict(
                    values=cell_values,
                    align="center",
                    font=dict(size=13),
                    height=30,
                ),
            )
        ]
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=360)
    return fig


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo",
        required=True,
        help="Path to nixpkgs repository",
    )
    args = parser.parse_args()

    assets = Path("docs/assets")
    assets.mkdir(parents=True, exist_ok=True)

    repo_path = args.repo

    counts = scan(repo_path, mode="directories", exclude_lib=True)
    info = get_repo_info(repo_path)
    total = sum(counts.values())

    title_heatmap = f"nixpkgs pkgs/by-name — {total:,} package directories"
    if info:
        title_heatmap += f" ({info['hash']}, {info['date']})"

    heatmap_fig = build_figure(counts, title=title_heatmap, log_scale=False)
    heatmap_fig.write_html(
        assets / "heatmap.html",
        full_html=True,
        include_plotlyjs="cdn",
    )

    table_fig = build_table(counts)
    table_fig.write_html(
        assets / "table.html",
        full_html=True,
        include_plotlyjs="cdn",
    )

    hist_fig = build_histogram(counts, title="Package Count per Prefix (descending)")
    hist_fig.write_html(
        assets / "histogram.html",
        full_html=True,
        include_plotlyjs="cdn",
    )

    stats_line = f"**Commit:** `{info['hash']}` ({info['date']}) — **{total:,}** package directories (lib\\* excluded)  \n"

    index_md = Path("docs/index.md").read_text()
    index_md = index_md.replace("<!-- STATS_PLACEHOLDER -->", stats_line)
    Path("docs/index.md").write_text(index_md)

    print(f"Generated site: {total:,} packages from nixpkgs@{info['hash']}")


if __name__ == "__main__":
    main()
