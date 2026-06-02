from pysr import PySRRegressor
import matplotlib.pyplot as plt
import scipy as sp
import numpy as np
import h5py

# Notes:)
# Data sampling time is consistently 8ns
T_interval = 8e-9 #seconds, 8 ns

# Discarding_info is 128x1, data included is of unknown purpose
# Acquisition info is 294x1, similarly of unknown purpose
# Duty cycle is ramped from 0.1P and 0.9N to 0.9P, 0.1N

with h5py.File('3C90_Pretest_data/3C90_TX-25-15-10_Data1_Combined.mat', 'r') as file:
    Data_raw = file['Data']
    for key in Data_raw.keys(): # Process dataset into something interpretable
        temp = Data_raw[key]
        if temp.dtype == "<u2": # Characters as unsigned ints
            str_assembly = ""
            for outer in temp: # Arrays are occasionally mismatching in terms of row/columnization
                for inner in outer:
                    str_assembly += chr(inner)
            print(f"{key}: {str_assembly}")
        elif temp.shape == (1, 1):
            print(f"{key}: {temp[0][0]}")
        else:
            print(temp)

    time_data = Data_raw['Sampling_Time']

    