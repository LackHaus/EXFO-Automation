import InstrumentControl
import numpy as np
import time

# Declaring platforms and modules
ltb8 = InstrumentControl.LTB('169.254.244.64', 5025).platform
osa = InstrumentControl.OSA("LTB8", ltb8, 5)
dfb = InstrumentControl.DFB("LTB8", ltb8, 4)


from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

# Study parameters
# Number of SOP sweeps of OSA
nsops = [1000, 2000, 5000]
# Insturment Warmup time (s)
warmup = 60*30*0
rep = 10

time.sleep(warmup)
for k in range(rep):
    for nsop in nsops:
        time.sleep(1)
        osa.inband_Analysis([1545, 1555], nsop, "C:/OSA/2024-04-22_NS-scrambler"+"_"+str(k)+"_"+str(nsop)+".xosawdm")
        time.sleep(1)
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)
        print('NSOP: '+str(nsop))
        print('Repetition: '+str(k))

