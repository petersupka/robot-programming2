from picoed import button_a, button_b, display
from time import sleep
import sys
from time import monotonic_ns
import board

from system_jc import PowerSupply, PinADC
from robot_jc import Robot
from sensors_line_jc import vycti_senzory, vrat_levy, vrat_centralni, vrat_pravy, vypis_senzory_cary
from lights_jc import LightsColorsEnum, LightsTypesEnum, Multiple_LEDs_on, LEDs_blink, All_LEDs_off#, Light

standard_rychlost = 120                 # standardna rychlost pohybu
trvanie_pohybu = 0.3                    # trvanie priameho pohybu
pauza_robota = 0.1                      # pauza motorov
displej_svietivost = 10                 # svietivost displeja

left_a = 15.92356688
left_b = 50
right_a = 26.00849257
right_b = 21.16666667
dopredna_rychlost = 4

leftPWM = left_a * dopredna_rychlost + left_b       +20
rightPWM = right_a * dopredna_rychlost + right_b    +20


'''
MAPA: (dvojita ciara je obluk)
Vychodzia pozicia a smer pohybu robota:
    ╔─┬─┬─┐
    ╟─┼─┼─┤
--> ╚─┴─┴─┘
'''
prikazy_pohybu = (   # vychadzame zo strany obluka dovnutra mapy po dlhsej trase
    "rovne",    # 2,1
    "rovne",    # 2,1
    "rovne",    # 2,1
#    "vlevo",    # 2,2
#    "vpravo", 
#    "vpravo",   # 2,3
#    "vpravo",   # roh
#    "rovne",    # 1,1
#    "vpravo",   # 1,2
#    "vlevo",    # 1,3
#    "vlevo",
    "rovne"    # STOP - navrat do vychodiskovej polohy
#    "vlevo"    # STOP - navrat do vychodiskovej polohy
    )

def stav_vycti_senzory() -> str:
    data_string = vycti_senzory()
    return data_string


def stav_reaguj_na_caru(data_string) -> bool:
    if joy_car.detekuj_krizovatku(data_string):
        return False
    
    if vrat_levy(data_string):
        joy_car.jed("pravy", "dopredu", rightPWM)
        joy_car.jed("levy", "dopredu", int(leftPWM/4))
        return True
    
    if vrat_pravy(data_string):
        joy_car.jed("pravy", "dopredu", int(rightPWM/4))
        joy_car.jed("levy", "dopredu", leftPWM)
        return True 

    if vrat_centralni(data_string):
        joy_car.jed("pravy", "dopredu", rightPWM)
        joy_car.jed("levy", "dopredu", leftPWM)
#        joy_car.pohyb_mierne_vpred()
        return True

#    if not(vrat_centralni(data_string)) and not(vrat_levy(data_string)) and not(vrat_pravy(data_string)):
#        display.show("E-4", displej_svietivost) # Error status = -4 (no line detected, robot lost)
#        return False

    return True


def stav_akcia_na_krizovatke(data_string):

    if data_string[5:8].count('1') >= 2:    # krizovatka detekovana
#        strana = prikazy_pohybu[9-pocet_krizovatiek] # poradie v liste chceme zachovat od 0 do 9 (krizovatky nam ale odpocitava od 9 do 0)
        strana = prikazy_pohybu[3-pocet_krizovatiek] # poradie v liste chceme zachovat od 0 do 9 (krizovatky nam ale odpocitava od 9 do 0)
       
        if strana == "vpravo":
#            display.show("<"+str(pocet_krizovatiek)+" ", displej_svietivost)
            joy_car.otocka_vpravo()

        elif strana == "vlevo":
#            display.show(" "+str(pocet_krizovatiek)+">", displej_svietivost)
            joy_car.otocka_vlavo()

        elif strana == "rovne":   # priamo
#            display.show("v"+str(pocet_krizovatiek)+"v", displej_svietivost)
            joy_car.pohyb_mierne_vpred()
        
        else:
            display.show("E-2", displej_svietivost) # Error status = -2 (Command ERROR)

        return True
    return False

     
if __name__ == "__main__":

    # inicializacia robota 
    joy_car = Robot()   # default params: x=0, y=0, theta=0, standard_rychlost=130, interval_pri_otocke=0.05, trvanie_pohybu=0.5, pauza_motorov=0.5
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
#        sys.exit()
    else:
#        display.show("BOK", displej_svietivost)
        sleep(0.2)
        display.fill(0)

    #--- kalibracia---  # spustena len na zaciatku pre ziskanie dat
#    joy_car.calibrate(0, 230, 1, pin2)
#    joy_car.zastav()
#    All_LEDs_off()
#    sys.exit()
    #--- koniec kalibracie ---

    aktualni_stav = "start"

#    x, y, theta = joy_car.odocalc([0, 0])
#    display.show(f'{int(x)},{int(y)}', displej_svietivost)
#    print(f'x: {x}, y: {y}, theta: {theta}')



    Multiple_LEDs_on(LightsTypesEnum.ALL_FRONT_INNER_LIGHTS, LightsColorsEnum.COLOR_WHITE_XENON)
#    Multiple_LEDs_on(LightsTypesEnum.ALL_FRONT_INNER_LIGHTS, LightsColorsEnum.COLOR_WHITE_DIMMED)
    Multiple_LEDs_on(LightsTypesEnum.ALL_REAR_LIGHTS, LightsColorsEnum.COLOR_RED_DIMMED)

    st_reaguj_na_caru = "reaguj na caru"
    st_vycti_senzory = "vycti senzory"
    st_stop = "zastav"
    st_spomal_a_popojed = "spomal a popojed"
    st_detekuj_krizovatku = "detekuj krizovatku"
    st_v_pohybe = "v pohybe"

#    display.show("A B", displej_svietivost)

    while (not button_a.was_pressed()) and (not button_b.was_pressed()):
#        print(aktualni_stav)
        data = stav_vycti_senzory()
        vypis_senzory_cary(vrat_levy(data), vrat_centralni(data), vrat_pravy(data))
        sleep(0.1)
        pass
    
    if button_a.is_pressed():
        joy_car.zastav()
        display.show('END')
        sleep(2)
        All_LEDs_off()
        display.fill(0)
        sys.exit()

    pocet_krizovatiek = 4
#    display.show(pocet_krizovatiek, displej_svietivost)
    aktualni_stav = st_vycti_senzory

    time_before = monotonic_ns()
    time_for_movement = monotonic_ns()

    distance = 0

    while (pocet_krizovatiek > 0) and (not button_a.was_pressed()):


        if aktualni_stav == st_vycti_senzory:
            data = stav_vycti_senzory()
#            vypis_senzory_cary(vrat_levy(data), vrat_centralni(data), vrat_pravy(data))
            aktualni_stav = st_reaguj_na_caru
#            print(aktualni_stav)
        
        if aktualni_stav == st_reaguj_na_caru:
            pokracuj_jizda_po_care = stav_reaguj_na_caru(data)
            if pokracuj_jizda_po_care:
                aktualni_stav = st_vycti_senzory
            else:
                aktualni_stav = st_spomal_a_popojed

        if aktualni_stav == st_spomal_a_popojed:
            joy_car.pohyb_mierne_vpred()    # popojed
#            sleep(trvanie_pohybu/1.3)
            aktualni_stav = st_v_pohybe

        if aktualni_stav == st_v_pohybe:
#            print(f"v pohybe: {(monotonic_ns() - time_for_movement)/1000000000}")
            if ((monotonic_ns() - time_for_movement)/1000000000) < (trvanie_pohybu/1.3):
                aktualni_stav = st_v_pohybe
            else:
                time_for_movement = monotonic_ns()
                aktualni_stav = st_stop

        if aktualni_stav == st_stop:
            joy_car.zastav()
#            sleep(pauza_robota)
            aktualni_stav = st_detekuj_krizovatku
#            print(aktualni_stav)
        
        if aktualni_stav == st_detekuj_krizovatku:
            # pokial sa robot dostal na krizovatku (kontrola v stave 'st_reaguj_na_caru'), 
            # robot sa mierne pohne dopredu bez zastavenia, napokon zastavit
            # a nasleduje instrukcie dalsieho pohybu podla vopred urceneho zoznamu 'prikazy_pohybu' na zaciatku kodu
            if joy_car.detekuj_krizovatku(data):  # T / X Crossroad / Corner (left/right)
                pocet_krizovatiek -= 1
                stav_akcia_na_krizovatke(data)
#                display.show(" "+str(pocet_krizovatiek)+" ", displej_svietivost)
                aktualni_stav = st_vycti_senzory
#                print(aktualni_stav)
            else:
                display.show("E-3", displej_svietivost)  # Error status = -3 (no crossroad detected, robot move error)
                sleep(0.2)
                joy_car.zastav()
                aktualni_stav = st_stop
                All_LEDs_off()
                display.fill(0)
                sys.exit()

        left_sum_ticks, right_sum_ticks = joy_car.calc_ticks()      # counting ticks in a given time until ~0.5s has passed
#        print(f'left_sum_ticks: {left_sum_ticks}, right_sum_ticks: {right_sum_ticks}')
        
        if (monotonic_ns() - time_before)/1000000000 >= 0.5:
            # ak sa robot pohybuje, tak sa zobrazi aktualna pozicia robota
            delta_x, x, y, theta = joy_car.odocalc([left_sum_ticks, right_sum_ticks])
            distance += delta_x
#            display.show(f'{int(x)},{int(y)}', displej_svietivost)
#            print(f'x: {x}, y: {y}, theta: {theta}')
#            print(f'distance: {distance:.1f}')
#            display.show(f'{distance:.1f}', displej_svietivost)
            time_before = monotonic_ns()


#        sleep(0.005)
    
    joy_car.zastav()
    distance *= 100
    display.show(f'{distance:.0f}', displej_svietivost)
#    display.show(f'{distance:.1f}', displej_svietivost)
    sleep(3)
    display.show('END', displej_svietivost)
    LEDs_blink(LightsTypesEnum.ALL_TURN_LIGHTS, LightsColorsEnum.COLOR_ORANGE, 1, 2)
    sleep(pauza_robota)
    All_LEDs_off()
    display.fill(0)