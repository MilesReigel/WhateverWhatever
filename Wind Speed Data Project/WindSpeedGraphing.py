import matplotlib.pyplot as mp
import numpy as np

ypoints = np.loadtxt("wind_data.csv", delimiter = ",")
datacounter = 0
binmod = np.arange(0.0, 30.0, 1.0)
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
print("Density[kg/m^3]: ", densityRho)

Prated = (.5) * (densityRho) * (np.pi * (40.0 ** 2)) * (0.44) * (0.9) * pow(Adj_vR, 3)
print("Rated power[W]: ", Prated)
print("Rated power[MW]: ", Prated / 1e6, "\n")

print("Part c)")
#compute Eannual

def PowerCalc(RawVelocity): #calculates power for a given wind velocity [j/s]
    if (RawVelocity > 15.0):
        return(Prated)
    elif(RawVelocity > 3.0):
        power = (0.5) * (densityRho) * (np.pi * (40.0 ** 2)) * (0.44) * (0.9) * pow((RawVelocity * pow((100/80), 0.14)), 3)
        return(power)
    else:
        return(0)


Eannual = 0
for f in ypoints: #sums wind velocity powers for the entire year [j * hours = Wh]
    Eannual += (PowerCalc(f) * 3600)

print("E annual[Wh]: ", Eannual)
print("E annual[GWh]: ", Eannual / 1e9, "\n")


#I roll my dice
mp.show()