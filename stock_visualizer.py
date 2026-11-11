import os
import time
import requests
import pygal

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def get_data(symbol, function):
    """Retrieve stock information from Alpha Vantage."""

    api_key = os.environ.get("API_KEY")

    if not api_key:
        raise ValueError("API key not found. Check your .env file.")

    url = "https://www.alphavantage.co/query"

    params = {
        "function": function,
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "compact"
    }

    if function == "TIME_SERIES_INTRADAY":
        params["interval"] = "60min"

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

    except requests.RequestException:
        raise ValueError("Could not connect to Alpha Vantage.")

    if "Error Message" in data:
        raise ValueError("Invalid stock symbol.")

    if "Note" in data or "Information" in data:
        message = data.get("Note") or data.get("Information")
        raise ValueError(f"Alpha Vantage API message: {message}")

    for key, value in data.items():
        if "Time Series" in key:
            return value

    raise ValueError("No stock data was returned by the API.")


def make_chart(symbol, data, chart_type, start, end):
    """Generate a stock chart for the selected date range."""

    dates = []
    opens = []
    highs = []
    lows = []
    closes = []

    for date in sorted(data.keys()):

        day = datetime.strptime(date[:10], "%Y-%m-%d").date()

        if start <= day <= end:
            dates.append(date)

            opens.append(float(data[date]["1. open"]))
            highs.append(float(data[date]["2. high"]))
            lows.append(float(data[date]["3. low"]))
            closes.append(float(data[date]["4. close"]))

    if not dates:
        raise ValueError("No stock data was found for those dates.")

    if chart_type == "bar":
        chart = pygal.Bar(x_label_rotation=45)
    else:
        chart = pygal.Line(x_label_rotation=45)

    chart.title = (
        f"Stock Data for {symbol}: {start} to {end}"
    )

    chart.x_labels = dates
    chart.x_labels_major_count = 10
    chart.show_minor_x_labels = False

    chart.add("Open", opens)
    chart.add("High", highs)
    chart.add("Low", lows)
    chart.add("Close", closes)

    # Return the chart as an embedded SVG instead of opening another window.
    return chart.render_data_uri()


def show_stock_chart(symbol, chart_type, function, start, end):
    """Retrieve stock data and generate the chart."""

    data = get_data(symbol.upper(), function)

    return make_chart(
        symbol.upper(),
        data,
        chart_type,
        start,
        end
    )
