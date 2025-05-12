from picoed import i2c, button_a, button_b, display
from time import sleep, monotonic_ns
from cas import Cas

dopredna_pwm = 100
uhlova_max_pwm = 80
uhlova_min_pwm = 0

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
    data = vycti_senzory()
    kolik_senzoru_meri_caru = vrat_levy(data) + vrat_centralni(data) + vrat_pravy(data)
    return kolik_senzoru_meri_caru >=2

def stav_reaguj_na_caru(data_string):
    if detekuj_krizovatku(data_string):
        return False
    
    if vrat_levy(data_string):
        jed("pravy", "dopredu", uhlova_max_pwm)
        jed("levy", "dopredu", uhlova_min_pwm)
        
        return True
    
    if vrat_pravy(data_string):
        jed("pravy", "dopredu", uhlova_min_pwm)
        jed("levy", "dopredu", uhlova_max_pwm)
 
        return True 
    
    if vrat_centralni(data_string):
        jed("pravy", "dopredu", dopredna_pwm)
        jed("levy", "dopredu", dopredna_pwm)
 
        return True 
    
    return True


if __name__ == "__main__":

    init_motoru()
    zastav()

    aktualni_stav = "start"

    st_reaguj_na_caru = "reaguj na caru"
    st_vycti_senzory = "vycti senzory"
    st_stop = "st_stop"
    st_cekej = "st_cekej"
    st_popojed = "st_popojed"
    st_jedu = "st_jedu"
    st_pootoc = "st_pootoc"
    st_tocim = "st_tocim"
    st_zatoc_na_caru = "st_zatoc_na_caru"
    st_konec = "st_konec"

    cas_zastaveni = 0.5 #sekundy
    cas_popojeti = 0.3 #sekundy
    cas_pootoceni = 0.5 #sekundy
    prikazy = ["vlevo", "vpravo", "vpravo", "vpravo", "rovne"]
    aktualni_prikaz = 0

    while not button_a.was_pressed():
        print(aktualni_stav)
        data = stav_vycti_senzory()
        vypis_senzory_cary(vrat_levy(data), vrat_centralni(data), vrat_pravy(data))
        sleep(0.1)
        pass

    aktualni_stav = st_vycti_senzory

    while not button_b.was_pressed():
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
            cas_zacatku_zastaveni = monotonic_ns()
            aktualni_stav = st_cekej
            print(aktualni_stav)
        
        if aktualni_stav == st_cekej:
            if Cas.ubehl_cas(monotonic_ns(), cas_zacatku_zastaveni, cas_zastaveni):
                zastav()
                aktualni_stav = st_popojed
                print(aktualni_stav)
        
        if aktualni_stav == st_popojed:
            # DU 8  - naprogramujte zde
            jed("pravy", "dopredu", dopredna_pwm)
            jed("levy", "dopredu", dopredna_pwm)
            cas_zacatku_jizdy = monotonic_ns()
            aktualni_stav = st_jedu
            print(aktualni_stav)
        
        if aktualni_stav == st_jedu:
            if Cas.ubehl_cas(monotonic_ns(), cas_zacatku_jizdy, cas_popojeti):
                zastav()
                aktualni_stav = st_pootoc
                print(aktualni_stav)
        
        if aktualni_stav == st_pootoc:
            if len(prikazy) == aktualni_prikaz:
                #dosly prikazy
                aktualni_stav = st_konec
                print(aktualni_stav)
                continue
            if prikazy[aktualni_prikaz] == "rovne":
                aktualni_stav = st_vycti_senzory
                aktualni_prikaz += 1
                print(aktualni_stav)
            elif prikazy[aktualni_prikaz] == "vlevo":
                jed("pravy", "dopredu", uhlova_max_pwm)
                jed("levy", "dozadu", uhlova_max_pwm)
                cas_zacatku_jizdy = monotonic_ns()
                aktualni_stav = st_tocim
                print(aktualni_stav)
            elif prikazy[aktualni_prikaz] == "vpravo":
                jed("pravy", "dozadu", uhlova_max_pwm)
                jed("levy", "dopredu", uhlova_max_pwm)
                cas_zacatku_jizdy = monotonic_ns()
                aktualni_stav = st_tocim
                print(aktualni_stav)
            else:
                #neplatny prikaz
                aktualni_stav = st_konec
                print(aktualni_stav)
                continue
        
        if aktualni_stav == st_tocim:
            if Cas.ubehl_cas(monotonic_ns(), cas_zacatku_jizdy, cas_pootoceni):
                aktualni_stav = st_zatoc_na_caru
        
        if aktualni_stav == st_zatoc_na_caru:
            data = vycti_senzory()
            if prikazy[aktualni_prikaz] == "vlevo":
                if vrat_levy(data):
                    aktualni_prikaz += 1
                    zastav()
                    aktualni_stav = st_vycti_senzory
            elif prikazy[aktualni_prikaz] == "vpravo":
                if vrat_pravy(data):
                    aktualni_prikaz += 1
                    zastav()
                    aktualni_stav = st_vycti_senzory
        
        if aktualni_stav == st_konec:
            zastav()
            print("Konec stavoveho automatu")
            break
        sleep(0.1)
    
    zastav()

    

   


