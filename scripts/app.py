from pathlib import Path

import streamlit as st
from nixpkgs_stats.heatmap import build_figure
from nixpkgs_stats.scanner import get_repo_info, scan

st.set_page_config(page_title="nixpkgs Stats", layout="centered")
st.title("nixpkgs Package Distribution Heatmap")


# @st.cache_data(show_spinner=False)
def cached_scan(repo_path: str, mode: str, exclude_lib: bool) -> dict[str, int]:
    return scan(repo_path, mode=mode, exclude_lib=exclude_lib)


repo_path = st.text_input(
    "Path to nixpkgs repository",
    value=st.session_state.get("last_path", "/home/mar/Development/nixpkgs/main"),
    placeholder="/home/user/nixpkgs",
)
st.session_state["last_path"] = repo_path

do_scan = st.button("Scan", type="primary", width="stretch")

with st.sidebar:
    st.subheader("Options")

    count_mode = st.selectbox(
        "Count mode",
        options=["directories", "files"],
        format_func=lambda m: (
            "Directories (packages)" if m == "directories" else "All .nix files"
        ),
    )

    log_scale = st.checkbox("Log color scale", value=False)
    exclude_lib = st.checkbox("Exclude lib* in li/", value=False)

if do_scan:
    if not repo_path or not repo_path.strip():
        st.error("Please enter a repository path.")
    elif not Path(repo_path).is_dir():
        st.error(f"Path does not exist or is not a directory: '{repo_path}'")
    else:
        try:
            with st.spinner("Scanning pkgs/by-name/..."):
                counts = cached_scan(
                    repo_path, mode=count_mode, exclude_lib=exclude_lib
                )

            if not counts:
                st.warning("No packages found in pkgs/by-name/.")
            else:
                total = sum(counts.values())
                top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
                repo_info = get_repo_info(repo_path)

                col_total, col_repo = st.columns([1, 2])
                with col_total:
                    st.subheader(f"Total entries: **{total:,}**")
                with col_repo:
                    if repo_info:
                        st.caption(
                            f"Repo at `{repo_info['hash']}` ({repo_info['date']})"
                        )
                st.caption(
                    "Top prefixes: " + " | ".join(f"**{p}** ({c})" for p, c in top)
                )

                title = (
                    r"nixpkgs pkgs/by-name - Package Directories"
                    if count_mode == "directories"
                    else r"nixpkgs pkgs/by-name - .nix Files"
                )
                fig = build_figure(counts, title=title, log_scale=log_scale)

                try:
                    st.plotly_chart(fig)
                except Exception as chart_err:
                    st.error(f"Failed to render chart: {chart_err}")
                    st.write("Raw counts (first 20):")
                    st.json({k: counts[k] for k in list(counts)[:20]})

        except FileNotFoundError as e:
            st.error(str(e))
