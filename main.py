import opendssdirect as dss
import pygad

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
    nominal_voltage = 1
    node_voltages = simulate(solution)
    # Calculate the mean squared error
    mse = sum((v - nominal_voltage) ** 2 for v in node_voltages) / len(node_voltages)
    return mse


# Define the GA parameters
ga_instance = pygad.GA(
    num_generations=10,
    num_parents_mating=5,
    fitness_func=fitness_func,
    sol_per_pop=10,
    num_genes=2,
    gene_space=[dss.Circuit.AllNodeNames()]*2
)

ga_instance.run()
solution, solution_fitness, solution_idx = ga_instance.best_solution()
print("Best solution : ", solution)
print("Best solution fitness : ", solution_fitness)