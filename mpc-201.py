import InstrumentControl
import numpy as np
import time

mpc_201 = InstrumentControl.MPC_201(5) # Connexion au scrambler

mpc_201.setDisc() # Change le mode pour Discrete
#mpc_201.setTri() # Change le mode pour Triangulaire
mpc_201.setRate(5) # Set la vitesse de scrambling a 1 Hz



