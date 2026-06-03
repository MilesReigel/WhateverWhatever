from pysr import PySRRegressor
import matplotlib.pyplot as plt
from scipy.fft import fft
import numpy as np
import h5py

# Potentially fft-modelable data: Freq. command, Hdc command, Flux command, Temp. command, Duty command

def P_loss(n_samples, m_per_n, voltage, current, sampling_time): # UPDATE TO USE READ_DIRECT FROM DATASET ENTIRELY INDEPENDENTLY
    print("Calculating Losses . . .")
    P_loss_list = []
    for i in range(n_samples):
        V, I = np.array(voltage[:, i]), np.array(current[:, i]) # allow element-wise multiplication of arrays
        P_loss_list.append(1/(m_per_n * sampling_time) * sum(V * I))
    print("-Loss Calculations Complete-")
    return(P_loss_list)

print("Organizing Data . . .")
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
    datapoints = len(time_raw[0])
    sampling_time = time_raw[0]
    del time_raw
  
    # loss = np.array(P_loss(datapoints, 10000, Data_raw['Voltage'], Data_raw['Current'], sampling_time), dtype = 'f8')

    duty_n = np.array(Data_raw['DutyN_command'][0, :])
    duty_p = np.array(Data_raw['DutyP_command'][0, :])
    duty_ratio = np.zeros((datapoints), dtype = 'f4')

    for i in range(datapoints): # clean duty cycle for regression processing and create a ratio to reduce memory usage
        duty_n[i] = 0 if np.isnan(duty_n[i]) else duty_n[i]
        duty_p[i] = 0 if np.isnan(duty_p[i]) else duty_p[i]
        duty_ratio[i] = 0 if duty_n[i] == 0 else duty_p[i] / duty_n[i]
    
    del duty_n, duty_p


    temp_data = Data_raw['Temperature_command'][0, :]
    print(len(temp_data))
    # temp_points = [25.0, 50.0, 70.0, 90.0]
    groups = {25.0: [None, 0, 0], 50.0: [None, 0, 0], 70.0: [None, 0, 0], 90.0: [None, 0, 0]}
    for i, t in enumerate(temp_data):
        if t in groups:
            groups[t][2] += 1
            groups[t][1] = i
            groups[t][0] = i if groups[t][0] is None else groups[t][0]
    del temp_data

    print(groups[25.0][0])

    xdata = np.column_stack((
        np.array(Data_raw['Temperature_command'][0, :], dtype = 'f8'),
        np.array(Data_raw['Flux_command'][0, :], dtype = 'f8'),
        np.array(Data_raw['Frequency_command'][0, :], dtype = 'f8'),
        np.array(Data_raw['Hdc_command'][0, :], dtype = 'f8'), 
        duty_ratio
        ))

    model = PySRRegressor(
        # warm_start = True,
        niterations = 10000000,
        population_size = 50,
        populations = 8,
        maxsize = 60,
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

    temp = np.arange(1000)

    plt.plot(temp, Data_raw['Flux_command'][0, 1000:2000])
    plt.savefig('temp_plot.png')
    
    # print("Beginning Optimization . . .")
    # model.fit(xdata, loss)


# Last changes made: power plotting!
# Next on the to-do list is to incorporate fft/modeling of other components in order to increase eff. of PySR, and potentially save P_loss data to a file so that it does not have to be recalculated every time