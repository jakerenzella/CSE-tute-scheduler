from flask import Flask
from flask import request

import csv

from allocate import run_allocate

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


def csv_to_dict(csv):
    headers = csv[0]
    data_rows = csv[1:]

    # Create a list of dictionaries, each representing a row of data
    return [
        {headers[i]: value for i, value in enumerate(row)} for row in data_rows
    ]

# an app/allocate get endpoint which accepts two .csv files and returns a json response
@app.route("/allocate", methods=["POST"])
def allocate():

    timetable_csv = request.get_json().get("timetable")
    preferences_csv = request.get_json().get("preferences")

    timetable = csv_to_dict(timetable_csv)
    preferences = csv_to_dict(preferences_csv)

    print(preferences)

    print(timetable)

    return run_allocate("comp1511", preferences, timetable)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
