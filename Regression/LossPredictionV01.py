from pysr import PySRRegressor
import matplotlib.pyplot as plt
from scipy.fft import fft, fft2, fftfreq
from scipy.signal import find_peaks, detrend
import numpy as np
import h5py


def B_t(A, N2, V_t, sampling_time):
    dt = sampling_time / 1024
    B_t = np.cumsum(V_t) * dt / (A * N2)
    return B_t

def B_from_fft(A, N2, data, sampling_time): # returns (frequency, amplitude, phase, dc offset) of B_t
    # 1/(A * N2) INT(V_t) = 1/(A * N2) * INT(a * cos(wt + p)) = 1/(A * N2) * a/w * sin(wt + p) = 1/(A * N2) * a/w * cos(wt + p + pi/2) -> a /= w*A*N2, f = f, p += pi/2
    TX = []
    for f, a, phase in data:
        new_a = a / (2 * np.pi * f * A * N2)
        new_p = phase - (np.pi / 2)
        dc_offset = -new_a * np.cos((f * 2 * np.pi * sampling_time / 1024) + new_p)
        TX.append((f, new_a, new_p, dc_offset))
    return TX

def H_t(L, N1, I_t):
    H_t = np.zeros(1024)
    for H, I in zip(H_t, I_t):
        H =  I * (N1 / L)
    return H_t

def H_from_fft(L, N1, data): # returns (frequency, amplitude, phase, 0) of H_t
    TX = []
    for f, a, phase in data:
        new_a = a * N1 / L
        TX.append((f, new_a, phase, 0))
    return TX

def mu_a(B_t, H_t):
    return (max(B_t) - min(B_t))/(max(H_t) - min(H_t))

def get_data(filename): # pull necessary data from the file, store to object and close the file to reduce memory usage
    data = h5py.File(filename, 'r')
    return data['Data']

def ship_of_theseus(sampling_time, wave, n): # returns (frequency, amplitude, phase) of n most prominent components of given wave
    x = fftfreq(1024, sampling_time / 1024)[:512]
    y = fft(wave)
    amplitudes = np.abs(y[:512]) / 512
    amplitudes[x < 1000] = 0.0 # filter any low frequency fft products out
    phases = np.angle(y[:512])
    frequency_idxs, _ = find_peaks(amplitudes, height = 0.01 * max(amplitudes))
    peak_amps = amplitudes[frequency_idxs]
    top_idxs = frequency_idxs[np.argsort(peak_amps)[-min(n, len(peak_amps)):]] # indexes of top amplitudes
    top = []
    for idx in top_idxs:
        top.append((x[idx], amplitudes[idx], phases[idx]))
    return top

def recombobulate(time, data):
    combobulated_wave = np.zeros(1024)
    for f, a, phase, dc in data:
        combobulated_wave += a * np.cos(2 * time * f * np.pi + phase) + dc
    return combobulated_wave


class Fourier_representation: #adjust to take variable number of terms as separate parameters (perhaps f1, f2, etc.)
    def __init__(self, span):
        self.frequency = np.zeros(span)
        self.amplitude = np.zeros(span)
        self.phase = np.zeros(span)
        self.dc_offset = np.zeros(span)

class Materials:
    def __init__(self, V, I, DutyN, DutyP, Temp, Flux, Freq, Hdc, Area, L, N1, N2, samples, sampling_time, num_f_coeffs):
        self.V = V
        self.I = I
        self.duty_dif = np.zeros((samples), dtype = 'f4')
        self.Temp = np.array(Temp[0, :], dtype = 'f8')
        self.Flux = np.array(Flux[0, :], dtype = 'f8')
        self.Freq = np.array(Freq[0, :], dtype = 'f8')
        self.Hdc = np.array(Hdc[0, :], dtype = 'f8')
        self.Area = Area[0, 0]
        self.L = L[0, 0]
        self.N1 = N1[0, 0]
        self.N2 = N2[0, 0]
        self.samples = samples
        self.sampling_time = sampling_time[0, :]
        self.num_f_coeffs = num_f_coeffs

        for i in range(samples): # clean duty cycle for regression processing and create a ratio to reduce memory demand
            self.duty_dif[i] = 1.0 if np.isnan(DutyN[0, i]) else DutyP[0, i] - DutyN[0, i]

        self.B_t = [Fourier_representation(samples) for _ in range(num_f_coeffs)]
        self.H_t = [Fourier_representation(samples) for _ in range(num_f_coeffs)]


print("Organizing Data. . .")
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


m1 = Materials( 
    Data_raw['Voltage'],
    Data_raw['Current'], 
    Data_raw['DutyN_command'], 
    Data_raw['DutyP_command'],
    Data_raw['Temperature_command'],
    Data_raw['Flux_command'],
    Data_raw['Frequency_command'],
    Data_raw['Hdc_command'],
    Data_raw['Effective_Area'],
    Data_raw['Effective_Length'],
    Data_raw['Primary_Turns'],
    Data_raw['Secondary_Turns'],
    len(Data_raw['Sampling_Time'][0]),
    Data_raw['Sampling_Time'],
    3)
del Data_raw


# temp_points = [25.0, 50.0, 70.0, 90.0]
groups = {25.0: [None, 0], 50.0: [None, 0], 70.0: [None, 0], 90.0: [None, 0]}
for i, t in enumerate(m1.Temp):
    if t in groups:
        groups[t][1] += 1 # size of group
        groups[t][0] = i if groups[t][0] is None else groups[t][0] # start index
r1 = groups[25.0][0]
r2 = groups[50.0][0]


print("Computing Losses. . .")

V_slice = m1.V[r1:r2]
I_slice = m1.I[r1:r2]
V_fft_bulk = fft2(V_slice)[:, :512]
I_fft_bulk = fft2(I_slice)[:, :512]
n = r2 - r1

for i in range(n):
    _ = _

for i in range(n):
    time = m1.sampling_time[i]
    for data, coeff in zip(B_from_fft(m1.Area, m1.N2, ship_of_theseus(time, m1.V[i], m1.num_f_coeffs), time), range(m1.num_f_coeffs)):
        m1.B_t[coeff].amplitude[i], m1.B_t[coeff].frequency[i], m1.B_t[coeff].phase[i], m1.B_t[coeff].dc_offset[i] = data
    for data, coeff in zip(H_from_fft(m1.L, m1.N1, ship_of_theseus(time, m1.I[i], m1.num_f_coeffs)), range(m1.num_f_coeffs)):
        m1.H_t[coeff].amplitude[i], m1.H_t[coeff].frequency[i], m1.H_t[coeff].phase[i], m1.H_t[coeff].dc_offset[i] = data
    if i % 500 == 0: print(f"Processed {i / n}% of data. . .")
del m1.V, m1.I


x = np.column_stack((
    m1.Temp[r1:r2],
    m1.Flux[r1:r2],
    m1.Freq[r1:r2],
    m1.Hdc[r1:r2],
    m1.duty_dif[r1:r2],
    m1.B_t[0].amplitude[r1:r2],
    m1.B_t[1].amplitude[r1:r2],
    m1.B_t[2].amplitude[r1:r2],
    m1.B_t[0].frequency[r1:r2],
    m1.B_t[1].frequency[r1:r2],
    m1.B_t[2].frequency[r1:r2],
    m1.B_t[0].phase[r1:r2],
    m1.B_t[1].phase[r1:r2],
    m1.B_t[2].phase[r1:r2],
    m1.B_t[0].dc_offset[r1:r2],
    m1.B_t[1].dc_offset[r1:r2],
    m1.B_t[2].dc_offset[r1:r2]))
del m1.duty_dif, m1.Temp, m1.Flux, m1.Freq, m1.Hdc, m1.B_t

y = np.column_stack((
    m1.H_t[0].amplitude[r1:r2],
    m1.H_t[1].amplitude[r1:r2],
    m1.H_t[2].amplitude[r1:r2],
    m1.H_t[0].frequency[r1:r2],
    m1.H_t[1].frequency[r1:r2],
    m1.H_t[2].frequency[r1:r2],
    m1.H_t[0].phase[r1:r2],
    m1.H_t[1].phase[r1:r2],
    m1.H_t[2].phase[r1:r2],
    m1.H_t[0].dc_offset[r1:r2],
    m1.H_t[1].dc_offset[r1:r2],
    m1.H_t[2].dc_offset[r1:r2]))
del m1.H_t

print("Beginning Optimization. . .") # divided into two sections to reduce weight randomization as precision increases
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
model1.fit(x, y)
model2.fit(x, y)