from picoed import i2c
import time
import pwmio
import board

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
    # je nesmirne dulezite vzdy mit zapnuty jen jeden kanal,
    # tedy tato funkce zarucuje, ze se druhy kanal vypne



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
