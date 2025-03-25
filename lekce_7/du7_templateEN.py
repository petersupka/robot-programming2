from picoed import i2c
from time import sleep

def init_motor():
    i2c.write(0x70, bytes([0, 0x01]))
    i2c.write(0x70, bytes([8, 0xAA]))
    sleep(0.01)

def go(forward, angular):
    # “forward” je float a obsahuje dopřednou rychlost robota
    #    pro tento úkol prozatím používejte hodnotu 135 nebo 0
    # “angular” je float a obsahuje rychlost otáčení robota
    #    pro tento úkol prozatím používejte hodnotu 1350 nebo 0
    # Použijte vzorečky kinematiky a spočítejte v_l a v_r
    # Podle znamínek v_l a v_r volejte příslušné příkazy na směr motorů
    # Metoda také zastaví pokud ji dám nulové rychlosti

    return 0

def go_pwm(side, direction, speed):
    # side může být jen “left” a “right”
    # “direction” je typu string a může mít hodnoty “forward”, "backward"
    if (speed >= 0 and speed <= 255):
        if (side == "left" and direction == "forward"):
            set_canals(4, 5, speed)
            return 0
        elif (side == "left" and direction == "backward"):
            set_canals(5, 4, speed)
            return 0
        elif (side == "right" and direction == "forward"):
            set_canals(2, 3, speed)
            return 0
        elif (side == "right" and direction == "backward"):
            set_canals(3, 2, speed) 
            return 0
        else:
            return -1
    else:
        return -2

def set_canals(canal_off, canal_on, pwm):
    while not i2c.try_lock():
        pass
    try:
        i2c.write(0x70, bytes([canal_off, 0]))
        i2c.write(0x70, bytes([canal_on, pwm]))
    finally:
        i2c.unlock()
    return 0

if __name__ == "__main__":
    # Write your code here :-)
    init_motor()
    # volejte funkci go, tak abyste ziskali:
    # Pohyb robota dopredu 1s
    # Zastaveni 1s - DULEZITE! Nikdy nemente smer jizdy bez zastaveni
    # Otáčení robota na místě doleva
    # zastaveni
