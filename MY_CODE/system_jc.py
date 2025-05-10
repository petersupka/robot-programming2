from analogio import AnalogIn

class PinADC:
    def __init__(self, pin) -> None:
        self.pinName = pin
        self.pin = AnalogIn(self.pinName)
    def read_analog(self) -> int:
        # print(self.pin.value)
        return self.pin.value // 64

class PowerSupply:
    @staticmethod
    def getPowerSupplyVoltage(pin) -> float:
        # vrat velkost napajacieho napetia
        return 0.00898 * pin.read_analog() 
    