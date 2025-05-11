import board
import sys
from picoed import button_a, button_b, display
from time import sleep
from system_jc import PowerSupply, PinADC
from robot_jc import Robot
from sensors_line_jc import vycti_senzory, vrat_levy, vrat_centralni, vrat_pravy, vypis_senzory_cary
from lights_jc import LightsColorsEnum, LightsTypesEnum, Multiple_LEDs_on, LEDs_blink, All_LEDs_off#, Light
from ultrazvuk_jc import Ultrazvuk
from digitalio import DigitalInOut

standard_rychlost = 120                 # standardna rychlost pohybu
trvanie_pohybu = 0.3                    # trvanie priameho pohybu
pauza_robota = 0.5                      # pauza motorov
displej_svietivost = 10                 # svietivost displeja

left_a = 15.04504178
left_b = 83.55171376
right_a = 21.81528662
right_b = 58.75

'''
MAPA: (dvojita ciara je obluk)
Vychodzia pozicia a smer pohybu robota:
    ╔─┬─┬─┐
    ╟─┼─┼─┤
--> ╚─┴─┴─┘
'''
prikazy_pohybu = (   # vychadzame zo strany obluka dovnutra mapy po dlhsej trase
    "rovne",    # 2,1
    "vlevo",    # 2,2
    "vpravo", 
    "vpravo",   # 2,3
    "vpravo",   # roh
    "rovne",    # 1,1
    "vpravo",   # 1,2
    "vlevo",    # 1,3
    "vlevo",
    "vlevo"    # STOP - navrat do vychodiskovej polohy
    )

def stav_vycti_senzory() -> str:
    data_string = vycti_senzory()
    return data_string


def stav_reaguj_na_caru(data_string) -> bool:
    if joy_car.detekuj_krizovatku(data_string):
        return False
    
    if vrat_levy(data_string):
        joy_car.jed("pravy", "dopredu", standard_rychlost)
        joy_car.jed("levy", "dopredu", int(standard_rychlost/4))
        return True
    
    if vrat_pravy(data_string):
        joy_car.jed("pravy", "dopredu", int(standard_rychlost/4))
        joy_car.jed("levy", "dopredu", standard_rychlost)
        return True 

    if vrat_centralni(data_string):
        joy_car.jed("pravy", "dopredu", standard_rychlost)
        joy_car.jed("levy", "dopredu", standard_rychlost)
#        joy_car.pohyb_mierne_vpred()
        return True

###    if not(vrat_centralni(data_string)) and not(vrat_levy(data_string)) and not(vrat_pravy(data_string)):
###        display.show("E-4", displej_svietivost) # Error status = -4 (no line detected, robot lost)
###        return False

    return True


def stav_akcia_na_krizovatke(data_string):

    if data_string[5:8].count('1') >= 2:    # krizovatka detekovana
        strana = prikazy_pohybu[9-pocet_krizovatiek] # poradie v liste chceme zachovat od 0 do 9 (krizovatky nam ale odpocitava od 9 do 0)
       
        if strana == "vpravo":
            display.show("<"+str(pocet_krizovatiek)+" ", displej_svietivost)
            joy_car.otocka_vpravo()

        elif strana == "vlevo":
            display.show(" "+str(pocet_krizovatiek)+">", displej_svietivost)
            joy_car.otocka_vlavo()

        elif strana == "rovne":   # priamo
            display.show("v"+str(pocet_krizovatiek)+"v", displej_svietivost)
            joy_car.pohyb_mierne_vpred()
        
        else:
            display.show("E-2", displej_svietivost) # Error status = -2 (Command ERROR)

        return True
    return False

     
if __name__ == "__main__":

    joy_car = Robot()
    joy_car.zastav()

    pin2 = PinADC(board.P2)
    voltage = PowerSupply.getPowerSupplyVoltage(pin2)
    napatie = f'{voltage:.1f}'
    display.show(napatie, displej_svietivost)
    sleep(0.5)
    if voltage < 5:
        joy_car.zastav()
        display.show("E-1", displej_svietivost)   # Error status = -1 (Init error)
        sleep(0.2)
        display.fill(0)
        sys.exit()
    else:
#        display.show("BOK", displej_svietivost)
        sleep(0.2)
        display.fill(0)

    ultrazvuk = Ultrazvuk(DigitalInOut(board.P8), DigitalInOut(board.P12))

    #--- kalibracia---  # spustena len na zaciatku pre ziskanie dat
#    joy_car.calibrate(0, 230, 1, pin2)
#    joy_car.zastav()
#    All_LEDs_off()
#    sys.exit()
    #--- koniec kalibracie ---

    aktualni_stav = "start"

#    Multiple_LEDs_on(LightsTypesEnum.ALL_FRONT_INNER_LIGHTS, LightsColorsEnum.COLOR_WHITE_XENON)
    Multiple_LEDs_on(LightsTypesEnum.ALL_REAR_LIGHTS, LightsColorsEnum.COLOR_RED_DIMMED)

    st_reaguj_na_caru = "reaguj na caru"
    st_vycti_senzory = "vycti senzory"
    st_stop = "zastav"
    st_spomal_a_popojed = "spomal a popojed"
    st_detekuj_krizovatku = "detekuj krizovatku"

    display.show("A B", displej_svietivost)
    sleep(0.5)

    while (not button_a.was_pressed()) and (not button_b.was_pressed()):
#        print(aktualni_stav)
        data = stav_vycti_senzory()
#        vypis_senzory_cary(vrat_levy(data), vrat_centralni(data), vrat_pravy(data))
    
        ret = ultrazvuk.proved_mereni_blokujici()
        ultrazvuk.reset()

        ret = ret*100
        print(ret)
        if (ret < 0) or (ret > 99):
            display.show(f"OUT", displej_svietivost)
        else:
            display.show(f"{int(ret)}", displej_svietivost)

        sleep(0.1)
        pass
    
    if button_a.is_pressed():
        joy_car.zastav()
        display.show('END')
        sleep(2)
        All_LEDs_off()
        display.fill(0)
        sys.exit()

    pocet_krizovatiek = 10    
#    display.show(pocet_krizovatiek, displej_svietivost)
    aktualni_stav = st_vycti_senzory

    
    pozadovana_vzdialenost_r = 0.2 # m
    chyba_e = 0.0 # m
    akcny_zasah_u = 0.0 # m/s
    P = -0.5 # Proporcionalny regulator

    # u = P * e

#    while (pocet_krizovatiek > 0) and (not button_a.was_pressed()):
    while not button_a.was_pressed():
        if aktualni_stav == st_vycti_senzory:
            data = stav_vycti_senzory()
#            vypis_senzory_cary(vrat_levy(data), vrat_centralni(data), vrat_pravy(data))
            ret_y = ultrazvuk.proved_mereni_blokujici()
            ultrazvuk.reset()

            chyba_e = pozadovana_vzdialenost_r - ret_y  # napr 0.2 - 0.5 = -0.3
            akcny_zasah_u = P * chyba_e                 # napr -0.5 * -0.3 = 0.15

            print(ret_y)
            ret_y = ret_y * 100 # prevod na cm

            if (ret_y < 0) or (ret_y > 99):
                display.show(f"OUT", displej_svietivost)
            else:
                display.show(f"{int(ret_y)}", displej_svietivost)

            sleep(0.1)

            if akcny_zasah_u > 0:   # pokracujeme dopredu o hodnotu akcneho zasahu doprednej rychlosti
                joy_car.jed("levy", "dopredu", int(left_a * akcny_zasah_u + left_b)*1.5)
                joy_car.jed("pravy", "dopredu", int(right_a * akcny_zasah_u + right_b + 30)*1.5)
            else:
                aktualni_stav = st_stop

#!#            if (ret <= 20) and (ret > 0):
#!#                aktualni_stav = st_stop
#!#            elif ret > 20:                              # still enough distance
#                aktualni_stav = st_reaguj_na_caru
#!#                aktualni_stav = st_spomal_a_popojed

#            print(aktualni_stav)
        
        if aktualni_stav == st_reaguj_na_caru:
            pokracuj_jizda_po_care = stav_reaguj_na_caru(data)
            if pokracuj_jizda_po_care:
                aktualni_stav = st_vycti_senzory
            else:
                aktualni_stav = st_spomal_a_popojed
        
        if aktualni_stav == st_spomal_a_popojed:
            joy_car.pohyb_mierne_vpred()    # popojed
            sleep(trvanie_pohybu)
#            aktualni_stav = st_stop
            aktualni_stav = st_vycti_senzory        # docasne kvoli demonstracii prace s ultrazvukom bez pouzitia mapy s ciarami
#            print(aktualni_stav)

        if aktualni_stav == st_stop:
            joy_car.zastav()
#            sleep(pauza_robota/2)
            aktualni_stav = st_vycti_senzory        # docasne kvoli demonstracii prace s ultrazvukom bez pouzitia mapy s ciarami
#            aktualni_stav = st_detekuj_krizovatku
#            print(aktualni_stav)
        
#        if aktualni_stav == st_detekuj_krizovatku:
            # pokial sa robot dostal na krizovatku (kontrola v stave 'st_reaguj_na_caru'), 
            # robot sa mierne pohne dopredu bez zastavenia, napokon zastavit
            # a nasleduje instrukcie dalsieho pohybu podla vopred urceneho zoznamu 'prikazy_pohybu' na zaciatku kodu
#            if joy_car.detekuj_krizovatku(data):  # T / X Crossroad / Corner (left/right)
#                pocet_krizovatiek -= 1
#                stav_akcia_na_krizovatke(data)
#                display.show(" "+str(pocet_krizovatiek)+" ", displej_svietivost)
#                print(aktualni_stav)
###            else:
###                display.show("E-3", displej_svietivost)  # Error status = -3 (no crossroad detected, robot move error)
###                sleep(0.2)
###                joy_car.zastav()
###                aktualni_stav = st_stop
###                All_LEDs_off()
###                display.fill(0)
###                sys.exit()

        sleep(0.005)
    
    joy_car.zastav()
    display.show('END', displej_svietivost)
    LEDs_blink(LightsTypesEnum.ALL_TURN_LIGHTS, LightsColorsEnum.COLOR_ORANGE, 1, 2)
    sleep(pauza_robota)
    All_LEDs_off()
    display.fill(0)