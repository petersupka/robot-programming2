from picoed import i2c, button_a, button_b, display
from time import sleep
import sys  # kvoli systemovej funkcii sys.exit() kvoli ukonceniu programu mimo cyklu

# list stavov senzorov po zbehnuti 'stav_reaguj_na_caru' 
senzory_posledne_aktivne = [0, 1, 0]

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

def display_off():
    display.fill(0)

def stav_reaguj_na_caru(data_string):

    if vrat_centralni(data_string):
        # doplnene - robot ide priamo a detekuje len centralny senzor
        jed("levy", "dopredu", 80)
        jed("pravy", "dopredu", 80)
        senzory_posledne_aktivne[1] = 1 # stav centralneho senzoru odlozime
        # zvysne 2 senzory v liste vynulujeme
        senzory_posledne_aktivne[0] = senzory_posledne_aktivne[2] = 0
        return True

    if vrat_levy(data_string):
        # DU naprogramujte zatoceni vlevo
        # a vhodne vyberte rychlosti
        jed("levy", "dopredu", 40)
        jed("pravy", "dopredu", 110)
        senzory_posledne_aktivne[0] = 1 # stav laveho senzoru odlozime
        # zvysne 2 senzory v liste vynulujeme
        senzory_posledne_aktivne[1] = senzory_posledne_aktivne[2] = 0
        return True
    
    if vrat_pravy(data_string):
        # DU naprogramujte zatoceni vpravo
        # a vhodne vyberte rychlosti
        jed("levy", "dopredu", 110)
        jed("pravy", "dopredu", 40)
        senzory_posledne_aktivne[2] = 1 # stav praveho senzoru odlozime
        # zvysne 2 senzory v liste vynulujeme
        senzory_posledne_aktivne[1] = senzory_posledne_aktivne[0] = 0
        return True

    # vsetky senzory na bielej ploche (mimo ciernej ciary)
    if not (vrat_levy(data_string) or vrat_centralni(data_string) or vrat_pravy(data_string)):
        # ak su vsetky senzory=false (cize na bielej ploche)
        # zaroven centralny senzor predtym nebol na ciare a ma ulozeny stav=false (cize 0)
        if not (senzory_posledne_aktivne[1]):
            # ak v stave vyssie bol predtym lavy senzor na ciare, 
            # posun robota o kusok blizsie k ocakavanej pozicii ciernej ciary (ak z nej zbehol mimo)
            if senzory_posledne_aktivne[0]:
                jed("levy", "dopredu", 20)
                jed("pravy", "dopredu", 100)
                sleep(0.5)
                # zaroven zaznam o predchadzajucom stave (True) pre lavy senzor nastav na 0
                senzory_posledne_aktivne[0] = 0
                return True
            
            # ak v stave centralny_senzor_predtym=false bol predtym pravy senzor na ciare, 
            # posun robota o kusok blizsie k ocakavanej pozicii ciernej ciary (ak z nej zbehol mimo)
            if senzory_posledne_aktivne[2]:
                jed("levy", "dopredu", 100)
                jed("pravy", "dopredu", 2 0)
                sleep(0.5)
                # zaroven zaznam o predchadzajucom stave (True) pre pravy senzor nastav na 0
                senzory_posledne_aktivne[2] = 0
                return True
            else: # k setreniu predchadzajuceho stavu
                zastav() # senzory su teraz na bielej ploche a predtym uz boli na bielej ploche
                return False # chybovy stav 'Err' na displeji picoedu (v hlavnej vetve sa program ukonci)
        else:   # k aktualnemu vycitanemu stave senzorov, ked centralny bol predtym = True
            return True
    # nasledujuci navrat True je dolezity kvoli osetreniu ostatnych stavov, 
    # aby nevracalo hodnotu 'None', ktora je potom nespravne interpretovana dalej
    return True  
                

if __name__ == "__main__":

    init_motoru()
    zastav()

    display.show('A B')  # zobrazenie 'menu'

    aktualni_stav = "start"

    st_reaguj_na_caru = "reaguj na caru"
    st_vycti_senzory = "vycti senzory"

    # button_b umoznuje program ukoncit bez dalsieho kodu pre spustanie motorov
    while not button_a.was_pressed() and not button_b.was_pressed():
        print(aktualni_stav)
        data = stav_vycti_senzory()
        vypis_senzory_cary(vrat_levy(data), vrat_centralni(data), vrat_pravy(data))
        sleep(0.1)
        pass

    # predbezne ukoncenie programu hned na zaciatku bez spustenia slucky pre hlavny pohyb
    if button_b.is_pressed():
        zastav()
        display.show('END')
        sleep(2)
        display_off()
        print("EXIT B")
        sys.exit()

    aktualni_stav = st_vycti_senzory

    display_off()
    while not button_b.was_pressed():
        if aktualni_stav == st_vycti_senzory:
            data = stav_vycti_senzory()
            vypis_senzory_cary(vrat_levy(data), vrat_centralni(data), vrat_pravy(data))
            aktualni_stav = st_reaguj_na_caru
            print(aktualni_stav)
        
        if aktualni_stav == st_reaguj_na_caru:
            povedlo_se = stav_reaguj_na_caru(data)

            # ak nastala chyba, robot sa zastavi a vygeneruje chybove hlasenie, program sa vypne
            if not povedlo_se:
                zastav()
                display.show('Err')
                sleep(1)
                display_off()
                print("Errored EXIT")
                sys.exit()

            aktualni_stav = st_vycti_senzory
            print(aktualni_stav)
        
        sleep(0.005)
    
    zastav()
    display.scroll('Thx for watching :)', 10)
    sleep(1)
    display_off()