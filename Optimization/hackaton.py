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
        print("Policy: ", results[i][0])
        print("Electricity Cost (euros): ", results[i][1])
        print("Confort Score: ", results[i][2])
        print("Accumulated Comfort Score: ", results[i][3])
        print("Atual Cost: ", results[i][4])
        print("Accumulated Cost: ", results[i][5])
        print("Atual Consumption: ", results[i][6])
        print("Accumulated Consumption: ", results[i][7])
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
                'Accumulated_daily_comfort_score_until_that_hour': Accumulated_daily_energy_cost_until_that_hour,
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

def printResults(results):
    #results is a list of results for each day
    #prints the results for each day
    for i in range(len(results)):
        print("Day: ", i+1)
        print("Policy: ", results[i][0])
        print("Electricity Cost (euros): ", results[i][1])
        print("Confort Score: ", results[i][2])
        print("Accumulated Comfort Score: ", results[i][3])
        print("Atual Cost: ", results[i][4])
        print("Accumulated Cost: ", results[i][5])
        print("Atual Consumption: ", results[i][6])
        print("Accumulated Consumption: ", results[i][7])
        print("")

    

def get_temperature_array_from_api(start_date):
    response = requests.get("http://localhost:5002/?start_date="+start_date+"&end_date="+start_date)
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


def simulate_policy_JSON_format(policy, date):
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
        json_object.append({
                    'hour': i,
                    'day': date,
                    "mode": policy[i],
                    'Energy_cost_for_that_complete_day': accumulated_cost[-1],
                    'accumulated_energy_cost_that_hour': accumulated_cost[i],
                    'Energy_cost_for_that_hour': cost[i],
                    'Accumulated_daily_comfort_score_until_that_hour': accumulated_comfort[i],
                    'Consumption_for_that_hour': comsumption[i],
                    'Accumulated_daily_consumption_until_that_hour': accumulated_comsumption[i],
                    'Comfort_score_for_that_complete_day': accumulated_comfort[-1],
                    'Accumulated_daily_comfort_score_until_that_hour': accumulated_comfort[i],
                    'exterior_temperature': temperature_array[i],
                    'energy_price': energy_cost_array[i]
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