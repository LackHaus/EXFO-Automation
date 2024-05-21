import InstrumentControl
import pyvisa
import time
import numpy as np
t100shp = InstrumentControl.T100(9,1)
osa = InstrumentControl.Yokogawa(16,0)
wlm = InstrumentControl.Keysight86122(3,2)

wls = np.linspace(1440, 1640, 1640-1440+1)

osa_id = osa.platform.query("*IDN?")


f = open(osa_id[:-2]+".txt", "w")
f.write("T100S-HP,OSA,WLM\n")
for wl in wls:
    t100shp.setWL(wl)
    time.sleep(1)
    osa.setSweepCenter(wl)
    osa.setSweepSpan(2)
    osa.setSweepPoints(5000)
    osa.sweep()
    osa_peak = osa.getPeaks(-20)
    osa_peak = osa_peak.split(",")[0]
    wlm_peak = wlm.getWL()
    f.write(str(wl)+","+str(osa_peak)+","+str(wlm_peak))

    




