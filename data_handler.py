import pandas as pd
import numpy as np
import plotly.express as px
import os

# Functions

def load_and_clean_data():

    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "data", "store_sales.csv")
    df = pd.read_csv(file_path)
    
    df.columns = df.columns.str.strip() 
    df['Date'] = pd.to_datetime(df['Date'])
    df['Profit Margin'] = df['Profit'] / df['Sales']
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    
    return df

def get_kpis(df):
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    total_orders = len(df)
    top_cat = df.groupby('Category')['Sales'].sum().idxmax()
    
    # 1. Average Order Value (AOV)
    aov = total_sales / total_orders if total_orders > 0 else 0
    
    # 2. Best Region by Profit
    best_region = df.groupby('Region')['Profit'].sum().idxmax()

    # 3. Current Month Sales & Month-over-Month Growth
    # Group sales by the Year-Month period and sort them chronologically
    monthly_sales = df.groupby('Month')['Sales'].sum().sort_index()
    
    current_month_sales = 0
    mom_growth = 0
    
    if len(monthly_sales) >= 2:
        # Get the last month (current) and the second to last month (previous)
        current_month_sales = monthly_sales.iloc[-1] 
        prev_month_sales = monthly_sales.iloc[-2]    
        
        # Calculate percentage growth: ((Current - Previous) / Previous) * 100
        if prev_month_sales > 0:
            mom_growth = ((current_month_sales - prev_month_sales) / prev_month_sales) * 100
    elif len(monthly_sales) == 1:
        current_month_sales = monthly_sales.iloc[0]

    return {
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "avg_margin": round((total_profit / total_sales) * 100, 2) if total_sales > 0 else 0,
        "total_orders": total_orders,
        "top_category": top_cat,
        
        # New KPIs added to the dictionary
        "current_month_sales": round(current_month_sales, 2),
        "mom_growth": round(mom_growth, 2),
        "aov": round(aov, 2),
        "best_region": best_region
    }

def get_charts(df):

    # Trend Chart
    monthly = df.groupby('Month')['Sales'].sum().reset_index()
    fig_trend = px.line(monthly, x='Month', y='Sales', title='Monthly Sales Trend', markers=True)
    
    # Region Chart
    region = df.groupby('Region')['Profit'].sum().reset_index()
    fig_region = px.bar(region, x='Region', y='Profit', title='Profit by Region', color='Region')

    # Category Pie Chart
    category = df.groupby('Category')['Sales'].sum().reset_index()
    fig_cat = px.pie(category, values='Sales', names='Category', title='Sales by Category', hole=0.3)
    
    # Top 5 Sub-Categories
    subcat = df.groupby('Sub_Category')['Sales'].sum().nlargest(5).reset_index()
    fig_subcat = px.bar(subcat, x='Sales', y='Sub_Category', orientation='h', title='Top 5 Selling Items', color='Sales')

    # backgrounds transparent so Dark Mode looks perfect
    for fig in [fig_trend, fig_region, fig_cat, fig_subcat]:
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)'
        )

    charts = {
        "trend_chart": fig_trend.to_html(full_html=False, include_plotlyjs='cdn'),
        "region_chart": fig_region.to_html(full_html=False, include_plotlyjs='cdn'),
        "category_chart": fig_cat.to_html(full_html=False, include_plotlyjs='cdn'),
        "subcat_chart": fig_subcat.to_html(full_html=False, include_plotlyjs='cdn')
    }
    return charts


def get_sales_forecast(df):
    
    monthly = df.groupby('Month')['Sales'].sum().reset_index()
    monthly['TimeIndex'] = np.arange(len(monthly))
    m, b = np.polyfit(monthly['TimeIndex'], monthly['Sales'], 1)
    
    next_time_index = len(monthly)
    predicted_sales = (m * next_time_index) + b
    return round(predicted_sales, 2)