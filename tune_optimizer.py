import numpy as np
from scipy.optimize import minimize
from epics import PV
import time

print('start tune optimizer')

tune_x = PV('TUNEZR:rdH')
tune_y = PV('TUNEZR:rdV')
current = PV('CUMZR:rdCur')

magnets = (
    PV('S3PTR:set'),
    PV('S4PDR:set'),
    PV('S4PTR:set'),
    PV('S4P1T6R:set'),
)

initial_values = np.array([magnet.get() for magnet in magnets])

print(initial_values)

for magnet in magnets:
    print(magnet.pvname, magnet.get())


def fitness(*args):
    while current.get() < 3:
        time.sleep(1)

    for magnet, value in zip(magnets, *args):
        magnet.put(value)
        print(f'set {magnet.pvname} to {value}')

    time.sleep(0.2)

    tune_diff = np.abs(tune_x.get() - 625)
    return tune_diff


def rest_to_initial():
    print('reset magnets to initial values')
    for magnet, value in zip(magnets, initial_values):
        magnet.put(value)

try:
    res = minimize(fitness, initial_values, method='Nelder-Mead')
except:
    rest_to_initial()
