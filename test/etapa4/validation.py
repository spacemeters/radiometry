# %% markdown
# <style>
# .center { /* Macros! */
#   display: block;
#   margin-left: auto;
#   margin-right: auto;
#   width: 50%;
# }
# </style>
# %% codecell
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
# sh('mkdir -p ./build/6SV/1.1')
# sh('make -C ./build/6SV1.1')

init6SWindows()

# wget(hostingURL + 'python/spacemeters6S.py')
# wget(hostingURL + 'python/ABSTRA_template.txt')
sixSDir = '.\\build\\6SV1.1\\sixsV1.1'
# %% codecell
from spacemeters6S import *
# chppm = [0,.5,1,1.5,2,2.5,3]
chppm = [0,3]
S = []
wl_start=1.62
wl_end=1.7
IR = []
sixS_wlSS_dict = {}
sixS_irradiance_dict = {}
# Optimize run_wavelengths. Do not use unnecessary resolution
Nwl = int(np.ceil((wl_end - wl_start)/0.001))
wlSS = np.linspace(wl_start, wl_end, Nwl)
for x in chppm:
  C = concentration(ch4ppm=x)
  C.set6S(prnt=True)
  s = quickSixS(dir=sixSDir)
  s.wavelength = Wavelength(wl_start, wl_end)
  wlSS, irradiance = SixSHelpers.Wavelengths.run_wavelengths(s,wlSS,output_name="pixel_radiance",verbose=False)
  IR.append(interpolateNans(wlSS,irradiance))
  sixS_wlSS_dict[x]= wlSS
  sixS_irradiance_dict[x]=irradiance
# %% markdown
# # Validatión de las modificaciones del PY6S para variar la concentración de CH4
# %% markdown
# La idea es comparar las modificaciones que Pato hizo en el cóódigo, con el méétodo Satellogic.
#
# Método satellogic para definir el Delta de iradianza debido a un exceso de CH4: Calcular la irradianza base con la atmóósfera default de ps6S y luego multiplicar por la transmisividad de unas ppm extra de CH4 en una columna L del orden de los kilómetros (obtenida mediante spectraplot).
#
# Para ello se elijióó el rango de longitudes de onda entre 1.665-1.66889 micróómetros
#
#
# %% codecell
from matplotlib import cm
# IRi = np.flat(IR)
IRnp = np.array(IR)
wlmesh, chmesh = np.meshgrid(wlSS, chppm)
fig = plt.figure()
ax = fig.gca(projection='3d')
surf = ax.plot_surface(wlmesh, chmesh, IRnp, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)

dictToCSV({'wl':list(wlmesh.flat),'ch':list(chmesh.flat),'ir':list(IRnp.flat)},filename='../test/plots/ch4ppmSurf-M%d.csv' % (len(chmesh)))


xyToCSV(list(wlmesh[0]),list(IRnp[0]), '../test/plots/IR0ppm.csv')
xyToCSV(list(wlmesh[len(IRnp)-1]),list(IRnp[len(IRnp)-1]), '../test/plots/IR3ppm.csv')
# for i in IRnp.flat:
#     print(i)
# for i in range(len(IRnp.flatten)):



# %% markdown
# # Método Satellogic para 1 ppm de CH4 en atmósfera con L = 10 Km
# %% codecell
# SPECTRA PLOT ---> L = 10 Km

# hostingURL = "http://200.61.170.210:8080/"
# 
#
# 
simFile = 'joinedSpectra.csv'
simNames = ['spectraplot/1.62_1.7_3ppm_.35atm_100km/CH4,x=3e-6,T=253K,P=.35atm,L=10000000cm,simNum0.csv','spectraplot/1.62_1.7_3ppm_.35atm_100km/CH4,x=3e-6,T=253K,P=.35atm,L=10000000cm,simNum1.csv', 'spectraplot/1.62_1.7_3ppm_.35atm_100km/CH4,x=3e-6,T=253K,P=.35atm,L=10000000cm,simNum2.csv','spectraplot/1.62_1.7_3ppm_.35atm_100km/CH4,x=3e-6,T=253K,P=.35atm,L=10000000cm,simNum3.csv']
simURLs = [hostingURL+x for x in simNames]
wgetData(simURLs, hostingURL)
joinSpectraPlots(simNames, filename='joinedSpectra.csv')


data = pd.read_csv(simFile)
wavenum=data['nu']
wlSpec = frecuencyToWavelength(wavenum) #Beware it's frecuency=wavelength

absorbance=data['CH4,x=3e-6,T=253K,P=.35atm,L=10000000cm'.replace(',','/')]
transmitance = [exp(-x) for x in absorbance]
plt.plot(wlSpec,transmitance);plt.title('Transmitancia')
plt.xlabel('wavelength [micrometer]');plt.ylabel('transmitance I/Io')
wlSpec, transmitance = sampleXY(wlSpec,transmitance, samples=4000)
plt.plot(wlSpec,transmitance);plt.title('Transmitancia')
plt.xlabel('wavelength [micrometer]');plt.ylabel('transmitance I/Io')


wl , modifiedIrradiance = listMult(wlSpec, transmitance, sixS_wlSS_dict[0], sixS_irradiance_dict[0])
# %% codecell
irradiance = list(IRnp[0])
mfig, ax = plt.subplots()
ax.plot(wl, modifiedIrradiance,'g-',linewidth=.5);plt.title('irradianzas')
ax.plot(wlSS, irradiance,'r--')
ax.plot(wlSS, list(IRnp[1]),'b-')
ax.legend(['Irradianza modificada','0ppm','3ppm'])
plt.show()

xyToCSV(wl, modifiedIrradiance, '../test/plots/modIR-3ppm-100km.csv', header=['wl','IR'])
xyToCSV(wlSpec,transmitance, '../test/plots/trans-3ppm-100km.csv')

PSS = Intgrt(wlSS,irradiance)
P3ppm = Intgrt(wlSS, list(IRnp[1]))
integratedModifiedIr = Intgrt(wl,modifiedIrradiance) # W/m2/sr
print('Energy analisis of methods of absorption')
print('Power incident at 0ppm:\t\t\t %2.5e [W/m2/sr]' % (PSS))
print('Power incident at 3ppm:\t\t\t %2.5e [W/m2/sr]' % (P3ppm))
print('Power incident affected by spectraplt:\t %2.5e [W/m2/sr]' % (integratedModifiedIr))

# %% markdown
# # Cálculo estilo nuevo
# %% codecell
Rearth = 6371e3 # [m] unused
hLEO   = 500e3  # [m] 
dlens  = 68e-3  # [m]   # GOSAT has 68mm aperture diameter
Asens  = dlens**2 * pi/4  # [m2] 
Apx    =  5000**2         # [m2] 
Q = 0.5  # quantum efficiency of sensor

photonMeanEnergy = h * c / 1.65e-6

intensityAtSat = Apx/(hLEO)**2 * Intgrt(wlSS, irradiance)
Psens = Asens * intensityAtSat
print(Psens)

wlMKS = [x * 1e-6 for x in wlSS] # convert sixS wavelength to [m]
_ , aux = listMult(wlSS, wlMKS, wlSS, irradiance)

baseAmperage = Q * Asens * Apx * q /h/c/(hLEO)**2 * Intgrt( wlSS, aux  )

deltaAmperage = baseAmperage * 0.01
print("Intensity at satellite:\t\t %2.4e W/m2" % (intensityAtSat))
print("Amperage measured:\t\t %2.4e A" % (baseAmperage))
print("Amperage difference due to CH4:\t %2.4e A" % (deltaAmperage))

Fmtf = 0.7
Tp = 0.85
Tm = 0.9
# Simpact = Intgrt(wlSS,Peff) * Fmtf * Tp * Tm  / ePhoton

# quantumEff = [gaussN(x,meanWl,sigma) * meanWl / 60 for x in wlMKS] #Quantum efficiency [] --> how many photons convert into electrons, it depends on the instrument.
# plt.plot(wlMKS,quantumEff); plt.title('Ejemplo de quantum efficiency');plt.show()


