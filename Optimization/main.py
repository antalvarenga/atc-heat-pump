from calendar import month
from flask import Flask, jsonify, request
from flask import url_for
from flask_cors import CORS
from hackaton import get_data_from_multiple_days, getAggratedData_free, create_json_object, simulate_policy_JSON_format_hourly, generate_Standard_Policy, get_DataByDay_accumulatePeriod, get_DataByDay_AccumulatingWeek, simulate_policy_JSON_format_period, getAggratedData_Hourly, getAggratedData_weekly
from scipy.optimize import linprog
from datetime import datetime, timedelta
from thermal_model import get_thermal_model_DataByDay

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


@app.route("/optimizeDaily/free")
def optimizeDaily_daily_granularity():
    """
    Usage: 
        response = requests.get("http://localhost:5000/optimizeDaily/free?start_date=2021-12-01&end_date=2021-12-31")
        response.json()
    """
    

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    json_object = get_DataByDay_accumulatePeriod(start_date, end_date)
    
    
    return jsonify(json_object)


@app.route("/optimizeDaily/weekly")
def optimizeDaily_weekly_granularity():
    """
    Usage: 
        response = requests.get("http://localhost:5010/optimizeDaily/weekly?start_date=2021-12-01&end_date=2021-12-31")
        response.json()
    """
    

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    json_object = get_DataByDay_AccumulatingWeek(start_date, end_date)
    
    
    return jsonify(json_object)
    



@app.route("/standardPolicy/hourly")
def standardPolicy_hourly_granularity():
    """
    Usage: 
        response = requests.get("http://localhost:5010/standardPolicy/hourly?start_date=2021-12-01&end_date=2021-12-31")
        response.json()
    """

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')


    #iterate over all days

    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    #print(start)
    #print(end)
    step = timedelta(days=1)

    results = []

    policy = generate_Standard_Policy()
    while start <= end:
        results.append(simulate_policy_JSON_format_hourly(policy, start.strftime('%Y-%m-%d')))
        start += step


    return jsonify(results)

@app.route("/standardPolicy/free")
def standardPolicy_daily_granularity():
    """
    Usage: 
        response = requests.get("http://localhost:5010/standardPolicy/free?start_date=2021-12-01&end_date=2021-12-31")
        response.json()
    """

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    policy = generate_Standard_Policy()
    
    results = simulate_policy_JSON_format_period(policy, start_date, end_date)


    return jsonify(results)

@app.route("/standardPolicy/weekly")
def standardPolicy_weekly_granularity():
    """
    Usage: 
        response = requests.get("http://localhost:5010/standardPolicy/weekly?start_date=2021-12-01&end_date=2021-12-31")
        response.json()
    """

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    results = getAggratedData_weekly(start_date, end_date)


    return jsonify(results)

with app.test_request_context():
    print(url_for('index'))



@app.route("/aggregated/hourly")
def aggregated_hourly_granularity():
    #both endpoint together
    """
    Usage: 
        response = requests.get("http://localhost:5010/aggregated/hourly?start_date=2021-12-01&end_date=2021-12-31")
        response.json()
    """

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    json_object = getAggratedData_Hourly(start_date, end_date)


    return jsonify(json_object)

with app.test_request_context():
    print(url_for('index'))


@app.route("/aggregated/weekly")
def aggregated_weekly_with_daily_granularity():
    #both endpoint together
    """
    Usage: 
        response = requests.get("http://localhost:5010/aggregated/hourly?start_date=2021-12-01&end_date=2021-12-31")
        response.json()
    """



    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    json_object = getAggratedData_weekly(start_date, end_date)


    return jsonify(json_object)
@app.route("/aggregated/free")
def aggregated_free_with_daily_granularity():
    #both endpoint together
    """
    Usage: 
        response = requests.get("http://localhost:5010/aggregated/hourly?start_date=2021-12-01&end_date=2021-12-31")
        response.json()
    """


    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    json_object = getAggratedData_free(start_date, end_date)


    return jsonify(json_object)

with app.test_request_context():
    print(url_for('index'))


@app.route("/continuousModel/hourly")
def continuous_model():
    """
    Usage: 
        response = requests.get("http://localhost:5010/continuousModel?start_date=2021-12-01&end_date=2021-12-31&storage=True&flexible=True")
        response.json()
    """
    

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    storage = request.args.get('storage') == "True"
    flexible = request.args.get('flexible') == "True"

    json_object = get_thermal_model_DataByDay(start_date, end_date, storage, flexible)
    
    return jsonify(json_object)

