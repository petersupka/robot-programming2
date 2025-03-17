from microbit import sleep, pin14, pin15
from utime import ticks_diff, ticks_us

if __name__ == "__main__":

    while True:
        cas_zacatek = ticks_us()
        surova_data_leva = pin14.read_digital()
        surova_data_prava = pin15.read_digital()
        print(surova_data_leva, surova_data_prava)
        sleep(5)
        cas_konec = ticks_us()
        print(cas_konec, cas_zacatek)

