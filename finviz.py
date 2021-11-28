from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import pandas as pd
import matplotlib.pyplot as plt
import flair
from prettytable import PrettyTable

sentiment_model = flair.models.TextClassifier.load('en-sentiment')

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

    table = PrettyTable([f'{ticker} ({parsed_news[0]})', 'Confidence Score', 'Sentiment'])
    table.add_rows(parsed_news[1])
    table.add_row(['-','-','-'])
    table.add_row(overall_sentiment)
    
    print(table)

def parseNews(news_table, stock_name, ticker):
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
                
            sentence = flair.data.Sentence(text)
            sentiment_model.predict(sentence)
            rating = sentence.labels[0].value
            score = f'{round(sentence.labels[0].score * 100)} %'
            results.append([text, score, rating])
            
    return [most_recent_date, results]

def calculateOverallSentiment(sentiments):
    positive_count = 0
    negative_count = 0
    
    for sen in sentiments:
        rating = sen[2]
        
        if rating == 'POSITIVE':
            positive_count += 1
        else:
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
    
# # Iterate through the headlines and get the polarity scores using vader
# scores = parsed_and_scored_news['headline'].apply(vader.polarity_scores).tolist()

# # Convert the 'scores' list of dicts into a DataFrame
# scores_df = pd.DataFrame(scores)

# # Join the DataFrames of the news and the list of dicts
# parsed_and_scored_news = parsed_and_scored_news.join(scores_df, rsuffix='_right')

# # Convert the date column from string to datetime
# parsed_and_scored_news['date'] = pd.to_datetime(parsed_and_scored_news.date).dt.date

# plt.rcParams['figure.figsize'] = [10, 6]

# # Group by date and ticker columns from scored_news and calculate the mean
# mean_scores = parsed_and_scored_news.groupby(['ticker','date']).mean()

# # Unstack the column ticker
# mean_scores = mean_scores.unstack()

# # Get the cross-section of compound in the 'columns' axis
# mean_scores = mean_scores.xs('compound', axis="columns").transpose()

# # Plot a bar chart with pandas
# mean_scores.plot(kind = 'bar')
# plt.grid()
# plt.show()