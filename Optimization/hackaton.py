from scipy.optimize import linprog
import numpy as np
import math
from electricity_prices import read_prices
from datetime import datetime, timedelta
import json
import pandas as pd

def OptimizeCost(Weights, minumum_confort_score=124):
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
    return policy, cost, score

def calculateWeights(temperature_array, energy_cost_array):
    #Temperature array is the temperature for each hour of the day
    #Energy cost array is the cost of energy for each hour of the day

    #calculate the weights for each hour
    weights = []
    modes = ['off', 'eco', 'conf']
    for i in range(len(temperature_array)):
        for mode in modes:
            external_temp = temperature_array[i]
            if mode == 'off':
                #1KW/hour regardless of temperature
                weights.append(energy_cost_array[i]*1)
            elif mode == 'eco':
                if external_temp < 10:
                    #1.6KW/hour
                    weights.append(energy_cost_array[i]*1.6)
                elif external_temp >= 10 and external_temp <= 20:
                    #0.8KW/hour
                    weights.append(energy_cost_array[i]*0.8)
                elif external_temp > 20:
                    #0.4KW/hour
                    weights.append(energy_cost_array[i]*0.4)
            elif mode == 'conf':

                if external_temp < 0:
                    #2.4KW/hour+9KW/hour
                    weights.append(energy_cost_array[i]*(2.4+9))
                elif external_temp < 10:
                    #2.4KW/hour
                    weights.append(energy_cost_array[i]*2.4)
                elif external_temp >= 10 and external_temp <= 20:
                    #1.6KW/hour
                    weights.append(energy_cost_array[i]*1.6)
                elif external_temp > 20:
                    #0.8KW/hour
                    weights.append(energy_cost_array[i]*0.8)
    return weights
    
        

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

#main
def main():
    date = '2021-12-01'
    temperature_array = get_temperature_array(date)
    energy_array = get_energy_array(date)
    results = OptimizeCost(calculateWeights(temperature_array, energy_array), minumum_confort_score=124)

    print("Policy: ", results[0])
    print("Electricity Cost (euros): ", results[1])
    print("Confort Score: ", results[2])

if __name__ == "__main__":
    main()