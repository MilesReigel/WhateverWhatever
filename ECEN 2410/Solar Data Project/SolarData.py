import csv
import matplotlib.pyplot as plt
import numpy as np
# Note: I am aware that this is python and that the template was given for matlab- 
# Professor Constante Flores told me that as long as I follow the same structure,
# it is okay to use python instead. Please let me know if this remains troublesome.
# Thank you!

#Variables (costant)
NOCT = 45.0
kv = 1.5

phi = 33.45
phi_r = np.radians(phi)

gamma_p = 0
beta_deg = 20
beta_deg_r = np.radians(beta_deg)

P_AC_RATED = 6e6
Vdc_min = 1300
Vdc_max = 2000
n_inv = 0.97

PDC_target = P_AC_RATED * 1.3 # PDC target = 6MW * 1.3 = 7.8e6
P_mod_STC = 550
Vmp_STC = 41.5
Vmp_beta = 0.12
Ns = 0

gammaT = -0.004

def delta(day):
    return(23.45 * np.sin(np.radians((360/365) * (284 + day))))

def omega(t_solar):
    return(15 * (t_solar - 12))

#requires redefinition of delta and omega for each value
def cos_tz(delta, omega):
    delta_r = np.radians(delta)
    omega_r = np.radians(omega)

    cos_tz = (
        np.sin(phi_r) * np.sin(delta_r) + 
        np.cos(phi_r) * np.cos(delta_r) * np.cos(omega_r)
    )

    return np.clip(cos_tz, -1, 1)

def daylight(cos_tz):
    return cos_tz > 0

def day(n):
    return ((n - 1) // 24) + 1

#pain
def cos_ti(delta, omega):
    delta_r = np.radians(delta)
    omega_r = np.radians(omega)
    cos_ti = (
        np.sin(delta_r) * np.sin(phi_r) * np.cos(beta_deg_r) - 
        np.sin(delta_r) * np.cos(phi_r) * np.sin(beta_deg_r) + 
        np.cos(delta_r) * np.cos(phi_r) * np.cos(beta_deg_r) * np.cos(omega_r) + 
        np.cos(delta_r) * np.sin(phi_r) * np.sin(beta_deg_r) * np.cos(omega_r))
    return(cos_ti)

def GPOA(albedo, DNI, DHI, GHI, daylight, cos_ti):
    if not daylight:
        return 0
    elif cos_ti > 0:
        return((DNI * cos_ti) + (DHI * (1 + np.cos(beta_deg_r)) * .5) + (albedo * GHI * (1 - np.cos(beta_deg_r)) * 0.5)) 
    elif cos_ti < 0:
        return((DHI * (1 + np.cos(beta_deg_r)) * .5) + (albedo * GHI * (1 - np.cos(beta_deg_r)) * 0.5))
    else:
        print("Error with GPOA calculations")

def Tcell(Tamb, GPOA, Vwind):
    Tcell = Tamb + (((NOCT - 20) / 800) * GPOA) - (kv * Vwind)
    if (Tamb > Tcell):
        return(Tamb)
    else:
        return(Tcell)

#open file
with open('phoenix_hourly.csv', 'r') as file:
    reader = csv.reader(file)
    header = next(reader)
    data = [[float(value) for value in row] for row in reader]

if len(data) != 8760:
    print(f"Error: expected 8760 hourly rows, but only {len(data)} were found")

n = 1
Vmpmod_min, Vmpmod_max = 1000.0, 0.0
Ns, Np ,Ns_min, Ns_max = 40, 0, 0, 60

for row in data:
    t_solar = abs(row[0])
    DNI = row[1]
    DHI = row[2]
    GHI = row[3]
    Tamb = row[4]
    albedo = row[5]
    Vwind = row[6]

    deltaD = delta(day(n))
    omegaH = omega(t_solar)

    currentGPOA = GPOA(
        albedo, 
        DNI, 
        DHI, 
        GHI, 
        daylight(
            cos_tz(deltaD, omegaH)),
            cos_ti(deltaD, omegaH)
    )

    # 6.1 - Hourly module MPP voltage Vmp,mod(t)
    Vmpmod = Vmp_STC - Vmp_beta * (Tcell(Tamb, currentGPOA, Vwind) - 25) # Vmpmod = Vmp_STC + Vmp_beta * (Tcell - 25)
    Vmpmod_min = min(Vmpmod, Vmpmod_min) #  Vmpmod_min = 35.61
    Vmpmod_max = max(Vmpmod, Vmpmod_max) #  Vmpmod_max = 44.62

    # 6.2 - Feasible range for Ns
    Ns_min = np.ceil(Vdc_min / Vmpmod_min) #  Ns_min = 37
    Ns_max = np.floor(Vdc_max / Vmpmod_max) #  Ns_max = 44
    # Vstring min at Ns_min = 1317.73
    # Vstring max at Ns_min = 1650.94
    # Vstring min at Ns_max = 1567.03
    # Vstring max at Ns_max = 1963.28

    n += 1

Vstring_min_at_NS_min = Vmpmod_min * Ns_min
Vstring_max_at_NS_min = Vmpmod_max * Ns_min
Vstring_min_at_NS_max = Vmpmod_min * Ns_max
Vstring_max_at_NS_max = Vmpmod_max * Ns_max

# 6.3 - Select Ns and compute Np to hit DC target
# Ns = 40

def PDCoptimization(Np):
    return(abs(PDC_target - Np * Ns * P_mod_STC))

i = 1
while i <= 400:
    if (PDCoptimization(i) < PDCoptimization(i - 1)): #  Np = 355
        Np = i
    i += 1

P_DC_Achieved_W = Ns * Np * P_mod_STC
P_DC_Achieved_MW = P_DC_Achieved_W / 1e6
dc_ac_achieved = P_DC_Achieved_W / P_AC_RATED


print("Vmpmod min/max: ")
print(f"Min: {Vmpmod_min}")
print(f"Max: {Vmpmod_max}")

print("Ns min/max: ")
print(f"Min: {Ns_min}")
print(f"Max: {Ns_max}")
print(f"Vstring min at Ns min: {Vstring_min_at_NS_min}")
print(f"Vstring max at Ns min: {Vstring_max_at_NS_min}")
print(f"Vstring min at Ns max: {Vstring_min_at_NS_max}")
print(f"Vstring max at Ns max: {Vstring_max_at_NS_max}")

print(f"optimal Np = {Np}")
print(f"Dc power achieved [W]: {P_DC_Achieved_W}")
print(f"Dc power achieved [MW]: {P_DC_Achieved_MW}")