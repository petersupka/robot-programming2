from utime import ticks_us, ticks_diff
from microbit import sleep

while True:
    print(ticks_us())
    sleep(100)
