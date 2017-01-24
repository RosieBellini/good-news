# AUTHOR: Daniel
# Welsh, d.welsh @ ncl.ac.uk
# DATE:   19 / 01 / 2017
# DESCRIPTION:
# -   Flask server to handle incoming headlines, write to database, and display headlines.

import urllib.request
import json
import dotenv
from flask import Flask
from flask import request

import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

app = Flask(__name__)
dotenv.load()
database = dotenv.get('DATABASE', 'no db')
user = dotenv.get('DB_USER', 'no user')
password = dotenv.get('DB_PASSWORD', 'no password')

@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/headlines/save', methods=['POST'])
def save_headlines():
    content = request.data
    content = bytes.decode(content)
    json_content = json.loads(content)

    headlines = json_content['headlines']
    # for h in headlines:
    #     print(h)

    db = MySQLdb.connect(host="localhost", user=user, passwd=password, db=database, charset='utf8')  # name of the data base

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor()
    cur.execute('SET NAMES utf8;')
    cur.execute('SET CHARACTER SET utf8;')
    cur.execute('SET character_set_connection=utf8;')

    # Use all the SQL you like
    cur.execute("SELECT * FROM headlines")

    # print all the first cell of all the rows
    for row in cur.fetchall():
        print(row[0])

    sql = "INSERT INTO headlines (headline, link, origin, semantic_value, hashcode, datetime) VALUES (%s, %s, %s, %s, %s, %s)"
    for h in headlines:
        print("HASH:\t" + h['hashcode'])
        cur.execute(sql, (h['headline'], h['link'], h['origin'], h["sentiment"], h['hashcode'], h['datetime']))
        db.commit()

    db.close()

    return content


if __name__ == '__main__':
    app.run()
