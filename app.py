# AUTHOR: Daniel
# Welsh, d.welsh @ ncl.ac.uk
# DATE:   19 / 01 / 2017
# DESCRIPTION:
# -   Flask server to handle incoming headlines, write to database, and display headlines.

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World'


if __name__ == '__main__':
    app.run()
