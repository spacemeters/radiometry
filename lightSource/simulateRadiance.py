
# Get Spacemeters module. Update server with # http://200.61.170.210:8080/gitpulloriginmaster
from wget import *
import host # ask for host file
print(host.URL+"\n")
wget(host.URL + "python/spacemeters.py")
wget(host.URL + "util/Makefile_edited.txt",dir="source")
wget(host.URL + "util/ABSTRA_template.txt",dir="source")


import spacemeters as sm

import numpy as np
import matplotlib.pyplot as plt
from Py6S import *
# init6SWindows()


sixSDir = ".\\build\\6SV1.1\\sixsV1.1"

# from spacemeters6S import *

# Define concentrations
# C0 = sm.sixs.concentration(ch4ppm=0,n2oppm=0,co2ppm=0,coppm=0,o2cent=0) # Modifies atmospheric concentration in 6S source code
# C0.set6S(prnt=True)

wl_start=.4
wl_end=.41
Dwl = 0.001
Nwl = int(np.ceil((wl_end - wl_start) / Dwl))
wlSS = np.linspace(wl_start, wl_end, Nwl) # discretization of studied wavelengths

s = sm.sixs.quickSixS(dir=sixSDir)
s.wavelength = Wavelength(wl_start, wl_end)  # micrometer  == mic
wlSS, irradiance = SixSHelpers.Wavelengths.run_wavelengths(s,wlSS,output_name="pixel_radiance",verbose=False)
irradiance = sm.interpolateNans(wlSS,irradiance)
plt.plot(wlSS,irradiance);plt.title('Irradianza espectral')

# sm.xyToCSV(wlSS, irradiance, '../simulation/IRsixS.csv', header=['wl','I_R'])

"""
	Transform to Intensity by defining orbital specification of satellite
"""
wlMKS = wlSS * 1e-6  # m
hLEO = 500e3    # m
Apx = (5e3)**2  # m2  area of observed pixel

I = Apx * irradiance / hLEO**2  # W/m2/mic   spectral intensity
_,aux =  sm.listMult(wlSS, I, wlSS,wlMKS, interp=False)  # photon/m2/mic
photonFlux = [1/sm.c/sm.h * x for x in aux]

sm.xyToCSV(wlSS, I, '../simulation/Isp.csv',header=['wl','Isp'])

"""
		Obtain current at sensor by defining constructive features of satellite
"""
Q = 0.8 # constant quantum efficency. 0.8 is typical for InGaAs sensors in Methane measuring range.
lensDiam = 30e-3 # lens diameter. Gosat has +70mm aperture
Alens = sm.pi * lensDiam ** 2 / 4
current = Q * Alens * sm.q * sm.Intgrt(wlSS, photonFlux )
print('current at sensor: %.3e' % current)
plt.show()
