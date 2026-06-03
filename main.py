import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from cleaning_and_plotting import *
from metrics import *

def main():

    df = clean_wind_commodity_data(
        "Copy of wind品种指数数据(1).xlsx"
    )
    #################################################
    trend_sharpe = compute_trend_sharpe(df)

    plot_metric(
        trend_sharpe,
        "趋势流畅度对比",
        "trend_sharpe.png",
        "Trend Sharpe"
    )
    #################################################
    noise_ratio = compute_noise_ratio(df)

    plot_metric(
        noise_ratio,
        "噪音比例对比",
        "noise_ratio.png",
        "Noise Ratio"
    )
    #################################################
    drawdown_ratio = (
    compute_drawdown_structure_ratios(
        df
        )
    )

    plot_metric(
        drawdown_ratio,
        title="回撤结构比",
        filename="drawdown_ratio.png",
        xlabel="Drawdown Ratio"
    )
    #################################################
    gap_ratio = (
        compute_gap_ratios(df)
    )

    plot_metric(
        gap_ratio,
        title="跳空次数占比",
        filename="gap_ratio.png",
        xlabel="Gap Ratio"
    )


if __name__ == "__main__":
    main()