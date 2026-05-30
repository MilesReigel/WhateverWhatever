# Practice learning PySR library

import numpy as np
from pysr import PySRRegressor
import matplotlib.pyplot as plt

X = 3 * np.random.randn(50, 7)
y = (8.445 * np.sin(X[:, 5])) - (X[:, 3] ** 4) + (3 / X[:, 0])

model = PySRRegressor(
    ncycles_per_iteration = 100,
    niterations = 10000000,
    early_stop_condition = ("stop_if(loss, complexity) = loss < 1 && complexity < 10"),
    timeout_in_seconds = 3600,
    binary_operators = ["+", "-", "*", "/"],
    unary_operators = ["cos", "sin", "exp", "inv(x) = 1/x", "square", "cos2(x) = cos(x)^2",],
    constraints = {"square": 5, "cube": 5, "exp": 5,},
    select_k_features = 4,
    turbo = True,
    extra_sympy_mappings = {"inv": lambda x: 1/x, "cos2": lambda x: sympy.cos(x) ** 2},
    elementwise_loss = "loss(prediction, target) = (prediction - target)^2",
)
model.reset()
model.fit(X, y)

print(model)
