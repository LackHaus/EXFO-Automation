import InstrumentControl
import numpy as np
import time

# Declaring platforms and modules
ltb8 = InstrumentControl.LTB('169.254.244.64', 5025).platform
mpc_201 = InstrumentControl.MPC_201(5)
osa = InstrumentControl.OSA("LTB8", ltb8, 5)
dfb = InstrumentControl.DFB("LTB8", ltb8, 4)
scr_arr = 2**(np.linspace(0, 14, 15))-1

n_acq = 5000
n_av = 2

for scrambling_rate in scr_arr:
    for i in range(n_acq):
        mpc_201.setRate(scrambling_rate)
        time.sleep(1)
        mpc_201.setRate(0)
        time.sleep(1)
        osa.inband_Analysis([1545, 1555], n_av, "C:/OSA/2024-04-05_av_"+str(scrambling_rate)+"_"+str(i)+".xosawdm")
        time.sleep(1)


mpc_201.setRate(0)


