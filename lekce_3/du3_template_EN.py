from microbit import pin1, pin2, pin8, pin9, pin15, pin16, sleep, display
class Motor:
    sides = ["left", "right"]
    directions = ["forward", "backward"]
    speeds = range(0, 1023)
    
    def __init__(self, left_spd=pin1, right_spd=pin2, left_dirA=pin15, left_dirB=pin16, right_dirA=pin8, right_dirB=pin9):
        self.left_speed = left_spd
        self.right_speed = right_spd
        self.left_directA = left_dirA
        self.left_directB = left_dirB
        self.right_directA = right_dirA
        self.right_directB = right_dirB
        
    def init_motor(self):
        self.left_speed.set_analog_period(1)
        self.right_speed.set_analog_period(1)
        sleep(100)
    
    def go(self, side, direction, speed):
        # side může být jen “left” a “right”
        if side not in self.sides:
            raise ValueError("Invalid side value! Use 'left' or 'right'")
        # “direction” je typu string a může mít hodnoty “forward”, "backward"
        if direction not in self.directions:
            raise ValueError("Invalid direction value! Use 'forward' or 'backward'")
        # speed je celočíselné číslo od 0-255 - v pripade pouzitia L293D driver motora je to 0-1023
        if speed not in self.speeds:
            raise ValueError("Invalid speed value! Use 0-1023")

        if direction == "forward":
            if side == "left":
                self.left_directA.write_digital(0)
                self.left_directB.write_digital(1)
                self.left_speed.write_analog(speed)
            elif side == "right":
                self.right_directA.write_digital(1)
                self.right_directB.write_digital(0)
                self.right_speed.write_analog(speed)
        elif direction == "backward":
            if side == "left":
                self.left_directA.write_digital(1)
                self.left_directB.write_digital(0)
                self.left_speed.write_analog(speed)
            elif side == "right":
                self.right_directA.write_digital(0)
                self.right_directB.write_digital(1)
                self.right_speed.write_analog(speed)

    def stop(self):
        self.left_speed.write_digital(0)
        self.right_speed.write_digital(0)
        self.left_directA.write_digital(0)
        self.left_directB.write_digital(0)
        self.right_directA.write_digital(0)
        self.right_directB.write_digital(0)
    # vyuzijte prikladu z hodiny, ktery poslal povel x03 - prave kolo pro jizdu rovne
    # ostatni povely:
    # Pravý motor:
    # 0x02 - příkaz pro pohyb vzad
    # 0x03 - příkaz pohyb vpřed
    # Levý motor:
    # 0x04 - příkaz pro pohyb vzad
    # 0x05 - příkaz pro pohyb vpřed

    #i2c.write(0x70, b'\x03' + bytes([speed]))

if __name__ == "__main__":
    # Write your code here :-)
    #i2c.init()
    # volejte funkci go, tak abyste ziskali:
    # Pohyb robota dopredu 1s
    # Zastaveni 1s - DULEZITE! Nikdy nemente smer jizdy bez zastaveni
    # Pohyb vzad 1s,
    # zastaveni
# Write your code here :-)
    try:
        Robot=Motor()
        print('Instance of Motor class created')
    
        Robot.init_motor()
        print('Motor initialized')

        Robot.go("left", "forward", 512)    # half speed
        Robot.go("right", "forward", 512)    # half speed
        print('Robot moving forward')
        display.show('F')
        sleep(1000)
    
        Robot.stop()
        print('Robot stopped')
        display.show('S')
        sleep(1000)
    
        Robot.go("left", "backward", 512)    # half speed
        Robot.go("right", "backward", 512)    # half speed
        print('Robot moving backward')
        display.show('B')
        sleep(1000)

        Robot.stop()
        print('Robot stopped finally')
        display.show('X')
        sleep(1000)

    except Exception as e:
        print('Error:', e)
        display.show('E')
        Robot.stop()
        sleep(1000)