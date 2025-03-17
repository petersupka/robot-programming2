from microbit import sleep, pin14, pin15
from utime import ticks_diff, ticks_us

if __name__ == "__main__":

    perioda_cyklu_ms = 5
    while True:
        cas_zacatek = ticks_us()
        surova_data_leva = pin14.read_digital()
        surova_data_prava = pin15.read_digital()
        print(surova_data_leva, surova_data_prava)
        cas_konec = ticks_us()
        perioda_uspani = perioda_cyklu_ms - int(ticks_diff(cas_konec, cas_zacatek)/1000)
        if perioda_uspani < 0:
            print("Nestiham pocitat, omezte maximalni rychlost robota!"
            break;
        else:
            sleep(perioda_uspani)

