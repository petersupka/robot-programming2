
from picoed import button_a, i2c
from time import sleep, monotonic_ns
from board import P8, P12
from digitalio import DigitalInOut
from ultrazvuk import Ultrazvuk
from math import fabs

def nastav_PWM_kanaly(kanal_on, kanal_off, rychlost):
    # je nesmirne dulezite vzdy mit zapnuty jen jeden kanal,
    # tedy tato funkce zarucuje, ze se druhy kanal vypne

    while not i2c.try_lock():
        pass
    try:
        i2c.writeto(0x70, kanal_off + bytes([0]))
        i2c.writeto(0x70, kanal_on + bytes([rychlost]))
    finally:
        i2c.unlock()
    
    return 0

def jed(strana, smer, rychlost):
    '''
       Tato funkce uvede dany motor do pohybu,
       zadanou rychlosti a v pozadovanem smeru.
       Vraci chybove hodnoty:
        0: vse je v poradku
       -1: program neprobehl spravne
       -2: zadane nepodporovane jmeno motoru
       -3: pozadovana rychlost je mimo mozny rozsah
       -4: zadany nepodporovany smer
    '''
    je_vse_ok = -1

    rychlost = int(rychlost)
    if rychlost < 0 or rychlost > 255:
        je_vse_ok = -3
        return

    if strana == "levy":
        if smer == "dopredu":
            je_vse_ok = nastav_PWM_kanaly(b"\x05", b"\x04", rychlost)
        elif smer == "dozadu":
            je_vse_ok = nastav_PWM_kanaly(b"\x04", b"\x05", rychlost)
        else:
            je_vse_ok = -4
    elif strana == "pravy":
        if smer == "dopredu":
            je_vse_ok = nastav_PWM_kanaly(b"\x03", b"\x02", rychlost)
        elif smer == "dozadu":
            je_vse_ok = nastav_PWM_kanaly(b"\x02", b"\x03", rychlost)
        else:
            je_vse_ok = -4
    else:
        je_vse_ok = -2

    return je_vse_ok

def zastav():
    jed("pravy", "dopredu", 0)
    jed("pravy", "dozadu", 0)
    jed("levy", "dopredu", 0)
    jed("levy", "dozadu", 0)

def sign(num):
    return -1 if num < 0 else 1

if __name__ == "__main__":

    zastav()
    ultrazvuk = Ultrazvuk(DigitalInOut(P8), DigitalInOut(P12))

    reference = 0.2 # na jakou vzdalenost cheme zastavit [m]
    P = -400
    max_PWM = 150 #teoreticky 255, ale ja se bojim :)
    min_PWM = 70 # idealne zjisteno kalibraci, nebo vypozorovano, kdy se robot odlepi
    mrtva_zona = 0.05 #napr 5cm - kdy regulace uz rekne "uz tu jsem" a prestane regulovat

    predchozi_akcni_zasah = 0 #potrebuji, abych osetrila, ze motory se nikdy nerozjedou skokove do protismeru
    
    while not button_a.was_pressed():
        merena_vzdalenost = ultrazvuk.proved_mereni_blokujici(timeout=0.01)
        if merena_vzdalenost < 0:
            print("error")
            continue
        else:
            error = reference - merena_vzdalenost
            akcni_zasah = P * error
            if fabs(akcni_zasah) > max_PWM:
                akcni_zasah = sign(akcni_zasah) * max_PWM
            if fabs(akcni_zasah) < min_PWM:
                if fabs(error) > mrtva_zona:
                    akcni_zasah = sign(akcni_zasah) * min_PWM
                else:
                    akcni_zasah = 0
            
            print(merena_vzdalenost, error, akcni_zasah)

            # osetreni, ze nikdy motory neposleme do protismeru hned
            # normalne bych tohle v regulaci nemela,
            # zde to mame, protoze nase motory jsou dost blbe
            if sign(predchozi_akcni_zasah) != sign(akcni_zasah):
                zastav()

            if akcni_zasah > 0:
                
                jed("pravy", "dopredu", fabs(akcni_zasah))
                jed("levy", "dopredu", fabs(akcni_zasah))
            else:
                jed("pravy", "dozadu", fabs(akcni_zasah))
                jed("levy", "dozadu", fabs(akcni_zasah))
            
            predchozi_akcni_zasah = akcni_zasah

        sleep(0.05)
    
    zastav()
    

   

