from picoed import button_a
from time import sleep, monotonic_ns
from board import P8, P12
from digitalio import DigitalInOut, Direction
from ultrazvuk import Ultrazvuk

if __name__ == "__main__":

    ultrazvuk = Ultrazvuk(DigitalInOut(P8), DigitalInOut(P12))
    
    ret = ultrazvuk.proved_mereni_blokujici()
    print("signal received", ret)

    ultrazvuk.__reset()

    ret = 0
    while not button_a.was_pressed():
        ret = ultrazvuk.proved_mereni_neblokujici()
        if ret == -3:
            continue
        else:
            break

        sleep(0.005)
    
    print(ret)
    

   

