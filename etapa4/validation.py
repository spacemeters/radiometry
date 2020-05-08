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

hostingURL = "http://200.61.170.210:8080/"
from spacemeters import *

import numpy as np
import matplotlib.pyplot as plt

init6SWindows()

wget(hostingURL + 'python/spacemeters6S.py')
wget(hostingURL + 'python/ABSTRA_template.txt')
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
  set6SCH4ppm(x)
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
# simURLs = [hostingURL+x for x in simNames]
# simFile = 'joinedSpectra.csv'
# wgetData(simURLs, hostingURL)

simNames = ['spectraplot/1.62_1.7_3ppm_.35atm_100km/CH4,x=3e-6,T=253K,P=.35atm,L=10000000cm,simNum0.csv','spectraplot/1.62_1.7_3ppm_.35atm_100km/CH4,x=3e-6,T=253K,P=.35atm,L=10000000cm,simNum1.csv', 'spectraplot/1.62_1.7_3ppm_.35atm_100km/CH4,x=3e-6,T=253K,P=.35atm,L=10000000cm,simNum2.csv','spectraplot/1.62_1.7_3ppm_.35atm_100km/CH4,x=3e-6,T=253K,P=.35atm,L=10000000cm,simNum3.csv']

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
# # Método Satellogic para 2 ppm de CH4 en atmósfera con L = 10 km
# %% codecell
# SPECTRA PLOT ---> L = 10 Km

# hostingURL = "http://200.61.170.210:8080/"

simNames = ['spectraplot/1.62_1.7_2ppm_L=10km/CH4,x=0.000002,T=253K,P=0.53atm,L=1000000cm,simNum0.csv']
simNames.append('spectraplot/1.62_1.7_2ppm_L=10km/CH4,x=0.000002,T=253K,P=0.53atm,L=1000000cm,simNum1.csv')
simNames.append('spectraplot/1.62_1.7_2ppm_L=10km/CH4,x=0.000002,T=253K,P=0.53atm,L=1000000cm,simNum2.csv')

simURLs = [hostingURL+x for x in simNames]
simFile = 'joinedSpectra.csv'
wgetData(simURLs, hostingURL)
joinSpectraPlots(simNames,filename=simFile)
data = pd.read_csv(simFile)
wavenum=data['nu']
wlSpec = frecuencyToWavelength(wavenum) #Beware it's frecuency=wavelength

absorbance=data['CH4,x=0.000002,T=253K,P=0.53atm,L=1000000cm'.replace(',','/')]
transmitance = [exp(-x) for x in absorbance]
SixSHelpers.Wavelengths.plot_wavelengths(wlSpec, absorbance, "absorption -ln(I/Io)")
plt.plot(wlSpec,transmitance);plt.title('Transmitancia')
plt.xlabel('wavelength [micrometer]');plt.ylabel('transmitance I/Io')
#print(waveNum,absorbance)
wl , modifiedIrradiance = listMult(wlSpec, transmitance, sixS_wlSS_dict[0], sixS_irradiance_dict[0])
# %% codecell
mfig, ax = plt.subplots()
ax.plot(wl, modifiedIrradiance,'b-');plt.title('irradianza default +'+simNames[0])
ax.plot(wlSS, irradiance,'r--');ax.legend(['Irradianza modificada','Irradianza 6S'])
plt.show()
xyToCSV(wl, modifiedIrradiance, 'modIR.csv', header=['wl','IR'])
integratedModifiedIr = Intgrt(wl,modifiedIrradiance) # W/m2/sr
print('\n Using Satellogic technique:')
print('Irradiance of ligth impacting the satellite lens :%2.5e W/m2/sr' % (integratedModifiedIr))
print('with wavelength = %1.3f micrometers and bandwidth = %1.3f micrometers\n' % ((wl_start+wl_end)/2, wl_end-wl_start))
print('')

integratedIr = Intgrt(sixS_wlSS_dict[2],sixS_irradiance_dict[2])
print('Original s6 data Unaffected by spectraplot data:')
print('Irradiance of ligth impacting the satellite lens :%2.10e W/m2/sr' % (integratedIr))
print('with wavelength = %1.3f micrometers and bandwidth = %1.3f micrometers' % ((wl_start+wl_end)/2, wl_end-wl_start))


# %% markdown
# # Signal to noise ratio - to complete
# %% codecell
satelliteAltitude = 500e3 # 500km altitude
areaLente = 0.0254*0.0254 # Lens area or entering area of the ligth before converging it [m^2]
areaObsTierra = 5000*5000 # Observed earth area [m^2]
Pwl = irradianceToPower(modifiedIrradiance, satelliteAltitude , areaObsTierra , areaLente ) # W/mic
SixSHelpers.Wavelengths.plot_wavelengths(wl, modifiedIrradiance, "Pixel radiance [w/m2/sr/mic]")

# Corremos la simulacion

meanWl = (wl_start + wl_end)/2  # [micro m]
meanWlmeter = meanWl*1e-6
#Calculations for SNR
# Vamos a obtener una curva real de quantumEff
wlQ = [x for x in np.linspace(wl_start,wl_end,20)]
quantumEff = [gaussN(x,meanWl,(meanWl-wl_start)/1.5)/400 for x in wlQ] #Quantum efficiency [] --> how many photons convert into electrons, it depends on the instrument.
plt.plot(wlQ,quantumEff); plt.title('Ejemplo de quantum efficiency');plt.show()

Fmtf = 0.7
Tp = 0.85
Tm = 0.9

#photon energy


ePhoton = h*c/(meanWl*1e-6)
# Psat in [W/mic],  wl [mic],  quantumEff [%]
#Simpact

wl, Peff = listMult(wl,Pwl,wlQ,quantumEff) # Effective power
plt.plot(wl,Peff);plt.title('Potencia eficaz  [W/mic]')
# print(Peff)
Simpact = Intgrt(wl,Peff) * Fmtf * Tp * Tm  / ePhoton



# %% codecell
# print([gaussN(x,meanWl,meanWl-wl_start*1e-6) for x in wl])
print(meanWl,wl_start)
# %% codecell
  #plt.set_xlabel('wavelength [micrometer]');ax.set_ylabel('irradiance [W/sr/m^2/mic]')
  # transmitancia = [exp(-x) for x in absorbSpec]
  # wlSpec = frecuencyToWavelength(frecSpec) # see spacemeters.py
  # SixSHelpers.Wavelengths.plot_wavelengths(wlSpec, absorbSpec, "absorption -ln(I/Io)")

  # #Multiplicación de transmitividad del spectraplot con los datos de irradianza de PyS6
  # wl , modifiedIrradiance = listMult(wlSpec,1-absorbSpec,wlSS, irradiance )
  # # absorbSpec = listInterpolate(wlSpec,wavelengths,irradiance)
  # plt.plot(wl,modifiedIrradiance,'b-');plt.title('irradianza default +'+simName);plt.show()

  #SixSHelpers.Aeronet.import_aeronet_data(s, aeronetFilename,  "12/01/2016 11:43")
  # satelliteAltitude = 500e3 # 500km altitude
  # areaLente = 0.0254*0.0254 # Lens area or entering area of the ligth before converging it [m^2]
  # areaObsTierra = 5000*5000 # Observed earth area [m^2]

  # Pwl = irradianceToPower(modifiedIrradiance, satelliteAltitude , areaObsTierra , areaLente ) # W/mic

  # # SixSHelpers.Wavelengths.plot_wavelengths(wl, Pwl, "Power at satellite  [w/mic]")
  # # Escribo nuestro archivo 6S de entrada. Util para debugear manualmente el 6S
  # s.write_input_file(filename="input6s.txt")

  # P = Intgrt(wl,Pwl) # W

  # print('Power of ligth impacting the satellite lens :%2.1e W' % (P))
  # print('with wavelength = %1.3f micrometers and bandwidth = %1.3f micrometers' % ((wl_start+wl_end)/2, wl_end-wl_start))



# for i in range(1,2):
#   simName = eval('simName'+str(i))
#   simFolder = 'spectraplot/1.665_1.66889'
#   simFilename = simName + '.csv'
#   urlSpectra = hostingURL + simFolder + '/' + simFilename
#   wget(urlSpectra)
#   data = pd.read_csv(simFilename)
#   frecSpec, absorbSpec = data["nu"], data[simName.replace(',','/')]
#   transmitancia = [exp(-x) for x in absorbSpec]
#   wlSpec = frecuencyToWavelength(frecSpec)

#   wl , modifiedIrradiance = listMult(wlSpec, transmitancia, wlSS, irradiance)
#   SixSHelpers.Wavelengths.plot_wavelengths(wlSpec, absorbSpec, "absorption -ln(I/Io)")
#   plt.plot(wlSpec,transmitancia);plt.title('Transmitancia')
#   plt.xlabel('wavelength [micrometer]');plt.ylabel('transmitance I/Io')

#   fig, ax = plt.subplots()

#   ax.plot(wl, modifiedIrradiance,'b-');plt.title('irradianza default +'+simName)
#   ax.plot(wlSS, irradiance,'r--');ax.legend(['Irradianza modificada','Irradianza 6S'])
#   plt.show()
  #plt.set_xlabel('wavelength [micrometer]');ax.set_ylabel('irradiance [W/sr/m^2/mic]')
  # transmitancia = [exp(-x) for x in absorbSpec]
  # wlSpec = frecuencyToWavelength(frecSpec) # see spacemeters.py
  # SixSHelpers.Wavelengths.plot_wavelengths(wlSpec, absorbSpec, "absorption -ln(I/Io)")

  # #Multiplicación de transmitividad del spectraplot con los datos de irradianza de PyS6
  # wl , modifiedIrradiance = listMult(wlSpec,1-absorbSpec,wlSS, irradiance )
  # # absorbSpec = listInterpolate(wlSpec,wavelengths,irradiance)
  # plt.plot(wl,modifiedIrradiance,'b-');plt.title('irradianza default +'+simName);plt.show()

  #SixSHelpers.Aeronet.import_aeronet_data(s, aeronetFilename,  "12/01/2016 11:43")
  # satelliteAltitude = 500e3 # 500km altitude
  # areaLente = 0.0254*0.0254 # Lens area or entering area of the ligth before converging it [m^2]
  # areaObsTierra = 5000*5000 # Observed earth area [m^2]

  # Pwl = irradianceToPower(modifiedIrradiance, satelliteAltitude , areaObsTierra , areaLente ) # W/mic

  # # SixSHelpers.Wavelengths.plot_wavelengths(wl, Pwl, "Power at satellite  [w/mic]")
  # # Escribo nuestro archivo 6S de entrada. Util para debugear manualmente el 6S
  # s.write_input_file(filename="input6s.txt")

  # P = Intgrt(wl,Pwl) # W

  # print('Power of ligth impacting the satellite lens :%2.1e W' % (P))
  # print('with wavelength = %1.3f micrometers and bandwidth = %1.3f micrometers' % ((wl_start+wl_end)/2, wl_end-wl_start))

# %% markdown
# ### Corremos la simulacion e imprimimos datos de interes
#
# %% codecell
s.run()
# Output específicos
print("Pixel Reflectance = ", s.outputs.pixel_reflectance,", Pixel Radiance = ", s.outputs.pixel_radiance,", Direct Solar Irradiance = ", s.outputs.direct_solar_irradiance)

# output de metáno, resultado dividido en los dos trayectos
print("ch4 = " , s.outputs.transmittance_ch4)

# Nota : (nW/cm^2) / sr/nm
# %% markdown
# El uso de los datos en "spectal plot" , http://www.spectraplot.com/absorption también puede ser muy útil. Con este programa se tiene como resultado el espectro de la luz después de pasar por una columna de gas. Similar al Py6s, pero en este caso los datos se obtienen teniendo en cuenta un rango de longitud de onda menor al que podemos acceder con el programa py6s. Aunque esto puede hacer que la descarga de datos sea muy largo, tiene la capacidad de editar el contenido de la columan (el gas) tanto como la longitud y el ancho de la columna. Puede ser util para la modelación de una fuga de metáno por ejémplo.
# %% markdown
# # Clases de Py6S
#
# %% codecell
# geometry class
  """Stores parameters for a user-defined geometry for 6S.
          Attributes:

          * ``solar_z`` -- Solar zenith angle
          * ``solar_a`` -- Solar azimuth angle
          * ``view_z`` -- View zenith angle
          * ``view_a`` -- View azimuth angle
          * ``day`` -- The day the image was acquired in (1-31)
          * ``month`` -- The month the image was acquired in (0-12)

    .User() method overwrites with default values, do not use! (pato note)
  """

# aero_profile
  """ Escalar correspondiente a:
      NoAerosols = 0
      Continental = 1
      Maritime = 2
      Urban = 3
      Desert = 5
      BiomassBurning = 6
      Stratospheric = 7
  """

# atmos_profile
  """ Escalar. Guarda un enumerate. El numero corresponde as follows:
      NoGaseousAbsorption = 0
      Tropical = 1
      MidlatitudeSummer = 2
      MidlatitudeWinter = 3
      SubarcticSummer = 4
      SubarcticWinter = 5
      USStandard1962 = 6
  """

# Wavelength
  """Select one or more wavelengths for the 6S simulation.

      There are a number of ways to do this:

      1. Pass a single value of a wavelength in micrometres.
        The simulation will be performed for just this wavelength::

          Wavelength(0.43)

      2. Pass a start and end wavelength in micrometres.
        The simulation will be performed across this wavelength range with a
        constant filter function (spectral response function) of 1.0::

          Wavelength(0.43, 0.50)

      3. Pass a start and end wavelength, and a filter given at 2.5nm intervals.
        The simulation will be performed across this wavelength range using the
        given filter function::

          Wavelength(0.400, 0.410, [0.7, 0.9, 1.0, 0.3, 0.15])

        The filter function must include values for the start and end wavelengths,
        plus values every 2.5nm (0.0025um) in between. So, in the example above,
        there are five values given: one each for 0.400, 0.4025, 0.405, 0.4075, 0.410.

      4. Pass a constant (as defined in this class) for a pre-defined wavelength
        range::

          Wavelength(PredefinedWavelengths.LANDSAT_TM_B1)
  """

# SixSHelpers.Wavelengths
  """ run_wavelengths
          Runs the given SixS parameterisation for each of the wavelengths given, optionally extracting a specific output.

          This function is used by all of the other wavelengths running functions, such as :method:`run_vnir`, and thus
          any arguments that are passed to this function can also be passed to these other functions.

          The calls to 6S for each wavelength will be run in parallel, making this function far faster than simply
          running a for loop over each wavelength.

          Arguments:

          * ``s`` -- A :class:`.SixS` instance with the parameters set as required
          * ``wavelengths`` -- An iterable containing the wavelengths to iterate over
          * ``output_name`` -- (Optional) The output to extract from ``s.outputs``, as a string that could be placed after ``s.outputs.``, for example ``pixel_reflectance``
          * ``n`` -- (Optional) The number of threads to run in parallel. This defaults to the number of CPU cores in your system, and is unlikely to need changing.
          * ``verbose`` -- (Optional) Print wavelengths as Py6S is running (default=True)

          Return value:

          A tuple containing the wavelengths used for the run and the results of the simulations. The results will be a list of :class:`SixS.Outputs` instances if ``output_name`` is not set,
          or a list of values of the selected output if ``output_name`` is set.

          Example usage::

            # Run for all wavelengths from 0.4 to 0.5 micrometers, with a spacing of 1nm, returns SixS.Outputs instances
            wavelengths, results = SixSHelpers.PredefinedWavelengths.run_wavelengths(s, np.arange(0.400, 0.500, 0.001))
            # Run for all wavelengths from 0.4 to 0.5 micrometers, with a spacing of 1nm, returns a list of pixel radiance values
            wavelengths, results = SixSHelpers.PredefinedWavelengths.run_wavelengths(s, np.arange(0.400, 0.500, 0.001), output_name='pixel_radiance')
            # Run for the first three Landsat TM bands
            wavelengths, results = SixSHelpers.PredefinedWavelengths.run_wavelengths(s, [PredefinedWavelengths.LANDSAT_TM_B1, PredefinedWavelengths.LANDSAT_TM_B2, PredefinedWavelengths.LANDSAT_TM_B3)
  """

# SixSHelpers.Aeronet
  """  def import_aeronet_data(s, filename, time):
  Imports data from an AERONET data file to a given SixS object.

          This requires a valid AERONET data file and the `pandas` package (see http://pandas.pydata.org/ for
          installation instructions).

          The type of AERONET file required is a *Combined file* for All Points (Level
          1.5 or 2.0)

          To download a file like this:

          1. Go to http://aeronet.gsfc.nasa.gov/cgi-bin/webtool_opera_v2_inv

          2. Choose the site you want to get data from

          3. Tick the box near the bottom labelled as "Combined file (all products without phase functions)"

          4. Choose either Level 1.5 or Level 2.0 data. Level 1.5 data is unscreened, so contains far more data meaning it is more likely for you to find data near your specified time.

          5. Choose All Points under Data Format

          6. Download the file

          7. Unzip

          8. Pass the filename to this function


          Arguments:

          * ``s`` -- A :class:`.SixS` instance whose parameters you would like to set with AERONET data
          * ``filename`` -- The filename of the AERONET file described above
          * ``time`` -- The date and time of the simulation you want to run, used to choose the AERONET data which is closest
            in time. Provide this as a string in almost any format, and Python will interpret it. For example, ``"12/03/2010 15:39"``. When dates are ambiguous, the parsing routine will favour DD/MM/YY rather than MM/DD/YY.

          Return value:

          The function will return ``s`` with the ``aero_profile`` and ``aot550`` fields filled in from the AERONET data.

          Notes:

          Beware, this function makes a number of assumptions and performs a number of possibly-inaccurate steps.

          1. The refractive indices for aerosols are only provided in AERONET data at a few wavelengths, but 6S requires
          them at 20 wavelengths. Thus, the refractive indices are extrapolated outside of their original range, to provide
          the necessary data. This is generally not a wonderful idea, but it is the only way to be able to use the data
          within 6S. In many cases the refractive indices seem to change very little - but please do check this yourself!

          2. The AERONET AOT measurement at the wavelength closest to 550nm (the wavelength required for the AOT
          specification in 6S) is used. This varies depending on the AERONET site, but may be 50-100nm (or more) away
          from 550nm. In future versions this code will interpolate the AOT at 550nm using the Angstrom coefficent.=
  """
# %% codecell
# INPUT FILE FOR 6S
"""
0 (User defined)
47.654178 320.353832 14.900000 171.300000 4 24
1
3
0
0.500000 value
0.000000
-1000.000000
0 constant filter function
1.500000 1.700000   (wavelength bandwidth)
0 Homogeneous surface
0 No directional effects
1

Using the above input file I determined pixel radiance for
the following concentrations of methane. Default value is 1.72 ppm.

CH4 [ppm], pixel rad at satel. level[w/m2/sr/mic]
0    ,  14.494
0.010,  14.493
0.025,  14.491
0.050,  14.489
0.075,  14.487
0.100,  14.485
0.200,  14.477
0.300,  14.468
0.400,  14.460
0.500,  14.453
0.600,  14.445
0.700,  14.437
0.800,  14.430
0.900,  14.423
1.000,  14.416
1.100,  14.409
1.200,  14.402
1.300,  14.395
1.400,  14.388
1.500,  14.382
1.600,  14.375
1.700,  14.369
1.720,  14.367
1.800,  14.362
1.900,  14.356
7.000,  14.099
"""

# wvAll = np.arange(0.2, 4.0, 0.01)
# # wavelengthsAll, irradianceAll = SixSHelpers.Wavelengths.run_wavelengths(s,wvAll,output_name="pixel_radiance")
# """ irradianceToIntensity
# takes irradiance [W/m^2/sr/micrometer] iterable and satellite altitude and returns
# intensity at said altitude in  W/m^2/micrometer
# """
# def irradianceToIntensity(IR, altitudeSatellite ):
#   areaObsTierra = 10e3*10e3
#   pi = 3.14159265359
#   RT = 6371e3 # earth radius in meters [m]
#   h_space = 100e3 # Altitude of space in meters (as 6S sets it)
#   #  factor = 4*pi*RT**2 * (RT + altitudeSatellite)**-2 # OLD
#   factor = areaObsTierra  * (RT + altitudeSatellite)**-2
#   I = []
#   for i in range(len(IR)):
#     I.append( factor * IR[i] )
#   return I # Returns W/m^2/micrometer

# Iall = irradianceToIntensity(irradianceAll, 500e3)

# SixSHelpers.Wavelengths.plot_wavelengths(wavelengthsAll, irradianceAll, "Pixel radiance [w/m2/sr/mic]")
# SixSHelpers.Wavelengths.plot_wavelengths(wavelengthsAll, Iall, "Intensity at satellite  [w/mic]")

# Pall = Intgrt(wavelengthsAll,Iall)
# print(Pall)
# %% codecell
s.write_input_file(filename="input6s.txt")
# %% codecell
