import csv
import os

from datetime import datetime
from flask import Flask, render_template, request

from stock_visualizer import show_stock_chart

app = Flask(__name__)


def load_stock_symbols():
    """Read stock symbols from stocks.csv."""

    symbols = []

    try:
        with open("stocks.csv", "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames:
                return []

            # Find the stock symbol column.
            symbol_column = next(
                (
                    column for column in reader.fieldnames
                    if column.strip().lower() in
                    ("symbol", "ticker", "stock symbol", "ticker symbol")
                ),
                None
            )

            if symbol_column is None:
                raise ValueError(
                    "Could not find a Symbol column in stocks.csv."
                )

            for row in reader:
                symbol = (row.get(symbol_column) or "").strip().upper()

                if symbol and symbol not in symbols:
                    symbols.append(symbol)

    except FileNotFoundError:
        raise FileNotFoundError(
            "stocks.csv was not found in the project folder."
        )

    return sorted(symbols)


@app.route("/", methods=["GET", "POST"])
def index():

    chart = None
    error = None

    try:
        symbols = load_stock_symbols()
    except (FileNotFoundError, ValueError) as e:
        symbols = []
        error = str(e)

    if request.method == "POST":

        try:
            symbol = request.form.get("symbol", "").upper()
            chart_type = request.form.get("chart_type")
            time_series = request.form.get("time_series")

            start_date = datetime.strptime(
                request.form.get("start_date", ""),
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                request.form.get("end_date", ""),
                "%Y-%m-%d"
            ).date()

            if symbol not in symbols:
                raise ValueError("Please select a valid stock symbol.")

            if chart_type not in ("bar", "line"):
                raise ValueError("Please select a valid chart type.")

            valid_series = {
                "intraday": "TIME_SERIES_INTRADAY",
                "daily": "TIME_SERIES_DAILY",
                "weekly": "TIME_SERIES_WEEKLY",
                "monthly": "TIME_SERIES_MONTHLY"
            }

            if time_series not in valid_series:
                raise ValueError("Please select a valid time series.")

            if end_date < start_date:
                raise ValueError(
                    "The end date cannot be before the start date."
                )

            chart = show_stock_chart(
                symbol,
                chart_type,
                valid_series[time_series],
                start_date,
                end_date
            )

        except ValueError as e:
            error = str(e)

        except Exception as e:
            error = "Something went wrong while generating the chart: " + str(e)

    return render_template(
        "index.html",
        symbols=symbols,
        chart=chart,
        error=error
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
