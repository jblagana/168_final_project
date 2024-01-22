import opendssdirect as dss
import pygad
from tabulate import tabulate
import sys
import logging
import numpy as np
logging.basicConfig(level=logging.WARNING)


# Load dss file
dss.Text.Command('Redirect ieee13.dss')

def simulate(new_buses, new_kvars):
    edit_cap(new_buses, new_kvars)
    dss.Solution.Solve()
    node_voltages = dss.Circuit.AllBusMagPu()
    return node_voltages

def edit_cap(new_buses, new_kvars):
    all_caps = dss.Capacitors.AllNames()
    for i, cap in enumerate(all_caps):
        dss.Text.Command(f'Edit Capacitor.{cap} bus1={new_buses[i]} kvar={new_kvars[i]}')


def display_voltages(solution):
    new_buses, new_kvars = split_solution(solution)

    dss.Text.Command('Redirect ieee13.dss')
    simulate(new_buses, new_kvars)
    node_names = dss.Circuit.AllNodeNames()
    node_voltages = [round(v, 6) for v in dss.Circuit.AllBusMagPu()]  # round to 6 decimal places

    min_voltage = min(node_voltages)
    max_voltage = max(node_voltages)

    node_voltages[node_voltages.index(min_voltage)] = f"**{min_voltage}**"
    node_voltages[node_voltages.index(max_voltage)] = f"**{max_voltage}**"

    data = list(zip(node_names, node_voltages))

    table = tabulate(data, headers=['Node', 'Voltage (p.u.)'], tablefmt='fancy_grid')
    print(table)


def display_loss(solution):
    new_buses, new_kvars = split_solution(solution)

    dss.Text.Command('Redirect ieee13.dss')
    simulate(new_buses, new_kvars)
    loss = dss.Circuit.Losses()
    print("Total Losses: ", loss)
    


def split_solution(solution):
    new_buses = [bus for i,bus in enumerate(solution) if i%2 == 0]
    new_kvars = [kvar for i,kvar in enumerate(solution) if i%2 != 0]
    return new_buses, new_kvars


def fitness_func(ga_instance, solution, solution_idx):
    V_thresh = 0.95
    new_buses, new_kvars = split_solution(solution)
    nominal_voltage = 1
    node_voltages = simulate(new_buses, new_kvars)
    cost_list = cap_costs(new_kvars)
    
    # mse_list = [(v - nominal_voltage) ** 2 for v in node_voltages]
    # min_mse = min(mse_list)
    # max_mse = max(mse_list)
    # nmse = sum((mse - min_mse)/(max_mse - min_mse) for mse in mse_list) / len(node_voltages)

    # cost_mse_list = [(1 - (cost/45000 - 1) ** 2) for cost in cost_list]
    # min_cost_mse = min(cost_mse_list)
    # max_cost_mse = max(cost_mse_list)
    # cost_nmse = sum((cost_mse - min_cost_mse)/(max_cost_mse+0.00000001 - min_cost_mse) for cost_mse in cost_mse_list) / len(node_voltages)


    # Calculate the mean squared error
    mse_voltage = sum((v - nominal_voltage) ** 2 for v in node_voltages) / len(node_voltages)
    mse_cost = 1 - sum((c/45000 - 1) ** 2 for c in cost_list) / len(cost_list)
    
    
    # if min(node_voltages) >= V_thresh:
    #     fitness = (1/mse_voltage)+(1/(1-mse_cost))+2000
    # else:
    #     fitness = (1/mse_voltage)+(1/(1-mse_cost))
    # return fitness
    # nmse_v = mse_voltage/0.1
    # nmse_c = (mse_cost-0.7)/0.3
    # minimize the mse and total cost
    # return 1/mse_voltage
    # print("mse: ", 1/mse_voltage, "cost: ", 1/mse_cost)
    return 1/mse_voltage + 1/mse_cost


def cap_costs(new_kvars):
    cost =  {25:20000.00, 50:35000.00, 75:30000.00, 100:35000.00, 150:38000.00, 200:45000.00}
    cap_costs = []
    for kvar in new_kvars:
        cap_costs.append(cost[kvar])
    return cap_costs


def on_generation(ga_instance):
    label = f"{ga_instance.generations_completed}/{ga_instance.num_generations}"
    progress = ga_instance.generations_completed / ga_instance.num_generations
    progress_bar_len = 50
    filled_len = int(progress_bar_len * progress)
    bar = '=' * filled_len + '-' * (progress_bar_len - filled_len)
    sys.stdout.write(f'\rGeneration progress: [{bar}] {progress * 100:.1f}% [{label}]')
    sys.stdout.flush()


def gene_space():
    cap_num = len(dss.Capacitors.AllNames())

    # Get bus space
    bus_space = []
    buses = dss.Circuit.AllNodeNames()
    for bus in buses:
        try:
            bus_space.append(float(bus))
        except ValueError:
            continue

    kvar_space = [25, 50, 75, 100, 150, 200]
    # kvar_space = {"low": 0, "high":1800}

    gene_space = []
    for _ in range(cap_num):
        gene_space.append(bus_space)
        gene_space.append(kvar_space)

    return gene_space


ga_instance = pygad.GA(
    num_generations=1000,
    num_parents_mating=25,
    fitness_func=fitness_func,
    sol_per_pop=50,
    num_genes=len(gene_space()),
    gene_space=gene_space(),
    on_generation=on_generation,
)


if __name__ == "__main__":
    print('\n')
    ga_instance.run()
    solution, solution_fitness, solution_idx = ga_instance.best_solution()

    cap_names = dss.Capacitors.AllNames()
    cap_locations, cap_kvars = split_solution(solution)
    data = list(zip(cap_names, cap_locations, cap_kvars))
    print('\n')

    table = tabulate(data, headers=['Capacitor', 'Optimal Location', 'kvar'], tablefmt='fancy_grid')
    print(table)
    # ga_instance.plot_fitness()

    display_voltages(solution)
    print("Total cost in PHP: ", sum(cap_costs(cap_kvars)))
    display_loss(solution)
    print("Fitness: ", solution_fitness)

    
    




