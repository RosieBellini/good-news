# AUTHOR: Daniel
# Welsh, d.welsh @ ncl.ac.uk
# DATE:   19 / 01 / 2017
# DESCRIPTION:
# -   Flask server to handle incoming headlines, write to database, and display headlines.


import json

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

    return content


if __name__ == '__main__':
    app.run()
