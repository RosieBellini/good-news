# AUTHOR: Daniel
# Welsh, d.welsh @ ncl.ac.uk
# DATE:   19 / 01 / 2017
# DESCRIPTION:
# -   Flask server to handle incoming headlines, write to database, and display headlines.

import math
import calendar
import dotenv
import pymysql

from flask import Flask, render_template
from datetime import timedelta, date

pymysql.install_as_MySQLdb()
import MySQLdb


def date_to_text(date):
    d = date.split('-')
    year = ""
    month = ""
    day = ""

    if d[2] == 1 or d[2] == 21 or d[2] == 31:
        day = "" + str(d[2]) + "st"
    elif d[2] == 2 or d[2] == 22:
        day = "" + str(d[2]) + "nd"
    elif d[2] == 3 or d[2] == 23:
        day = "" + str(d[2]) + "rd"
    else:
        day = "" + str(d[2]) + "th"

    month = calendar.month_name[int(d[1])]
    year = str(d[0])

    return "on the " + day + " of " + month + ", " + year


app = Flask(__name__, static_url_path='/static')
dotenv.load()
database = dotenv.get('DATABASE', 'no database')
db_user = dotenv.get('DB_USER', 'no user')
db_password = dotenv.get('DB_PASSWORD', 'no password')
db_host = dotenv.get('DB_HOST', 'no host')

db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_password, db=database,
                     charset='utf8')  # name of the data base

cur = db.cursor()
cur.execute('SET NAMES utf8;')
cur.execute('SET CHARACTER SET utf8;')
cur.execute('SET character_set_connection=utf8;')


@app.route('/')
def hello_world():
    global cur

    back_date = date.today() + timedelta(days=-2)

    cur.execute(
        'SELECT headline, link, origin, semantic_value, published_at, id FROM headlines WHERE published_at BETWEEN \'%s\' AND now() ORDER BY semantic_value DESC LIMIT 10' %back_date)

    pos_headlines = []
    for row in cur.fetchall():
        pos_headlines.append([row[0], row[1], row[2], "%.0f" % abs(float(row[3] * 100)) + "%", date_to_text(str(row[4])), row[5]])

    cur.execute(
        'SELECT headline, link, origin, semantic_value, published_at, id FROM headlines WHERE published_at BETWEEN \'%s\' AND now() ORDER BY semantic_value ASC LIMIT 10' %back_date)

    neg_headlines = []
    for row in cur.fetchall():
        neg_headlines.append([row[0], row[1], row[2], "%.0f" % abs(float(row[3] * 100)) + "%", date_to_text(str(row[4])), row[5]])

    return render_template('index.html', pos_headlines=pos_headlines, neg_headlines=neg_headlines)


if __name__ == '__main__':
    app.run()
