import requests
import flair
import pandas as pd

BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAHhYWAEAAAAAiXCCEI39aVn7Np4%2BXG1%2FMmr91pk%3DiEPbu7aZPu5FOOZrM7VRuJxhrWcRZpU4uzYLOmexmoPBUyZHEl'
params = {
    'query': 'from:TwitterDev',
    'tweet.field': 'created_at',
    'expansions': 'author_id',
    'user.fields': 'description'
}

ticker = input('Ticker Name: ')

response = requests.get(
    f'https://api.twitter.com/2/tweets/search/recent?query={ticker}&tweet.fields=created_at&expansions=author_id&user.fields=created_at',
    headers = {
        'authorization': 'Bearer '+BEARER_TOKEN
    }
)

tweets = pd.DataFrame()

for tweet in response.json()['data']:
    row = {
        'id': tweet['id'],
        'created_at': tweet['created_at'],
        'text': tweet['text']
    }
    tweets = tweets.append(row, ignore_index=True)

sentiment_model = flair.models.TextClassifier.load('en-sentiment')
probs = []
sentiments = []

for tweet in tweets['text'].to_list():
    sentence = flair.data.Sentence(tweet)
    sentiment_model.predict(sentence)
    # extract sentiment prediction
    probs.append(sentence.labels[0].score)  # numerical score 0-1
    sentiments.append(sentence.labels[0].value)  # 'POSITIVE' or 'NEGATIVE'
    
tweets['probability'] = probs
tweets['sentiment'] = sentiments

print(tweets)