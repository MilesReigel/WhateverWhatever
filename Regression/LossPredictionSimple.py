from pysr import PySRRegressor, TemplateExpressionSpec
import matplotlib.pyplot as plt
from scipy.fft import fft2, fftfreq
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
from scipy.integrate import simpson
import numpy as np
import h5py
import csv

def B_ac(V, N2, A, sampling_time):
    TX = (1/ (A * N2)) * sampling_time * np.cumsum(V)
    return (np.max(TX) - np.min(TX)) / 2.0

def B_t(V, N2, A, sampling_time):
    return (1/ (A * N2)) * sampling_time * np.cumsum(V)

def get_data(filename): # pull necessary data from the file, store to object and close the file to reduce memory usage
    data = h5py.File(filename, 'r')
    return data['Data']

def cf_func_GSE(xdata, k, a, b):
    f, B = xdata
    return k + np.log10(f) * a + np.log10(B) * b

def cf_func_iGSE(xdata, k_i, a, b): # xdata needs to be (B_wave, sampling_time) - returns volumetric losses 
    TX = []
    for d in xdata:
        B_wave = d[:1024]
        t = d[1024]
        x = np.arange(0, t, t / 1024)
        integrand = k_i * (abs(np.gradient(B_wave, x)) ** a) * ((max(B_wave) - min(B_wave)) ** (b - a))
        TX.append((1 / t) * simpson(integrand, x = x))
    return TX

def recombobulate_2(xdata_norm, y_norm_amount, k, a, b):
    f, B = xdata_norm
    return (k * (f ** a) * (B ** b)) * y_norm_amount

def the_best_thing_since_sliced_bread(x, y_norm_scale): # manually entered output of PySR solution to compute losses
    f, B = [], []
    for group in x:
        f.append(group[0])
        B.append(group[1])
        # T.append(group[2])
    f = np.array(f)
    B = np.array(B)
    # T = np.array(T)
    return  ((f * B) * (f + B)) * np.log(B + 0.93002) * y_norm_scale

def normal(array, name):
    norm_scale = max(array) / 2
    print(f"{name} normalized about 0 by magnitude {norm_scale}")
    array /= norm_scale
    return (array, norm_scale)


class Material:
    def __init__(self, V, I, Temp, Freq, Area, Volume, L, N1, N2, samples, sampling_time, dutyN):
        self.V = np.array(V)
        self.I = np.array(I)
        self.Temp = np.array(Temp[0, :]) # [C]
        self.Freq = np.array(Freq[0, :]) # [Hz]
        self.Area = Area[0, 0]
        self.Volume = Volume[0, 0]
        self.L = L[0, 0]
        self.N1 = N1[0, 0]
        self.N2 = N2[0, 0]
        self.samples = samples
        self.sampling_time = sampling_time[0, :]
        self.Bac = np.zeros(samples)
        self.B = np.zeros((samples, 1024))
        self.loss = np.zeros(samples) # [W/m^3], computed on line 112 (line may change, its down there somewhere trust me)
        self.dutyN = dutyN[0, :]

        for i in range(samples):
            self.Bac[i] = B_ac(self.V[:, i], self.N2, self.Area, self.sampling_time[i])
            self.B[i, :] = B_t(self.V[:, i], self.N2, self.Area, self.sampling_time[i])


print("Organizing data...")
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

m1 = Material( 
    Data_raw['Voltage'],
    Data_raw['Current'], 
    Data_raw['Temperature_command'],
    Data_raw['Frequency_command'],
    Data_raw['Effective_Area'],
    Data_raw['Effective_Volume'],
    Data_raw['Effective_Length'],
    Data_raw['Primary_Turns'],
    Data_raw['Secondary_Turns'],
    len(Data_raw['Sampling_Time'][0]),
    Data_raw['Sampling_Time'],
    Data_raw['DutyN_command'])
del Data_raw


y, ydata = [], []
x, x_f, x_B_ac, xdata_iGSE = [], [], [], [] # terrible formatting has been chosen here (different methods require different data formats :( )
for i in range(m1.samples): # define part of the dataset used for training/testing ALL models
    m1.loss[i] = (m1.Freq[i] / m1.Volume) * sum(m1.V[:, i] * m1.I[:, i] * m1.sampling_time[i])
    if np.isnan(m1.dutyN[i]): # only use sinusoidal excitations for now (duty cycle for sinusoids stored as NaN)
        x_f.append(m1.Freq[i])
        x_B_ac.append(m1.Bac[i])
        iGSE_row = np.zeros(1025)
        iGSE_row[:1024], iGSE_row[1024] = m1.B[i], m1.sampling_time[i]
        xdata_iGSE.append(iGSE_row)
        y.append(m1.loss[i])
        x.append((m1.Freq[i], m1.Bac[i])) # , m1.Temp[i])
del m1.Temp, m1.Freq, m1.Bac, m1.loss

x = np.array(x) # data intended for PySR
y = np.array(y) #

xdata = (np.array(x_f), np.array(x_B_ac)) # data intended for GSE curve-fit function
xdata_iGSE = np.array(xdata_iGSE) # data intended for iGSE curve-fit function
ydata = y # losses pre-normalization

y, y_norm_scale = normal(y, "Losses") # Normalize all data for PySR, algorithm does not easily evolve integers beyond +/- 5, everyting is normalized to +/- 2 somewhat arbitrarily
x[:, 0], _0 = normal(x[:, 0], "Frequency")
x[:, 1], _1 = normal(x[:, 1], "Peak Flux Density")
# x[:, 2], _2 = normal(x[:, 2], "Temperature")

x_train, x_test, y_train, y_test = [], [], [], []
count = 0
for i in range(len(x)): # separate data into training and testing sets for PySR (75% train, 25% test)
    xrow = x[i]
    yrow = y[i]
    if (i % (len(x) // 100)) == 0:
        if count == 3:
            x_test.append(xrow)
            y_test.append(yrow)
            count = 0
        else:
            x_train.append(xrow)
            y_train.append(yrow) 
            count += 1   


popt_GSE, _ = curve_fit(cf_func_GSE, xdata, np.log10(ydata), p0 = [0, 1.5, 2.5])
predictions_GSE = np.array(cf_func_GSE(xdata, *popt_GSE))
print(f"\nObjective parameters: K = {10 ** popt_GSE[0]:.4e}, a = {popt_GSE[1]:.4f}, b = {popt_GSE[2]:.4f}")
print(f"Mean Prediction Error in standard curve-fit (GSE): {100 * (np.mean(abs(ydata - (10 ** predictions_GSE))) / np.mean(ydata)):.2f}%\n")

popt_iGSE, _ = curve_fit(cf_func_iGSE, xdata_iGSE, ydata, p0 = [0, 1.5, 2.5])
predictions_iGSE = np.array(cf_func_iGSE(xdata_iGSE, *popt_iGSE))
print(f"Objective parameters: K_i = {popt_iGSE[0]:.4e}, a = {popt_iGSE[1]:.4f}, b = {popt_iGSE[2]:.4f}")
print(f"Mean Prediction Error in standard curve-fit (iGSE): {100 * (np.mean(abs(ydata - predictions_iGSE)) / np.mean(ydata)):.2f}%\n")

predictions_PySR = the_best_thing_since_sliced_bread(x_test, y_norm_scale)
print("Previous best equation: ((#1 * #2) * (#1 + #2)) * log(#2 + 0.93002)")
print(f"Mean Prediction Error in previous PySR equation: {100 * (np.mean(abs((y_norm_scale * np.array(y_test)) - predictions_PySR)) / np.mean(np.array(y_test) * y_norm_scale)):.2f}%\n")


for fandb, l in zip(x, y):
    f, b = fandb[0], fandb[1]
    if f == 0 or b == 0 or l == 0:
        print("Error: All datapoints should have nonzero values")
        exit()

template = TemplateExpressionSpec(
    expressions = ["f"],
    variable_names = ["FR", "B"],
    combine = "f(FR, B)")

model = PySRRegressor(
    warm_start = True,
    precision = 64,
    expression_spec = template,
    niterations = 100000,
    population_size = 50,
    populations = 8,
    maxsize = 20,
    maxdepth = 5,
    weight_randomize = 0.05, # expression randomization weight
    optimize_probability = 0.2, #constant randomization weight
    ncycles_per_iteration = 600,
    complexity_of_constants = 6,
    early_stop_condition = "(loss, complexity) -> (complexity < 10 && loss < 1e-4) || (loss < 5e-5)",
    timeout_in_seconds = 3600 * .5,
    binary_operators = ["+", "-", "*", "/", "^"],
    constraints = {'^': (-1, 1)},
    unary_operators = ["exp", "log", "sin", "cos"],
     )
print(f"Training on {len(x_train)} datapoints")
# model.fit(x_train, y_train)