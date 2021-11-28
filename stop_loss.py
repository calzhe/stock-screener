import requests

ticker = input('Ticker: ').upper()
API_KEY = 'SH4ECUDU6EDKPWY4'

url = f'https://www.alphavantage.co/query?function=ATR&symbol={ticker}&interval=5min&time_period=14&apikey={API_KEY}'
print(url)
r = requests.get(url)
data = r.json()

print(data['Technical Analysis: ATR']['2021-11-19 20:00'])
