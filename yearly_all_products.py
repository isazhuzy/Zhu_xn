"""
All-product yearly metric line graphs: noise ratio, drawdown structure ratio,
gap ratio. Pastable into your project.

HOW IT IS COMPUTED
------------------
For ONE product, your existing per-commodity yearly functions already do the
work, year by year:
    compute_yearly_noise_ratio(close)     median(20d return vol / 20d directional move) within each calendar year
    compute_yearly_drawdown_ratio(close)  |max drawdown| / |net move| within each year (denominator floored at 0.05)
    compute_yearly_gap_ratio(close)       share of days with |daily return| > 2% within each year

all_products_yearly_table() just runs the chosen function over EVERY column and
stacks the per-year Series into a single (year x product) DataFrame.

plot_all_products_yearly() then draws that table as a line graph: one faint line
per product, plus a bold cross-sectional MEDIAN line and a shaded 25-75% band so
the 62-product cloud stays readable.

WHERE TO PASTE
--------------
    all_products_yearly_table()  -> metrics module
    plot_all_products_yearly()   -> cleaning_and_plotting module
    main()                       -> make_figures / your main
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# standalone-run import; in your project these live in your own modules
from metrics_lib import (
    load_clean_prices,
    compute_yearly_noise_ratio,
    compute_yearly_drawdown_ratio,
    compute_yearly_gap_ratio,
)


# =============================================================================
# METRICS  (paste into metrics module)
# =============================================================================
def all_products_yearly_table(df: pd.DataFrame, metric_func, **kwargs) -> pd.DataFrame:
    """
    Apply a per-commodity yearly metric to EVERY column of df.
    Returns a DataFrame indexed by year, one column per product.
    """
    return pd.DataFrame({
        col: metric_func(df[col].dropna(), **kwargs)
        for col in df.columns
    }).sort_index()


# =============================================================================
# PLOTTING  (paste into cleaning_and_plotting module)
# =============================================================================
def plot_all_products_yearly(
    table: pd.DataFrame,
    title: str,
    ylabel: str,
    savepath: str | None = None,
    ymax: float | None = None,
    good_low: bool = True,
) -> None:
    """
    Line graph of a yearly metric across ALL products.
    Thin grey line per product + bold median + shaded 25-75% band.
    `ymax` clips the y-axis (drawdown ratio can spike on round-trip years).
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # faint individual products
    for col in table.columns:
        ax.plot(table.index, table[col].values, color="0.7", lw=0.6, alpha=0.5)

    # cross-sectional summary
    med = table.median(axis=1)
    q1, q3 = table.quantile(0.25, axis=1), table.quantile(0.75, axis=1)
    ax.fill_between(table.index, q1, q3, color="#2c6fbb", alpha=0.15,
                    label="25–75% band")
    ax.plot(med.index, med.values, color="#c1452b", lw=2.4, marker="o", ms=4,
            label="Cross-sectional median")

    ax.set_title(title, fontsize=13, pad=8)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Year")
    if ymax is not None:
        ax.set_ylim(0, ymax)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, fontsize=10)
    note = "lower = better" if good_low else "higher = better"
    ax.text(0.99, 0.97, note, transform=ax.transAxes, ha="right", va="top",
            fontsize=9, color="0.4")

    plt.tight_layout()
    if savepath:
        plt.savefig(savepath, dpi=150, bbox_inches="tight")
    plt.close()


# =============================================================================
# MAIN
# =============================================================================
def main():
    PATH = "/mnt/user-data/uploads/Copy_of_wind品种指数数据_1_.xlsx"
    df = load_clean_prices(PATH)
    out = "/mnt/user-data/outputs"

    noise = all_products_yearly_table(df, compute_yearly_noise_ratio)
    plot_all_products_yearly(
        noise, "全品种年度噪声比 (Yearly noise ratio, all products)",
        "Noise ratio", f"{out}/yearly_noise_all.png", ymax=1.2, good_low=True)

    draw = all_products_yearly_table(df, compute_yearly_drawdown_ratio)
    plot_all_products_yearly(
        draw, "全品种年度回撤结构比 (Yearly drawdown structure ratio, all products)",
        "|max DD| / |net move|", f"{out}/yearly_drawdown_all.png",
        ymax=8.0, good_low=True)

    gap = all_products_yearly_table(df, compute_yearly_gap_ratio)
    plot_all_products_yearly(
        gap, "全品种年度跳空比 (Yearly gap ratio >2%, all products)",
        "Gap ratio", f"{out}/yearly_gap_all.png", ymax=0.6, good_low=True)

    for name, t in [("noise", noise), ("drawdown", draw), ("gap", gap)]:
        t.round(4).to_csv(f"{out}/yearly_{name}_all_table.csv", encoding="utf-8-sig")
    print("done.")


if __name__ == "__main__":
    plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei", "Noto Sans CJK JP"]
    plt.rcParams["axes.unicode_minus"] = False
    main()
