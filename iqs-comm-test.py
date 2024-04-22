import LTBIQS
import pyvisa

rm = pyvisa.ResourceManager()
iqs = rm.open_resource('GPIB0::12::INSTR')
print("Communication established with:" + str(iqs.query('*IDN?')))

voa_ase = LTBIQS.VOA(iqs, "IQS", 4)