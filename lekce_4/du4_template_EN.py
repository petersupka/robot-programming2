from microbit import sleep, pin14, pin15

def left_sum_ticks():
    surova_data_leva = pin14.read_digital()
    #zde napiste vas kod
    #scitejte tiky pro levy enkoder od zacatku behu progamu
    return #vratte soucet

def right_sum_ticks():
    surova_data_prava = pin15.read_digital()
    #zde napiste vas kod
    #scitejte tiky pro pravy enkoder od zacatku behu progamu
    return #vratte soucet

if __name__ == "__main__":

    while True:
        print(left_sum_ticks(), right_sum_ticks())
        sleep(5)
