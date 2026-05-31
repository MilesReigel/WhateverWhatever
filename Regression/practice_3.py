# Practice learning PySR library

import numpy as np
from pysr import PySRRegressor
import matplotlib.pyplot as plt
import time

start_time = time.perf_counter()
print(f"PySR optimization started at time stamp{start_time: .3f}")

X = 3 * np.random.randn(50, 6)
y = (8.445 * np.sin(X[:, 5])) - (X[:, 3] ** 4) + (3 / X[:, 0]) + 4

model = PySRRegressor(
    # warm_start = True,
    niterations = 10000000,
    population_size = 50,
    populations = 8,
    maxsize = 40,
    maxdepth = 5,
    weight_randomize = 0.1,
    ncycles_per_iteration = 400,
    complexity_of_constants = 2,
    early_stop_condition = ("stop_if(loss, complexity) = (complexity < 21 && loss < 1e-10) || (complexity < 16 && loss < 1e-3)"),
    timeout_in_seconds = 3600,
    binary_operators = ["+", "-", "*", "/"],
    unary_operators = ["cos", "sin", "exp", "square",],
    constraints = {"square": 5, "cube": 5, "exp": 5,},
    nested_constraints = {
        "square": {"square": 1, "sin": 2, "cos": 2, "exp": 1},
        "sin": {"square": 1, "sin": 2, "cos": 2, "exp": 1},
        "cos": {"square": 1, "sin": 2, "cos": 2, "exp": 1},
        "exp": {"square": 1, "sin": 2, "cos": 2, "exp": 1},},
    turbo = True,
    elementwise_loss = "loss(prediction, target) = (prediction - target)^4",
)

model.fit(X, y)

end_time = time.perf_counter()
exec_time = end_time - start_time
print(f"Finished execution at{end_time: .3f}")
print(f"Execution time: {exec_time: .3f}s")

print(model)
