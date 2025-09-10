# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2024.HF3 replay file
# Internal Version: 2024_05_20-17.43.19 RELr426 191376
# Run by ougbine on Wed Aug 27 19:04:59 2025
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(1.40774, 1.40952), width=207.219, 
    height=139.825)
session.viewports['Viewport: 1'].makeCurrent()
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
execfile('C:/Users/Ougbine/CutForce.py', __main__.__dict__)
#: [19:05:00] Python inside Abaqus : 3.10.5
#: [19:05:00] Opening ODB          : C:\Users\Ougbine\Yil.odb
#: Model: C:/Users/Ougbine/Yil.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     2
#: Number of Meshes:             2
#: Number of Element Sets:       7
#: Number of Node Sets:          9
#: Number of Steps:              1
#: [19:05:00] Found 1 RP node(s) : [963]
#: [19:05:02] Average cutting  force Fc = 622.114 N
#: [19:05:02] Average passive force Fp = 192.339 N
#: [19:05:02] Saved forces to out\Yil.hrf
#: [19:05:02] Done.
print('RT script done')
#: RT script done
