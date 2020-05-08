from Py6S import *
from spacemeters import *

"""
    Crea el objeto SixS con opciones/parametros genericos para ahorrar espacio de codigo
"""
def quickSixS(dir="./build/6SV1.1/sixsV1.1"):
    s = SixS(path=dir)
    s.aero_profile = AeroProfile.PredefinedType(AeroProfile.Urban)
    s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.Tropical)
    s.geometry.from_time_and_location(-25.31, 33.23, "11:41", 14.9, 171.3)
    s.altitudes.set_sensor_satellite_level()
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(GroundReflectance.GreenVegetation)
    return s
