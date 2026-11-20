import os

from flask import Flask, render_template

import data_handler


app = Flask(__name__)


@app.route("/")
def dashboard():
    try:
        df = data_handler.load_and_clean_data()
        kpis = data_handler.get_kpis(df)
        charts = data_handler.get_charts(df)
        forecast = data_handler.get_sales_forecast(df)
        return render_template(
            "index.html",
            kpis=kpis,
            charts=charts,
            forecast=forecast,
        )
    except (FileNotFoundError, ValueError):
        app.logger.exception("Store Analytics could not load a valid sales dataset")
        return (
            "The dashboard data is unavailable or invalid. "
            "Check data/store_sales.csv and the application logs.",
            500,
        )
    except Exception:
        app.logger.exception("Store Analytics dashboard failed")
        return "The dashboard could not be generated. Check the application logs.", 500


if __name__ == "__main__":
    app.run(
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
        port=int(os.environ.get("PORT", 5000)),
    )
