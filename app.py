# AUTHOR: Daniel
# Welsh, d.welsh @ ncl.ac.uk
# DATE:   19 / 01 / 2017
# DESCRIPTION:
# -   Flask server to handle incoming headlines, write to database, and display headlines.


import json
import MySQLdb

from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/headlines/save', methods=['POST'])
def save_headlines():
    content = request.data
    json_content = json.loads(content)

    headlines = json_content['headlines']
    for h in headlines:
        print(h)

	db = MySQLdb.connect(host="localhost",  user="root", passwd="pass", db="good_news")        # name of the data base

	# you must create a Cursor object. It will let
	#  you execute all the queries you need
	cur = db.cursor()

	# Use all the SQL you like
	cur.execute("SELECT * good_news")

	# print all the first cell of all the rows
	for row in cur.fetchall():
    		print row[0]

	db.close()

    return content


if __name__ == '__main__':
    app.run()
