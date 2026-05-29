#Simple LinReg program
import numpy as np
import matplotlib.pyplot as plt

x = [5, 7, 8, 7, 2, 17, 2, 9, 4, 11, 12, 9, 6]
y = [99, 86, 87, 88, 111, 86, 103, 87, 94, 78, 77, 85, 86]
num, den = 0, 0

x_bar = np.mean(x)
y_bar = np.mean(y)

for i in range(len(x)):
    num += (x[i] - x_bar) * (y[i] - y_bar)
    den += (x[i] - x_bar) ** 2
    
k = num/den

intercept = y_bar - (k * x_bar)

def prediction(x):
    return(intercept + (x * k))

x_tests = np.arange(0, 20, 1)

plt.scatter(x, y)
plt.plot(x_tests, prediction(x_tests))
plt.show()