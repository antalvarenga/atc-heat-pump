from flask import Flask, jsonify, request
from flask import url_for
from hackaton import get_data_from_multiple_days, get_data_from_month, get_data_from_week, get_temperature_array, get_energy_array, calculateWeights, OptimizeCost, create_json_object
from scipy.optimize import linprog


app = Flask(__name__)

@app.route('/')
def index():
    return 'index2'

@app.route("/optimizeDaily")
def optimizeDaily():
    #PRINT KWAJALIKWARGS OF linprog
    print(linprog.__doc__)

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    print(start_date)
    print(end_date)

    results = get_data_from_multiple_days(start_date, end_date)
    json_object = create_json_object(results, start_date)
    return jsonify(json_object)


with app.test_request_context():
    print(url_for('index'))