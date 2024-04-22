import pyvisa

rm = pyvisa.ResourceManager()
print(rm.list_resources())

mpc_201 = rm.open_resource("GPIB0::5::INSTR")
print("Connexion established with: "+ mpc_201.query("*IDN?"))

mpc_201.write("INP:SCR:DISC:RATE 100")

