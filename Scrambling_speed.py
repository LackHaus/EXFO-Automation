import InstrumentControl
import numpy as np
import time

# Declaring platforms and modules
ltb8 = InstrumentControl.LTB('169.254.244.64', 5025).platform
mpc_201 = InstrumentControl.MPC_201(5)
osa = InstrumentControl.OSA("LTB8", ltb8, 5)
dfb = InstrumentControl.DFB("LTB8", ltb8, 4)


from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

# Study parameters
# Discrete scrambling number of points per second
disc_spd = [0]
# Triangle scrambling number of periods per second
#tri_spd = np.linspace(0, 5, 6)
# Number of SOP sweeps of OSA
nsops = [1000,2000,3000,4000,5000]
# Insturment Warmup time (s)
warmup = 60*30*0
rep = 5
times = []
time.sleep(warmup)
for k in range(rep):
    for nsop in nsops:
        for i in range(len(disc_spd)):
            ds = round(disc_spd[i])
            mpc_201.setDisc()
            time.sleep(1)
            mpc_201.setRate(ds)
            time.sleep(1)
            osa.inband_Analysis([1545, 1555], nsop, "C:/OSA/2024-04-18_disc_"+str(ds)+"_"+str(k)+"_"+str(nsop)+".xosawdm")
            time.sleep(1)
            now = datetime.now()

            current_time = now.strftime("%H:%M:%S")
            print("Current Time =", current_time)
            print('NSOP: '+str(nsop))
            print('Scrambling rate: '+str(ds))
            print('Repetition: '+str(k))
            times.append(current_time)

mpc_201.setRate(0)
