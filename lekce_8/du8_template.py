from picoed import i2c, button_a, button_b, display
from time import sleep
from random import choice

standard_rychlost = 120                 # standardna rychlost pohybu
pauza_otocka = 0.05                     # pauza pri otocke
pauza_pohyb = 0.3                       # pauza pri pohybe
pauza_motorov = 1                       # pauza motorov
centralny_senzor_predtym = [0, 0]       # vpravo/vlavo pre ulozenie stavu centralneho senzoru predtym
displej_svietivost = 10                 # svietivost displeja

def vypis_senzory_cary(levy, centralni, pravy):
    print(levy, centralni, pravy)
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

def stav_vycti_senzory():
    data_string = vycti_senzory()
    return data_string

def init_motoru():
    while not i2c.try_lock():
        pass
    try:
        i2c.writeto(0x70, b'\x00\x01')
        i2c.writeto(0x70, b'\xE8\xAA')
        sleep(0.1)
    finally:
        i2c.unlock()
    
def nastav_PWM_kanaly(kanal_on, kanal_off, rychlost):
    # je nesmirne dulezite vzdy mit zapnuty jen jeden kanal,
    # tedy tato funkce zarucuje, ze se druhy kanal vypne

    while not i2c.try_lock():
        pass
    try:
        i2c.writeto(0x70, kanal_off + bytes([0]))
        i2c.writeto(0x70, kanal_on + bytes([rychlost]))
    finally:
        i2c.unlock()
    
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
        return

    if strana == "levy":
        if smer == "dopredu":
            je_vse_ok = nastav_PWM_kanaly(b"\x05", b"\x04", rychlost)
        elif smer == "dozadu":
            je_vse_ok = nastav_PWM_kanaly(b"\x04", b"\x05", rychlost)
        else:
            je_vse_ok = -4
    elif strana == "pravy":
        if smer == "dopredu":
            je_vse_ok = nastav_PWM_kanaly(b"\x03", b"\x02", rychlost)
        elif smer == "dozadu":
            je_vse_ok = nastav_PWM_kanaly(b"\x02", b"\x03", rychlost)
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

def detekuj_krizovatku(data_string):
    # DU 8 
    # situace 1: vsechny tri senzory detekuji cernou
    # situace 2: jenom dva senzory detekuji cernou
    #return True/False

    # rychla konstrola, ci je robot na krizovatke -> 2+ senzorov detekuje ciernu ciaru
    print(data_string[5:8].count('1'))
    if data_string[5:8].count('1') >= 2:
        return True # nahradte tento return
    else:
        return False

def stav_reaguj_na_caru(data_string):
    if detekuj_krizovatku(data_string):
        return False

    if vrat_centralni(data_string):
        jed("pravy", "dopredu", standard_rychlost)
        jed("levy", "dopredu", standard_rychlost)
        
        return True

    if vrat_levy(data_string):
        jed("pravy", "dopredu", standard_rychlost)
        jed("levy", "dopredu", 0)
        
        return True
    
    if vrat_pravy(data_string):
        jed("pravy", "dopredu", 0)
        jed("levy", "dopredu", standard_rychlost)
 
        return True 
    
    return True

def otocka_vlavo():
    centralny_senzor_predtym[0] = 1
    while True:
        jed("levy", "dozadu", standard_rychlost)
        jed("pravy", "dopredu", standard_rychlost)

        # podmienka zabezpeci, ze sa robot otoci pred novym citanim senzorov 
        # o tolko, aby bol centralny senzor pozicne na bielej ploche
        # aby sa nestalo, ze pri miernom vyboceni a otacani ku ciernej ciare ju zachyti 
        # a vlastne sa vobec neotoci
        if centralny_senzor_predtym[0] == 1:
            centralny_senzor_predtym[0] = 0
            sleep(pauza_otocka*10)

        sleep(pauza_otocka)
        data_string = stav_vycti_senzory()
        if vrat_centralni(data_string):
            break
    zastav()
    sleep(pauza_motorov)    
    return True
    
def otocka_vpravo():
    centralny_senzor_predtym[1] = 1
    while True:
        jed("levy", "dopredu", standard_rychlost)
        jed("pravy", "dozadu", standard_rychlost)

        # podmienka zabezpeci, ze sa robot otoci pred novym citanim senzorov 
        # o tolko, aby bol centralny senzor pozicne na bielej ploche
        # aby sa nestalo, ze pri miernom vyboceni a otacani ku ciernej ciare ju zachyti 
        # a vlastne sa vobec neotoci
        if centralny_senzor_predtym[1] == 1:
            centralny_senzor_predtym[1] = 0
            sleep(pauza_otocka*10)

        sleep(pauza_otocka)
        data_string = stav_vycti_senzory()
        if vrat_centralni(data_string):
            break
    zastav()
    sleep(pauza_motorov)
    return True

def pohyb_mierne_vpred():
    # pohneme robotom dopredu pocas 'pauza_pohyb' sekund
    jed("levy", "dopredu", standard_rychlost)
    jed("pravy", "dopredu", standard_rychlost)
    sleep(pauza_pohyb)
    return True

def stav_akcia_na_krizovatke(data_string):
    if data_string[5:8] == "111":  # 'X' alebo 'T' krizovatka
        # situacia 1: vsetky senzory detekuju ciernu ciaru
        if vrat_centralni(vycti_senzory()):
            # vyberieme nahodne, ale moznost vyberu priamo je mozna len ak 
            # centralny senzor detekuje ciernu ciaru aj po pohybe dopredu (popojed),
            # ktory prebehne tesne pred touto funkciou v hlavnej vetve programu
            # detto pre 110 (chybajuca ciara vlavo) a 011 (chybajuca ciara vpravo)
            strana = choice(["vpravo", "priamo", "vlavo"])
        else:
            strana = choice(["vpravo", "vlavo"])

        if strana == "vpravo":
            display.show("<"+str(pocet_krizovatiek)+" ", displej_svietivost)
#            display.show("<B ")
            otocka_vpravo()
        elif strana == "vlavo":
            display.show(" "+str(pocet_krizovatiek)+">", displej_svietivost)
#            display.show(" B>")
            otocka_vlavo()
        else:   # priamo
            display.show("v"+str(pocet_krizovatiek)+"v", displej_svietivost)
#            display.show(" B ")
            pohyb_mierne_vpred()

        sleep(pauza_otocka)
        return True
    
    if data_string[5:8] == "110":  # 'T' krizovatka alebo roh smerujuci doprava
        # situacia 2: len dva senzory detekuju ciernu ciaru
        if vrat_centralni(vycti_senzory()):
            # ak je aj po pohybe priamo (popojed) centralny senzor na ciare, 
            # tak sa pohneme priamo/vpravo
            # inak sa pohneme vpravo
            strana = choice(["priamo", "vpravo"])
        else:
            strana = choice(["vpravo"])

        if strana == "vpravo":
            display.show("<"+str(pocet_krizovatiek)+" ", displej_svietivost)
#            display.show("<B ")
            otocka_vpravo()
        else:   # priamo
            display.show("v"+str(pocet_krizovatiek)+"v", displej_svietivost)
#            display.show(" B ")
            pohyb_mierne_vpred()
        return True
    
    if data_string[5:8] == "011":  # 'T' krizovatka alebo roh smerujuci dolava
        # situacia 3: len dva senzory detekuju ciernu ciaru
        if vrat_centralni(vycti_senzory()):
            # ak je aj po pohybe priamo (popojed) centralny senzor na ciare, 
            # tak sa pohneme vlavo/priamo
            # inak sa pohneme vlavo
            strana = choice(["vlavo", "priamo"])
        else:
            strana = choice(["vlavo"])

        if strana == "vlavo":
            display.show(" "+str(pocet_krizovatiek)+">", displej_svietivost)
            otocka_vlavo()
        else:   # priamo
            display.show("v"+str(pocet_krizovatiek)+"v", displej_svietivost)
#            display.show(" B ")
            pohyb_mierne_vpred()
        return True
    
    return False

if __name__ == "__main__":

    init_motoru()
    zastav()
    sleep(pauza_motorov)

    aktualni_stav = "start"

    st_reaguj_na_caru = "reaguj na caru"
    st_vycti_senzory = "vycti senzory"
    st_stop = "st_stop"
    st_popojed = "st_popojed"

    display.show("A", displej_svietivost)

    while not button_a.was_pressed():
        print(aktualni_stav)
        data = stav_vycti_senzory()
        vypis_senzory_cary(vrat_levy(data), vrat_centralni(data), vrat_pravy(data))
        sleep(0.1)
        pass

    aktualni_stav = st_vycti_senzory

    pocet_krizovatiek = 10    
    display.show(pocet_krizovatiek, displej_svietivost)

    while not button_b.was_pressed() and pocet_krizovatiek > 0:
        if aktualni_stav == st_vycti_senzory:
            data = stav_vycti_senzory()
            vypis_senzory_cary(vrat_levy(data), vrat_centralni(data), vrat_pravy(data))
            aktualni_stav = st_reaguj_na_caru
            print(aktualni_stav)
        
        if aktualni_stav == st_reaguj_na_caru:
            pokracuj_jizda_po_care = stav_reaguj_na_caru(data)
            if pokracuj_jizda_po_care:
                aktualni_stav = st_vycti_senzory
            else:
                aktualni_stav = st_stop
            print(aktualni_stav)
        
        if aktualni_stav == st_stop:
            zastav()
            sleep(pauza_motorov)
            aktualni_stav = st_popojed
            print(aktualni_stav)
        
        if aktualni_stav == st_popojed:
            # DU 8  - naprogramujte zde
            print(aktualni_stav)
            if detekuj_krizovatku(data):  # T / X Crossroad / Corner (left/right)
                pocet_krizovatiek -= 1
                pohyb_mierne_vpred()    # popojed
                zastav()
                sleep(pauza_motorov)
                stav_akcia_na_krizovatke(data)
                zastav()
                display.show(" "+str(pocet_krizovatiek)+" ", displej_svietivost)
                sleep(pauza_motorov)
                aktualni_stav = st_vycti_senzory
        sleep(0.005)
    
    zastav()
    display.show('END', displej_svietivost)
    sleep(pauza_motorov)
    display.fill(0)

    

   

