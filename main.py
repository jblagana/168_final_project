import random
import opendssdirect as dss

dss.Text.Command('Redirect ieee13.dss')

# Define your GA parameters
POPULATION_SIZE = 100
GENERATIONS = 50


bus_phases = []
for bus in dss.Circuit.AllBusNames():
    num_phases = dss.Bus.NPhases(bus)

    for phase in range(1, num_phases + 1):
        bus_phases.append(f"{bus}.{phase}")

# Print the list of bus names with their phases
print(bus_phases)


# # Define your network parameters
# BUS_NUMBERS = [1, 2, 3, 4, 5]  # replace with your actual bus numbers

# # Define the fitness function
# def fitness(bus1, bus2):
#     # Edit the DSS file with the new capacitor locations
#     # This is a placeholder, replace with your actual DSS editing code
#     edit_dss_file(bus1, bus2)

#     # Run the OpenDSS simulation
#     dss.run_command("Solve")

#     # Get the bus voltages and total power loss
#     voltages = dss.Circuit.AllBusVmagPu()
#     losses = dss.Circuit.Losses()[0]

#     # Compute the fitness value based on your criteria
#     # This is a placeholder, replace with your actual fitness computation
#     fitness_value = compute_fitness(voltages, losses)

#     return fitness_value

# # Define the GA
# population = [(random.choice(BUS_NUMBERS), random.choice(BUS_NUMBERS)) for _ in range(POPULATION_SIZE)]

# for generation in range(GENERATIONS):
#     # Evaluate the fitness of the population
#     fitness_values = [fitness(bus1, bus2) for bus1, bus2 in population]

#     # Select the best individuals, crossover, mutate, etc.
#     # This is a placeholder, replace with your actual GA operations
#     population = perform_ga_operations(population, fitness_values)
