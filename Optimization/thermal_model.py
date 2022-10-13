from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from scipy.optimize import minimize

import numpy as np

from hackaton import get_energy_array_from_api, get_temperature_array_from_api
from ExternalAPI.electricity_prices import read_prices


def simulate(prices, out_temps, modes, storage=True):

    if storage:
        power_modes = modes[:int(len(modes)/2)]
        storage_modes = modes[int(len(modes)/2):]
    else:
        power_modes = modes
        storage_modes = [0] * len(modes)

    heat_capacity_room = 1000
    heat_loss_coef = 200
    base_power = 1000
    min_heater_power = 100
    heat_transfer_coef = 200
    reservoir_capacity = 5000

    room_temp = 15
    current_reservoir_energy = 0
    max_reservoir_charge_rate = 1000
    max_reservoir_discharge_rate = 1000

    # https://heatpumps.co.uk/heat-pump-information-without-the-hype/what-is-the-cop/
    COP_at_45 = 3
    COP_coef = 2.5/30

    room_temps = []
    costs = []
    reservoir_energy = []
    power_transfered = []
    power_input = []
    power_stored = []

    for price, out_temp, power_mode, storage_mode in zip(prices, out_temps, power_modes, storage_modes):

        heat_loss = heat_loss_coef * (room_temp - out_temp)

        # Calculate power stored without passing the reservoir limits
        power_stored_aux = max(min(storage_mode * base_power, max_reservoir_charge_rate), -max_reservoir_discharge_rate)  # Withing charge/discharge rates
        prev_reservoir_energy = current_reservoir_energy
        current_reservoir_energy = max(min(prev_reservoir_energy + power_stored_aux, reservoir_capacity), 0)  # Within capacity
        current_power_stored = current_reservoir_energy - prev_reservoir_energy

        current_power_input = max(power_mode * base_power, min_heater_power)
        current_power_transfered = current_power_input + current_power_stored

        # 2 Equations on 2 variables:
        # heat_pumped = current_power_input * (COP_at_45 - COP_coef * (heater_temperature - out_temp - 45))  
        # heater_temperature = room_temp + heat_pumped / heat_transfer_coef

        # With some manipulation:
        heat_pumped = current_power_input * (COP_at_45 - COP_coef * (room_temp - out_temp - 45)) / (1 + current_power_input * COP_coef / heat_transfer_coef)
        
        room_temp -= heat_loss / heat_capacity_room
        room_temp += heat_pumped / heat_capacity_room

        room_temps.append(room_temp)
        costs.append(price * current_power_transfered / 1000)

        reservoir_energy.append(current_reservoir_energy / 1000)
        power_transfered.append(current_power_transfered / 1000)
        power_input.append(current_power_input / 1000)
        power_stored.append(current_power_stored / 1000)

    return {
        "room_temps": room_temps,
        "costs": costs,
        "power_modes": power_modes,
        "storage_modes": storage_modes,
        "reservoir_energy": reservoir_energy,
        "power_transfered": power_transfered,
        "power_input": power_input,
        "power_stored": power_stored,
    }


def temperature_contraints(
    room_temps, 
    not_home_hours, 
    sleep_hours,
    low_deviation_cost = 2,
    high_deviation_cost = 1,
):

    not_home_min_temperature = 18
    sleep_min_temperature = 22
    at_home_min_temperature = 25

    loss = 0
    min_temps = []
    for rt, nh, s in zip(room_temps, not_home_hours, sleep_hours):
        if nh:
            if rt < not_home_min_temperature:
                loss += low_deviation_cost * (not_home_min_temperature - rt)**2
            else:
                loss += high_deviation_cost * (rt - not_home_min_temperature)**2
            min_temps.append(not_home_min_temperature)
        elif s:
            if rt < sleep_min_temperature:
                loss += low_deviation_cost * (sleep_min_temperature - rt)**2
            else:
                loss += high_deviation_cost * (rt - sleep_min_temperature)**2
            min_temps.append(sleep_min_temperature)
        else:
            if rt < at_home_min_temperature:
                loss += low_deviation_cost * (at_home_min_temperature - rt)**2
            else:
                loss += high_deviation_cost * (rt - at_home_min_temperature)**2
            min_temps.append(at_home_min_temperature)

    return loss, min_temps


def print_results(solution, prices, out_temps, not_home_hours, sleep_hours, storage=True):
    results = simulate(prices, out_temps, solution, storage)
    _, min_temps = temperature_contraints(results["room_temps"], not_home_hours, sleep_hours)

    plt.plot(out_temps, label="Outside Temperature [ºC]")
    plt.plot(results["room_temps"], label="Room Temperature [ºC]")
    plt.plot(min_temps, label="Target Temperature [ºC]")
    plt.legend()
    plt.grid()
    plt.show()

    plt.plot(results["power_input"], label="Heating Power [kW]")
    if storage:
        plt.plot(results["power_transfered"], label="Power Demanded [kW]")
        plt.plot(results["power_stored"], label="Power Stored [kW]")
        plt.plot(results["reservoir_energy"], label="Stored Energy [kWh]")
    plt.plot(prices, label="Electricty Price [€/kWh]")
    plt.legend()
    plt.grid()
    plt.show() 

    return results


def get_thermal_model_DataByDay(start_date, end_date, storage, flexible):

    prices = np.concatenate(get_energy_array_from_api(start_date, end_date)).tolist()
    out_temps =  get_temperature_array_from_api(start_date, end_date)

    num_days = (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)).days + 1

    init_power_modes = ([1] * 24) * num_days
    init_storage_modes = ([0.2] * 12 + [-0.2] * 12) * num_days
    init_modes = init_power_modes + init_storage_modes

    not_home_hours = ([0] * 9 + [1] * 10 + [0] * 5) * num_days
    sleep_hours = ([1] * 7 + [0] * 17) * num_days

    if flexible:
        low_deviation_cost = 0.01
        high_deviation_cost = 0.002
    else:
        low_deviation_cost = 2
        high_deviation_cost = 1

    if storage:
        def objective(modes):
            results = simulate(prices, out_temps, modes.tolist())
            temperature_deviations_cost, _ = temperature_contraints(results["room_temps"], not_home_hours, sleep_hours, low_deviation_cost, high_deviation_cost)
            return sum(results["costs"]) + temperature_deviations_cost

        solution = minimize(objective, tuple(init_modes), options={"maxiter": 1e8}).x.tolist()
    else:
        def objective(modes):
            results = simulate(prices, out_temps, modes.tolist(), storage=False)
            temperature_deviations_cost, _ = temperature_contraints(results["room_temps"], not_home_hours, sleep_hours, low_deviation_cost, high_deviation_cost)
            return sum(results["costs"]) + temperature_deviations_cost

        solution = minimize(objective, tuple(init_power_modes), options={"maxiter": 1e8}).x.tolist()
       
    results = simulate(prices, out_temps, solution, storage)
    _, min_temps = temperature_contraints(results["room_temps"], not_home_hours, sleep_hours)

    results["min_temps"] = min_temps
    results["accumulated_costs"] = np.cumsum(np.array(results["costs"]))

    results["day"] = [start_date] * 24
    results["hour"] = list(range(24))
    date = datetime.fromisoformat(start_date)
    date_end = datetime.fromisoformat(end_date)
    while date != date_end:
        date += timedelta(days=1)
        results["day"] += [date.strftime("%Y-%m-%d")] * 24
        results["day"] += list(range(24))

    return [dict(zip(results.keys(), t)) for t in zip(*results.values())]  # Convert Dict of Lists into List of Dicts


if __name__ == "__main__":

    num_days = 3

    t0 = datetime.fromisoformat('2021-12-03')
    t1 = t0 + timedelta(days=num_days)

    prices = np.concatenate(read_prices(t0, t1))[:24 * num_days].tolist()
    out_temps = (10 - 5 * np.sin(np.arange(24 * num_days) * 2 * np.pi / 24)).tolist()

    init_power_modes = ([1] * 24) * num_days
    init_storage_modes = ([0.2] * 12 + [-0.2] * 12) * num_days
    init_modes = init_power_modes + init_storage_modes

    not_home_hours = ([0] * 9 + [1] * 10 + [0] * 5) * num_days
    sleep_hours = ([1] * 7 + [0] * 17) * num_days


    # With Storage + Flexible

    low_deviation_cost = 0.01
    high_deviation_cost = 0.002

    def objective(modes):
        results = simulate(prices, out_temps, modes.tolist())
        temperature_deviations_cost, _ = temperature_contraints(results["room_temps"], not_home_hours, sleep_hours, low_deviation_cost, high_deviation_cost)
        return sum(results["costs"]) + temperature_deviations_cost
    solution = minimize(objective, tuple(init_modes), options={"maxiter": 1e8}).x.tolist()
    flexible_storage_optimized_costs = print_results(solution, prices, out_temps, not_home_hours, sleep_hours)["costs"]



    # With Storage

    def objective(modes):
        results = simulate(prices, out_temps, modes.tolist())
        temperature_deviations_cost, _ = temperature_contraints(results["room_temps"], not_home_hours, sleep_hours)
        return sum(results["costs"]) + temperature_deviations_cost

    solution = minimize(objective, tuple(init_modes), options={"maxiter": 1e8}).x.tolist()
    storage_optimized_costs = print_results(solution, prices, out_temps, not_home_hours, sleep_hours)["costs"]


    # Without Storage

    def objective(modes):
        results = simulate(prices, out_temps, modes.tolist(), storage=False)
        temperature_deviations_cost, _ = temperature_contraints(results["room_temps"], not_home_hours, sleep_hours)
        return sum(results["costs"]) + temperature_deviations_cost

    solution = minimize(objective, tuple(init_power_modes), options={"maxiter": 1e8}).x.tolist()
    optimized_costs = print_results(solution, prices, out_temps, not_home_hours, sleep_hours, storage=False)["costs"]


    # Fixed power schedule

    naive_costs = print_results(init_power_modes, prices, out_temps, not_home_hours, sleep_hours, storage=False)["costs"]


    # Comparison

    plt.plot(np.cumsum(np.array(naive_costs)), label="Accumulated Cost Naive [€]")
    plt.plot(np.cumsum(np.array(optimized_costs)), label="Accumulated Cost Optimized [€]")
    plt.plot(np.cumsum(np.array(storage_optimized_costs)), label="Accumulated Cost Optimized + Storage [€]")
    plt.plot(np.cumsum(np.array(flexible_storage_optimized_costs)), label="Accumulated Cost Optimized + Storage + Flexible [€]")
    plt.legend()
    plt.grid()
    plt.show()

