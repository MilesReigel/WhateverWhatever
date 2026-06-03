from pysr import PySRRegressor
import matplotlib.pyplot as plt
from scipy.fft import fft
import numpy as np
import h5py

# Potentially fft-modelable data: Freq. command, Hdc command, Flux command, Temp. command, Duty command

def P_loss(meas_duration, voltage, current): # Requires input array of entire measurement periods for voltage and current
    V, I = np.array(voltage), np.array(current) # allow element-wise multiplication of arrays
    p = 1/(meas_duration) * sum(V * I)
    return(p)

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
            print(f"{key}: {temp[0, 0]}")
        else:
            print(temp)
    
    time_raw = Data_raw['Sampling_Time']
    datapoints = len(time_raw[0, :])
    sampling_time = time_raw[0, 0]

    voltage_raw = Data_raw['Voltage']
    current_raw = Data_raw['Current']

    # xdata = np.arange(0, sampling_time * datapoints, sampling_time)
    P_loss_list = []
    for i in range(datapoints):
        P_loss_list.append(P_loss(10000 * sampling_time, voltage_raw[:, i], current_raw[:, i]))

    xdata = np.arange(datapoints)

    plt.plot(xdata, P_loss_list)
    plt.savefig('temp_plot.png')

# Last changes made: power plotting!
# Next on the to-do list is to incorporate fft/modeling of other components in order to increase eff. of PySR, and potentially save P_loss data to a file so that it does not have to be recalculated every time