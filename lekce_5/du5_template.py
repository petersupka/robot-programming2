from microbit import sleep, pin14, pin15

def pocet_tiku_levy():
    surova_data_leva = pin14.read_digital()
    #zde napiste vas kod
    #scitejte tiky pro levy enkoder od zacatku behu progamu
    return #vratte soucet

def pocet_tiku_pravy():
    surova_data_prava = pin15.read_digital()
    #zde napiste vas kod
    #scitejte tiky pro pravy enkoder od zacatku behu progamu
    return #vratte soucet

def vypocti_rychlost(pocet_tiku):
    # zde patri ukol DU5
    
    return #vratte rychlost v radianech za sekundu
    
if __name__ == "__main__":

    aktualni_rychlost = 0
    
    while True:
        print(pocet_tiku_levy(), pocet_tiku_pravy())
        #volejte zde funkci aktualni_rychlost = vypocti_rychlost s vhodnou peridou - viz slidy min 166ms;
        #budete potrebovat vyuzit praci s casem pres tick_us, ticks_diff (mozna prikazy jsou jinak na pico:edu, pokud nenajdete, zeptejte se na discordu)
        #staci udelat pro jedno kolo
        
        print(aktualni_rychlost)
        sleep(5)
