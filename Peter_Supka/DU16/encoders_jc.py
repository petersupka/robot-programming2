from board import P14, P15
from digitalio import DigitalInOut

class Encoder:
    def __init__(self, side):
        self.pin = P14 if side == "left" else P15  # nastav pin pre enkoder
        self.encoder = DigitalInOut(self.pin)
#        self.encoder.direction = DigitalInOut.Direction.INPUT
        self.total_value = 0  # inicializacia hodnoty tickov - total
        self.previous_total_value = 0  # inicializacia hodnoty tickov - predchadzajuca total
        self.previous_value = int(self.encoder.value)  # predchadzajuca hodnota enkodera

    def ticks_number(self):
        raw_data = int(self.encoder.value)  # citanie surovej hodnoty z enkodera
        if self.previous_value != raw_data:
            self.total_value += 1
            self.previous_value = raw_data
        return self.total_value #vratte soucet

    def calc_angular_speed(self, ticks, T_period = 0.5):
        angle_radians = (ticks / 40) * 2*3.14       # 40 tikov = 1 otacka, 1 otacka = 2*pi radianov
        angular_speed = angle_radians / T_period    # T_perioda = .5s default - je perioda citania suboru tikov
        return angular_speed                        # rad/s - vratte rychlost v radianech za sekundu

    def calc_linear_speed(self, ticks, wheel_radius = 0.03):
        # 0.03 m = 3 cm - polomer kolesa
        # 40 tikov = 1 otacka, 1 otacka = 2*pi radianov
        # linear_speed = angular_speed * wheel_radius
        linear_speed = (ticks / 40) * (2*3.14) * wheel_radius
        return linear_speed                         # m/s
    
    def get_delta_ticks(self, ticks):
        # vrati rozdiel medzi aktualnym a predchadzajucim citanim
        # aktualna hodnota enkodera - sumar tickov
        delta_ticks = 0
        if ticks > self.previous_total_value:
            delta_ticks = ticks - self.previous_total_value
            self.previous_total_value = ticks
        return delta_ticks    

    def ticks_reset(self):
        self.total_value = 0
