from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "store_sales.csv"
REQUIRED_COLUMNS = {
    "Order_ID", "Date", "Category", "Sub_Category", "Region",
    "Sales", "Quantity", "Profit",
}


def load_and_clean_data(file_path=None):
    """Load the store CSV and normalize fields used by the dashboard."""
    source = Path(file_path) if file_path is not None else DATA_PATH
    if not source.is_file():
        raise FileNotFoundError(f"Sales dataset not found: {source}")

    df = pd.read_csv(source)
    df.columns = df.columns.astype(str).str.strip()

    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"Sales dataset is missing required columns: {', '.join(missing)}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for column in ("Sales", "Quantity", "Profit"):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Exclude records that cannot contribute to the required sales analysis.
    df = df.dropna(subset=[
        "Order_ID", "Date", "Category", "Sub_Category", "Region",
        "Sales", "Quantity", "Profit",
    ]).copy()

    for column in ("Sales", "Quantity", "Profit"):
        df = df[np.isfinite(df[column])]

    df["Category"] = df["Category"].astype(str).str.strip()
    df["Sub_Category"] = df["Sub_Category"].astype(str).str.strip()
    df["Region"] = df["Region"].astype(str).str.strip()
    df = df[
        df["Category"].ne("")
        & df["Sub_Category"].ne("")
        & df["Region"].ne("")
    ].copy()

    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["Profit Margin"] = np.divide(
        df["Profit"],
        df["Sales"],
        out=np.full(len(df), np.nan, dtype=float),
        where=df["Sales"].to_numpy() != 0,
    )
    return df


def get_kpis(df):
    """Calculate dashboard KPIs using the latest month present in the data."""
    total_sales = float(df["Sales"].sum()) if not df.empty else 0.0
    total_profit = float(df["Profit"].sum()) if not df.empty else 0.0
    total_orders = int(len(df))

    top_cat = "N/A"
    best_region = "N/A"
    latest_month = "N/A"
    current_month_sales = 0.0
    mom_growth = 0.0

    if not df.empty:
        category_sales = df.groupby("Category")["Sales"].sum()
        region_profit = df.groupby("Region")["Profit"].sum()
        if not category_sales.empty:
            top_cat = category_sales.idxmax()
        if not region_profit.empty:
            best_region = region_profit.idxmax()

        monthly_sales = df.groupby("Month")["Sales"].sum().sort_index()
        if not monthly_sales.empty:
            latest_month = str(monthly_sales.index[-1])
            current_month_sales = float(monthly_sales.iloc[-1])
        if len(monthly_sales) >= 2:
            previous_month_sales = float(monthly_sales.iloc[-2])
            if previous_month_sales != 0:
                mom_growth = (
                    (current_month_sales - previous_month_sales)
                    / abs(previous_month_sales)
                ) * 100

    aov = total_sales / total_orders if total_orders else 0.0
    avg_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0.0

    return {
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "avg_margin": round(avg_margin, 2),
        "total_orders": total_orders,
        "top_category": top_cat,
        "current_month_sales": round(current_month_sales, 2),
        "latest_month": latest_month,
        "mom_growth": round(mom_growth, 2),
        "aov": round(aov, 2),
        "best_region": best_region,
    }


def get_charts(df):
    """Build the four Plotly visualizations used by the dashboard."""
    monthly = df.groupby("Month")["Sales"].sum().reset_index()
    region = df.groupby("Region")["Profit"].sum().reset_index()
    category = df.groupby("Category")["Sales"].sum().reset_index()
    subcat = (
        df.groupby("Sub_Category")["Sales"]
        .sum()
        .nlargest(5)
        .reset_index()
    )

    fig_trend = px.line(
        monthly, x="Month", y="Sales",
        title="Monthly Sales Trend", markers=True,
    )
    fig_region = px.bar(
        region, x="Region", y="Profit",
        title="Profit by Region", color="Region",
    )
    fig_cat = px.pie(
        category, values="Sales", names="Category",
        title="Sales by Category", hole=0.3,
    )
    fig_subcat = px.bar(
        subcat, x="Sales", y="Sub_Category",
        orientation="h", title="Top 5 Selling Items", color="Sales",
    )

    for fig in (fig_trend, fig_region, fig_cat, fig_subcat):
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

    return {
        "trend_chart": fig_trend.to_html(full_html=False, include_plotlyjs="cdn"),
        "region_chart": fig_region.to_html(full_html=False, include_plotlyjs="cdn"),
        "category_chart": fig_cat.to_html(full_html=False, include_plotlyjs="cdn"),
        "subcat_chart": fig_subcat.to_html(full_html=False, include_plotlyjs="cdn"),
    }


def get_sales_forecast(df):
    """Return a simple linear trend estimate for the month after the data."""
    monthly = df.groupby("Month")["Sales"].sum().sort_index()
    if len(monthly) < 2:
        return None

    time_index = np.arange(len(monthly), dtype=float)
    slope, intercept = np.polyfit(time_index, monthly.to_numpy(dtype=float), 1)
    predicted_sales = (slope * len(monthly)) + intercept
    if not np.isfinite(predicted_sales):
        return None
    return round(float(predicted_sales), 2)
