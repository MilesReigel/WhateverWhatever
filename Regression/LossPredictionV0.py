from pysr import PySRRegressor
from scipy.integrate import simpson
import numpy as np
import matplotlib.pyplot as plt
import csv

# Data sampling frequency: 16MHz
# File prefixes B, H, T for magnetic flux density, magnetic field strength and temperature

T_ns = 62.5

with open('TrainingData/3C90/3C90_1_B.csv', 'r') as readData:
    reader = csv.reader(readData)
    B1_3C90_data = [[float(value) for value in sequence] for sequence in reader]

with open('TrainingData/3C90/3C90_1_H.csv', 'r') as readData:
    reader = csv.reader(readData)
    H1_3C90_data = [[float(value) for value in sequence] for sequence in reader]

with open('TrainingData/3C90/3C90_1_T.csv', 'r') as readData:
    reader = csv.reader(readData)
    T1_3C90_data = [[float(value) for value in sequence] for sequence in reader]

def Pv_loss_row(B, H):
    np_H = np.array(H)
    dB = np.gradient(B, T_ns)
    P_loss = (dB * np_H) # H * dB given dt = T_ns
    return(P_loss)

for Brow, Hrow in zip(B1_3C90_data, H1_3C90_data):
    Pv_loss_total += Pv_loss_row(Brow, Hrow)
