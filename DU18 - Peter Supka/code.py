from picoed import button_a, button_b, i2c, display
from time import sleep
from digitalio import DigitalInOut
from ultrazvuk import Ultrazvuk
from math import fabs, radians, pi
import board, pwmio, time, sys

pin_forward = pwmio.PWMOut(board.P13, duty_cycle=0) # Forward direction, P13 from servo driver #2
pin_reverse = pwmio.PWMOut(board.P16, duty_cycle=0) # Reverse direction, P16 from speaker
__robot_radius = 0.075 # distance between wheel center and robot center [m]

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


def go(forward, angular):
    v_l = int(forward - __robot_radius * angular)
    v_r = int(forward + __robot_radius * angular)
    if (v_l >= 0):
        jed("levy", "dopredu", v_l)
    else:
        jed("levy", "dozadu", abs(v_l))
    if (v_r >= 0):
        jed("pravy", "dopredu", v_r)
    else:
        jed("pravy", "dozadu", abs(v_r))
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

    pwm_servo = pwmio.PWMOut(board.P1, duty_cycle=0, frequency=100)  # Initialize PWM on P1 with a frequency of 100 Hz

    reference = 0.1 # na jakou vzdalenost chceme zastavit [m]
    error = 0
    sum_error = 0
    P = -400
    I = -10
    max_PWM = 130 #teoreticky 255, ale ja se bojim :)
    min_PWM = 100 # idealne zjisteno kalibraci, nebo vypozorovano, kdy se robot odlepi
    mrtva_zona = 0.05 #napr 5cm - kdy regulace uz rekne "uz tu jsem" a prestane regulovat

    predchozi_akcni_zasah = 0 #potrebuji, abych osetrila, ze motory se nikdy nerozjedou skokove do protismeru

    while not button_b.was_pressed():
        vzdialenost_najblizsieho_objektu = 999 # vzdialenost, na ktoru chceme reagovat, ak je mensia ako tato hodnota, tak zastavime
        uhol_k_najblizsiemu_objektu = 0 # uhol, na ktorom je najblizsi objekt
        for cycle in range(3000, 16000, 100):
#            print(cycle)
            if (cycle == 3000) or (cycle == 16000) or ((cycle-3000) % 1300 == 0):   # berieme krajne hodnoty a 9 uhlov medzi nimi  (16tis - 3tis) / 100 = 130 => o 1300 jednotiek sa servo posunie o 1 uhol kedy meriame ultrazvukom
                vzdialenost = int(ultrazvuk.proved_mereni_blokujici(timeout=0.003)*100) # meranie v cm
#                print(f'uhol: {int((cycle-3000)/72)} | cycle: {cycle}, vzdialenost: {vzdialenost}')  # int((cycle-3000)/72) je uhol v stupnoch, pretoze 16tis - 3tis = 13000, 13000 / 180 = 72.2222 => 1 stupen = PWM hodnota 72.2222
                if vzdialenost > 0:
                    if vzdialenost < vzdialenost_najblizsieho_objektu:
                        vzdialenost_najblizsieho_objektu = vzdialenost
                        uhol_k_najblizsiemu_objektu = int((cycle-3000)/72)  # ulozime si uhol, na ktorom je najblizsi objekt
            pwm_servo.duty_cycle = cycle  
            sleep(0.015)
        print('')
        print(f'Najblizsia vzdialenost: {vzdialenost_najblizsieho_objektu} cm')
        print(f'Uhol objektu: {uhol_k_najblizsiemu_objektu}°')
        print('')
        if vzdialenost_najblizsieho_objektu < 999:
            display.show(f'{vzdialenost_najblizsieho_objektu}', 10)
            sleep(0.1)
            display.show(f'{uhol_k_najblizsiemu_objektu}', 10)
            sleep(0.2)
        else: 
            display.show('Out', 10)
        
        if vzdialenost_najblizsieho_objektu > 50:  # ak je vzdialenost vacsia nez 50 cm, otocime sa o 180st a hladame v okoli robota objekt v okruhu .5m
            go(0, 0)  # zastavime motory, aby sa robot nepohol
            sleep(0.01)  # pockame, kym sa robot zastavi
            go(0, pi*600)  # otocime sa o 180 stupnov
            sleep(0.7)  # pockame, kym sa robot otoci na miesto

        rel_phi = radians(uhol_k_najblizsiemu_objektu) # relativny uhol k najblizsiemu objektu, pretoze servo je v 90 stupnoch, ked je v strede
        rel_phi = rel_phi - pi/2  # odratame 90 stupnov, pretoze servo je v 90 stupnoch, ked je v strede
#        print(f'Relativny uhol k najblizsiemu objektu: {rel_phi} radianov')
        # nastavime servo na relativny uhol k najblizsiemu objektu
#        pwm_servo.duty_cycle = int(3000 + uhol_k_najblizsiemu_objektu * 72.2222)  # 3000 + uhol_k_najblizsiemu_objektu * 72.2222 je PWM hodnota pre servo na danom uhle

        omega = pi  # uhlova rychlost, otacanie sa na mieste
        if uhol_k_najblizsiemu_objektu != 90:
            if uhol_k_najblizsiemu_objektu < 90:
                omega = -omega  # ak je uhol mensi ako 90 stupnov, otacame sa na mieste v smere natocenia kolmo k objektu (90st)
            go(0, 0)  # zastavime motory, aby sa robot nepohol
            sleep(0.01)  # pockame, kym sa robot zastavi
            go(0, omega*600)  # otocime sa na mieste na dany smer
    #        print(fabs(rel_phi/omega))  # vypocitame, ako dlho sa budeme tocit
    #        sleep(0.5)  # pockame, kym sa robot otoci na miesto
            sleep(fabs(rel_phi/omega))  # pockame, kym sa robot otoci na miesto
            go(0, 0)  # zastavime motory, aby sa robot nepohol
            sleep(0.01)  # pockame, kym sa robot zastavi


        vzdialenost_najblizsieho_objektu = 999 # resetujeme pre dalsie meranie
        uhol_k_najblizsiemu_objektu = 0 # uhol, na ktorom je najblizsi objekt
        for cycle in range(16000, 3000, -100):  # posuvame servo od 16tis do 3tis (v cykle je 2900, pretoze tuto poslednu hodnotu uz neberie do uvahy pri posune o -100 jednotiek)
            if (cycle == 3000) or (cycle == 16000) or ((cycle-3000) % 1300 == 0):   # berieme krajne hodnoty a 9 uhlov medzi nimi  (16tis - 3tis) / 100 = 130 => o 1300 jednotiek sa servo posunie o 1 uhol kedy meriame ultrazvukom
                vzdialenost = int(ultrazvuk.proved_mereni_blokujici(timeout=0.003)*100) # meranie v cm
#                print(f'uhol: {int((cycle-3000)/72)} | cycle: {cycle}, vzdialenost: {vzdialenost}')  # int((cycle-3000)/72) je uhol v stupnoch, pretoze 16tis - 3tis = 13000, 13000 / 180 = 72.2222 => 1 stupen = PWM hodnota 72.2222
                if vzdialenost > 0:
                    if vzdialenost < vzdialenost_najblizsieho_objektu:
                        vzdialenost_najblizsieho_objektu = vzdialenost
                        uhol_k_najblizsiemu_objektu = int((cycle-3000)/72)  # ulozime si uhol, na ktorom je najblizsi objekt
            pwm_servo.duty_cycle = cycle
            sleep(0.015)
        print('')
        print(f'Najblizsia vzdialenost: {vzdialenost_najblizsieho_objektu} cm')
        print(f'Uhol objektu: {uhol_k_najblizsiemu_objektu}°')
        print('')

        if vzdialenost_najblizsieho_objektu < 999:
            display.show(f'{vzdialenost_najblizsieho_objektu}', 10)
            sleep(0.1)
            display.show(f'{uhol_k_najblizsiemu_objektu}', 10)
            sleep(0.2)
        else:
            display.show('Out', 10)
        
        if vzdialenost_najblizsieho_objektu > 50:  # ak je vzdialenost vacsia nez 50 cm, otocime sa o 180st a hladame v okoli robota objekt v okruhu .5m
            go(0, 0)  # zastavime motory, aby sa robot nepohol
            sleep(0.01)  # pockame, kym sa robot zastavi
            go(0, -pi*600)  # otocime sa o 180 stupnov
            sleep(0.7)  # pockame, kym sa robot otoci na miesto
            go(0, 0)  # zastavime motory, aby sa robot nepohol
            sleep(0.01)  # pockame, kym sa robot zastavi
#        sys.exit()

        if button_a.is_pressed():
            display.fill(0)
            sys.exit()

#        sleep(0.1)
    
        rel_phi = radians(uhol_k_najblizsiemu_objektu) # relativny uhol k najblizsiemu objektu, pretoze servo je v 90 stupnoch, ked je v strede
        rel_phi = rel_phi - pi/2  # odratame 90 stupnov, pretoze servo je v 90 stupnoch, ked je v strede
#        print(f'Relativny uhol k najblizsiemu objektu: {rel_phi} radianov')
        # nastavime servo na relativny uhol k najblizsiemu objektu
#        pwm_servo.duty_cycle = int(3000 + uhol_k_najblizsiemu_objektu * 72.2222)  # 3000 + uhol_k_najblizsiemu_objektu * 72.2222 je PWM hodnota pre servo na danom uhle

        omega = pi  # otacanie sa na mieste
        if uhol_k_najblizsiemu_objektu != 90:
            if uhol_k_najblizsiemu_objektu < 90:
                omega = -omega  # ak je uhol mensi ako 90 stupnov, otacame sa na mieste v smere natocenia kolmo k objektu (90st)
            go(0, 0)  # zastavime motory, aby sa robot nepohol
            sleep(0.01)  # pockame, kym sa robot zastavi
            go(0, omega*600)  # otocime sa na mieste na dany smer
    #        print(fabs(rel_phi/omega))  # vypocitame, ako dlho sa budeme tocit
    #        sleep(0.5)  # pockame, kym sa robot otoci na miesto
            sleep(fabs(rel_phi/omega))  # pockame, kym sa robot otoci na miesto
            go(0, 0)  # zastavime motory, aby sa robot nepohol
            sleep(0.01)  # pockame, kym sa robot zastavi

        pwm_servo.duty_cycle = 9500  # nastavime servo na 'priamy pohlad'
        sleep(0.5)  # pockame, kym sa servo nastavi na priamy smer

#    while not button_a.was_pressed():
        merena_vzdalenost = ultrazvuk.proved_mereni_blokujici(timeout=0.003)

        if merena_vzdalenost < 0:
            display.show('Err', 10)
            continue
        else:
            display.show(f'{int(merena_vzdalenost*100)}', 5)

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
            sleep(0.5)
            zastav()  # zastavime motory, aby sa robot nepohol

        sleep(0.05)
    
    display.fill(0)
    zastav()