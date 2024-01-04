import opendssdirect as dss
import pygad
from tabulate import tabulate
import sys
import logging
logging.basicConfig(level=logging.WARNING)


# Load dss file
dss.Text.Command('Redirect ieee13.dss')

def simulate(new_buses):
    edit_cap_loc(new_buses)
    dss.Solution.Solve()
    node_voltages = dss.Circuit.AllBusMagPu()
    return node_voltages

def edit_cap_loc(new_buses):
    cap_names = dss.Capacitors.AllNames()

    for i, cap in enumerate(cap_names):
        dss.Text.Command(f'Edit Capacitor.{cap} bus1={new_buses[i]}')

def fitness_func(ga_instance, solution, solution_idx):
    str_solution = [str_gene_space[int(gene)] for gene in solution]
    nominal_voltage = 1
    node_voltages = simulate(str_solution)
    # Calculate the mean squared error
    mse = sum((v - nominal_voltage) ** 2 for v in node_voltages) / len(node_voltages)
    return mse


def on_generation(ga_instance):
    label = f"{ga_instance.generations_completed}/{ga_instance.num_generations}"
    progress = ga_instance.generations_completed / ga_instance.num_generations
    progress_bar_len = 50
    filled_len = int(progress_bar_len * progress)
    bar = '=' * filled_len + '-' * (progress_bar_len - filled_len)
    sys.stdout.write(f'\rGeneration progress: [{bar}] {progress * 100:.1f}% [{label}]')
    sys.stdout.flush()  # Ensure the output is displayed immediately

# Define the GA parameters
str_gene_space = dss.Circuit.AllNodeNames()
gene_space = [list(range(len(str_gene_space)))]*2   # Map the strings to integers

ga_instance = pygad.GA(
    num_generations=500,
    num_parents_mating=25,
    fitness_func=fitness_func,
    sol_per_pop=50,
    num_genes=2,
    gene_space=gene_space,
    on_generation=on_generation,
    mutation_num_genes=1
)

print('\n')
ga_instance.run()
solution, solution_fitness, solution_idx = ga_instance.best_solution()
str_solution = [str_gene_space[int(gene)] for gene in solution]

cap_names = dss.Capacitors.AllNames()
cap_locations = str_solution
data = list(zip(cap_names, cap_locations))
print('\n')

table = tabulate(data, headers=['Capacitor', 'Optimal Location'], tablefmt='fancy_grid')
print(table)




