from microbit import sleep, pin14, pin15

def pocet_tiku_levy():
    surova_data_leva = pin14.read_digital()
    #zde napiste vas kod
    #scitejte tiky pro levy enkoder od zacatku behu progamu
    return #vratte soucet

def pocet_tiku_pravy():
    surova_data_prava = pin15.read_digital()
    #zde napiste vas kod
    #scitejte tiky pro pravy enkoder od zacatku behu progamu
    return #vratte soucet

if __name__ == "__main__":

    while True:
        print(pocet_tiku_levy(), pocet_tiku_pravy())
        sleep(5)
