"""
Stock portfolio suggestion web application with stock data API.

This program pulls stock data through IEX Group, Inc.'s  API.

Reference: “Data provided for free by IEX.” @ https://iextrading.com/developer/
"""

# Import Flask packages
import requests
from flask import Flask, render_template, request


# Define an instance of Flask object
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)


""" Hard-code stocks for investment strategies (can modify later) """

# Testing with just one stock for now
ethical_investing = ["TSLA", "AAPL", "ADBE"]
growth_investing = ["OXLC", "ECC", "AMD"]
index_investing = ["VOO", "VTI", "ILTB"]
quality_investing = ["NVDA", "MU", "CSCO"]
value_investing = ["INTC", "BABA", "GE"]


def get_stock_quote(stock_list):
    """Function that calls IEX stock API for stock information"""

    # Define filter to specify what parameters to extract from API
    param_filter = '?filter=companyName,latestPrice'

    # List of stock quotes (JSON format) pulled from IEX API
    stock_quote = []

    # Loop through and get stock information for every stock in the list
    for ticker in stock_list:
        # HTTP GET request to the IEX stock API
        resp = requests.get(
            'https://api.iextrading.com/1.0/stock/{}/realtime-update/{}'.format(ticker, param_filter))

        # Status Code
        status_code = resp.status_code
        success = True

        # Check for error in response
        if resp.status_code != 200:
            # Error calling API (add some feature to handle errors)
            success = False
        else:
            # Get stock JSON data
            stock_quote.append(resp.json()["quote"])

    return stock_quote

# Defines the routes and view function


@app.route('/submit', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def suggestion_engine():
    # If a POST request is coming through to send route --> process information
    if request.method == 'POST':

        """ Retrieve inputs given to form and store in variables after user submits form (POST request) """

        # Input dollar amount to invest in USD (minimum is $5000 USD)
        investment_amount = float(request.form['inv_amt'])

        # Investment strategies (pick one or two)
        strategy1 = (request.form['strategy1'])
        strategy2 = (request.form['strategy2'])
        two_strategies = 1
        if strategy1 == strategy2:
            return render_template('index.html')

        # Lists to hold both investment strategies and their stock quotes
        strategies = [strategy1, strategy2]

        # Stock quote
        stock_quote = []
        weekly_trend = []

        """ Process user inputs to pull stock quotes """

        # User can either give 1 or 2 investment strategies
        for x in strategies:
            if x == "Ethical Investing":
                stock_quote.append(get_stock_quote(ethical_investing))
                weekly_trend.append(get_week_trend(ethical_investing))
            elif x == "Growth Investing":
                stock_quote.append(get_stock_quote(growth_investing))
                weekly_trend.append(get_week_trend(growth_investing))
            elif x == "Index Investing":
                stock_quote.append(get_stock_quote(index_investing))
                weekly_trend.append(get_week_trend(index_investing))
            elif x == "Quality Investing":
                stock_quote.append(get_stock_quote(quality_investing))
                weekly_trend.append(get_week_trend(quality_investing))
            elif x == "Value Investing":
                stock_quote.append(get_stock_quote(value_investing))
                weekly_trend.append(get_week_trend(value_investing))
            elif x == "None":
                """Only one investment strategy wanted"""
                # do something to process only one investing strategy
                two_strategies = 0

        # Lists to hold stock information for strategy 1
        stock_name1 = []
        current_price1 = []
        last_five1 = []

        i = 0
        # Investment strategy 1
        for stock in stock_quote[0]:
            stock_name1.append(stock['companyName'])
            current_price1.append(stock['latestPrice'])
            st = str(weekly_trend[0][i])
            st = st.replace("'", "")
            st = st.replace("{", "")
            st = st.replace("}", "")
            last_five1.append(st)
            i += 1

        # Lists to hold stock information for strategy 2
        stock_name2 = []
        current_price2 = []
        last_five2 = []

        j = 0
        # Investment strategy 2 -- only needed if user specified a second investment strategy
        if two_strategies == 1:
            for stock in stock_quote[1]:
                stock_name2.append(stock['companyName'])
                current_price2.append(stock['latestPrice'])
                st = str(weekly_trend[1][j])
                st = st.replace("'", "")
                st = st.replace("{", "")
                st = st.replace("}", "")
                last_five2.append(st)
                j += 1

        # Divide investment_amount to each stock (can implement smarter partitions later on)
        amt1 = investment_amount*0.2
        amt2 = investment_amount*0.5
        amt3 = investment_amount*0.3

        return render_template('report.html', two_strategies=two_strategies, inv_amt=investment_amount,
                               strategy1=strategy1, strategy2=strategy2, stock_name1=stock_name1,
                               current_price1=current_price1, stock_name2=stock_name2, current_price2=current_price2,
                               last_five1=last_five1, last_five2=last_five2, amt1=amt1, amt2=amt2, amt3=amt3)

    # If not POST request, it is a GET request. Return render_template: 'index.html'
    return render_template('index.html')


def get_week_trend(strategy):

    weekly_trend = []

    base_url = 'https://financialmodelingprep.com/api/v3/historical-price-full/'
    apikey = "?apikey=b3e4a07d35011e4506ad3cb9e7e73453"

    for ticker in strategy:
        response = requests.get(base_url + ticker + apikey)
        if response.status_code != 200:
            Exception("API Error")
        response_json = response.json()
        ticker = response_json['symbol']

        historical = response_json["historical"]

        i = 0
        ticker_week = {}
        for his in historical:
            ticker_week[his["date"]] = his["close"]
            i += 1
            if i > 4:
                break

        weekly_trend.append(ticker_week)
    return weekly_trend


if __name__ == "__main__":
    app.run()
