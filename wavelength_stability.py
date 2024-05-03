import InstrumentControl
import pyvisa

rm = pyvisa.ResourceManager()
print(rm.list_resources())


osa = InstrumentControl