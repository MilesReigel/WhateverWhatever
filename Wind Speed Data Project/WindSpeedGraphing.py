import matplotlib.pyplot as mp
import numpy as np

ypoints = np.loadtxt("wind_data.csv", delimiter = ",")
datacounter = 0
binmod = np.arange(0.0, 20.0, 1.0)
npypoints = np.array(ypoints)

#straight up plotting it
#how evil
style = {'facecolor': 'indigo', 'edgecolor': 'white', 'linewidth': 1}

mp.hist(ypoints, bins = binmod, histtype = 'bar', **style)
mp.xlabel("Wind Speed (mph)")
mp.ylabel("Number of occurences")


mp.show()