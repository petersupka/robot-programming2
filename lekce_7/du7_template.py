from picoed import i2c
from time import sleep

def init_motoru():
    i2c.write(0x70, bytes([0, 0x01]))
    i2c.write(0x70, bytes([8, 0xAA]))
    sleep(0.01)

def jed(dopredna, uhlova):
    # “dopredna” je float a obsahuje dopřednou rychlost robota
    #    pro tento úkol prozatím používejte hodnotu 135 nebo 0
    # “uhlova” je float a obsahuje rychlost otáčení robota
    #    pro tento úkol prozatím používejte hodnotu 1350 nebo 0
    # Použijte vzorečky kinematiky a spočítejte v_l a v_r
    # Podle znamínek v_l a v_r volejte příslušné příkazy na směr motorů
    # Metoda také zastaví pokud ji dám nulové rychlosti

    return 0

def jed_pwm(strana, smer, rychlost):
    if (rychlost >= 0 and rychlost <= 255):
        if (strana == "leva" and smer == "dopredu"):
            nastav_kanaly(4, 5, rychlost)
            return 0
        elif (strana == "leva" and smer == "dozadu"):
            nastav_kanaly(5, 4, rychlost)
            return 0
        elif (strana == "prava" and smer == "dopredu"):
            nastav_kanaly(2, 3, rychlost)
            return 0
        elif (strana == "prava" and smer == "dozadu"):
            nastav_kanaly(3, 2, rychlost) 
            return 0
        else:
            return -1
    else:
        return -2

def nastav_kanaly(kanal_off, kanal_on, rychlost):
    while not i2c.try_lock():
        pass
    try:
        i2c.write(0x70, bytes([kanal_off, 0]))
        i2c.write(0x70, bytes([kanal_on, rychlost]))
    finally:
        i2c.unlock()
    return 0

if __name__ == "__main__":
    # Write your code here :-)
    init_motoru()
    # volejte funkci jed, tak abyste ziskali:
    # Pohyb robota dopredu 1s
    # Zastaveni 1s - DULEZITE! Nikdy nemente smer jizdy bez zastaveni
    # Otáčení robota na místě doleva
    # zastaveni
