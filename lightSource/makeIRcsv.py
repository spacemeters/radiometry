
# Get Spacemeters module. Update server with # http://200.61.170.210:8080/gitpulloriginmaster
from wget import *
from host import *
print(hostingURL+"\n")
wget(hostingURL + "python/spacemeters.py")
wget(hostingURL + "python/spacemeters6S.py")
wget(hostingURL + "util/Makefile_edited.txt",dir="source")
wget(hostingURL + "util/ABSTRA_template.txt",dir="source")


from spacemeters import *

import numpy as np
import matplotlib.pyplot as plt

# init6SWindows()


sixSDir = '.\\build\\6SV1.1\\sixsV1.1'

from spacemeters6S import *
# Define concentrations

# C0 = concentration(ch4ppm=0,n2oppm=0,co2ppm=0,coppm=0)
C0 = concentration()
C0.set6S(prnt=True)

wl_start=.4
wl_end=2.5
Dwl = 0.001
Nwl = int(np.ceil((wl_end - wl_start) / Dwl))
wlSS = np.linspace(wl_start, wl_end, Nwl) # discretization of studied wavelengths

s = quickSixS(dir=sixSDir)
s.wavelength = Wavelength(wl_start, wl_end)
wlSS, irradiance = SixSHelpers.Wavelengths.run_wavelengths(s,wlSS,output_name="pixel_radiance",verbose=False)
irradiance = interpolateNans(wlSS,irradiance)
plt.plot(wlSS,irradiance);plt.title('Irradianza espectral')
plt.show()
xyToCSV(wlSS, irradiance, 'IRsixS.csv', header=['wl','I_R'])

