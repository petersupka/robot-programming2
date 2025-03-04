from microbit import i2c

if __name__ == "__main__":
    # Write your code here :-)
    i2c.init()

    adresy = i2c.scan()

    for adresa in adresy:
        print(hex(adresa))
