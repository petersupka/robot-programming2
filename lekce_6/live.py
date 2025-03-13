from picoed import i2c

def byte_na_bity(buffer):
    data_int = int.from_bytes(buffer, "big")
    data_bit_string = bin(data_int)
    return data_bit_string

if __name__ == "__main__":

    while not i2c.try_lock():
        pass

    # pokud se program dostane sem, tak se i2c podarilo zamknout
    try:
        buffer = bytearray(1)
        i2c.readfrom_into(0x38, buffer, start = 0, end = 1)
        print(buffer)
        data_bit_string = byte_na_bity(buffer)
        print(data_bit_string)
        for i in range(0, len(data_bit_string)):
            print(i, data_bit_string[i])
            #5 pravy
            #6 centralni
            #7 levy
    finally:
        i2c.unlock()

