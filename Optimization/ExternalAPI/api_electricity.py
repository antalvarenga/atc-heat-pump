from flask import Flask, jsonify, request
from flask import url_for
from .electricity_prices import read_prices, read_prices_JSON_Format
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    print(start_date)
    print(end_date)
    #transform start_date and end_date into datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')


    results = read_prices_JSON_Format(start_date, end_date)
    #print(type(results))
    return results


