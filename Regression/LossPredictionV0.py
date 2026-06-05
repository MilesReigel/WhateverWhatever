from pysr import PySRRegressor
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
import numpy as np
import h5py

#figure out fft of data, complete B, H and mu functions, figure out how to group SR batches/ downsample data

def B_t(n_samples):
    return()

def H_cycle(n_samples,):
    semthing = here

def mu_a_cycle(n_samples,):
    same = thing

def get_data(filename):
    data = h5py.File(filename, 'r')
    return(data['Data'])

def ship_of_theseus(sampling_time, wave): # returns (frequency, amplitude) of 10 most prominent components of given wave
    x = fftfreq(1024, sampling_time)[:512] # its funny because if you take apart the wave and replace all of its parts with new waves is it the same wave? also double entendre because its a ship... and waves... 
    y = fft(wave)
    amplitudes = np.abs(y[:512]) / 512
    frequency_idxs, _ = find_peaks(amplitudes, height = 0.05 * max(amplitudes))
    a_s = np.sort(amplitudes)
    cutoff = a_s[10] # take top 10 amplitudes
    del a_s
    top = []
    for idx in frequency_idxs:
        if amplitudes[idx] > cutoff:
            top.append((x[idx], amplitudes[idx]))
    return(top)

class Materials:
    def __init__(self, V, I, DutyN, DutyP, Temp, Flux, Freq, Hdc, Area, N1, N2, samples, sampling_time):
        self.V = V
        self.I = I
        self.duty_dif = np.zeros((samples), dtype = 'f4')
        self.Temp = np.array(Temp[0, :], dtype = 'f8')
        self.Flux = np.array(Flux[0, :], dtype = 'f8')
        self.Freq = np.array(Freq[0, :], dtype = 'f8')
        self.Hdc = np.array(Hdc[0, :], dtype = 'f8')
        self.Area = Area[0, 0]
        self.N1 = N1[0, 0]
        self.N2 = N2[0, 0]
        self.B_t = np.zeros(samples, dtype = 'f8')
        self.H_t = np.zeros(samples, dtype = 'f8')
        self.samples = samples
        self.sampling_time = sampling_time[0, :]

        for i in range(samples): # clean duty cycle for regression processing and create a ratio to reduce memory usage
            self.duty_dif[i] = 1.0 if np.isnan(DutyN[0, i]) else DutyP[0, i] - DutyN[0, i]
        

print("Organizing Data . . .")
Data_raw = get_data('3C90_Pretest_data/3C90_TX-25-15-10_Data1_Cycle.mat')
for key in Data_raw.keys():
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
        print(f"{key}: Shape {temp.shape}, type {temp.dtype}")


m1 = Materials( # pull necessary data from the file, store to object m1 and close the file to reduce memory usage
    Data_raw['Voltage'],
    Data_raw['Current'], 
    Data_raw['DutyN_command'], 
    Data_raw['DutyP_command'],
    Data_raw['Temperature_command'],
    Data_raw['Flux_command'],
    Data_raw['Frequency_command'],
    Data_raw['Hdc_command'],
    Data_raw['Effective_Area'],
    Data_raw['Primary_Turns'],
    Data_raw['Secondary_Turns'],
    len(Data_raw['Sampling_Time'][0]),
    Data_raw['Sampling_Time'])
del Data_raw


# calculate b and h here
del m1.V, m1.I


# temp_points = [25.0, 50.0, 70.0, 90.0]
groups = {25.0: [None, 0], 50.0: [None, 0], 70.0: [None, 0], 90.0: [None, 0]}
for i, t in enumerate(m1.Temp):
    if t in groups:
        groups[t][1] += 1 # size of group
        groups[t][0] = i if groups[t][0] is None else groups[t][0] # start index


xdata = np.column_stack((
    m1.Temp[groups[25.0][0]:groups[50.0][0]],
    m1.Flux[groups[25.0][0]:groups[50.0][0]],
    m1.Freq[groups[25.0][0]:groups[50.0][0]],
    m1.Hdc[groups[25.0][0]:groups[50.0][0]],
    m1.duty_dif[groups[25.0][0]:groups[50.0][0]]
    ))
del m1.duty_dif, m1.Temp, m1.Flux, m1.Freq, m1.Hdc

print("Beginning Optimization . . .") # divided into two sections to reduce weight randomization as precision increases
model1 = PySRRegressor(
    # warm_start = True,
    niterations = 10000000,
    population_size = 50,
    populations = 8,
    maxsize = 60,
    maxdepth = 5,
    denoise = True,
    weight_randomize = 0.2,
    ncycles_per_iteration = 600,
    complexity_of_constants = 2,
    early_stop_condition = ("stop_if(loss, complexity) = (complexity < 40 && loss < 1e10) || (loss < 1e9)"),
    timeout_in_seconds = 3600 * 5,
    binary_operators = ["+", "-", "*", "/"],
    unary_operators = ["cos", "sin", "exp", "square",],
    constraints = {"square": 5, "exp": 5,},
    nested_constraints = {
        "square": {"square": 1, "sin": 2, "cos": 2, "exp": 1},
        "sin": {"square": 1, "sin": 2, "cos": 2, "exp": 1},
        "cos": {"square": 1, "sin": 2, "cos": 2, "exp": 1},
        "exp": {"square": 1, "sin": 2, "cos": 2, "exp": 1},},
    turbo = True,
    elementwise_loss = "loss(prediction, target) = (prediction - target)^2",)
model2 = PySRRegressor(
    warm_start = True,
    niterations = 10000000,
    population_size = 50,
    populations = 8,
    maxsize = 60,
    maxdepth = 5,
    denoise = True,
    weight_randomize = 0.1,
    ncycles_per_iteration = 400,
    complexity_of_constants = 2,
    early_stop_condition = ("stop_if(loss, complexity) = (complexity < 40 && loss < 1e3) || (loss < 1e2)"),
    timeout_in_seconds = 3600 * 3,
    binary_operators = ["+", "-", "*", "/"],
    unary_operators = ["cos", "sin", "exp", "square",],
    constraints = {"square": 5, "exp": 5,},
    nested_constraints = {
        "square": {"square": 1, "sin": 2, "cos": 2, "exp": 1},
        "sin": {"square": 1, "sin": 2, "cos": 2, "exp": 1},
        "cos": {"square": 1, "sin": 2, "cos": 2, "exp": 1},
        "exp": {"square": 1, "sin": 2, "cos": 2, "exp": 1},},
    turbo = True,
    elementwise_loss = "loss(prediction, target) = (prediction - target)^2",)
# model1.fit(xdata, loss[groups[25.0][0]:groups[50.0][0]])
# model2.fit(xdata, loss[groups[25.0][0]:groups[50.0][0]])