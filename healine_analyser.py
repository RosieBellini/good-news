# AUTHOR:       Daniel Welsh
# CREATED:      15/01/2017
# DESCRIPTION:
#               A python script that pulls headlines from popular news sites using the
#               NewsAPI (http://www.newsapi.org) api and performs semantic analysis
#               with vaderSentiment to show the most positive and most negative
#               headlines at the current time.

import json
import urllib.request

import dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Data-type for a headline
class Headline(object):
    headline = ""
    link = ""
    semantic_value = 0.0
    origin = ""
    datetime = ""
    hashcode = 0

    def __str__(self, *args, **kwargs):
        return "{: <120} {: <10} {: <25} {: <180} {: <25}".format(self.headline, str(self.semantic_value), self.origin,
                                                                  self.link, str(self.datetime))

    def __hash__(self, *args, **kwargs):
        base = 37
        base *= hash(self.headline)
        base *= hash(self.link)
        base *= hash(self.semantic_value)
        base *= hash(self.origin)
        base *= hash(self.datetime)

        return base

    def __init__(self, headline, link, semantic_value, origin, datetime):
        self.headline = headline
        self.link = link
        self.semantic_value = semantic_value
        self.origin = origin
        self.datetime = datetime
        self.hashcode = hash(self)


# Performs semantic analysis on the headline and saves as Headline data-type
# PARAMS:   array of headlines, array items = [headline, link, origin, and date published]
# RETURNS:  array of Headlines
def analyze_headlines(blocks):
    analyzer = SentimentIntensityAnalyzer()
    headlines = []

    for block in blocks:
        vs = analyzer.polarity_scores(block[0])
        h = Headline(block[0], block[1], vs['compound'], block[2], block[3])
        headlines.append(h)

    return headlines


# Gets headlines from http://www.newsapi.org
# PARAMS:   url - string
# RETURNS:  array of headlines, array items = [headline, link, origin, and date published]
def get_headlines(url):
    headlines = []

    url += dotenv.get('API_KEY', 'no-key')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req).read()
    r = json.loads(response)

    for re in r['articles']:
        headlines.append([re['title'], re['url'], r['source'], str(re['publishedAt'])])

    return headlines


# Prints and formats headlines
# PARAMS:   Headlines[]
def print_results(headlines):
    print("{:-<359}".format('-'))
    print("{: <120} {: <10} {: <25} {: <180} {: <25}".format('Headline', 'Semantic', 'Origin', 'Link', 'Date-Time'))
    print("{:-<359}".format('-'))

    i = 0
    idx = 0
    l_idx = 0
    highest = 0.0
    lowest = 0.0
    cumulative_sentiment = 0.0
    for h in headlines:
        print(str(h))

        if float(h.semantic_value) > highest:
            highest = float(h.semantic_value)
            idx = i

        if lowest > float(h.semantic_value):
            lowest = float(h.semantic_value)
            l_idx = i

        cumulative_sentiment += float(h.semantic_value)

        i += 1

    print('\n')

    print("{:-<359}".format('-'))

    print('Total headlines analysed: ' + str(len(headlines)))
    print('Cumulative Sentiment:     ' + str(cumulative_sentiment))

    print('\nThe most positive article of the day is:')
    print(str(headlines[idx]))

    print('\nThe most negative article of the day is:')
    print(str(headlines[l_idx]))


raw_headlines = []
dotenv.load()
key = dotenv.get('API_KEY', 'no key')

urls = \
    [
        'https://newsapi.org/v1/articles?source=bbc-news&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=cnn&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=daily-mail&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=independent&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=the-guardian-uk&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=the-new-york-times&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=the-telegraph&sortBy=top&apiKey='
    ]

for url in urls:
    lines = get_headlines(url)
    raw_headlines.extend(lines)

all_headlines = analyze_headlines(raw_headlines)

print_results(all_headlines)
