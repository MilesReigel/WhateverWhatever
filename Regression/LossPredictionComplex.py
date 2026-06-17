from pysr import PySRRegressor, TemplateExpressionSpec
import matplotlib.pyplot as plt
from scipy.fft import fft2, fftfreq
from scipy.signal import find_peaks
import numpy as np
import h5py
import csv


def B_from_fft(A, N2, data, sampling_time): # returns (frequency, amplitude, phase, dc offset) of B_t
    # 1/(A * N2) INT(V_t) = 1/(A * N2) * INT(a * cos(wt + p)) = 1/(A * N2) * a/w * sin(wt + p) = 1/(A * N2) * a/w * cos(wt + p + pi/2) -> a /= w*A*N2, f = f, p += pi/2
    TX = []
    for f, a, phase in data:
        new_a = a / (2 * np.pi * f * A * N2)
        new_p = phase - (np.pi / 2)
        dc_offset = -new_a * np.cos((f * 2 * np.pi * sampling_time / 1024) + new_p)
        TX.append((f, new_a, new_p, dc_offset))
    return TX

def H_from_fft(L, N1, data, sampling_time):
    TX = []
    for f, a, p in data:
        new_a = a * (m1.N1 / m1.L)
        dc_offset = -new_a * np.cos((f * 2 * np.pi * sampling_time / 1024) + p)
        TX.append((f, new_a, p, dc_offset))
    return TX
        
def get_data(filename): # pull necessary data from the file, store to object and close the file to reduce memory usage
    data = h5py.File(filename, 'r')
    return data['Data']

def ship_of_theseus(sampling_time, y, n): # returns (frequency, amplitude, phase) of n most prominent components of given wave
    x = fftfreq(1024, sampling_time / 1024)[:512]
    amplitudes = np.abs(y) / 512
    amplitudes[x < 1000] = 0.0 # filter any low frequency fft products out
    phases = np.angle(y)
    frequency_idxs, _ = find_peaks(amplitudes, height = 0.01 * max(amplitudes))
    peak_amps = amplitudes[frequency_idxs]
    top_idxs = frequency_idxs[np.argsort(peak_amps)[-min(n, len(peak_amps)):]] # indices of top amplitudes
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
    def __init__(self, V, I, Temp, Freq, Area, Volume, L, N1, N2, samples, sampling_time, num_f_coeffs):
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
        self.num_f_coeffs = num_f_coeffs
        self.B_t = [Fourier_representation(samples) for _ in range(num_f_coeffs)] # [T]
        self.H_t = [Fourier_representation(samples) for _ in range(num_f_coeffs)] # [A/m]
        self.loss = np.zeros(samples) # [W/m^3]


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


m1 = Materials( 
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
    3)
del Data_raw


try: # Process data or use preprocessed data in csv file
    with open(f"3C90_Processed_data_{m1.num_f_coeffs}_coeffs.csv", "r") as preprocessed_data:
        reader = csv.reader(preprocessed_data)
        for row, i in zip(reader, range(m1.samples)):
            for coeff in range(m1.num_f_coeffs):
                m1.B_t[coeff].frequency[i], m1.B_t[coeff].amplitude[i], m1.B_t[coeff].phase[i], m1.B_t[coeff].dc_offset[i] = row[coeff * 4:(1 + coeff) * 4]
                m1.H_t[coeff].frequency[i], m1.H_t[coeff].amplitude[i], m1.H_t[coeff].phase[i], m1.H_t[coeff].dc_offset[i] = row[(m1.num_f_coeffs * 4) + coeff * 4:(m1.num_f_coeffs * 4) + (coeff + 1) * 4]
            m1.loss[i] = row[m1.num_f_coeffs * 8]
    print(f"Using preprocessed data from file 3C90_Processed_data_{m1.num_f_coeffs}_coeffs.csv")

except FileNotFoundError:
    print("Processing data...")
    V_fft_bulk = fft2(np.transpose(m1.V))[:, :512]
    I_fft_bulk = fft2(np.transpose(m1.I))[:, :512]
    with open(f"3C90_Processed_data_{m1.num_f_coeffs}_coeffs.csv", "w") as preprocessed_data:
        writer = csv.writer(preprocessed_data)
        for i in range(m1.samples):
            time = m1.sampling_time[i]
            B_t_raw = B_from_fft(m1.Area, m1.N2, ship_of_theseus(time, V_fft_bulk[i], m1.num_f_coeffs), time)
            H_t_raw = H_from_fft(m1.L, m1.N1, ship_of_theseus(time, I_fft_bulk[i], m1.num_f_coeffs), time)
            while len(B_t_raw) < m1.num_f_coeffs:
                B_t_raw.append((0, 0, 0, 0))
            while len(H_t_raw) < m1.num_f_coeffs:
                H_t_raw.append((0, 0, 0, 0))
            row = []
            for Bdata, Hdata, coeff in zip(B_t_raw, H_t_raw, range(m1.num_f_coeffs)):
                m1.B_t[coeff].frequency[i], m1.B_t[coeff].amplitude[i], m1.B_t[coeff].phase[i], m1.B_t[coeff].dc_offset[i] = Bdata
                m1.H_t[coeff].frequency[i], m1.H_t[coeff].amplitude[i], m1.H_t[coeff].phase[i], m1.H_t[coeff].dc_offset[i] = Hdata
                for d in Bdata: row.append(d)
                for d in Hdata: row.append(d)
            m1.loss[i] = (m1.Freq[i] / m1.Volume) * sum(m1.V[:, i] * m1.I[:, i] * m1.sampling_time[i]) # Volumetric core loss: f/Ve * INT 0|1/f (V(t) * I(t)) dt
            row.append(m1.loss[i])
            writer.writerow(row) # organized data as B(f1, a1, p1, dc1, f2, a2)... H(f1, a1, p1, dc1, f2, a2)... losses
            if i % 4000 == 0: print(f"Processed {((i / m1.samples) * 100):.2f}% of data...")
    print("Data processed!")
del m1.V, m1.I


print("Beginning optimization...")
num = m1.samples // 400
j = 0
y = np.zeros(400)
x = np.zeros((400, (m1.num_f_coeffs * 8) + 3))
for i in range(m1.samples):
    if (i % num == 0 and i != 0):
        x[j, :] = [
            m1.B_t[0].amplitude[i],
            m1.B_t[0].frequency[i],
            m1.B_t[0].phase[i],
            m1.B_t[0].dc_offset[i],
            m1.B_t[1].amplitude[i],
            m1.B_t[1].frequency[i],
            m1.B_t[1].phase[i],
            m1.B_t[1].dc_offset[i],
            m1.B_t[2].amplitude[i],
            m1.B_t[2].frequency[i],
            m1.B_t[2].phase[i],
            m1.B_t[2].dc_offset[i],
            m1.Temp[i],
            m1.Freq[i], 
            m1.sampling_time[i],
            m1.H_t[0].amplitude[i],
            m1.H_t[0].frequency[i],
            m1.H_t[0].phase[i],
            m1.H_t[0].dc_offset[i],
            m1.H_t[1].amplitude[i],
            m1.H_t[1].frequency[i],
            m1.H_t[1].phase[i],
            m1.H_t[1].dc_offset[i],
            m1.H_t[2].amplitude[i],
            m1.H_t[2].frequency[i],
            m1.H_t[2].phase[i],
            m1.H_t[2].dc_offset[i]]
        y[j] = m1.loss[i]
        j += 1
del m1.Temp, m1.Freq, m1.B_t, m1.H_t

template = TemplateExpressionSpec(
    expressions = ["f"],
    variable_names = ["F0", "A0", "P0", "D0", "F1", "A1", "P1", "D1", "F2", "A2", "P2", "D2", "T", "FR", "t"],
    combine = "f(T, FR, (A0 * cos((pi * 2 * F0 * t) + P0) + A1 * cos((pi * 2 * F1 * t) + P1) + A2 * cos((pi * 2 * F2 * t) + P2) + D0 + D1 + D2))" # attempting to encourage pysr to reassemble the original B_t waveform
)

model1 = PySRRegressor(
    warm_start = True,
    precision = 64,
    expression_spec = template,
    niterations = 10000000,
    population_size = 50,
    populations = 8,
    maxsize = 30,
    maxdepth = 8,
    weight_randomize = 0.1,
    ncycles_per_iteration = 600,
    complexity_of_constants = 3,
    early_stop_condition = ("stop_if(loss, complexity) = (complexity < 30 && loss < 5e4) || (loss < 1e2)"),
    timeout_in_seconds = 3600 * 10,
    binary_operators = ["+", "-", "*", "/"],
    unary_operators = ["cos", "sin", "exp", "log"],
    nested_constraints = {
        "log": {"log": 1, "sin": 1, "cos": 1, "exp": 1},
        "sin": {"log": 1, "sin": 1, "cos": 1, "exp": 1},
        "cos": {"log": 1, "sin": 1, "cos": 1, "exp": 1},
        "exp": {"log": 1, "sin": 1, "cos": 1, "exp": 1},},
    loss_function = """
    function custom_wave_loss(tree, dataset::) # CUSTOM LOSS FUNCTION HAS TO BE COMPLETED, H_t IS STILL APPENDED TO X AND THEREFORE TEMPLATE MUST BE ADJUSTED
    """
     )
model1.fit(x, y)