from microbit import sleep, pin14, pin15

if __name__ == "__main__":

    while True:
        surova_data_leva = pin14.read_digital()
        surova_data_prava = pin15.read_digital()
        print(surova_data_leva, surova_data_prava)
        sleep(5)
