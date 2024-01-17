import opendssdirect as dss
import pygad
from tabulate import tabulate
import sys
import logging
logging.basicConfig(level=logging.WARNING)


# Load dss file
dss.Text.Command('Redirect ieee13.dss')

def simulate(new_buses, new_kvars):
    edit_cap(new_buses, new_kvars)
    dss.Solution.Solve()
    node_voltages = dss.Circuit.AllBusMagPu()
    return node_voltages

def edit_cap(new_buses, new_kvars):
    for i in range(len(new_buses)):
        dss.Text.Command(f'Edit Capacitor.cap{i+1} bus1={new_buses[i]} kvar={new_kvars[i]}')


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


def split_solution(solution):
    new_buses = [bus for i,bus in enumerate(solution) if i%2 == 0]
    new_kvars = [kvar for i,kvar in enumerate(solution) if i%2 != 0]
    return new_buses, new_kvars


def fitness_func(ga_instance, solution, solution_idx):
    new_buses, new_kvars = split_solution(solution)
    nominal_voltage = 1
    node_voltages = simulate(new_buses, new_kvars)
    
    # Calculate the mean squared error
    mse = sum((v - nominal_voltage) ** 2 for v in node_voltages) / len(node_voltages)
    
    total_kvar = sum(kvar for kvar in new_kvars)
    
    return [1/mse, 1/total_kvar] #minimize the mse and total kvar
    # return 1/mse


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

    kvar_space = [25, 50, 75, 100, 150, 200, 300, 400, 500, 600]
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
    mutation_num_genes=1
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
    print("Fitness: ", solution_fitness)
    # ga_instance.plot_fitness()

    display_voltages(solution)
    print("Total kvar: ", sum(cap_kvars))

    
    




