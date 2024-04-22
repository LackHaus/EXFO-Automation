import InstrumentControl

ltb2 = InstrumentControl.LTB('169.254.54.44', 5025).platform
osa = InstrumentControl.OSA("LTB8", ltb2, 0)

for i in range(10):
    osa.inband_Analysis([1550, 1560], 10, "C:Users/Public/test"+str(i)+".xosawdm")
