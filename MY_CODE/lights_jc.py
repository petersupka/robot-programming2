from neopixel import NeoPixel
from board import P0
from time import sleep

#class LightsActionsEnum:
#    OFF = 0
#    ON = 1
#    BLINK_DOUBLE = 2
#    BLINKING = 3

class LightsColorsEnum:
    COLOR_NONE = (0, 0, 0)
    COLOR_WHITE_DIMMED = (10, 10, 10)
    COLOR_WHITE_XENON = (56, 184, 205)
    COLOR_WHITE_BRIGHT = (255, 255, 255)
    COLOR_ORANGE = (230, 60, 0)
    COLOR_RED_BRIGHT = (255, 0, 0)
    COLOR_RED_DIMMED = (10, 0, 0)
    COLOR_GREEN_BRIGHT = (0, 255, 0)
    COLOR_BLUE_BRIGHT = (0, 0, 255)

class LightsTypesEnum:
    ALL_LIGHTS = (0, 1, 2, 3, 4, 5, 6, 7)
    ALL_FRONT_LIGHTS = (0, 1, 2, 3)
    ALL_FRONT_LIGHTS = (0, 1, 2, 3)
    ALL_FRONT_INNER_LIGHTS = (0, 3)
    ALL_REAR_LIGHTS = (4, 5, 6, 7)
    ALL_LEFT_TURN_LIGHTS = (1, 4)
    ALL_RIGHT_TURN_LIGHTS = (2, 7)
    ALL_TURN_LIGHTS = (1, 2, 4, 7)
    ALL_BREAK_LIGHTS = (5, 6)
    REAR_LIGHT_REVERSE = (5, )
    FRONT_LEFT_REFLECTOR_LIGHT = 0
    FRONT_RIGHT_REFLECTOR_LIGHT = 3
    REAR_LEFT_BREAK_LIGHT = 5
    REAR_RIGHT_BREAK_LIGHT = 6
    FRONT_LEFT_TURN_LIGHT = 1
    FRONT_RIGHT_TURN_LIGHT = 2
    REAR_LEFT_TURN_LIGHT = 4
    REAR_RIGHT_TURN_LIGHT = 7

class Light:
    __LEDs = NeoPixel(P0, 8)

    def __init__(self, position) -> None:
#        self.__LEDs
        self.position = position
        self.color = LightsColorsEnum.COLOR_NONE
#        self.state = LightsActionsEnum.OFF


#    def LED_on(self, ledNo:int, color:tuple[int, int, int]) -> None:
    def LED_on(self, color:tuple[int, int, int]) -> None:
        # nastav farbu pre jednu LED diodu
        self.__LEDs[self.position] = color
        self.__LEDs.write()


    def LED_off(self) -> None:
        self.__LEDs[self.position] = LightsColorsEnum.COLOR_NONE
        self.__LEDs.write()


def Multiple_LEDs_on(ledList:list[int], color:tuple[int, int, int]) -> None:
    for i in ledList:
        Light(i).LED_on(color)


def Multiple_LEDs_off(ledList:list[int]) -> None:
    for i in ledList:
        Light(i).LED_off()


def LEDs_blink(ledList:list[int], color:tuple[int, int, int], duration:float, no_blinks:int) -> None:
        led_previous_status = {}
        for led in ledList:
            led_previous_status[led] = Light(led).color

        while no_blinks > 0:
            for led in ledList:
                Light(led).LED_on(color)
            sleep(duration/no_blinks)
            for led in ledList:
#                Light(led).LED_off()
                Light(led).LED_on(led_previous_status[led])
            sleep(duration/no_blinks)
            no_blinks -= 1

def All_LEDs_off() -> None:
    for i in range(8):
        Light(i).LED_off()
