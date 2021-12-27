from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import os
from texttable import Texttable
from google.cloud import language_v1

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Documents/certs/serious-case-336420-420fbde15dea.json"

def main():
    ticker = input('Ticker: ').upper()

    finviz_url = f'https://finviz.com/quote.ashx?t={ticker}'

    req = Request(url=finviz_url,headers={'user-agent': 'my-app/0.0.1'}) 
    response = urlopen(req)    

    html = BeautifulSoup(response, features="lxml")
    news_table = html.find(id='news-table')
    stock_name = html.find('title').get_text() \
        .split(',')[0] \
        .split('.')[0] \
        .split()[1]
        
    parsed_news = parseNews(news_table, stock_name, ticker)
    overall_sentiment = calculateOverallSentiment(parsed_news[1])

    table_data = [[f'{ticker} ({parsed_news[0]})', 'Confidence Score', 'Sentiment']]
    table_data.extend(parsed_news[1])
    table_data.append(['-','-','-'])
    table_data.append(overall_sentiment)
    
    table = Texttable()
    table.add_rows(table_data)
    table.set_cols_align(['l', 'c', 'c'])
    table.set_deco(Texttable.HEADER | Texttable.BORDER)
    
    print(table.draw())

def parseNews(news_table, stock_name, ticker):
    google_client = language_v1.LanguageServiceClient()
    results = []
    most_recent_date = news_table.find('tr').td.text.split()[0]
    
    for x in news_table.findAll('tr'):
        text = x.a.get_text() 
        date_scrape = x.td.text.split()

        if len(date_scrape) != 1 and date_scrape[0] < most_recent_date and len(results) != 0:
            break
        
        if stock_name.lower() in text.lower() or ticker.lower() in text.lower():
            if len(date_scrape) != 1:
                most_recent_date = date_scrape[0]
                
            document = {"content": text, "type_": language_v1.Document.Type.PLAIN_TEXT, "language": "en"}
            encoding_type = language_v1.EncodingType.UTF8
            response = google_client.analyze_sentiment(request = {'document': document, 'encoding_type': encoding_type})

            score = f'{round(response.document_sentiment.score * 100)} %'
            rating = ''
            if response.document_sentiment.score > 0:
                rating = 'POSITIVE'
            elif response.document_sentiment.score < 0:
                rating = 'NEGATIVE'
            else:
                rating = 'NEUTRAL'

            results.append([text, score, rating])
            
    return [most_recent_date, results]

def calculateOverallSentiment(sentiments):
    positive_count = 0
    negative_count = 0
    
    for sen in sentiments:
        rating = sen[2]
        
        if rating == 'POSITIVE':
            positive_count += 1
        elif rating == 'NEGATIVE':
            negative_count += 1
    
    if positive_count == 0 and negative_count == 0:
        return ['OVERALL', 'N/A', 'N/A']
    
    percent_positive = round(positive_count/(positive_count + negative_count) * 100)
    percent_negative = round(negative_count/(positive_count + negative_count) * 100)
    overall_sentiment = ['OVERALL']
    
    if percent_positive > percent_negative:
        overall_sentiment.append(f'{percent_positive} %')
        overall_sentiment.append('POSITIVE')
    elif percent_positive < percent_negative:
        overall_sentiment.append(f'{percent_negative} %')
        overall_sentiment.append('NEGATIVE')
    else:
        overall_sentiment.append('50 %')
        overall_sentiment.append('NEUTRAL')
    
    return overall_sentiment
    
while True:
    main()