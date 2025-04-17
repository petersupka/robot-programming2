from time import sleep
from motors_jc import init_motoru, nastav_PWM_kanaly
from lights_jc import Multiple_LEDs_on, LightsTypesEnum, LightsColorsEnum, LEDs_blink
from sensors_line_jc import vycti_senzory, vrat_levy, vrat_centralni, vrat_pravy, vypis_senzory_cary

rychlost_dorovnania = 10                # rychlost dorovnania pre lavy motor

class Robot:
    def __init__(self, standard_rychlost=120, interval_pri_otocke=0.05, trvanie_pohybu=0.3, pauza_motorov=0.5):
        self.standard_rychlost = standard_rychlost                 # standardna rychlost pohybu
        self.interval_pri_otocke = interval_pri_otocke             # trvanie otocky
        self.trvanie_pohybu = trvanie_pohybu                       # trvanie priameho pohybu
        self.pauza_motorov = pauza_motorov                         # pauza motorov
        self.centralny_senzor_predtym = [0, 0]                     # vpravo/vlavo pre ulozenie stavu centralneho senzoru predtym
        init_motoru()                                          # inicializacia motorov
    
    def jed(self, strana, smer, rychlost):
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
                je_vse_ok = nastav_PWM_kanaly(b"\x05", b"\x04", rychlost + rychlost_dorovnania)
            elif smer == "dozadu":
                je_vse_ok = nastav_PWM_kanaly(b"\x04", b"\x05", rychlost)
            else:
                je_vse_ok = -4
        elif strana == "pravy":
            if smer == "dopredu":
                je_vse_ok = nastav_PWM_kanaly(b"\x03", b"\x02", rychlost)
            elif smer == "dozadu":
                je_vse_ok = nastav_PWM_kanaly(b"\x02", b"\x03", rychlost +  rychlost_dorovnania)
            else:
                je_vse_ok = -4
        else:
            je_vse_ok = -2

        return je_vse_ok


    def zastav(self):
        self.jed("pravy", "dopredu", 0)
        self.jed("pravy", "dozadu", 0)
        self.jed("levy", "dopredu", 0)
        self.jed("levy", "dozadu", 0)
        Multiple_LEDs_on(LightsTypesEnum.ALL_REAR_LIGHTS, LightsColorsEnum.COLOR_RED_BRIGHT)
        sleep(0.3)
        Multiple_LEDs_on(LightsTypesEnum.ALL_REAR_LIGHTS, LightsColorsEnum.COLOR_RED_DIMMED)


    def detekuj_krizovatku(self, data_string):
        # rychla konstrola, ci je robot na krizovatke 2+ senzorov detekuje ciernu ciaru
        print(data_string[5:8].count('1'))
        if data_string[5:8].count('1') >= 2:
            return True
        else:
            return False


    def pohyb_mierne_vpred(self):
        # pohneme robotom dopredu o pauza_pohyb sekund
        self.jed("levy", "dopredu", self.standard_rychlost)
        self.jed("pravy", "dopredu", self.standard_rychlost)
        return True


    def otocka_vlavo(self):
        self.centralny_senzor_predtym[0] = 1
        LEDs_blink(LightsTypesEnum.ALL_LEFT_TURN_LIGHTS,LightsColorsEnum.COLOR_ORANGE, self.interval_pri_otocke*2, 1)

        self.jed("levy", "dozadu", int(self.standard_rychlost/1.2))
        self.jed("pravy", "dopredu", int(self.standard_rychlost/1.2))

        while True:
            if self.centralny_senzor_predtym[0] == 1:    # zbehne len 1x na zaciatku otocky
                self.centralny_senzor_predtym[0] = 0
                LEDs_blink(LightsTypesEnum.ALL_LEFT_TURN_LIGHTS,LightsColorsEnum.COLOR_ORANGE, self.interval_pri_otocke*2, 1)
            self.jed("levy", "dozadu", int(self.standard_rychlost/1.3))
            self.jed("pravy", "dopredu", int(self.standard_rychlost/1.3))
            LEDs_blink(LightsTypesEnum.ALL_LEFT_TURN_LIGHTS,LightsColorsEnum.COLOR_ORANGE, self.interval_pri_otocke, 1)
            data_string = vycti_senzory()
            if vrat_centralni(data_string):
                self.zastav()
                break

        sleep(self.pauza_motorov)
        return True
    

    def otocka_vpravo(self):
        self.centralny_senzor_predtym[1] = 1
        LEDs_blink(LightsTypesEnum.ALL_RIGHT_TURN_LIGHTS,LightsColorsEnum.COLOR_ORANGE, self.interval_pri_otocke*2, 1)

        self.jed("levy", "dopredu", int(self.standard_rychlost/1.2))
        self.jed("pravy", "dozadu", int(self.standard_rychlost/1.2))

        while True:
            if self.centralny_senzor_predtym[1] == 1:    # zbehne len 1x na zaciatku otocky
                self.centralny_senzor_predtym[1] = 0
                LEDs_blink(LightsTypesEnum.ALL_RIGHT_TURN_LIGHTS,LightsColorsEnum.COLOR_ORANGE, self.interval_pri_otocke*2, 1)
            self.jed("levy", "dopredu", int(self.standard_rychlost/1.4))
            self.jed("pravy", "dozadu", int(self.standard_rychlost/1.4))
            LEDs_blink(LightsTypesEnum.ALL_RIGHT_TURN_LIGHTS,LightsColorsEnum.COLOR_ORANGE, self.interval_pri_otocke, 1)
            data_string = vycti_senzory()
            if vrat_centralni(data_string):
                self.zastav()
                break

        sleep(self.pauza_motorov)
        return True