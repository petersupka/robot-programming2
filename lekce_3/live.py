from microbit import i2c, sleep

def vycti_adresy():
    adresy = i2c.scan()

    for adresa in adresy:
        print(hex(adresa))

    print("konec")
    print(len(adresy))

def init_motoru():
    i2c.write(0x70, b'\x00\x01')
    i2c.write(0x70, b'\xE8\xAA')
    sleep(100)

def jed(rychlost):
    i2c.write(0x70, b'\x03' + bytes([rychlost]))

if __name__ == "__main__":
    # Write your code here :-)
    i2c.init()
    init_motoru()
    jed(135) # 0 - 255
    sleep(1000)
    jed(0)
