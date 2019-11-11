import numpy as np
from scipy.optimize import minimize
from epics import PV
import time

print('start tune optimizer')

tune_x = PV('TUNEZR:rdH')
tune_y = PV('TUNEZR:rdV')
tune_put = PV('TUNEXPV:sign_apply')
current = PV('CUMZR:rdCur')

magnets = (
    PV('S3PTR:set'),
    PV('S4PDR:set'),
    PV('S4PTR:set'),
    PV('S4P1T6R:set'),
)

lifetime = PV('TOPUPCC:rdLT')

initial_values = np.array([magnet.get() for magnet in magnets])
diff = 0.005
bounds = ((value * (1 - diff), value * (1 + diff)) for value in initial_values)

print(initial_values)

for magnet in magnets:
    print(magnet.pvname, magnet.get())

counter = 0


def fitness(*args):
    while current.get() < 3:
        print('wait for 5 seconds, paul please give me new current!')
        time.sleep(5)
        return 1000

    for magnet, value in zip(magnets, *args):
        magnet.put(value)
        print(f'set {magnet.pvname} to {value}')

    global counter
    if counter % 20:
        if tune_x.get() < 625:
            tune_put.put(1)
        else:
            tune_put.put(-1)

    time.sleep(2)
    counter += 1

    return -lifetime.get()


def rest_to_initial():
    print('reset magnets to initial values')
    for magnet, value in zip(magnets, initial_values):
        magnet.put(value)


try:
    # while True:
    #     tmp = tune_x.get() - 625
    #     if tmp < 5:
    #         break
    #
    #     if tune_x.get() < 625:
    #         tune_put.put(1)
    #         tune_put.put(1)
    #         tune_put.put(1)
    #     else:
    #         tune_put.put(-1)
    #         tune_put.put(-1)
    #         tune_put.put(-1)

    res = minimize(fitness, initial_values, method='Nelder-Mead')

except:
    rest_to_initial()
