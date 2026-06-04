import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from metrics import *
# ==========================================================
# df cleaning
# ==========================================================

def basic_clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform generic dataframe cleaning.

    Removes:
    - empty rows
    - empty columns
    - duplicate rows
    """

    df = df.copy()

    df.dropna(axis=0, how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)
    df.drop_duplicates(inplace=True)

    return df


def clean_wind_commodity_data(filepath: str) -> pd.DataFrame:
    """
    Load and clean Wind commodity index data.

    Parameters
    ----------
    filepath : str
        Path to Excel file.

    Returns
    -------
    pd.DataFrame
        Clean dataframe indexed by date.
    """

    df = pd.read_excel(
        filepath,
        sheet_name="Sheet1",
        header=3
    )

    df = basic_clean_df(df)
    # Remove Wind ticker row
    df = df.iloc[1:].copy()
    # Convert date column
    df["日期"] = pd.to_datetime(df["日期"])
    # Convert all commodity columns to numeric
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # Set date as index
    df.set_index("日期", inplace=True)
    return df


# ==========================================================
# plotting
# ==========================================================

def plot_metric(
    metric: pd.Series,
    title: str,
    filename: str,
    xlabel: str
) -> None:
    """
    Plot a horizontal bar chart and save it.
    """

    plt.rcParams["font.sans-serif"] = [
        "PingFang HK"
    ]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(
        figsize=(12, 10)
    )

    metric.plot(
        kind="barh",
        ax=ax
    )

    for i, v in enumerate(metric):
        ax.text(
            v,
            i,
            f"{v:.2f}",
            va="center"
        )

    plt.title(title)
    plt.xlabel(xlabel)

    plt.tight_layout()

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    plt.close()


def plot_time_series(
    metric: pd.Series,
    title: str,
    filename: str
):
    """
    line graph
    """

    plt.figure(figsize=(10,6))

    metric.plot(
        marker="o"
    )

    plt.title(title)

    plt.ylabel(
        "Trend Sharpe"
    )

    plt.tight_layout()

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    plt.close()
def plot_multiple_time_series(
    data_dict: dict,
    title: str,
    filename: str
    ) -> None:
    """
    Plot multiple time series
    on the same figure.
    """

    plt.rcParams["font.sans-serif"] = [
        "PingFang HK"
    ]

    plt.rcParams["axes.unicode_minus"] = False

    plt.figure(figsize=(12, 8))

    for label, series in data_dict.items():

        plt.plot(
            series.index,
            series.values,
            marker="o",
            label=label
        )

    plt.legend()

    plt.title(title)

    plt.ylabel("Trend Sharpe")

    plt.tight_layout()

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

def plot_multiple_yearly_sharpes(
    df,
    commodities
    ):

    plt.figure(figsize=(12,8))

    for commodity in commodities:

        yearly_sharpe = (
            compute_yearly_sharpe(
                df[commodity]
            )
        )

        plt.plot(
            yearly_sharpe.index,
            yearly_sharpe.values,
            marker="o",
            label=commodity
        )

    plt.legend()

    plt.title(
        "Yearly Trend Sharpe"
    )

    plt.tight_layout()

    plt.savefig(
        "selected_commodities_sharpe.png",
        dpi=300
    )

    plt.show()

    # =============================================================================
# PLOTTING  (cleaning & plotting module)
# =============================================================================

# Optional: enable Chinese labels. If you don't need CJK, leave labels English.
def setup_cjk_font(path: str | None = None) -> None:
    """
    Register a CJK font so Chinese titles/legends render. Pass a .ttf/.ttc
    path, e.g. on macOS "/System/Library/Fonts/PingFang.ttc", on Linux a
    Noto CJK file. Call once before plotting; skip if labels are English.
    """
    if path is None:
        return
    from matplotlib import font_manager as fm
    fm.fontManager.addfont(path)
    prop = fm.FontProperties(fname=path)
    plt.rcParams["font.family"] = prop.get_name()
    plt.rcParams["axes.unicode_minus"] = False


# shared house style
plt.rcParams.update({
    "font.size": 11,
    "font.sans-serif": ["PingFang HK", "PingFang SC", "Heiti SC", "Arial Unicode MS", "Arial"],
    "axes.unicode_minus": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

PALETTE = [
    "#C8A02A", "#2c6fbb", "#c1452b", "#6a6a6a",
    "#2e8b57", "#8e44ad", "#d98c00", "#1f7a7a",
]


def plot_yearly_metric(
    series_by_name: dict[str, pd.Series],
    title: str,
    ylabel: str,
    max_year: int | None = None,
    hline: float | None = None,
    savepath: str | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """
    Generic line chart of a yearly metric for several commodities.
    `series_by_name` = {label: yearly Series} (output of yearly_metric_table).
    """
    own_fig = ax is None
    if own_fig:
        fig, ax = plt.subplots(figsize=(12, 4.8))

    for i, (name, s) in enumerate(series_by_name.items()):
        if max_year is not None:
            s = s[s.index <= max_year]
        ax.plot(
            s.index, s.values,
            marker="o", ms=4, lw=1.8,
            label=name, color=PALETTE[i % len(PALETTE)],
        )

    if hline is not None:
        ax.axhline(hline, color="grey", lw=0.7)

    ax.set_title(title, fontsize=12, pad=8)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Year")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=9, frameon=False, ncol=min(3, len(series_by_name)))

    if own_fig and savepath:
        plt.tight_layout()
        plt.savefig(savepath, dpi=130, bbox_inches="tight")
        plt.close()
    return ax


def plot_block_sharpe(
    df: pd.DataFrame,
    selected: list[str],
    blocks: list[tuple[int, int]],
    savepath: str | None = None,
) -> None:
    """
    Grouped bar chart: each commodity's Sharpe across consecutive multi-year
    blocks (the "5-year Sharpe" comparison).
    """
    table = pd.DataFrame({
        col: compute_block_sharpe(df[col].dropna(), blocks)
        for col in selected if col in df.columns
    })  # index = block labels, columns = commodities

    labels = table.index.tolist()
    x = np.arange(len(labels))
    n = len(table.columns)
    width = 0.8 / max(n, 1)

    fig, ax = plt.subplots(figsize=(12, 5))
    for i, col in enumerate(table.columns):
        ax.bar(
            x + i * width - 0.4 + width / 2,
            table[col].values,
            width=width, label=col, color=PALETTE[i % len(PALETTE)],
        )

    ax.axhline(0, color="grey", lw=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Annualized Sharpe")
    ax.set_title(f"Sharpe by {blocks[0][1] - blocks[0][0] + 1}-year period")
    ax.legend(fontsize=9, frameon=False, ncol=min(4, n))
    ax.grid(alpha=0.25, axis="y")

    if savepath:
        plt.tight_layout()
        plt.savefig(savepath, dpi=130, bbox_inches="tight")
        plt.close()


def plot_rolling_sharpe(
    df: pd.DataFrame,
    selected: list[str],
    window_years: int = 5,
    savepath: str | None = None,
) -> None:
    """Rolling N-year Sharpe lines for several commodities."""
    fig, ax = plt.subplots(figsize=(12, 4.8))

    for i, col in enumerate(selected):
        if col not in df.columns:
            continue
        roll = compute_rolling_sharpe(df[col].dropna(), window_years)
        ax.plot(roll.index, roll.values, lw=1.8,
                label=col, color=PALETTE[i % len(PALETTE)])

    ax.axhline(0, color="grey", lw=0.7)
    ax.set_ylabel("Annualized Sharpe")
    ax.set_title(f"Rolling {window_years}-year Sharpe")
    ax.legend(fontsize=9, frameon=False, ncol=min(4, len(selected)))
    ax.grid(alpha=0.25)

    if savepath:
        plt.tight_layout()
        plt.savefig(savepath, dpi=130, bbox_inches="tight")
        plt.close()


def plot_four_dim_yearly(
    df: pd.DataFrame,
    selected: list[str],
    metric_funcs: dict,       # {panel_title: (func, ylabel, kwargs)}
    max_year: int | None = None,
    savepath: str | None = None,
) -> None:
    """2x2 panel comparing four yearly metrics for the same commodity set."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    for ax, (title, (func, ylabel, kwargs)) in zip(axes.ravel(), metric_funcs.items()):
        series_by_name = yearly_metric_table(df, selected, func, **kwargs)
        plot_yearly_metric(series_by_name, title, ylabel,
                           max_year=max_year, ax=ax)

    plt.tight_layout()
    if savepath:
        plt.savefig(savepath, dpi=130, bbox_inches="tight")
        plt.close()


# -- minimal loader (use YOUR cleaning function instead if you already have one)
def load_clean_prices(path: str, skiprows: int = 4) -> pd.DataFrame:
    """Load the Wind 品种指数 export (4 metadata rows, then Date + tickers)."""
    raw = pd.read_excel(path, sheet_name=0, skiprows=skiprows)
    raw = raw.rename(columns={raw.columns[0]: "Date"})
    raw["Date"] = pd.to_datetime(raw["Date"], errors="coerce")
    raw = raw.dropna(subset=["Date"]).set_index("Date").sort_index()
    return raw.apply(pd.to_numeric, errors="coerce")
