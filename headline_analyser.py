# AUTHOR:       Daniel Welsh
# CREATED:      15/01/2017
# DESCRIPTION:
#               A python script that pulls headlines from popular news sites using the
#               NewsAPI (http://www.newsapi.org) api and performs semantic analysis
#               with vaderSentiment to show the most positive and most negative
#               headlines at the current time.

import hashlib
import json
import urllib.request
from datetime import datetime
from json import JSONEncoder

import dotenv
import pymysql
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

pymysql.install_as_MySQLdb()
import MySQLdb


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class Headline(object):
    headline = ""
    link = ""
    semantic_value = 0.0
    origin = ""
    datetime = ""
    neg = 0.0
    pos = 0.0
    neu = 0.0

    def __str__(self, *args, **kwargs):
        return "{: <120} {: <10} {: <25} {: <180} {: <25}".format(self.headline, str(self.semantic_value), self.origin,
                                                                  self.link, str(self.datetime))

    def __hash__(self, *args, **kwargs):

        string = "{: <120} {: <10} {: <25} {: <180} {: <10} {: <10} {: <10}".format(self.headline,
                                                                                    str(self.semantic_value),
                                                                                    self.origin, self.link,
                                                                                    str(self.pos), str(self.neg),
                                                                                    str(self.neu))

        return hash(string)

    def sha256(self):
        string = "{: <120} {: <10} {: <25} {: <180} {: <10} {: <10} {: <10}".format(self.headline,
                                                                                    str(self.semantic_value),
                                                                                    self.origin, self.link,
                                                                                    str(self.pos), str(self.neg),
                                                                                    str(self.neu))

        hash_object = hashlib.sha256(bytes(string, 'utf-8'))
        hex_dig = hash_object.hexdigest()

        return hex_dig

    # FROM: http://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
    def default(self, o):
        try:
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)

    def __init__(self, headline, link, origin, datetime):
        self.headline = headline
        self.link = link
        # self.semantic_value = semantic_value
        self.origin = origin
        self.datetime = datetime
        # self.pos = pos
        # self.neg = neg
        # self.neu = neu


# Performs semantic analysis on the headline and saves as Headline data-type
# PARAMS:   array of headlines, array items = [headline, link, origin, and date published]
# RETURNS:  array of Headlines
def analyze_headlines(blocks):
    analyzer = SentimentIntensityAnalyzer()
    headlines = []

    for block in blocks:

        vs = analyzer.polarity_scores(block.headline)

        block.semantic_value = vs['compound']
        block.pos = vs['pos']
        block.neg = vs['neg']
        block.neu = vs['neu']

        headlines.append(block)

    return headlines


# Gets headlines from http://www.newsapi.org
# PARAMS:   url - string
# RETURNS:  array of headlines, array items = [headline, link, origin, and date published]
def get_headlines(url):
    headlines = []

    url += dotenv.get('API_KEY', 'no-key')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req).read().decode('utf8')
    r = json.loads(response)

    prev_published_at = str(datetime.now()).split(" ")[0]

    for re in r['articles']:

        if str(re['publishedAt']) == 'None':
            published_at = prev_published_at
        else:
            published_at = "" + str(re['publishedAt']).split('T')[0]
            prev_published_at = published_at

        h = Headline(re['title'].split('\n')[0], re['url'], r['source'], published_at)
        headlines.append(h)

    return headlines


def post_data(headlines):
    json_headlines = []

    print(type(headlines[0]))
    for h in headlines:
        line = {
            "headline": h.headline,
            "link": h.link,
            "sentiment": str(h.semantic_value),
            "origin": h.origin,
            "hashcode": h.sha256(),
            "datetime": h.datetime
        }
        json_headlines.append(line)

    data = {
        'headlines': json_headlines
    }

    print(data['headlines'])

    url = 'http://127.0.0.1:5000/headlines/save'

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(url, json.dumps(data), headers=headers)

    return response


def save_to_db(headlines):
    db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_password, db=database,
                         charset='utf8')  # name of the data base

    cur = db.cursor()
    cur.execute('SET NAMES utf8;')
    cur.execute('SET CHARACTER SET utf8;')
    cur.execute('SET character_set_connection=utf8;')

    sql = "INSERT INTO headlines (headline, link, origin, semantic_value, hashcode, published_at, pos, neg, neu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    for h in headlines:
        print("Added Headline:\t" + h.sha256())
        try:
            cur.execute(sql,
                        (h.headline, h.link, h.origin, h.semantic_value, h.sha256(), h.datetime, h.pos, h.neg, h.neu))
        except pymysql.err.IntegrityError as e:
            print("ERROR: {}".format(e))
            continue
        db.commit()

    db.close()


def print_to_file(headlines):
    f = open('headlines.txt', 'w')

    f.write("{:-<359}".format('-') + '\n')
    f.write("{: <120} {: <10} {: <25} {: <180} {: <25}".format('Headline', 'Semantic', 'Origin', 'Link',
                                                               'Date-Time') + '\n')
    f.write("{:-<359}".format('-') + '\n')

    i = 0
    idx = 0
    l_idx = 0
    highest = 0.0
    lowest = 0.0
    cumulative_sentiment = 0.0
    for h in headlines:
        f.write(str(h) + '\n')

        if float(h.semantic_value) > highest:
            highest = float(h.semantic_value)
            idx = i

        if lowest > float(h.semantic_value):
            lowest = float(h.semantic_value)
            l_idx = i

        cumulative_sentiment += float(h.semantic_value)

        i += 1

    f.write('\n')

    f.write("{:-<359}".format('-') + '\n')

    f.write('Total headlines analysed: ' + str(len(headlines)) + '\n')
    f.write('Cumulative Sentiment:     ' + str(cumulative_sentiment) + '\n')

    f.write('\nThe most positive article of the day is:' + '\n')
    f.write(str(headlines[idx]) + '\n')

    f.write('\nThe most negative article of the day is:' + '\n')
    f.write(str(headlines[l_idx]) + '\n')


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
database = dotenv.get('DATABASE', 'no database')
db_user = dotenv.get('DB_USER', 'no user')
db_password = dotenv.get('DB_PASSWORD', 'no password')
db_host = dotenv.get('DB_HOST', 'no host')

urls = \
    [
        'https://newsapi.org/v1/articles?source=bbc-news&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=cnn&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=daily-mail&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=independent&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=the-guardian-uk&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=the-new-york-times&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=the-telegraph&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=the-economist&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=the-huffington-post&sortBy=top&apiKey=',
        'https://newsapi.org/v1/articles?source=national-geographic&sortBy=top&apiKey=',
    ]

for url in urls:
    lines = get_headlines(url)
    raw_headlines.extend(lines)

all_headlines = analyze_headlines(raw_headlines)

print_results(all_headlines)
save_to_db(all_headlines)
