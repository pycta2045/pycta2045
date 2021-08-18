import pybamm

model = pybamm.lithium_ion.DFN()
sim = pybamm.Simulation(model)
x = sim.solve([0,3600])
print(help(x))

