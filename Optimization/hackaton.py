from itertools import accumulate
from scipy.optimize import linprog
import numpy as np
import math
from electricity_prices import read_prices
from datetime import datetime, timedelta
import json
import pandas as pd
import requests


#Global variables
CONFORT_PROVIDED_MODE_ECO=4
CONFORT_PROVIDED_MODE_CONFORT=8


#Table values (should be global vars)
MODE_OFF_CONSUMPTION = 1

MODE_ECO_CONSUMPTION_TEMPERATURE_LOWER_10 = 1.6
MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20 = 0.8
MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_20 = 0.4

MODE_CONFORT_CONSUMPTION_TEMPERATURE_LOWER_0 = 2.4+9
MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_0_LOWER_10 = 2.4
MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20 = 1.6
MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_20 = 0.8




def OptimizeCost(Weights, costs, consumptionForEachWeight, temperature_array, minumum_confort_score=124):
    """inputs:
    Weights: list of weights for each hour
    contraints: list of contraints
    bounds: list of bounds
    integrality: 1 : Integer variable; decision variable must be an integer within bounds."""
    #Optimize cost
    #weights

    #contraints
    lhs_eq = [[1, 1, 1]+[0]*69, [0]*3+[1]*3+[0]*66, [0]*6+[1]*3+[0]*63, [0]*9+[1]*3+[0]*60, [0]*12+[1]*3+[0]*57, [0]*15+[1]*3+[0]*54, [0]*18+[1]*3+[0]*51, [0]*21+[1]*3+[0]*48, [0]*24+[1]*3+[0]*45, [0]*27+[1]*3+[0]*42, [0]*30+[1]*3+[0]*39, [0]*33+[1]*3+[0]*36, [0]*36+[1]*3+[0]*33, [0]*39+[1]*3+[0]*30, [0]*42+[1]*3+[0]*27, [0]*45+[1]*3+[0]*24, [0]*48+[1]*3+[0]*21, [0]*51+[1]*3+[0]*18, [0]*54+[1]*3+[0]*15, [0]*57+[1]*3+[0]*12, [0]*60+[1]*3+[0]*9, [0]*63+[1]*3+[0]*6, [0]*66+[1]*3+[0]*3, [0]*69+[1]*3]
    rhs_eq = [1]*24

    #lhs_ineq = [[0, -4, -8, 0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8]]
    lhs_ineq = [[0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT, 0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT,0, -CONFORT_PROVIDED_MODE_ECO, -CONFORT_PROVIDED_MODE_CONFORT]]
    
    rhs_ineq = [-minumum_confort_score]

    bounds = [(0,1) for i in range(72)]
    integrality = [1 for i in range(72)]

    opt = linprog(c=Weights, A_ub=lhs_ineq, b_ub=rhs_ineq,
              A_eq=lhs_eq, b_eq=rhs_eq, bounds=bounds, integrality=integrality,
              method="highs")

    cost = np.dot(opt['x'], costs)

    #find if its eco, off or conf and conver to string 
    policy = np.array(opt['x']).reshape(24,3).argmax(axis=1)
    #convert array number to off, eco or confort
    policy = np.vectorize(lambda x: 'off' if x == 0 else 'eco' if x == 1 else 'conf')(policy)
    
    #cost = opt['fun']
    
    #comfort score accumulated across the day
    accumulated_comfort_score = [CONFORT_PROVIDED_MODE_CONFORT if policy[i] == 'conf' else CONFORT_PROVIDED_MODE_ECO if policy[i] == 'eco' else 0 for i in range(24)]
    for i in range(1,24):
        accumulated_comfort_score[i] = accumulated_comfort_score[i-1]+accumulated_comfort_score[i]
    
    confort_score = accumulated_comfort_score[-1]
    #cost accumulated across the day
    #need to check weights and see which are active

    #Consumo energético atual e acumulado -> weights
    accumulated_cost = []
    accumulated_comsumption = []
    weights_count = 0
    for mode in policy:
        if mode == 'conf':
            accumulated_cost.append(Weights[2+weights_count])
            accumulated_comsumption.append(consumptionForEachWeight[2+weights_count])
        elif mode == 'eco':
            accumulated_cost.append(Weights[1+weights_count])
            accumulated_comsumption.append(consumptionForEachWeight[1+weights_count])
        else:
            accumulated_cost.append(Weights[weights_count])
            accumulated_comsumption.append(consumptionForEachWeight[weights_count])
        weights_count += 3
    atual_cost= accumulated_cost.copy()
    atual_comsumption= accumulated_comsumption.copy()
    for i in range(1,24):
        accumulated_cost[i] = accumulated_cost[i-1]+accumulated_cost[i]
        accumulated_comsumption[i] = accumulated_comsumption[i-1]+accumulated_comsumption[i]

    #Comsumption accumulated across the day
    # receives the consumption for each weight
       

    return policy, cost, confort_score, accumulated_comfort_score, atual_cost, accumulated_cost, atual_comsumption, accumulated_comsumption, temperature_array

def calculateWeights(temperature_array, energy_cost_array, confort_score_coef=0):
    #confort_score_coef is bassicaly the amount of money you are willing to pay for 1 point extra confort
    #Temperature array is the temperature for each hour of the day
    #Energy cost array is the cost of energy for each hour of the day


    #calculate the weights for each hour
    weights = []
    comsumption = []
    cost = []
    modes = ['off', 'eco', 'conf']
    for i in range(len(temperature_array)):
        for mode in modes:
            external_temp = temperature_array[i]
            if mode == 'off':
                #1KW/hour regardless of temperature
                weights.append(energy_cost_array[i]*MODE_OFF_CONSUMPTION-(confort_score_coef*0))
                comsumption.append(MODE_OFF_CONSUMPTION)
                cost.append(energy_cost_array[i]*MODE_OFF_CONSUMPTION)
            elif mode == 'eco':
                if external_temp < 10:
                    #1.6KW/hour
                    weights.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_LOWER_10-(confort_score_coef*4))
                    comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_LOWER_10)
                    cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_LOWER_10)
                elif external_temp >= 10 and external_temp <= 20:
                    #0.8KW/hour
                    weights.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20-(confort_score_coef*4))
                    comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                    cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                elif external_temp > 20:
                    #0.4KW/hour
                    weights.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_20-(confort_score_coef*4))
                    comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_20)
                    cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_20)
            elif mode == 'conf':

                if external_temp < 0:
                    #2.4KW/hour+9KW/hour
                    weights.append(energy_cost_array[i]*(MODE_CONFORT_CONSUMPTION_TEMPERATURE_LOWER_0)-(confort_score_coef*8))
                    comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_LOWER_0)
                    cost.append(energy_cost_array[i]*(MODE_CONFORT_CONSUMPTION_TEMPERATURE_LOWER_0))
                elif external_temp < 10:
                    #2.4KW/hour
                    weights.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_0_LOWER_10-(confort_score_coef*8))
                    comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_0_LOWER_10)
                    cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_0_LOWER_10)
                elif external_temp >= 10 and external_temp <= 20:
                    #1.6KW/hour
                    weights.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20-(confort_score_coef*8))
                    comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                    cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                elif external_temp > 20:
                    #0.8KW/hour
                    weights.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_20-(confort_score_coef*8))
                    comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_20)
                    cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_20)
    return weights, comsumption, cost
    
def get_temperature_array(date_string):
    #date_string is a string in the format '2021-12-01'
    #returns an array of temperatures for the day
    with open('data/temp_data.json') as json_file:
        data = json.load(json_file)
    df = pd.DataFrame(data)
    df['dt'] = pd.to_datetime(df['dt'], unit='s')
    target_day = pd.to_datetime(date_string).date()
    df_day = df[df['dt'].dt.date == target_day]
    temperature_array = df_day['temp'].to_numpy()
    return temperature_array

def get_energy_array(date_string):
    #date_string is a string in the format '2021-12-01'
    #returns an array of energy prices for the day
    t0 = pd.to_datetime(date_string) - pd.Timedelta(days=1)
    energy_array = read_prices(t0, t0)[0]
    return energy_array


def printResults(results):
    #results is a list of results for each day
    #prints the results for each day
    for i in range(len(results)):
        print("Day: ", i+1)
        print("Policy: ", results[i]['OptimizeCost'][0])
        print("Electricity Cost (euros): ", results[i]['OptimizeCost'][1])
        print("Confort Score: ", results[i]['OptimizeCost'][2])
        print("Accumulated Comfort Score: ", results[i]['OptimizeCost'][3])
        print("Atual Cost: ", results[i]['OptimizeCost'][4])
        print("Accumulated Cost: ", results[i]['OptimizeCost'][5])
        print("Atual Consumption: ", results[i]['OptimizeCost'][6])
        print("Accumulated Consumption: ", results[i]['OptimizeCost'][7])
        print("")

#function to optimize cost for all days in a month
def get_data_from_month(year, month):
    #year and month are integers
    #returns a list of results for each day
    results = []
    start_date = pd.to_datetime(f'{year}-{month}-01')
    end_date = pd.to_datetime(f'{year}-{month}-01') + pd.Timedelta(days=31)
    #see if end date is in the same month
    if end_date.month != month:
        end_date = end_date - pd.Timedelta(days=1)

    for i in range((end_date-start_date).days+1):
        date = start_date + pd.Timedelta(days=i)
        temperature_array = get_temperature_array(date)
        energy_array = get_energy_array(date)
        weights, consumption, cost = calculateWeights(temperature_array, energy_array)
        results.append(OptimizeCost(weights, cost, consumption, temperature_array, minumum_confort_score=124))
    return results


#function to optiize per week
def get_data_from_week(year, week):
    #year and week are integers
    #returns a list of results for each day
    results = []
    start_date = pd.to_datetime(f'{year}-01-01') + pd.Timedelta(days=7*(week-1))
    end_date = pd.to_datetime(f'{year}-01-01') + pd.Timedelta(days=7*(week-1)+6)
    #see if end date is in the same month
    if end_date.month != start_date.month:
        end_date = end_date - pd.Timedelta(days=1)

    for i in range((end_date-start_date).days+1):
        date = start_date + pd.Timedelta(days=i)
        temperature_array = get_temperature_array(date)
        energy_array = get_energy_array(date)
        weights, consumption, cost= calculateWeights(temperature_array, energy_array)
        results.append(OptimizeCost(weights, cost, consumption, temperature_array, minumum_confort_score=124))
    return results
    
def create_json_object(results, start_date):
    #create json object with following structure
    #{hour, day, mode, energy_cost, accumulated_energy_cost, consumption, accumulated_consumption, confort_score, accumulated_confort_score}
    #results is a list of results from get_data_from_multiple_days
    #start_date is a string in the format '2021-12-01'
    #returns a json object with the structure described above
    start_date = pd.to_datetime(start_date)
    json_object = []
    for i in range(len(results)):
        date = start_date + pd.Timedelta(days=i)
        
        hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        
        accumulated_cost_per_hour = results[i]['OptimizeCost'][4]
        for j in range(1, len(accumulated_cost_per_hour)):
            accumulated_cost_per_hour[j] = accumulated_cost_per_hour[j]+accumulated_cost_per_hour[j-1]


        for hour in hours:
            #hour
            Mode_for_that_hour = results[i]['OptimizeCost'][0][hour]
            #swap mode for 0, 1 and 2
            if Mode_for_that_hour == 'off':
                Mode_for_that_hour = 0
            elif Mode_for_that_hour == 'eco':
                Mode_for_that_hour = 1
            elif Mode_for_that_hour == 'conf':
                Mode_for_that_hour = 2


            Energy_cost_for_that_complete_day = results[i]['OptimizeCost'][1]
            Comfort_score_for_that_complete_day = results[i]['OptimizeCost'][2]
            Accumulated_daily_comfort_score_until_that_hour = results[i]['OptimizeCost'][3][hour]
            Energy_cost_for_that_hour = results[i]['OptimizeCost'][4][hour]
            accumulated_energy_cost_that_hour = accumulated_cost_per_hour[hour]
            Accumulated_daily_energy_cost_until_that_hour = results[i]['OptimizeCost'][5][hour]
            Consumption_for_that_hour = results[i]['OptimizeCost'][6][hour]
            Accumulated_daily_consumption_until_that_hour = results[i]['OptimizeCost'][7][hour]
            exterior_temperature = results[i]['OptimizeCost'][8][hour]

            Energy_Price_hour = results[i]['energy_array'][hour]


            json_object.append({
                'hour': hour,
                'day': date.strftime('%Y-%m-%d'),
                'mode': Mode_for_that_hour,
                'Energy_cost_for_that_complete_day': Energy_cost_for_that_complete_day,
                'accumulated_energy_cost_that_hour': accumulated_energy_cost_that_hour,
                'Energy_cost_for_that_hour': Energy_cost_for_that_hour,
                'Accumulated_daily_energy_cost_until_that_hour': Accumulated_daily_energy_cost_until_that_hour,
                'Consumption_for_that_hour': Consumption_for_that_hour,
                'Accumulated_daily_consumption_until_that_hour': Accumulated_daily_consumption_until_that_hour,
                'Comfort_score_for_that_complete_day': Comfort_score_for_that_complete_day,
                'Accumulated_daily_comfort_score_until_that_hour': Accumulated_daily_comfort_score_until_that_hour,
                'exterior_temperature': exterior_temperature, 
                'energy_price': Energy_Price_hour
            })
        
    return json_object

    


def saveJsonFIle(json_object, file_name):
    #json_object is a json object
    #file_name is a string
    #saves the json object in a file
    with open(file_name, 'w') as f:
        json.dump(json_object, f, indent=4)

#read first entry of results
def printResults(results):
    #results is a list of results for each day
    #prints the results for each day
    for i in range(len(results)):
        print("Day: ", i+1)
        print("Policy: ", results[i]['OptimizeCost'][0])
        print("Electricity Cost (euros): ", results[i]['OptimizeCost'][1])
        print("Confort Score: ", results[i]['OptimizeCost'][2])
        print("Accumulated Comfort Score: ", results[i]['OptimizeCost'][3])
        print("Atual Cost: ", results[i]['OptimizeCost'][4])
        print("Accumulated Cost: ", results[i]['OptimizeCost'][5])
        print("Atual Consumption: ", results[i]['OptimizeCost'][6])
        print("Accumulated Consumption: ", results[i]['OptimizeCost'][7])
        print("")

def get_temperature_array_from_api(start_date, end_date=None):
    if end_date == None:
        response = requests.get("http://localhost:5002/?start_date="+start_date+"&end_date="+start_date)
    else:
        response = requests.get("http://localhost:5002/?start_date="+start_date+"&end_date="+end_date)
    temperature_array=[]
    for i in range(len(response.json())):
        temperature_array.append(response.json()[i]['temperature'])
    
    return temperature_array[0]



def get_energy_array_from_api(start_date, end_date):
    #get energy cost array
    response = requests.get("http://localhost:5001/?start_date="+start_date+"&end_date="+end_date)
    energy_cost_array = []
    for i in range(len(response.json())):
        energy_cost_array.append(response.json()[i]['price'])

    #split array into arrays of 24 dimensions
    energy_cost_array = np.array_split(energy_cost_array, len(energy_cost_array)/24)
    return energy_cost_array



def generate_Standard_Policy():
    """
    O padrão normal de utilização de uma bomba de calor geralmente é definido semanalmente em que a bomba
    de calor trabalha diariamente em modo Comfort das 6:30 às 21:30 e Eco das 00:00 às 6:30 e depois das 21:30
    até à 00:00.

    Let's assume 7and 22h
    """
    policy = []
    for i in range(24):
        if i < 6 or i >= 21:
            policy.append('conf')
        else:
            policy.append('eco')
    return policy

def simulate_policy(policy, date):
    #get the temperature array
    #temperature_array = get_temperature_array(date)
    temperature_array = get_temperature_array_from_api(date)

    #get the energy array

    #energy_cost_array = get_energy_array(date)
    energy_cost_array = get_energy_array_from_api(date, date)[0]
    print(energy_cost_array)
    #calculate the weights

    #calculate the weights for each hour
    comsumption = []
    cost = []

    for i in range(len(temperature_array)):
        mode = policy[i]
        external_temp = temperature_array[i]
        if mode == 'off':
            #1KW/hour regardless of temperature
            comsumption.append(MODE_OFF_CONSUMPTION)
            cost.append(energy_cost_array[i]*MODE_OFF_CONSUMPTION)
        elif mode == 'eco':
            if external_temp < 10:
                #1.6KW/hour
                comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_LOWER_10)
                cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_LOWER_10)
            elif external_temp >= 10 and external_temp <= 20:
                #0.8KW/hour
                comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
            elif external_temp > 20:
                #0.4KW/hour
                comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_20)
                cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_20)
        elif mode == 'conf':
            if external_temp < 0:
                #2.4KW/hour+9KW/hour
                comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_LOWER_0)
                cost.append(energy_cost_array[i]*(MODE_CONFORT_CONSUMPTION_TEMPERATURE_LOWER_0))
            elif external_temp < 10:
                #2.4KW/hour
                comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_0_LOWER_10)
                cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_0_LOWER_10)
            elif external_temp >= 10 and external_temp <= 20:
                #1.6KW/hour
                comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
            elif external_temp > 20:
                #0.8KW/hour
                comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_20)
                cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_20)


    return comsumption, cost


def simulate_policy_JSON_format_hourly(policy, date):
    #get the temperature array
    #temperature_array = get_temperature_array(date)
    temperature_array = get_temperature_array_from_api(date)

    #get the energy array

    #energy_cost_array = get_energy_array(date)
    energy_cost_array = get_energy_array_from_api(date, date)[0]
    #print(energy_cost_array)
    #calculate the weights

    #calculate the weights for each hour
    comsumption = []
    cost = []
    comfort = []

    for i in range(len(temperature_array)):
        mode = policy[i]
        external_temp = temperature_array[i]
        if mode == 'off':
            #1KW/hour regardless of temperature
            comsumption.append(MODE_OFF_CONSUMPTION)
            cost.append(energy_cost_array[i]*MODE_OFF_CONSUMPTION)
            comfort.append(0)
        elif mode == 'eco':
            if external_temp < 10:
                #1.6KW/hour
                comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_LOWER_10)
                cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_LOWER_10)
                comfort.append(CONFORT_PROVIDED_MODE_ECO)
            elif external_temp >= 10 and external_temp <= 20:
                #0.8KW/hour
                comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                comfort.append(CONFORT_PROVIDED_MODE_ECO)
            elif external_temp > 20:
                #0.4KW/hour
                comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_20)
                cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_20)
                comfort.append(CONFORT_PROVIDED_MODE_ECO)
        elif mode == 'conf':
            if external_temp < 0:
                #2.4KW/hour+9KW/hour
                comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_LOWER_0)
                cost.append(energy_cost_array[i]*(MODE_CONFORT_CONSUMPTION_TEMPERATURE_LOWER_0))
                comfort.append(CONFORT_PROVIDED_MODE_CONFORT)
            elif external_temp < 10:
                #2.4KW/hour
                comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_0_LOWER_10)
                cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_0_LOWER_10)
                comfort.append(CONFORT_PROVIDED_MODE_CONFORT)
            elif external_temp >= 10 and external_temp <= 20:
                #1.6KW/hour
                comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                comfort.append(CONFORT_PROVIDED_MODE_CONFORT)
            elif external_temp > 20:
                #0.8KW/hour
                comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_20)
                cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_20)
                comfort.append(CONFORT_PROVIDED_MODE_CONFORT)
                
                
                
    accumulated_cost = []
    
    for i in range(len(cost)):
        if i == 0:
            accumulated_cost.append(cost[i])
        else:
            accumulated_cost.append(accumulated_cost[i-1]+cost[i])

    accumulated_comsumption = []

    for i in range(len(comsumption)):
        if i == 0:
            accumulated_comsumption.append(comsumption[i])
        else:
            accumulated_comsumption.append(accumulated_comsumption[i-1]+comsumption[i])

    accumulated_comfort = []

    for i in range(len(comfort)):
        if i == 0:
            accumulated_comfort.append(comfort[i])
        else:
            accumulated_comfort.append(accumulated_comfort[i-1]+comfort[i])

    json_object = []



    for i in range(len(temperature_array)):
        if policy[i] == 'off':
            mode = 0
        elif policy[i] == 'eco':
            mode = 1
        elif policy[i] == 'conf':
            mode = 2

        json_object.append({
                    'hour': i,
                    'day': date,
                    "mode": mode,
                    'Energy_cost_for_that_complete_day': accumulated_cost[-1],
                    'accumulated_energy_cost_that_hour': accumulated_cost[i],
                    'Energy_cost_for_that_hour': cost[i],
                    'Accumulated_daily_comfort_score_until_that_hour': accumulated_comfort[i],
                    'Consumption_for_that_hour': comsumption[i],
                    'Accumulated_daily_consumption_until_that_hour': accumulated_comsumption[i],
                    'Comfort_score_for_that_complete_day': accumulated_comfort[-1],
                    'Accumulated_daily_comfort_score_until_that_hour': accumulated_comfort[i],
                    'exterior_temperature': temperature_array[i],
                    'energy_price': energy_cost_array[i],

                })
            

    return json_object


#function to optimize cost for multiple days
def get_data_from_multiple_days(start_date, end_date, confort_score_coef=0.00):
    #start_date and end_date are strings in the format '2021-12-01'
    #returns a list of results for each day
    results = []
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    energy_arrays = get_energy_array_from_api(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

    for i in range((end_date-start_date).days+1):
        date = start_date + pd.Timedelta(days=i)
        #temperature_array = get_temperature_array(date)
        temperature_array= get_temperature_array_from_api(date.strftime('%Y-%m-%d'))
        #energy_array = get_energy_array(date)
        energy_array = energy_arrays[i]

        weights, consumption, cost = calculateWeights(temperature_array, energy_array, confort_score_coef=confort_score_coef)
        #append OptimizeCost and energyARRAY
        results.append({
            'OptimizeCost': OptimizeCost(weights, cost, consumption, temperature_array, minumum_confort_score=124),
            'energy_array': energy_array
        })

    return results

def get_DataByDay_accumulatePeriod(start_date, end_date, confort_score_coef=0.00):
    #receives a start date and end date and returns a list of dictionaries with the data for each day
    #the data is the same as the json object

    json_object = []
    results = get_data_from_multiple_days(start_date, end_date, confort_score_coef=confort_score_coef)
    

    accumulated_cost_across_days = []
    accumulated_comsumption_across_days = []
    accumulated_comfort_across_days = []


    for i in range(len(results)):
        #add i days to start date
        day = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=i)
        energy_cost = results[i]['OptimizeCost'][1]
        confort_score = results[i]['OptimizeCost'][2]

        max_energy_cost_hours = max(results[i]['OptimizeCost'][4])
        min_energy_cost_hours = min(results[i]['OptimizeCost'][4])
        max_energy_comsumption_hours = max(results[i]['OptimizeCost'][6])
        min_energy_comsumption_hours = min(results[i]['OptimizeCost'][6])

        daily_energy_comsumption = results[i]['OptimizeCost'][7][-1]

        temperature_avg= sum(results[i]['OptimizeCost'][8])/len(results[i]['OptimizeCost'][8])
        temperature_max = max(results[i]['OptimizeCost'][8])
        temperature_min = min(results[i]['OptimizeCost'][8])
        avg_energy_price = sum(results[i]['energy_array'])/len(results[i]['energy_array'])
        max_energy_price = max(results[i]['energy_array'])
        min_energy_prive = min(results[i]['energy_array'])
        
        
        accumulated_cost_across_days.append(energy_cost)
        accumulated_comsumption_across_days.append(daily_energy_comsumption)
        accumulated_comfort_across_days.append(confort_score)

        if i > 0:
            accumulated_cost_across_days[i] = accumulated_cost_across_days[i-1] + energy_cost
            accumulated_comsumption_across_days[i] = accumulated_comsumption_across_days[i-1] + daily_energy_comsumption
            accumulated_comfort_across_days[i] = accumulated_comfort_across_days[i-1] + confort_score


        
        json_object.append({
            "day": day.strftime('%Y-%m-%d'),
            "daily_energy_cost": energy_cost,
            "daily_confort_score": confort_score,
            "daily_energy_comsumption": daily_energy_comsumption,
            "daily_temperature_avg": temperature_avg,
            "daily_avg_energy_price": avg_energy_price,
            "accumulated_cost_across_days": accumulated_cost_across_days[i],
            "accumulated_comsumption_across_days": accumulated_comsumption_across_days[i],
            "accumulated_comfort_across_days": accumulated_comfort_across_days[i],
            "max_energy_cost_hour": max_energy_cost_hours,
            "min_energy_cost_hour": min_energy_cost_hours,
            "max_energy_comsumption_hour": max_energy_comsumption_hours,
            "min_energy_comsumption_hour": min_energy_comsumption_hours,
            "max_energy_price": max_energy_price,
            "min_energy_price": min_energy_prive,
            "max_temperature": temperature_max,
            "min_temperature": temperature_min,



        })
    
    
    return json_object

def get_DataByDay_AccumulatingWeek(start_date, end_date, confort_score_coef=0.00):
    #get data from multiple days
    #start_date and end_date must be in the format 'YYYY-MM-DD'
    #confort_score_coef is the coeficient that multiplies the confort score
    #returns a list with the results of the optimization for each day
    results = get_data_from_multiple_days(start_date, end_date, confort_score_coef=confort_score_coef)
    
    #separate results by week depending on the start_date and end_date
    #get the week number of the start_date
    start_date_temp = datetime.strptime(start_date, '%Y-%m-%d')
    start_week = start_date_temp.isocalendar()[1]
    #get the week number of the end_date
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    end_week = end_date.isocalendar()[1]


    #Add days from each week to a list
    weeks = []
    for week in range(start_week, end_week+1):
        weeks.append([])
        for i in range(7):
            weeks[week-start_week].append(start_date_temp + timedelta(days=i))
        start_date_temp = start_date_temp + timedelta(days=7)




    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    #assume the first element of results is the start_date
    #aggregate the results of the first week
    json_object = []
    for week in weeks:
        
        accumulated_energy_consumption = []
        accumulated_cost = []
        accumulated_confort_score = []
        for i in range(len(results)):
            current_day = start_date + timedelta(days=i)
            #print(week)
            #print(current_day)
            if current_day in week:
                #print("week", week)
                energy_cost = results[i]['OptimizeCost'][1]
                daily_energy_comsumption = results[i]['energy_array'][0]
                temperatures= results[i]['OptimizeCost'][8]
                confort_score = results[i]['OptimizeCost'][2]
                energy_prices = results[i]['OptimizeCost'][4]

                #accumlate the energy consumption and cost
                accumulated_energy_consumption.append(daily_energy_comsumption)
                accumulated_cost.append(energy_cost)
                accumulated_confort_score.append(confort_score)
                if len(accumulated_energy_consumption) > 1:
                    accumulated_energy_consumption[-1]= accumulated_energy_consumption[-1] + accumulated_energy_consumption[-2]
                
                if len(accumulated_cost) > 1:
                    accumulated_cost[-1]= accumulated_cost[-1] + accumulated_cost[-2]
                if len(accumulated_confort_score) > 1:
                                    accumulated_confort_score[-1]= accumulated_confort_score[-1] + accumulated_confort_score[-2]


                accumulated_energy_consumption_day = accumulated_energy_consumption[-1]
                accumulated_cost_day = accumulated_cost[-1]
                accumulated_confort_score_day = accumulated_confort_score[-1]

                json_object.append({
                    'Date': current_day.strftime('%Y-%m-%d'),
                    'AccumulatedEnergyConsumption': accumulated_energy_consumption_day,
                    'AccumulatedCost': accumulated_cost_day,
                    'MaxEnergyCostInADay': max(accumulated_cost),
                    'MinEnergyCostInADay': min(accumulated_cost),
                    'AvgEnergyCostInADay': sum(accumulated_cost)/len(accumulated_cost),
                    'MaxEnergyConsumptionInADay': max(accumulated_energy_consumption),
                    'MinEnergyConsumptionInADay': min(accumulated_energy_consumption),
                    'AvgEnergyConsumptionInADay': sum(accumulated_energy_consumption)/len(accumulated_energy_consumption),
                    'AvgEnergyHourlyPrice': sum(energy_prices)/len(energy_prices),
                    'MaxEnergyHourlyPriceInAHour': max(energy_prices),
                    'MinEnergyHourlyPriceInAHour': min(energy_prices),
                    'ExternalTemperatureAvg': sum(temperatures)/len(temperatures),
                    'MaxExternalTemperature': max(temperatures),
                    'MinExternalTemperature': min(temperatures),
                    
                    'AccumulatedConfortScore': accumulated_confort_score_day,
                    'ConfortScore': confort_score,

                    

                })
            current_day = current_day + timedelta(days=1)
                
    return json_object

def simulate_policy_JSON_format_period(policy, start_date, end_date):


    json_object = []

    accumulated_cost_across_days = []
    accumulated_comsumption_across_days = []
    accumulated_comfort_across_days = []
    for day in pd.date_range(start_date, end_date):
        date = day.strftime("%Y-%m-%d")

        #get the temperature array
        #temperature_array = get_temperature_array(date)
        temperature_array = get_temperature_array_from_api(date)
        

        #get the energy array
        #energy_cost_array = get_energy_array(date)
        energy_cost_array = get_energy_array_from_api(date, date)[0]
        #print(energy_cost_array)
        #calculate the weights

        #calculate the weights for each hour
        comsumption = []
        cost = []
        comfort = []

        for i in range(len(temperature_array)):
            mode = policy[i]
            external_temp = temperature_array[i]
            if mode == 'off':
                #1KW/hour regardless of temperature
                comsumption.append(MODE_OFF_CONSUMPTION)
                cost.append(energy_cost_array[i]*MODE_OFF_CONSUMPTION)
                comfort.append(0)
            elif mode == 'eco':
                if external_temp < 10:
                    #1.6KW/hour
                    comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_LOWER_10)
                    cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_LOWER_10)
                    comfort.append(CONFORT_PROVIDED_MODE_ECO)
                elif external_temp >= 10 and external_temp <= 20:
                    #0.8KW/hour
                    comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                    cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                    comfort.append(CONFORT_PROVIDED_MODE_ECO)
                elif external_temp > 20:
                    #0.4KW/hour
                    comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_20)
                    cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_20)
                    comfort.append(CONFORT_PROVIDED_MODE_ECO)
            elif mode == 'conf':
                if external_temp < 0:
                    #2.4KW/hour+9KW/hour
                    comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_LOWER_0)
                    cost.append(energy_cost_array[i]*(MODE_CONFORT_CONSUMPTION_TEMPERATURE_LOWER_0))
                    comfort.append(CONFORT_PROVIDED_MODE_CONFORT)
                elif external_temp < 10:
                    #2.4KW/hour
                    comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_0_LOWER_10)
                    cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_0_LOWER_10)
                    comfort.append(CONFORT_PROVIDED_MODE_CONFORT)
                elif external_temp >= 10 and external_temp <= 20:
                    #1.6KW/hour
                    comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                    cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                    comfort.append(CONFORT_PROVIDED_MODE_CONFORT)
                elif external_temp > 20:
                    #0.8KW/hour
                    comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_20)
                    cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_20)
                    comfort.append(CONFORT_PROVIDED_MODE_CONFORT)
                    
                    
                    
        accumulated_cost_hourly = []
        
        for i in range(len(cost)):
            if i == 0:
                accumulated_cost_hourly.append(cost[i])
            else:
                accumulated_cost_hourly.append(accumulated_cost_hourly[i-1]+cost[i])

        accumulated_comsumption_hourly = []

        for i in range(len(comsumption)):
            if i == 0:
                accumulated_comsumption_hourly.append(comsumption[i])
            else:
                accumulated_comsumption_hourly.append(accumulated_comsumption_hourly[i-1]+comsumption[i])

        accumulated_comfort_hourly = []

        for i in range(len(comfort)):
            if i == 0:
                accumulated_comfort_hourly.append(comfort[i])
            else:
                accumulated_comfort_hourly.append(accumulated_comfort_hourly[i-1]+comfort[i])


        energy_cost = accumulated_cost_hourly[-1]
        confort_score = accumulated_comfort_hourly[-1]

        max_energy_cost_hours = max(cost)
        min_energy_cost_hours = min(cost)
        max_energy_comsumption_hours = max(comsumption)
        min_energy_comsumption_hours = min(comsumption)

        daily_energy_comsumption = accumulated_comsumption_hourly[-1]

        temperature_avg= sum(temperature_array)/len(temperature_array)
        temperature_max = max(temperature_array)
        temperature_min = min(temperature_array)
        avg_energy_price = sum(energy_cost_array)/len(energy_cost_array)
        max_energy_price = max(energy_cost_array)
        min_energy_price = min(energy_cost_array)
        
        accumulated_cost_across_days.append(energy_cost)
        accumulated_comsumption_across_days.append(daily_energy_comsumption)
        accumulated_comfort_across_days.append(confort_score)

        if len(accumulated_cost_across_days)>1:
            accumulated_cost_across_days[-1] = accumulated_cost_across_days[-1] + accumulated_cost_across_days[-2]
            accumulated_comsumption_across_days[-1] = accumulated_comsumption_across_days[-1] + accumulated_comsumption_across_days[-2]
            accumulated_comfort_across_days[-1] = accumulated_comfort_across_days[-1] + accumulated_comfort_across_days[-2]

        json_object.append({
            "day": date,
            "daily_energy_cost": energy_cost,
            "daily_confort_score": confort_score,
            "daily_energy_comsumption": daily_energy_comsumption,
            "daily_temperature_avg": temperature_avg,
            "daily_avg_energy_price": avg_energy_price,
            "accumulated_cost_across_days": accumulated_cost_across_days[-1],
            "accumulated_comsumption_across_days": accumulated_comsumption_across_days[-1],
            "accumulated_comfort_across_days": accumulated_comfort_across_days[-1],
            "max_energy_cost_hour": max_energy_cost_hours,
            "min_energy_cost_hour": min_energy_cost_hours,
            "max_energy_comsumption_hour": max_energy_comsumption_hours,
            "min_energy_comsumption_hour": min_energy_comsumption_hours,
            'AvgTemperature': temperature_avg,
            'MaxTemperature': temperature_max,
            'MinTemperature': temperature_min,
            'MaxEnergyCostInADay': max_energy_price,
            'MinEnergyCostInADay': min_energy_price,
            'AvgEnergyCostInADay': avg_energy_price,

        })

    return json_object


def simulate_policy_JSON_format_week(policy, start_date, end_date):


    json_object = []



    start_date_temp = datetime.strptime(start_date, '%Y-%m-%d')
    start_week = start_date_temp.isocalendar()[1]
    #get the week number of the end_date
    end_date_temp = datetime.strptime(end_date, '%Y-%m-%d')
    end_week = end_date_temp.isocalendar()[1]


    #Add days from each week to a list
    weeks = []
    for week in range(start_week, end_week+1):
        weeks.append([])
        for i in range(7):
            weeks[week-start_week].append(start_date_temp + timedelta(days=i))
        start_date_temp = start_date_temp + timedelta(days=7)

    for week in weeks:
        
        accumulated_cost_across_days = []
        accumulated_comsumption_across_days = []
        accumulated_comfort_across_days = []
        for day in pd.date_range(start_date, end_date):
            date = day.strftime("%Y-%m-%d")
            if day in week:
                    
                #get the temperature array
                #temperature_array = get_temperature_array(date)
                temperature_array = get_temperature_array_from_api(date)
                

                #get the energy array
                #energy_cost_array = get_energy_array(date)
                energy_cost_array = get_energy_array_from_api(date, date)[0]
                #print(energy_cost_array)
                #calculate the weights

                #calculate the weights for each hour
                comsumption = []
                cost = []
                comfort = []

                for i in range(len(temperature_array)):
                    mode = policy[i]
                    external_temp = temperature_array[i]
                    if mode == 'off':
                        #1KW/hour regardless of temperature
                        comsumption.append(MODE_OFF_CONSUMPTION)
                        cost.append(energy_cost_array[i]*MODE_OFF_CONSUMPTION)
                        comfort.append(0)
                    elif mode == 'eco':
                        if external_temp < 10:
                            #1.6KW/hour
                            comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_LOWER_10)
                            cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_LOWER_10)
                            comfort.append(CONFORT_PROVIDED_MODE_ECO)
                        elif external_temp >= 10 and external_temp <= 20:
                            #0.8KW/hour
                            comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                            cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                            comfort.append(CONFORT_PROVIDED_MODE_ECO)
                        elif external_temp > 20:
                            #0.4KW/hour
                            comsumption.append(MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_20)
                            cost.append(energy_cost_array[i]*MODE_ECO_CONSUMPTION_TEMPERATURE_BIGGER_20)
                            comfort.append(CONFORT_PROVIDED_MODE_ECO)
                    elif mode == 'conf':
                        if external_temp < 0:
                            #2.4KW/hour+9KW/hour
                            comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_LOWER_0)
                            cost.append(energy_cost_array[i]*(MODE_CONFORT_CONSUMPTION_TEMPERATURE_LOWER_0))
                            comfort.append(CONFORT_PROVIDED_MODE_CONFORT)
                        elif external_temp < 10:
                            #2.4KW/hour
                            comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_0_LOWER_10)
                            cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_0_LOWER_10)
                            comfort.append(CONFORT_PROVIDED_MODE_CONFORT)
                        elif external_temp >= 10 and external_temp <= 20:
                            #1.6KW/hour
                            comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                            cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_10_LOWER_20)
                            comfort.append(CONFORT_PROVIDED_MODE_CONFORT)
                        elif external_temp > 20:
                            #0.8KW/hour
                            comsumption.append(MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_20)
                            cost.append(energy_cost_array[i]*MODE_CONFORT_CONSUMPTION_TEMPERATURE_BIGGER_20)
                            comfort.append(CONFORT_PROVIDED_MODE_CONFORT)
                            
            
                accumulated_cost_hourly = []
                
                for i in range(len(cost)):
                    if i == 0:
                        accumulated_cost_hourly.append(cost[i])
                    else:
                        accumulated_cost_hourly.append(accumulated_cost_hourly[i-1]+cost[i])

                accumulated_comsumption_hourly = []

                for i in range(len(comsumption)):
                    if i == 0:
                        accumulated_comsumption_hourly.append(comsumption[i])
                    else:
                        accumulated_comsumption_hourly.append(accumulated_comsumption_hourly[i-1]+comsumption[i])

                accumulated_comfort_hourly = []

                for i in range(len(comfort)):
                    if i == 0:
                        accumulated_comfort_hourly.append(comfort[i])
                    else:
                        accumulated_comfort_hourly.append(accumulated_comfort_hourly[i-1]+comfort[i])


                energy_cost = accumulated_cost_hourly[-1]
                confort_score = accumulated_comfort_hourly[-1]

                max_energy_cost_hours = max(cost)
                min_energy_cost_hours = min(cost)
                max_energy_comsumption_hours = max(comsumption)
                min_energy_comsumption_hours = min(comsumption)

                daily_energy_comsumption = accumulated_comsumption_hourly[-1]

                temperature_avg= sum(temperature_array)/len(temperature_array)
                temperature_max = max(temperature_array)
                temperature_min = min(temperature_array)
                avg_energy_price = sum(energy_cost_array)/len(energy_cost_array)
                max_energy_price = max(energy_cost_array)
                min_energy_price = min(energy_cost_array)
                
                
                accumulated_cost_across_days.append(energy_cost)
                accumulated_comsumption_across_days.append(daily_energy_comsumption)
                accumulated_comfort_across_days.append(confort_score)

                if len(accumulated_cost_across_days)>1:
                    accumulated_cost_across_days[-1] = accumulated_cost_across_days[-1] + accumulated_cost_across_days[-2]
                    accumulated_comsumption_across_days[-1] = accumulated_comsumption_across_days[-1] + accumulated_comsumption_across_days[-2]
                    accumulated_comfort_across_days[-1] = accumulated_comfort_across_days[-1] + accumulated_comfort_across_days[-2]


                json_object.append({
                    "Date": date,
                    "AccumulatedCost": accumulated_cost_across_days[-1],
                    "AccumulatedEnergyConsumption": accumulated_comsumption_across_days[-1],

                    'MaxEnergyCostInADay': max_energy_cost_hours,
                    'MinEnergyCostInADay': min_energy_cost_hours,
                    'AvgEnergyCostInADay': sum(cost)/len(cost),
                    'MaxEnergyConsumptionInADay': max_energy_comsumption_hours,
                    'MinEnergyConsumptionInADay': min_energy_comsumption_hours,
                    'AvgEnergyConsumptionInADay': sum(comsumption)/len(comsumption),
                    'AvgEnergyHourlyPrice': sum(energy_cost_array)/len(energy_cost_array),
                    'MaxEnergyHourlyPriceInAHour': max(energy_cost_array),
                    'MinEnergyHourlyPriceInAHour': min(energy_cost_array),
                    'ExternalTemperatureAvg': sum(temperature_array)/len(temperature_array),
                    'MaxExternalTemperature': max(temperature_array),
                    'MinExternalTemperature': min(temperature_array),
                    'AvgTemperature': temperature_avg,
                    'MaxTemperature': temperature_max,
                    'MinTemperature': temperature_min,
                    'AccumulatedComfort': accumulated_comfort_across_days[-1],
                    'MaxEnergyCostInADay': max_energy_price,
                    'MinEnergyCostInADay': min_energy_price,
                    'AvgEnergyCostInADay': avg_energy_price,
                    'ConfortScore': confort_score,
                    'AccumulatedComfortScore': accumulated_comfort_across_days[-1]


                })
               

    return json_object



def getAggratedData_Hourly(start_date, end_date):
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



    results_algorithm = get_data_from_multiple_days(start_date, end_date)
    json_object = create_json_object(results_algorithm, start_date)


    #concat element wise the results and the json_object 
    #reshape results to be a 1D array
    results_policy = np.concatenate(results)
    results_policy = results_policy.reshape(-1)
    len(results_policy)

    aggreatedresults =[]
    for entry in range(len(json_object)):
        hour = json_object[entry]['hour']
        mode = json_object[entry]['mode']
        day = json_object[entry]['day']
        Energy_cost_for_that_complete_day = json_object[entry]['Energy_cost_for_that_complete_day']
        accumulated_energy_cost_that_hour = json_object[entry]['accumulated_energy_cost_that_hour']
        Energy_cost_for_that_hour = json_object[entry]['Energy_cost_for_that_hour']
        Consumption_for_that_hour = json_object[entry]['Consumption_for_that_hour']
        Accumulated_daily_consumption_until_that_hour = json_object[entry]['Accumulated_daily_consumption_until_that_hour']
        Comfort_score_for_that_complete_day = json_object[entry]['Comfort_score_for_that_complete_day']
        Accumulated_daily_comfort_score_until_that_hour = json_object[entry]['Accumulated_daily_comfort_score_until_that_hour']
        exterior_temperature = json_object[entry]['exterior_temperature']
        energy_price  = json_object[entry]['energy_price']


        Standard_Mode = results_policy[entry]['mode']
        Standard_Energy_cost_for_that_complete_day = results_policy[entry]['Energy_cost_for_that_complete_day']
        Standard_accumulated_energy_cost_that_hour = results_policy[entry]['accumulated_energy_cost_that_hour']
        Standard_Energy_cost_for_that_hour = results_policy[entry]['Energy_cost_for_that_hour']
        Standard_Accumulated_daily_comfort_score_until_that_hour = results_policy[entry]['Accumulated_daily_comfort_score_until_that_hour']
        Standard_Consumption_for_that_hour = results_policy[entry]['Consumption_for_that_hour']
        Standard_Accumulated_daily_consumption_until_that_hour = results_policy[entry]['Accumulated_daily_consumption_until_that_hour']
        Standard_Comfort_score_for_that_complete_day = results_policy[entry]['Comfort_score_for_that_complete_day']
        Standard_AccumulatedEnergyConsumption = results_policy[entry]['accumulated_energy_cost_that_hour']

        aggreatedresults.append({
                "hour": hour,
                "mode": mode,
                "Date": day,
                "Energy_cost_for_that_complete_day": Energy_cost_for_that_complete_day,
                "AccumulatedCost": accumulated_energy_cost_that_hour,
                "Energy_cost_for_that_hour": Energy_cost_for_that_hour,
                "EnergyComsumption": Consumption_for_that_hour,
                "AccumulatedEnergyConsumption": Accumulated_daily_consumption_until_that_hour,
                "ComfortScore": Comfort_score_for_that_complete_day,
                "AccumulatedComfortScore": Accumulated_daily_comfort_score_until_that_hour,
                "ExternalTemperature": exterior_temperature,
                
                #not avergaed... just to have equal between apis
                "AvgEnergyHourlyPrice": energy_price,

                "Standard_Mode": Standard_Mode,

                #cost per hour
                "Standard_AvgEnergyCostInADay": Standard_Energy_cost_for_that_complete_day,
                "Standard_Accumulated_daily_energy_cost_until_that_hour": Standard_accumulated_energy_cost_that_hour,
                "Standard_AvgEnergyCostInADay": Standard_Energy_cost_for_that_hour,
                "Standard_Consumption_for_that_hour": Standard_Consumption_for_that_hour,
                "Standard_AvgEnergyConsumptionInADay": Standard_Accumulated_daily_consumption_until_that_hour,
                "Standard_ComfortScore": Standard_Comfort_score_for_that_complete_day,
                "Standard_AccumulatedComfortScore": Standard_Accumulated_daily_comfort_score_until_that_hour,
                "Standard_AccumulatedEnergyConsumption":Standard_AccumulatedEnergyConsumption
            })
        
    return aggreatedresults

def getAggratedData_weekly(start_date, end_date):
    json_object = get_DataByDay_AccumulatingWeek(start_date, end_date)


    policy = generate_Standard_Policy()
    results_policy = simulate_policy_JSON_format_week(policy, start_date, end_date)
    """
    {'Date': '2021-12-01',
    'AccumulatedEnergyConsumption': 0.2891,
    'AccumulatedCost': 10.720672,
    'MaxEnergyCostInADay': 10.720672,
    'MinEnergyCostInADay': 10.720672,
    'AvgEnergyCostInADay': 10.720672,
    'MaxEnergyConsumptionInADay': 0.2891,
    'MinEnergyConsumptionInADay': 0.2891,
    'AvgEnergyConsumptionInADay': 0.2891,
    'AvgEnergyHourlyPrice': 0.4466946666666667,
    'MaxEnergyHourlyPriceInAHour': 0.57096,
    'MinEnergyHourlyPriceInAHour': 0.38576,
    'ExternalTemperatureAvg': 4.942499999999999,
    'MaxExternalTemperature': 8.83,
    'MinExternalTemperature': 1.94}



    {'Date': '2021-12-01',
    'AccumulatedCost': 11.185312,
    'AccumulatedEnergyConsumption': 45.600000000000016,
    'MaxEnergyCostInADay': 11.185312,
    'MinEnergyCostInADay': 0.69384,
    'AvgEnergyCostInADay': 6.034718999999999,
    'MaxEnergyConsumptionInADay': 45.600000000000016,
    'MinEnergyConsumptionInADay': 2.4,
    'AvgEnergyConsumptionInADay': 24.500000000000004,
    'AvgEnergyHourlyPrice': 0.24720958333333332,
    'MaxEnergyHourlyPriceInAHour': 0.2891,
    'MinEnergyHourlyPriceInAHour': 0.19281,
    'ExternalTemperatureAvg': 4.942499999999999,
    'MaxExternalTemperature': 8.83,
    'MinExternalTemperature': 1.94}
    """


    aggreatedresults =[]
    for entry in range(len(json_object)):
        Date = json_object[entry]['Date']
        AccumulatedEnergyConsumption = json_object[entry]['AccumulatedEnergyConsumption']
        AccumulatedCost = json_object[entry]['AccumulatedCost']
        MaxEnergyCostInADay = json_object[entry]['MaxEnergyCostInADay']
        MinEnergyCostInADay = json_object[entry]['MinEnergyCostInADay']
        AvgEnergyCostInADay = json_object[entry]['AvgEnergyCostInADay']
        MaxEnergyConsumptionInADay = json_object[entry]['MaxEnergyConsumptionInADay']
        MinEnergyConsumptionInADay = json_object[entry]['MinEnergyConsumptionInADay']
        AvgEnergyConsumptionInADay = json_object[entry]['AvgEnergyConsumptionInADay']
        AvgEnergyHourlyPrice = json_object[entry]['AvgEnergyHourlyPrice']
        MaxEnergyHourlyPriceInAHour = json_object[entry]['MaxEnergyHourlyPriceInAHour']
        MinEnergyHourlyPriceInAHour = json_object[entry]['MinEnergyHourlyPriceInAHour']
        ExternalTemperatureAvg = json_object[entry]['ExternalTemperatureAvg']
        MaxExternalTemperature = json_object[entry]['MaxExternalTemperature']
        MinExternalTemperature = json_object[entry]['MinExternalTemperature']

        accumulated_comfort_across_days = json_object[entry]['AccumulatedConfortScore']
        daily_confort_score = json_object[entry]['ConfortScore']

        #policy
        Standard_AccumulatedCost = results_policy[entry]['AccumulatedCost']
        Standard_AccumulatedEnergyConsumption = results_policy[entry]['AccumulatedEnergyConsumption']
        Standard_MaxEnergyCostInADay = results_policy[entry]['MaxEnergyCostInADay']
        Standard_MinEnergyCostInADay = results_policy[entry]['MinEnergyCostInADay']
        Standard_AvgEnergyCostInADay = results_policy[entry]['AvgEnergyCostInADay']
        Standard_MaxEnergyConsumptionInADay = results_policy[entry]['MaxEnergyConsumptionInADay']
        Standard_MinEnergyConsumptionInADay = results_policy[entry]['MinEnergyConsumptionInADay']
        Standard_AvgEnergyConsumptionInADay = results_policy[entry]['AvgEnergyConsumptionInADay']
        Standard_AvgEnergyHourlyPrice = results_policy[entry]['AvgEnergyHourlyPrice']
        Standard_MaxEnergyHourlyPriceInAHour = results_policy[entry]['MaxEnergyHourlyPriceInAHour']
        Standard_MinEnergyHourlyPriceInAHour = results_policy[entry]['MinEnergyHourlyPriceInAHour']
        Standard_AvgExternalTemperature = results_policy[entry]['ExternalTemperatureAvg']
        Standard_MaxExternalTemperature = results_policy[entry]['MaxExternalTemperature']
        Standard_MinExternalTemperature = results_policy[entry]['MinExternalTemperature']


        standard_daily_confort_score= results_policy[entry]['ConfortScore']
        standard_accumulated_comfort_across_days= results_policy[entry]['AccumulatedComfort']

        aggreatedresults.append({
            'Date': Date,
            'AccumulatedEnergyConsumption': AccumulatedEnergyConsumption,
            'AccumulatedCost': AccumulatedCost,
            'MaxEnergyCostInADay': MaxEnergyCostInADay,
            'MinEnergyCostInADay': MinEnergyCostInADay,
            'AvgEnergyCostInADay': AvgEnergyCostInADay,
            'MaxEnergyConsumptionInADay': MaxEnergyConsumptionInADay,
            'MinEnergyConsumptionInADay': MinEnergyConsumptionInADay,
            #avg
            'EnergyConsumption': AvgEnergyConsumptionInADay,
            'AvgEnergyHourlyPrice': AvgEnergyHourlyPrice,

            'MaxEnergyHourlyPriceInAHour': MaxEnergyHourlyPriceInAHour,
            'MinEnergyHourlyPriceInAHour': MinEnergyHourlyPriceInAHour,

            'ExternalTemperatureAvg': ExternalTemperatureAvg,
            'MaxExternalTemperature': MaxExternalTemperature,
            'MinExternalTemperature': MinExternalTemperature,


            "AccumulatedComfortScore": accumulated_comfort_across_days,
            'ComfortScore': daily_confort_score,


            'Standard_AccumulatedCost': Standard_AccumulatedCost,
            'Standard_AccumulatedEnergyConsumption': Standard_AccumulatedEnergyConsumption,
            
            'Standard_MaxEnergyCostInADay': Standard_MaxEnergyCostInADay,
            'Standard_MinEnergyCostInADay': Standard_MinEnergyCostInADay,
            'Standard_AvgEnergyCostInADay': Standard_AvgEnergyCostInADay,
            
            'Standard_MaxEnergyConsumptionInADay': Standard_MaxEnergyConsumptionInADay,
            'Standard_MinEnergyConsumptionInADay': Standard_MinEnergyConsumptionInADay,
            #avg
            'Standard_EnergyConsumption': Standard_AvgEnergyConsumptionInADay,
            
            'Standard_AvgEnergyHourlyPrice': Standard_AvgEnergyHourlyPrice,
            'Standard_MaxEnergyHourlyPriceInAHour': Standard_MaxEnergyHourlyPriceInAHour,
            'Standard_MinEnergyHourlyPriceInAHour': Standard_MinEnergyHourlyPriceInAHour,
            
            'Standard_ExternalTemperatureAvg': Standard_AvgExternalTemperature,
            'Standard_MaxExternalTemperature': Standard_MaxExternalTemperature,
            'Standard_MinExternalTemperature': Standard_MinExternalTemperature,
            

            'Standard_ComfortScore': standard_daily_confort_score,
            'Standard_AccumulatedComfortScore': standard_accumulated_comfort_across_days
            
            })
        
    return aggreatedresults

def getAggratedData_free(start_date, end_date):
    json_object = get_DataByDay_accumulatePeriod(start_date, end_date)


    policy = generate_Standard_Policy()
    results_policy = simulate_policy_JSON_format_period(policy, start_date, end_date)
    """
    {'day': '2021-12-01',
    'daily_energy_cost': 10.720672,
    'daily_confort_score': 124,
    'daily_energy_comsumption': 44.00000000000001,
    'daily_temperature_avg': 4.942499999999999,
    'daily_avg_energy_price': 0.24720958333333332,
    'accumulated_cost_across_days': 10.720672,
    'accumulated_comsumption_across_days': 44.00000000000001,
    'accumulated_comfort_across_days': 124,
    'max_energy_cost_hour': 0.57096,
    'min_energy_cost_hour': 0.38576,
    'max_energy_comsumption_hour': 2.4,
    'min_energy_comsumption_hour': 1.6}



    {'day': '2021-12-01',
    'daily_energy_cost': 11.185312,
    'daily_confort_score': 132,
    'daily_energy_comsumption': 45.600000000000016,
    'daily_temperature_avg': 4.942499999999999,
    'daily_avg_energy_price': 0.24720958333333332,
    'accumulated_cost_across_days': 11.185312,
    'accumulated_comsumption_across_days': 45.600000000000016,
    'accumulated_comfort_across_days': 132,
    'max_energy_cost_hour': 11.185312,
    'min_energy_cost_hour': 0.69384,
    'max_energy_comsumption_hour': 45.600000000000016,
    'min_energy_comsumption_hour': 2.4}
        """


    aggreatedresults =[]
    for entry in range(len(json_object)):
        day = json_object[entry]['day']
        daily_energy_cost = json_object[entry]['daily_energy_cost']
        daily_confort_score = json_object[entry]['daily_confort_score']
        daily_energy_comsumption = json_object[entry]['daily_energy_comsumption']
        daily_temperature_avg = json_object[entry]['daily_temperature_avg']
        daily_avg_energy_price = json_object[entry]['daily_avg_energy_price']
        accumulated_cost_across_days = json_object[entry]['accumulated_cost_across_days']
        accumulated_comsumption_across_days = json_object[entry]['accumulated_comsumption_across_days']
        accumulated_comfort_across_days = json_object[entry]['accumulated_comfort_across_days']
        max_energy_cost_hour = json_object[entry]['max_energy_cost_hour']
        min_energy_cost_hour = json_object[entry]['min_energy_cost_hour']
        max_energy_comsumption_hour = json_object[entry]['max_energy_comsumption_hour']
        min_energy_comsumption_hour = json_object[entry]['min_energy_comsumption_hour']
        

        AvgEnergyCostInADay= daily_energy_cost/24
        AvgEnergyConsumptionInADay= daily_energy_comsumption/24

        MaxEnergyHourlyPriceInAHour = json_object[entry]['max_energy_price']
        MinEnergyHourlyPriceInAHour =json_object[entry]['min_energy_price']

        MaxExternalTemperature = json_object[entry]['max_temperature']
        MinExternalTemperature =json_object[entry]['min_temperature']

        #policy
        standard_daily_energy_cost = results_policy[entry]['daily_energy_cost']
        standard_daily_confort_score = results_policy[entry]['daily_confort_score']
        standard_daily_energy_comsumption = results_policy[entry]['daily_energy_comsumption']
        standard_daily_temperature_avg = results_policy[entry]['daily_temperature_avg']
        standard_daily_avg_energy_price = results_policy[entry]['daily_avg_energy_price']
        standard_accumulated_cost_across_days = results_policy[entry]['accumulated_cost_across_days']
        standard_accumulated_comsumption_across_days = results_policy[entry]['accumulated_comsumption_across_days']
        standard_accumulated_comfort_across_days = results_policy[entry]['accumulated_comfort_across_days']
        standard_max_energy_cost_hour = results_policy[entry]['max_energy_cost_hour']
        standard_min_energy_cost_hour = results_policy[entry]['min_energy_cost_hour']
        standard_max_energy_comsumption_hour = results_policy[entry]['max_energy_comsumption_hour']
        standard_min_energy_comsumption_hour = results_policy[entry]['min_energy_comsumption_hour']

        Standard_MaxEnergyHourlyPriceInAHour= results_policy[entry]['MaxEnergyCostInADay']
        Standard_MinEnergyHourlyPriceInAHour= results_policy[entry]['MinEnergyCostInADay']

        Standard_MaxExternalTemperature= results_policy[entry]['MaxTemperature']
        Standard_MinExternalTemperature= results_policy[entry]['MinTemperature']

        aggreatedresults.append({
            "Date": day,
            "AccumulatedEnergyConsumption": accumulated_comsumption_across_days,
            "AccumulatedCost": accumulated_cost_across_days,
            'MaxEnergyCostInADay': max_energy_cost_hour,
            'MinEnergyCostInADay': min_energy_cost_hour,
            'AvgEnergyCostInADay': AvgEnergyCostInADay,
            'MaxEnergyConsumptionInADay': max_energy_comsumption_hour,
            'MinEnergyConsumptionInADay': min_energy_comsumption_hour,
            #avg
            'EnergyConsumption': AvgEnergyConsumptionInADay,
            'AvgEnergyHourlyPrice': daily_avg_energy_price,

            'MaxEnergyHourlyPriceInAHour': MaxEnergyHourlyPriceInAHour,
            'MinEnergyHourlyPriceInAHour': MinEnergyHourlyPriceInAHour,
            
            'ExternalTemperatureAvg': daily_temperature_avg,
            'MaxExternalTemperature': MaxExternalTemperature,
            'MinExternalTemperature': MinExternalTemperature,


            #TODO: add on weekly endpoint
            "AccumulatedComfortScore": accumulated_comfort_across_days,
            'ComfortScore': daily_confort_score,
            ####


            'Standard_AccumulatedCost': standard_accumulated_cost_across_days,
            'Standard_AccumulatedEnergyConsumption': standard_accumulated_comsumption_across_days,


            'Standard_MaxEnergyCostInADay': standard_max_energy_cost_hour,
            'Standard_MinEnergyCostInADay': standard_min_energy_cost_hour,
            'Standard_AvgEnergyCostInADay': standard_daily_energy_cost/24,


            'Standard_MaxEnergyConsumptionInADay': standard_max_energy_comsumption_hour,
            'Standard_MinEnergyConsumptionInADay': standard_min_energy_comsumption_hour,
            #avg
            'Standard_EnergyConsumption': standard_daily_energy_comsumption/24,



            'Standard_AvgEnergyHourlyPrice': standard_daily_avg_energy_price,
            'Standard_MaxEnergyHourlyPriceInAHour': Standard_MaxEnergyHourlyPriceInAHour,
            'Standard_MinEnergyHourlyPriceInAHour': Standard_MinEnergyHourlyPriceInAHour,


            'Standard_ExternalTemperatureAvg': standard_daily_temperature_avg,
            'Standard_MaxExternalTemperature': Standard_MaxExternalTemperature,
            'Standard_MinExternalTemperature': Standard_MinExternalTemperature,

            "Standard_ComfortScore": standard_daily_confort_score,
            "Standard_AccumulatedComfortScore": standard_accumulated_comfort_across_days
            

            })


    return aggreatedresults





#main
def main():
    start_date='2021-12-01'
    end_date='2021-12-31'

    results = get_data_from_multiple_days(start_date, end_date)
    printResults(results)
    json_object = create_json_object(results, start_date)
    #save json object to file as pretify json
    with open('data/ourData.json', 'w') as outfile:
        json.dump(json_object, outfile, indent=4)

if __name__ == "__main__":
    main()