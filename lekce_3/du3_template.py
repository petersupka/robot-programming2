from microbit import i2c, sleep

def init_motoru():
    i2c.write(0x70, b'\x00\x01')
    i2c.write(0x70, b'\xE8\xAA')
    sleep(100)

def jed(strana, smer, rychlost):
    # Strana může být jen “leva” a “prava”
    # “smer” je typu string a může mít hodnoty “dopredu”, "dozadu"
    # Rychlost je celočíselné číslo od 0-255
    # vyuzijte prikladu z hodiny, ktery poslal povel x03 - prave kolo pro jizdu rovne
    # ostatni povely:
    # Pravý motor:
    # 0x02 - příkaz pro pohyb vzad
    # 0x03 - příkaz pohyb vpřed
    # Levý motor:
    # 0x04 - příkaz pro pohyb vzad
    # 0x05 - příkaz pro pohyb vpřed

    i2c.write(0x70, b'\x03' + bytes([rychlost]))

if __name__ == "__main__":
    # Write your code here :-)
    i2c.init()
    init_motoru()
    # volejte funkci jed, tak abyste ziskali:
    # Pohyb robota dopredu 1s
    # Zastaveni 1s - DULEZITE! Nikdy nemente smer jizdy bez zastaveni
    # Pohyb vzad 1s,
    # zastaveni
