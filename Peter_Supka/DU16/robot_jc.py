from time import sleep, monotonic_ns
from motors_jc import init_motors, set_canals
from lights_jc import Multiple_LEDs_on, LightsTypesEnum, LightsColorsEnum, LEDs_blink
from sensors_line_jc import vycti_senzory, vrat_centralni
from encoders_jc import Encoder
from picoed import display
import circuitpython_csv as csv
from system_jc import PowerSupply
from math import pi, sin, cos


class Robot:
    def __init__(self, x=0, y=0, theta=0, standard_rychlost=130, interval_pri_otocke=0.05, trvanie_pohybu=0.5, pauza_motorov=0.5):
        self.__standard_rychlost = standard_rychlost                 # standardna rychlost pohybu
        self.__dopredna_rychlost = 4                                 # rychlost rad/s   
        self.__interval_pri_otocke = interval_pri_otocke             # trvanie otocky
        self.__trvanie_pohybu = trvanie_pohybu                       # trvanie priameho pohybu
        self.__pauza_motorov = pauza_motorov                         # pauza motorov
        self.__centralny_senzor_predtym = [0, 0]                     # vpravo/vlavo pre ulozenie stavu centralneho senzoru predtym
        self.__left_encoder = Encoder("left")
        self.__right_encoder = Encoder("right")
        self.__robot_radius = 0.075 # distance between wheel center and robot center [m]
        self.__wheel_radius = 0.034 # wheel radius [m]
        self.__left_a = 15.92356688
        self.__left_b = 50
        self.__right_a = 26.00849257
        self.__right_b = 21.16666667
        self.__leftPWM = self.__left_a * self.__dopredna_rychlost + self.__left_b       +20
        self.__rightPWM = self.__right_a * self.__dopredna_rychlost + self.__right_b    +20
        self.__odoconst = 2 * pi * self.__wheel_radius / 40 # odometer constant  (40 = ticks per 1 rotation)
        self.__pos_x = x
        self.__pos_y = y
        self.__pos_theta = theta


        init_motors()                                             # inicializacia motorov


    def calibrate(self, PWM_from, PWM_to, inc, pin2):
        # kalibracia robota
        # robot sa roztoci od 'PWM_from' do 'PWM_to' s inkrementaciou 'inc' + zostupne {PWM_to -> PWM_from)}
        # a zmeria rychlost na motore (uhlova z tickov), vo finale sa ulozi do CSV suboru na Picoed-e

        csvheader = ["battery", "pace", "PWM", "left_speed", "right_speed"]

        list_of_dict_calibrate_values = []

        pause = 0.5

        left_ticks = 0
        right_ticks = 0
        left_speed = 0
        right_speed = 0

        voltage = PowerSupply.getPowerSupplyVoltage(pin2)

        i = 0
        for PWM in range(PWM_from, PWM_to, inc):
            i += 1
            time_before = monotonic_ns()
            # nastavit PWM na motore
            # zmerat rychlost na motore (uhlova z tickov)
            # ulozit do CSV suboru na Picoed-e
            # vypisat na displej
            display.show(str(PWM), 5)
            self.jed("pravy", "dopredu", PWM)
            self.jed("levy", "dozadu", PWM)

            if i == 10: # po 10 hodnotach (5 sekundach) sa odcita napatie
                voltage = PowerSupply.getPowerSupplyVoltage(pin2)
                print(voltage)
                i = 0

            while pause > (monotonic_ns() - time_before)/1000000000: # nanosekundy na sekundy
                left_ticks = self.__left_encoder.ticks_number()
                right_ticks = self.__right_encoder.ticks_number()
                sleep(0.005) # uspime na periodu po ktorej citame znovu tiky

            left_speed = self.__left_encoder.calc_angular_speed(left_ticks, self.__trvanie_pohybu)
            right_speed = self.__right_encoder.calc_angular_speed(right_ticks, self.__trvanie_pohybu)

            list_of_dict_calibrate_values.append(
                {"battery":voltage,
                 "pace":"I", 
                 "PWM":PWM, 
                 "left_speed":left_speed, 
                 "right_speed":right_speed}
            )

            self.__left_encoder.ticks_reset()
            self.__right_encoder.ticks_reset()

        left_ticks = 0
        right_ticks = 0
        left_speed = 0
        right_speed = 0

        i = 0
        for PWM in range(PWM_to, PWM_from, inc*(-1)):
            i += 1
            time_before = monotonic_ns()
            # nastavit PWM na motore
            # zmerat rychlost na motore (uhlova z tickov)
            # ulozit do CSV suboru na Picoed-e
            # vypisat na displej
            display.show(str(PWM), 5)
            self.jed("pravy", "dopredu", PWM)
            self.jed("levy", "dozadu", PWM)

            if i == 10: # po 10 hodnotach (5 sekundach) sa odcita napatie
                voltage = PowerSupply.getPowerSupplyVoltage(pin2)
                print(voltage)
                i = 0

            while pause > (monotonic_ns() - time_before)/1000000000: # nanosekundy na sekundy
                left_ticks = self.__left_encoder.ticks_number()
                right_ticks = self.__right_encoder.ticks_number()
                sleep(0.005) # uspime na periodu po ktorej citame znovu tiky

            left_speed = self.__left_encoder.calc_angular_speed(left_ticks, self.__trvanie_pohybu)
            right_speed = self.__right_encoder.calc_angular_speed(right_ticks, self.__trvanie_pohybu)

            list_of_dict_calibrate_values.append(
                {"battery":voltage,
                 "pace":"D", 
                 "PWM":PWM, 
                 "left_speed":left_speed, 
                 "right_speed":right_speed}
            )

            self.__left_encoder.ticks_reset()
            self.__right_encoder.ticks_reset()

        self.zastav()

#        print(list_of_dict_calibrate_values)

        try:
            with open("calibration.csv", mode="w", encoding="utf-8") as writablefile:
                csvwriter = csv.DictWriter(writablefile, csvheader)
                csvwriter.writeheader()
                display.show("SAV", 5)
                csvwriter.writerows(list_of_dict_calibrate_values)

                display.show("OK", 5)
        except OSError as e:
#            print("Error: ", e)
            display.show("Err", 5)

        return 0


    def go(self, forward, angular):
        v_l = int(forward - self.__robot_radius * angular)
        v_r = int(forward + self.__robot_radius * angular)

        if (v_l >= 0):
            self.jed("levy", "dopredu", v_l)
        else:
            self.jed("levy", "dozadu", abs(v_l))

        if (v_r >= 0):
            self.jed("pravy", "dopredu", v_r)
        else:
            self.jed("pravy", "dozadu", abs(v_r))

        return 0

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
            return je_vse_ok

        if strana == "levy":
            if smer == "dopredu":
                je_vse_ok = set_canals(b"\x05", b"\x04", rychlost)
            elif smer == "dozadu":
                je_vse_ok = set_canals(b"\x04", b"\x05", rychlost)
            else:
                je_vse_ok = -4
        elif strana == "pravy":     # riesime cez L293D (externy H-Bridge)
            if smer == "dopredu":
#                je_vse_ok = set_canals(b"\x03", b"\x02", rychlost)
#                je_vse_ok = set_canals(self.pin_forward.duty_cycle, self.pin_reverse.duty_cycle, rychlost)
                je_vse_ok = set_canals("P13", "P16", rychlost)
            elif smer == "dozadu":
#                je_vse_ok = set_canals(b"\x02", b"\x03", rychlost)
#                je_vse_ok = set_canals(self.pin_reverse.duty_cycle, self.pin_forward.duty_cycle, rychlost)
                je_vse_ok = set_canals("P16", "P13", rychlost)
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
        sleep(0.1)
        Multiple_LEDs_on(LightsTypesEnum.ALL_REAR_LIGHTS, LightsColorsEnum.COLOR_RED_DIMMED)


    def detekuj_krizovatku(self, data_string):
        # rychla konstrola, ci je robot na krizovatke 2+ senzorov detekuje ciernu ciaru
#        print(data_string[5:8].count('1'))
        if data_string[5:8].count('1') >= 2:
            return True
        else:
            return False

    def calc_ticks(self) -> tuple:
        return self.__left_encoder.ticks_number(), self.__right_encoder.ticks_number()

    def pohyb_mierne_vpred(self):
        self.jed("levy", "dopredu", self.__leftPWM)
        self.jed("pravy", "dopredu", self.__rightPWM)
        return True


    def otocka_vlavo(self):
        self.__centralny_senzor_predtym[0] = 1
        LEDs_blink(LightsTypesEnum.ALL_LEFT_TURN_LIGHTS,LightsColorsEnum.COLOR_ORANGE, self.__interval_pri_otocke*2, 1)

        self.jed("levy", "dozadu", int(self.__leftPWM))
        self.jed("pravy", "dopredu", int(self.__rightPWM))

        while True:
            if self.__centralny_senzor_predtym[0] == 1:    # zbehne len 1x na zaciatku otocky
                self.__centralny_senzor_predtym[0] = 0
                LEDs_blink(LightsTypesEnum.ALL_LEFT_TURN_LIGHTS,LightsColorsEnum.COLOR_ORANGE, self.__interval_pri_otocke*2, 1)
            self.jed("levy", "dozadu", int(self.__leftPWM/1.2))
            self.jed("pravy", "dopredu", int(self.__rightPWM/1.2))
            LEDs_blink(LightsTypesEnum.ALL_LEFT_TURN_LIGHTS,LightsColorsEnum.COLOR_ORANGE, self.__interval_pri_otocke, 1)
            data_string = vycti_senzory()
            if vrat_centralni(data_string):
                self.zastav()
                break

        sleep(self.__pauza_motorov)
        return True
    

    def otocka_vpravo(self):
        self.__centralny_senzor_predtym[1] = 1
        LEDs_blink(LightsTypesEnum.ALL_RIGHT_TURN_LIGHTS,LightsColorsEnum.COLOR_ORANGE, self.__interval_pri_otocke*2, 1)

        self.jed("levy", "dopredu", int(self.__leftPWM))
        self.jed("pravy", "dozadu", int(self.__rightPWM))

        while True:
            if self.__centralny_senzor_predtym[1] == 1:    # zbehne len 1x na zaciatku otocky
                self.__centralny_senzor_predtym[1] = 0
                LEDs_blink(LightsTypesEnum.ALL_RIGHT_TURN_LIGHTS,LightsColorsEnum.COLOR_ORANGE, self.__interval_pri_otocke*2, 1)
            self.jed("levy", "dopredu", int(self.__leftPWM/1.2))
            self.jed("pravy", "dozadu", int(self.__rightPWM/1.2))
            LEDs_blink(LightsTypesEnum.ALL_RIGHT_TURN_LIGHTS,LightsColorsEnum.COLOR_ORANGE, self.__interval_pri_otocke, 1)
            data_string = vycti_senzory()
            if vrat_centralni(data_string):
                self.zastav()
                break

        sleep(self.__pauza_motorov)
        return True

    def normalize_angle(self, angle):
        angle = angle % (2*pi)       # normalizacia uhla do intervalu [0, 2pi]
        if angle > pi:
            angle = angle - 2*pi
        if angle < -pi:
            angle = angle + 2*pi
        return angle

    def odocalc(self, ticks:tuple[int, int]) -> tuple[float, float, float, float]:
        left_delta_ticks = self.__left_encoder.get_delta_ticks(ticks[0])
        right_delta_ticks = self.__right_encoder.get_delta_ticks(ticks[1])
        delta_X = self.__odoconst * (left_delta_ticks + right_delta_ticks) / 2
#        print(f'delta_X: {delta_X}, left_delta_ticks: {left_delta_ticks}, right_delta_ticks: {right_delta_ticks}')
        delta_theta = self.__odoconst * (right_delta_ticks - left_delta_ticks) / self.__robot_radius
        final_theta = self.__pos_theta + delta_theta / 2
        self.__pos_x += cos(final_theta) * delta_X
        self.__pos_y += sin(final_theta) * delta_X
        self.__pos_theta += delta_theta
        self.__pos_theta = self.normalize_angle(self.__pos_theta)
        return delta_X, self.__pos_x, self.__pos_y, self.__pos_theta