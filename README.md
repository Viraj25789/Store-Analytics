# Store Analytics Dashboard

A small Flask + Pandas analytics dashboard that turns a store sales CSV into business KPIs, monthly trends, regional profit comparisons, category mix, and a simple next-month trend estimate.

## Dashboard metrics

- **Total sales:** sum of the Sales column.
- **Total profit:** sum of the Profit column.
- **Average profit margin:** total profit divided by total sales.
- **Average order value:** total sales divided by the number of valid rows/orders.
- **Top category:** category with the highest total sales.
- **Best region:** region with the highest total profit.
- **Latest month sales:** sales in the latest calendar month present in the dataset.
- **Month-over-month growth:** latest month compared with the immediately preceding calendar month; missing months are treated as zero sales.
- **Next-month trend estimate:** a simple linear trend fitted to monthly sales history. This is an illustrative baseline, not a production forecasting model.

## Visualizations

- Monthly sales trend
- Profit by region
- Sales distribution by category
- Top five sub-categories by sales

The dashboard also includes a dark-mode toggle and a browser-generated PDF export.

## Technology

Python, Flask, Pandas, NumPy, and Plotly.

## Run locally

Python 3.10+ is recommended.

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies and start the app:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000.

Optional environment variables:

| Variable | Purpose |
|---|---|
| `PORT` | Local server port; defaults to `5000` |
| `FLASK_DEBUG` | Set to `true` only during local debugging |

## Data format

The dashboard reads `data/store_sales.csv`. Required columns:

`Order_ID`, `Date`, `Category`, `Sub_Category`, `Region`, `Sales`, `Quantity`, and `Profit`.

Dates and numeric fields are parsed explicitly. Rows missing required values or containing non-finite numeric measurements are excluded. The dashboard reports a generic error to visitors and writes diagnostic details to the Flask application log.

## Project structure

```text
Store-Analytics/
├── app.py
├── data_handler.py
├── data/
│   └── store_sales.csv
├── templates/
│   └── index.html
├── tests/
│   └── test_data_handler.py
└── requirements.txt
```

## Limitations

- The included CSV is a demonstration dataset; results should not be interpreted as real company performance.
- A row is treated as one order for AOV and order counts.
- The trend estimate is a simple linear baseline. It does not model seasonality, holidays, promotions, or external factors.
- No database or live data ingestion is included; the dashboard reads the local CSV file.
- PDF export depends on browser-side JavaScript libraries and CDN availability.

## Tests

Run:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the same test suite on pushes and pull requests affecting this project.
