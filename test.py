import InstrumentControl
import numpy as np
ltb8 = InstrumentControl.LTB('169.254.244.64', 5025).platform
tla = InstrumentControl.TLS('LTB8', ltb8, 0)
import time
osa = InstrumentControl.Yokogawa(1)
osa.setSweepSpan(5)
osa.setSweepPoints(20000)

wlm = InstrumentControl.Keysight86122(2)

wlm.setPeakThreshold(0)

f = open('results.csv', 'w')

f.write('asked wl,osa wl,wlm wl\n')


for wl in np.linspace(1545, 1560, 10):
    tla.setWL(wl*1e-9)
    osa.setSweepCenter(wl)
    time.sleep(1)
    osa.sweep()
    time.sleep(1)
    wl2 = osa.getPeaks(0).split(',')[0]
    time.sleep(1)
    wl3 = wlm.getWL()
    time.sleep(1)
    f.write(str(wl)+','+str(wl2)+','+str(wl3))
    time.sleep(1)
