import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

import data_handler


class StoreAnalyticsTests(unittest.TestCase):
    def sample_data(self):
        return pd.DataFrame({
            "Order_ID": [1, 2, 3],
            "Date": pd.to_datetime(["2025-01-10", "2025-03-10", "2025-03-15"]),
            "Category": ["Books", "Electronics", "Books"],
            "Sub_Category": ["Fiction", "Phones", "Education"],
            "Region": ["West", "East", "West"],
            "Sales": [100.0, 300.0, 200.0],
            "Quantity": [1, 2, 1],
            "Profit": [20.0, 60.0, -10.0],
            "Month": ["2025-01", "2025-03", "2025-03"],
            "Profit Margin": [0.2, 0.2, -0.05],
        })

    def test_loads_repository_dataset(self):
        df = data_handler.load_and_clean_data()
        self.assertGreater(len(df), 0)
        self.assertTrue(data_handler.REQUIRED_COLUMNS.issubset(df.columns))
        self.assertTrue(np.isfinite(df["Sales"]).all())

    def test_missing_required_column_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            pd.DataFrame({"Date": ["2025-01-01"], "Sales": [10]}).to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "missing required columns"):
                data_handler.load_and_clean_data(path)

    def test_invalid_rows_are_excluded_and_zero_sales_margin_is_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sales.csv"
            frame = pd.DataFrame({
                "Order_ID": [1, 2],
                "Date": ["2025-01-01", "not-a-date"],
                "Category": ["Books", "Books"],
                "Sub_Category": ["Fiction", "Fiction"],
                "Region": ["West", "West"],
                "Sales": [0, 10],
                "Quantity": [1, 1],
                "Profit": [5, 2],
            })
            frame.to_csv(path, index=False)
            result = data_handler.load_and_clean_data(path)
            self.assertEqual(len(result), 1)
            self.assertTrue(pd.isna(result.iloc[0]["Profit Margin"]))

    def test_kpis_use_latest_data_month_and_handle_empty_data(self):
        kpis = data_handler.get_kpis(self.sample_data())
        self.assertEqual(kpis["latest_month"], "2025-03")
        self.assertEqual(kpis["current_month_sales"], 500.0)
        self.assertEqual(kpis["total_orders"], 3)
        self.assertEqual(kpis["top_category"], "Books")

        empty = data_handler.get_kpis(self.sample_data().iloc[0:0])
        self.assertEqual(empty["top_category"], "N/A")
        self.assertEqual(empty["best_region"], "N/A")
        self.assertEqual(empty["total_sales"], 0)

    def test_forecast_handles_sparse_and_single_month_data(self):
        df = self.sample_data()
        forecast = data_handler.get_sales_forecast(df)
        self.assertIsInstance(forecast, float)
        self.assertTrue(np.isfinite(forecast))
        self.assertIsNone(data_handler.get_sales_forecast(df.iloc[:1]))

    def test_empty_dataset_still_builds_charts(self):
        charts = data_handler.get_charts(self.sample_data().iloc[0:0])
        self.assertEqual(set(charts), {
            "trend_chart", "region_chart", "category_chart", "subcat_chart"
        })
        self.assertTrue(all(isinstance(value, str) for value in charts.values()))

    def test_dashboard_route_returns_success(self):
        from app import app
        app.config.update(TESTING=True)
        response = app.test_client().get("/")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
