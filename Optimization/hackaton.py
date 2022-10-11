from scipy.optimize import linprog
import numpy as np
import math
from electricity_prices import read_prices
from datetime import datetime, timedelta
import json
import pandas as pd

def OptimizeCost(Weights, consumptionForEachWeight, temperature_array, minumum_confort_score=124):
    """inputs:
    Weights: list of weights for each hour
    contraints: list of contraints
    bounds: list of bounds
    integrality: 1 : Integer variable; decision variable must be an integer within bounds."""



    lhs_eq = [[1, 1, 1]+[0]*69, [0]*3+[1]*3+[0]*66, [0]*6+[1]*3+[0]*63, [0]*9+[1]*3+[0]*60, [0]*12+[1]*3+[0]*57, [0]*15+[1]*3+[0]*54, [0]*18+[1]*3+[0]*51, [0]*21+[1]*3+[0]*48, [0]*24+[1]*3+[0]*45, [0]*27+[1]*3+[0]*42, [0]*30+[1]*3+[0]*39, [0]*33+[1]*3+[0]*36, [0]*36+[1]*3+[0]*33, [0]*39+[1]*3+[0]*30, [0]*42+[1]*3+[0]*27, [0]*45+[1]*3+[0]*24, [0]*48+[1]*3+[0]*21, [0]*51+[1]*3+[0]*18, [0]*54+[1]*3+[0]*15, [0]*57+[1]*3+[0]*12, [0]*60+[1]*3+[0]*9, [0]*63+[1]*3+[0]*6, [0]*66+[1]*3+[0]*3, [0]*69+[1]*3]
    rhs_eq = [1]*24

    lhs_ineq = [[0, -4, -8, 0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8,0, -4, -8]]
    rhs_ineq = [-minumum_confort_score]

    bounds = [(0,1) for i in range(72)]
    integrality = [1 for i in range(72)]

    opt = linprog(c=Weights, A_ub=lhs_ineq, b_ub=rhs_ineq,
              A_eq=lhs_eq, b_eq=rhs_eq, bounds=bounds, integrality=integrality,
              method="highs")

    #find if its eco, off or conf and conver to string 
    policy = np.array(opt['x']).reshape(24,3).argmax(axis=1)
    #convert array number to off, eco or confort
    policy = np.vectorize(lambda x: 'off' if x == 0 else 'eco' if x == 1 else 'conf')(policy)
    
    cost = opt['fun']
    score = np.array(minumum_confort_score)+opt['ineqlin']['residual'][0]
    
    #comfort score accumulated across the day
    accumulated_comfort_score = [8 if policy[i] == 'conf' else 4 if policy[i] == 'eco' else 0 for i in range(24)]
    for i in range(1,24):
        accumulated_comfort_score[i] = accumulated_comfort_score[i-1]+accumulated_comfort_score[i]
    
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
       

    return policy, cost, score, accumulated_comfort_score, atual_cost, accumulated_cost, atual_comsumption, accumulated_comsumption, temperature_array

def calculateWeights(temperature_array, energy_cost_array):
    #Temperature array is the temperature for each hour of the day
    #Energy cost array is the cost of energy for each hour of the day

    #calculate the weights for each hour
    weights = []
    comsumption = []
    modes = ['off', 'eco', 'conf']
    for i in range(len(temperature_array)):
        for mode in modes:
            external_temp = temperature_array[i]
            if mode == 'off':
                #1KW/hour regardless of temperature
                weights.append(energy_cost_array[i]*1)
                comsumption.append(1)
            elif mode == 'eco':
                if external_temp < 10:
                    #1.6KW/hour
                    weights.append(energy_cost_array[i]*1.6)
                    comsumption.append(1.6)
                elif external_temp >= 10 and external_temp <= 20:
                    #0.8KW/hour
                    weights.append(energy_cost_array[i]*0.8)
                    comsumption.append(0.8)
                elif external_temp > 20:
                    #0.4KW/hour
                    weights.append(energy_cost_array[i]*0.4)
                    comsumption.append(0.4)
            elif mode == 'conf':

                if external_temp < 0:
                    #2.4KW/hour+9KW/hour
                    weights.append(energy_cost_array[i]*(2.4+9))
                    comsumption.append(2.4+9)
                elif external_temp < 10:
                    #2.4KW/hour
                    weights.append(energy_cost_array[i]*2.4)
                    comsumption.append(2.4)
                elif external_temp >= 10 and external_temp <= 20:
                    #1.6KW/hour
                    weights.append(energy_cost_array[i]*1.6)
                    comsumption.append(1.6)
                elif external_temp > 20:
                    #0.8KW/hour
                    weights.append(energy_cost_array[i]*0.8)
                    comsumption.append(0.8)
    return weights, comsumption
    
        
     

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


#function to optimize cost for multiple days
def get_data_from_multiple_days(start_date, end_date):
    #start_date and end_date are strings in the format '2021-12-01'
    #returns a list of results for each day
    results = []
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    for i in range((end_date-start_date).days+1):
        date = start_date + pd.Timedelta(days=i)
        temperature_array = get_temperature_array(date)
        energy_array = get_energy_array(date)
        weights, consumption = calculateWeights(temperature_array, energy_array)
        results.append(OptimizeCost(weights, consumption, temperature_array, minumum_confort_score=124))
    return results

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
        weights, consumption = calculateWeights(temperature_array, energy_array)
        results.append(OptimizeCost(weights, consumption, temperature_array, minumum_confort_score=124))
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
        weights, consumption = calculateWeights(temperature_array, energy_array)
        results.append(OptimizeCost(weights, consumption, temperature_array, minumum_confort_score=124))
    return results
    
def create_json_object(results, start_date):
    #results is a list of results from get_data_from_multiple_days
    #start_date is a string in the format '2021-12-01'
    #returns a json object with the structure described above
    start_date = pd.to_datetime(start_date)
    json_object = []
    for i in range(len(results)):
        date = start_date + pd.Timedelta(days=i)
        
        hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        
        accumulated_cost_per_hour = results[i][4]
        for i in range(1, len(accumulated_cost_per_hour)):
            accumulated_cost_per_hour[i] = accumulated_cost_per_hour[i]+accumulated_cost_per_hour[i-1]


        for hour in hours:
            #hour
            Mode_for_that_hour = results[i][0][hour]
            Energy_cost_for_that_complete_day = results[i][1]
            Comfort_score_for_that_complete_day = results[i][2]
            Accumulated_daily_comfort_score_until_that_hour = results[i][3][hour]
            Energy_cost_for_that_hour = results[i][4][hour]
            accumulated_energy_cost_that_hour = accumulated_cost_per_hour[hour]
            Accumulated_daily_energy_cost_until_that_hour = results[i][5][hour]
            Consumption_for_that_hour = results[i][6][hour]
            Accumulated_daily_consumption_until_that_hour = results[i][7][hour]
            
            exterior_temperature = results[i][8][hour]


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
                'exterior_temperature': exterior_temperature.tolist()
            })
        
    return json_object

#main
def main():
    start_date='2021-12-01'
    end_date='2021-12-31'

    results = get_data_from_multiple_days(start_date, end_date)
    json_object = create_json_object(results, start_date)

    print("1st day Policy :", results[0][9])


if __name__ == "__main__":
    main()