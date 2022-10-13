from calendar import month
from flask import Flask, jsonify, request
from flask import url_for
from flask_cors import CORS
from hackaton import get_data_from_multiple_days, get_data_from_month, get_data_from_week, get_temperature_array, get_energy_array, calculateWeights, OptimizeCost, create_json_object, simulate_policy, simulate_policy_JSON_format, generate_Standard_Policy, get_DataByDay
from scipy.optimize import linprog


app = Flask(__name__)
cors = CORS(app, origins=["http://localhost:3000"])

@app.route('/')
def index():
    return 'index2'

@app.route("/optimizeDaily/hourly")
def optimizeDaily():
    """
    Usage: 
        response = requests.get("http://localhost:5000/optimizeDaily/hourly?start_date=2021-12-01&end_date=2021-12-31")
        response.json()
    """
    

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    #print(start_date)
    #print(end_date)

    results = get_data_from_multiple_days(start_date, end_date)
    json_object = create_json_object(results, start_date)
    return jsonify(json_object)


@app.route("/optimizeDaily/daily")
def optimizeDaily_daily_granularity():
    """
    Usage: 
        response = requests.get("http://localhost:5000/optimizeDaily/daily?start_date=2021-12-01&end_date=2021-12-31")
        response.json()
    """
    

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    json_object = get_DataByDay(start_date, end_date)
    
    
    return jsonify(json_object)


@app.route("/optimizeDaily/weekly")
def optimizeDaily_weekly_granularity():
    """
    Usage: 
        response = requests.get("http://localhost:5000/optimizeDaily/weekly?year=2021&month=12")
        response.json()
    """
    

    year = request.args.get('year')
    month = request.args.get('month')

    #json_object = get_DataByDay(start_date, end_date)
    
    
    return 



@app.route("/standardPolicy/hourly")
def standardPolicy():
    """
    Usage: 
        response = requests.get("http://localhost:5000/standardPolicy?start_date=2021-12-01&end_date=2021-12-31")
        response.json()
    """

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')


    #iterate over all days
    from datetime import datetime, timedelta

    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    #print(start)
    #print(end)
    step = timedelta(days=1)

    results = []

    policy = generate_Standard_Policy()
    while start <= end:
        results.append(simulate_policy_JSON_format(policy, start.strftime('%Y-%m-%d')))
        start += step


    return jsonify(results)


with app.test_request_context():
    print(url_for('index'))

