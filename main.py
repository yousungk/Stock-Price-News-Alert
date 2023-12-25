import os
import requests
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from twilio.rest import Client

# INPUT SETTINGS
STOCK = "TSLA"  # (1) input the ticker of the stock you want to be alerted on
COMPANY_NAME = "Tesla Inc"  # (2) input full name of company for news article search
RECIPIENT_NUMBER = os.environ.get("MY_NUMBER")  # (3) input recipient phone number
SENDER_NUMBER = os.environ.get("TWILIO_NUMBER")

# API SETTINGS
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = os.environ.get("STOCK_API_KEY")

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

# TODAY AND YESTERDAY DATE
today_date = dt.now().date()
yesterday_date = dt.now() - relativedelta(days=1)
yesterday_date = yesterday_date.date()


# FUNCTION TO RETRIEVE NEWS DATA
# get US news from yesterday and today
def fetch_news():
    parameters = {
        "apiKey": NEWS_API_KEY,
        "q": COMPANY_NAME,
        "language": "en",
        "sortBy": "popularity"
    }
    response = requests.get(url=NEWS_ENDPOINT, params=parameters)
    response.raise_for_status()
    articles = response.json()["articles"]
    top_three = articles[:3]
    return top_three


# FUNCTION TO CHECK IF STOCK PRICE CHANGED BY 5%
def check_market():
    stock_parameters = {
        "apikey": STOCK_API_KEY,
        "symbol": STOCK,
        "function": "TIME_SERIES_DAILY",
    }
    stock_response = requests.get(url=STOCK_ENDPOINT, params=stock_parameters)
    stock_response.raise_for_status()
    stock_data = stock_response.json()["Time Series (Daily)"]
    prices = [value for key, value in stock_data.items()]
    d0price = float(prices[0]["4. close"])
    d1price = float(prices[1]["4. close"])
    return abs(d0price - d1price) / d1price


# FUNCTION TO SEND SMS
def send_alert(top_three, diff):
    context = [f"{STOCK}: {diff * 100}%\nHeadline: {article['title']}\nBrief: {article['description']}" for article in
               top_three]
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    for i in context:
        message = client.messages.create(
            body=i,
            from_=os.environ.get("TWILIO_NUMBER"),
            to=RECIPIENT_NUMBER)
        print(message.status)


diff = check_market()
if diff > 0.05:
    top_three = fetch_news()
    send_alert(top_three, diff)
