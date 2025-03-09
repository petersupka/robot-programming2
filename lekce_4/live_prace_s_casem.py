from microbit import sleep, pin15, pin14
from utime import ticks_us, ticks_diff

if __name__ == "__main__":

    cas_minule = ticks_us()

    while True:
        surova_data_prava = pin15.read_digital() #pravy enkoder je pripojeny na pin15 na microbitu, levy na pin14
        surova_data_leva = pin14.read_digital()
        cas_ted = ticks_us()
        if ticks_diff(cas_ted, cas_minule) > 1000000: # tato podminka dela to, ze hodnotu vypiseme jen jednou za 1s do terminalu
            print(surova_data_leva, surova_data_prava)
            cas_minule = cas_ted

        sleep(100) # hlavni smycka bezi na 100ms
