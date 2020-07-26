# Radiometry - SpaceMeters

## Requirements *Requerimientos*

### Python library requirements *requerimientos Python*:
* numpy
* pathlib
* requests
* matplotlib
* pandas
* Py6S

```
pip install numpy
pip install pathlib
pip install requests
pip install matplotlib
pip install pandas
pip install Py6S
```

### Spacemeter library *libreria de spacemeters*
Obtained from `github.com/spacemeters/serve/public/python`
* spacemeters
* spacemeters6S

### Other requirements *otros requerimientos*:
These files are downloaded automatically from spacemeter server upon running initalization function. 
*Estos archivos se descargan autmaticamente al correr una funci'on de inicialización de 6S de la libreria spacemeters*

* makefile (old distribution, comes in fortran zip *viene con el zip en el repositorio `serve`*)
* Fortran99 compiler (add `bin` folder to path *agregar la carpeta `bin` a la variable de entorno `PATH`*)

## Documentation *Documentación*
There are two simulations to date. One to obtain light incident on satellite with [6S](http://6s.ltdri.org/). 
This simulation can be found in `lightSource` folder. This simulation creates .csv files with incident light
intensity for use in FTS ([Fourier Transform Spectroscopy](https://en.wikipedia.org/wiki/Fourier-transform_spectroscopy)) simulation

*Existen dos simulaciones. En la simulación en la carpeta `lightSource` se encuentra la simulacion de 6S
en la cual se obtiene el espectro a medir en el satélite. La simulación genera archivos .csv con estos datos
para luego ser usados en la simulación FTS.*

---
Steps to recreate simulations *Pasos a seguir*

1. Run `lightSource/radianceSim.py` with python 3.8

2. Verify `simulation/Isp.csv` was created by first step

3. Run `simulation/ftsSim.py`



