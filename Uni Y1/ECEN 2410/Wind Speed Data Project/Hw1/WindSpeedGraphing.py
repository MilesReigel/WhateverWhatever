import matplotlib.pyplot as mp
import numpy as np

ypoints = np.loadtxt("wind_data.csv", delimiter = ",")
datacounter = 0
binmod = np.arange(0.0, 25.0, 1.0)
npypoints = np.array(ypoints)
datapointnum = len(ypoints)
style = {'facecolor': 'indigo', 'edgecolor': 'white', 'linewidth': 1}

#straight up plotting it
#how evil
mp.hist(ypoints, bins = binmod, histtype = 'bar', **style)
mp.xlabel("Wind Speed (mph)")
mp.ylabel("Number of occurences")

ypoints.sort()
print("\nPart a)")
#For part a) choose vR such that Pr(v > vR) ~= 5 - 10%
print("Total Datapoints: ", datapointnum)
print("90th percentile: ", np.percentile(ypoints, 90))
print("92.5th percentile: ", np.percentile(ypoints, 92.5))
print("95th percentile: ", np.percentile(ypoints, 95))

#Given that the range from the 90th to the 95th percentiles is between 13.6 and 15.1,
#I choose vR = 15m/s
vR = 15.0
print("Rated Velocity: ", vR, "m/s\n")
Adj_vR = vR * pow((100/80), 0.14)

print("Part b)")
#For part b) compute rated power 1/2(rho)(A)(Cp*)(ntot)(vR^3)
densityRho = ((101325 * 0.028964) / (8.314 * 288.15))
print("Density[kg/m^3]: ", round(densityRho, 3))

Prated = (.5) * (densityRho) * (np.pi * (40.0 ** 2)) * (0.44) * (0.9) * pow(Adj_vR, 3)
print("Rated power[W]: ", round(Prated, 3))
print("Rated power[MW]: ", round(Prated / 1e6, 3), "\n")

print("Part c)")
#compute Eannual

def PowerCalc(RawVelocity): #calculates power for a given wind velocity [W]
    if (RawVelocity > 15.0):
        return(Prated)
    elif(RawVelocity > 3.0):
        power = (0.5) * (densityRho) * (np.pi * (40.0 ** 2)) * (0.44) * (0.9) * pow((RawVelocity * pow((100/80), 0.14)), 3)
        return(power)
    else:
        return(0)


Eannual = 0
for f in ypoints: #sums wind velocity powers for the entire year [Wh]
    Eannual += PowerCalc(f)

print("E annual[Wh]: ", round(Eannual, 3))
print("E annual[GWh]: ", round(Eannual / 1e9, 3), "\n")

print("Part d)")
#calculate capacity factor for this wind turbine
TEannual = 8760 * Prated
CapacityFactor = Eannual / TEannual
print("Capacity Factor: ", round(CapacityFactor * 100, 3), "%, or ", round(CapacityFactor, 4), "\n")

print("Part e)")
#repeat analysis for alternative vR, vR = 14m/s
vR2 = 14.0
print("Rated Velocity 2: ", vR2, "m/s")
Adj_vR2 = vR2 * pow((100/80), 0.14)
Prated2 = (.5) * (densityRho) * (np.pi * (40.0 ** 2)) * (0.44) * (0.9) * pow(Adj_vR2, 3)
print("Rated power 2[W]: ", round(Prated2, 3))
print("Rated power 2[MW]: ", round(Prated2 / 1e6, 3))
#compute Eannual

def PowerCalc2(RawVelocity): #calculates power for a given wind velocity [W]
    if (RawVelocity > vR2):
        return(Prated2)
    elif(RawVelocity > 3.0):
        power2 = (0.5) * (densityRho) * (np.pi * (40.0 ** 2)) * (0.44) * (0.9) * pow((RawVelocity * pow((100/80), 0.14)), 3)
        return(power2)
    else:
        return(0)


Eannual2 = 0
for f in ypoints: #sums wind velocity powers for the entire year [Wh]
    Eannual2 += PowerCalc2(f)

print("E annual 2[Wh]: ", round(Eannual2, 3))
print("E annual 2[GWh]: ", round(Eannual2 / 1e9, 3))
#calculate capacity factor for this wind turbine
TEannual2 = 8760 * Prated2
CapacityFactor2 = Eannual2 / TEannual2
print("Capacity Factor 2: ", round(CapacityFactor2 * 100, 3), "%, or ", round(CapacityFactor2, 4), "\n")

print("Result Comparison:")
print("While the capacity factor of the calculations with the lower rated velocity is higher, the amount of power\n" \
"generated over the course of the year is lower by around half a gigawatt (or 500MW). This leads to the\n" \
"conclusion that a rated wind velocity of between 14 and 15 m/s would likely be optimal, since this would\n" \
"maximize performance for a lower cost than a rated wind speed of 15 m/s.\n" \
"It is also important to note that considering the goal of any system is to operate as efficiently as possible,\n" \
"a lower rated wind speed would improve the percentage of time that the wind turbine operates at full efficiency")

#I roll my dice
mp.show()