from picoed import i2c, display

def vypis_senzory_cary(levy, centralni, pravy):
#    print(levy, centralni, pravy)
    if levy:
        display.pixel(display.width-1,0, 255)
    else:
        display.pixel(display.width-1,0,0)

    if centralni:
        display.pixel(int(display.width/2),0, 255)
    else:
        display.pixel(int(display.width/2),0,0)
    
    if pravy:
        display.pixel(0,0, 255)
    else:
        display.pixel(0,0,0)

def byte_na_bity(buffer):
    data_int = int.from_bytes(buffer, "big")
    data_bit_string = bin(data_int)
    return data_bit_string

def vycti_senzory():
    while not i2c.try_lock():
        pass

    data_bit_string = ""
    # pokud se program dostane sem, tak se i2c podarilo zamknout
    try:
        buffer = bytearray(1)
        i2c.readfrom_into(0x38, buffer, start = 0, end = 1)
        data_bit_string = byte_na_bity(buffer)  
    finally:
        i2c.unlock()

    return data_bit_string

def vrat_levy(data_string):
    return bool(int(data_string[7]))

def vrat_centralni(data_string):
    return bool(int(data_string[6]))

def vrat_pravy(data_string):
    return bool(int(data_string[5]))