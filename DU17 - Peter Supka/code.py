from picoed import button_a, button_b, i2c, display
from time import sleep
from digitalio import DigitalInOut
from ultrazvuk import Ultrazvuk
from math import fabs
import board, pwmio, time, sys

pin_forward = pwmio.PWMOut(board.P13, duty_cycle=0) # Forward direction, P13 from servo driver #2
pin_reverse = pwmio.PWMOut(board.P16, duty_cycle=0) # Reverse direction, P16 from speaker

def init_motors():
    while not i2c.try_lock():
        pass
    try:
        i2c.writeto(0x70, b'\x00\x01')
        i2c.writeto(0x70, b'\xE8\xAA')
        time.sleep(0.1)
    finally:
        i2c.unlock()

def set_canals(canal_on, canal_off, speed):
    if ((canal_on == b"\x05") and (canal_off == b"\x04")) or \
       ((canal_on == b"\x04") and (canal_off == b"\x05")):
        while not i2c.try_lock():
            pass
        try:
            i2c.writeto(0x70, canal_off + bytes([0]))
            i2c.writeto(0x70, canal_on + bytes([speed]))
        finally:
            i2c.unlock()
    else:   # pokial je kanal pravy, ovlada sa cez L293D (inak interny H-Bridge priamo na doske pre lavy motor)
        if canal_on == "P13":
            pin_reverse.duty_cycle = 0
            pin_forward.duty_cycle = int(speed * 65535 / 255)
        elif canal_on == "P16":
            pin_forward.duty_cycle = 0
            pin_reverse.duty_cycle = int(speed * 65535 / 255)
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
        return je_vse_ok
    if strana == "levy":
        if smer == "dopredu":
            je_vse_ok = set_canals(b"\x05", b"\x04", rychlost)
        elif smer == "dozadu":
            je_vse_ok = set_canals(b"\x04", b"\x05", rychlost)
        else:
            je_vse_ok = -4
    elif strana == "pravy":     # riesime cez L293D (externy H-Bridge)
        if smer == "dopredu":
             je_vse_ok = set_canals(b"\x03", b"\x02", rychlost)
             je_vse_ok = set_canals(pin_forward.duty_cycle, pin_reverse.duty_cycle, rychlost)
             je_vse_ok = set_canals("P13", "P16", rychlost)
        elif smer == "dozadu":
             je_vse_ok = set_canals(b"\x02", b"\x03", rychlost)
             je_vse_ok = set_canals(pin_reverse.duty_cycle, pin_forward.duty_cycle, rychlost)
             je_vse_ok = set_canals("P16", "P13", rychlost)
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

    init_motors()

    zastav()
    ultrazvuk = Ultrazvuk(DigitalInOut(board.P8), DigitalInOut(board.P12))

    reference = 0.2 # na jakou vzdalenost cheme zastavit [m]
    error = 0
    sum_error = 0
    P = -400
    I = -10
    max_PWM = 150 #teoreticky 255, ale ja se bojim :)
    min_PWM = 100 # idealne zjisteno kalibraci, nebo vypozorovano, kdy se robot odlepi
    mrtva_zona = 0.05 #napr 5cm - kdy regulace uz rekne "uz tu jsem" a prestane regulovat

    predchozi_akcni_zasah = 0 #potrebuji, abych osetrila, ze motory se nikdy nerozjedou skokove do protismeru

    while not button_b.was_pressed():
        vzdialenost = int(ultrazvuk.proved_mereni_blokujici(timeout=0.01)*100)
        print(vzdialenost)
        if vzdialenost < 0:
            display.show('Err', 10)
        else:
            display.show(f'{vzdialenost}', 10)
        
        if button_a.is_pressed():
            display.fill(0)
            sys.exit()

#        sleep(0.1)
        pass
    
    while not button_a.was_pressed():
        merena_vzdalenost = ultrazvuk.proved_mereni_blokujici(timeout=0.05)

        if merena_vzdalenost < 0:
            display.show('Err', 10)
            continue
        else:
            display.show(f'{int(merena_vzdalenost*100)}', 10)

            error = reference - merena_vzdalenost
            sum_error += error
            
            if sum_error < -2:
                sum_error = -1

            akcni_zasah = P * error + I * sum_error

            if fabs(akcni_zasah) > max_PWM:
                akcni_zasah = sign(akcni_zasah) * max_PWM
            if fabs(akcni_zasah) < min_PWM:
                if fabs(error) > mrtva_zona:
                    akcni_zasah = sign(akcni_zasah) * min_PWM
                else:
                    akcni_zasah = 0
            
#            print(merena_vzdalenost, error, akcni_zasah)

            # osetreni, ze nikdy motory neposleme do protismeru hned
            # normalne bych tohle v regulaci nemela,
            # zde to mame, protoze nase motory jsou dost blbe
            if sign(predchozi_akcni_zasah) != sign(akcni_zasah):
                zastav()

            if akcni_zasah > 0:
                
                jed("pravy", "dopredu", fabs(akcni_zasah) + 30)
                jed("levy", "dopredu", fabs(akcni_zasah))
            else:
                jed("pravy", "dozadu", fabs(akcni_zasah) + 30)
                jed("levy", "dozadu", fabs(akcni_zasah))
            
            predchozi_akcni_zasah = akcni_zasah

        sleep(0.05)
    
    display.fill(0)
    zastav()
