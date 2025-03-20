from board import P14, P15
from digitalio import DigitalInOut
from time import sleep, time, monotonic_ns  # monotonic_ns pre pracu s intervalmi v ns (nanosekundach)

pocet_tikov_dict = {"lava": {"pocet_tikov": 0, "stav_predtym": 0}, "prava": {"pocet_tikov": 0, "stav_predtym": 0}}
levy_encoder = DigitalInOut(P14)
pravy_encoder = DigitalInOut(P15)

class FifoList:  # trieda pre FIFO zasobnik (typ LIST) - sluzi pre vypocet SMA (jednoducheho klzaveho priemeru)
    def __init__(self):
        self.data = []

    def append(self, data):
        self.data.append(data)

    def pop(self):
        value_removed = self.data[0]
        self.data.pop(0)
        return value_removed

    def get_len(self):
        return len(self.data)

    def get_avg(self):
        return sum(self.data) / len(self.data)

def SMA(data, N = 10):  # Simple Moving Average - jednoduchy klzavy priemer
    # N = 10 - defaultne 10 hodnot pre vypocet SMA
    if data.get_len() >= N:
        data.pop()
    return data.get_avg()
  
def pocet_tiku_levy():
    surova_data_leva = int(levy_encoder.value)
    #zde napiste vas kod
    #scitejte tiky pro levy enkoder od zacatku behu progamu
    if pocet_tikov_dict["lava"]["stav_predtym"] != surova_data_leva:
        pocet_tikov_dict["lava"]["pocet_tikov"] += 1
        pocet_tikov_dict["lava"]["stav_predtym"] = surova_data_leva
    return pocet_tikov_dict["lava"]["pocet_tikov"] #vratte soucet

def pocet_tiku_pravy():
    surova_data_prava = int(pravy_encoder.value)
    #zde napiste vas kod
    #scitejte tiky pro pravy enkoder od zacatku behu progamu
    if pocet_tikov_dict["prava"]["stav_predtym"] != surova_data_prava:
        pocet_tikov_dict["prava"]["pocet_tikov"] += 1
        pocet_tikov_dict["prava"]["stav_predtym"] = surova_data_prava
    return pocet_tikov_dict["prava"]["pocet_tikov"] #vratte soucet

def vypocti_rychlost(pocet_tiku, T_perioda = 0.5):
    # zde patri ukol DU5
    uhol_v_radianoch = (pocet_tiku / 40) * 2*3.14 # 40 tikov = 1 otacka, 1 otacka = 2*pi radianov
    uhlova_rychlost = uhol_v_radianoch / T_perioda # T_perioda = .5s default - je perioda citania suboru tikov
    return uhlova_rychlost # rad/s - vratte rychlost v radianech za sekundu

def reset_tikov():
    pocet_tikov_dict["lava"]["pocet_tikov"] = 0
    pocet_tikov_dict["prava"]["pocet_tikov"] = 0

def pauza(cas_pred_ulohami, interval_uspania=0.005):
    # vypocitame cas citania tikov a pripadnych vypoctov + vypisu dat
    interval_uspania = interval_uspania - (monotonic_ns() - cas_pred_ulohami)/1000000000 # nanosekundy na sekundy
    if interval_uspania < 0: # ak je interval_uspania vacsi ako 0, uspime sa na tento cas
        return False # ukoncime program, ak sa neda citat tiky v danom intervale
    else:
        sleep(interval_uspania) # uspime na periodu po ktorej citame znovu tiky
    return True # pokracujeme v programe

if __name__ == "__main__":
    aktualna_rychlost_vlavo = 0
    aktualna_rychlost_vpravo = 0

    # FIFO zasobnik pre ukladanie rychlosti vlavo/vpravo pre buduci vypocet klzaveho priemeru
    buffer_rychlosti_vlavo = FifoList()
    buffer_rychlosti_vpravo = FifoList()

    posledny_cas_vypisu = zmerana_perioda_T = time() # aktualny cas v sekundach
    cas_pred_spracovanim = monotonic_ns() # casova zlozka (nie aktualny cas, ale incrementovane cislo)

    while True:
        interval_pauzy = 0.005 # v sekundach - perioda uspania/pauzy pre citanie tikov, max 8.33ms

        lave_tiky = pocet_tiku_levy()
        prave_tiky = pocet_tiku_pravy()

        print("lave_tiky: ", lave_tiky, "prave_tiky: ", prave_tiky)

        if lave_tiky >= 20 or prave_tiky >= 20:
            zmerana_perioda_T = time() - zmerana_perioda_T # zmeriame periodu T v sekundach pre vypocet rychlosti
            # tymto sposobom zabezpecime, ze vzdy nazbierame min 20 tikov pre vypocet rychlosti (vlavo alebo vpravo alebo aj aj)
            # vdaka dynamickej zmene periody T urcime rychlost presnejsie nez ak by sme mali fixny interval citania tikov
            # ak by sa nam aj podarilo dosiahnut max rychlost a teda T perioda by bola 166ms, pre vypocet SMA pri 10 meranych 
            # hodnotach pokryjeme 1.66s (0.166s * (N-1) period = ~1.5s), co by stacilo pre vypocet klzaveho priemeru SMA(N=10)
            # realne pri nizsich rychlostiach bude T_perioda vacsia, co bude znamenat vacsi casovy rozsah pre vypocet SMA

            
            #volejte zde funkci aktualni_rychlost = vypocti_rychlost s vhodnou peridou - viz slidy min 166ms;
            #budete potrebovat vyuzit praci s casem pres tick_us, ticks_diff (mozna prikazy jsou jinak na pico:edu, pokud nenajdete, zeptejte se na discordu)
            #staci udelat pro jedno kolo
            aktualna_rychlost_vlavo = vypocti_rychlost(lave_tiky, zmerana_perioda_T)
            aktualna_rychlost_vpravo = vypocti_rychlost(prave_tiky, zmerana_perioda_T)
            
            # pridame aktualnu rychlost do FIFO zasobnika pre rychlosti vlavo/vpravo pre buduci vypocet klzaveho priemeru
            buffer_rychlosti_vlavo.append(aktualna_rychlost_vlavo)
            buffer_rychlosti_vpravo.append(aktualna_rychlost_vpravo)

            # vypocitame SMA pre rychlost vlavo/vpravo, defaultne pre 10 hodnot
            SMA_rychlost_vlavo = SMA(buffer_rychlosti_vlavo)
            SMA_rychlost_vpravo = SMA(buffer_rychlosti_vpravo)

#            print("zmerana_perioda_T (s): ", zmerana_perioda_T)
            
            if time() - posledny_cas_vypisu > 1: # 1s pauza medzi vypismi
#                print("Pocet tikov vlavo | vpravo: ", lave_tiky, " | ", prave_tiky)
                print("Aktualna rychlost vlavo | vpravo (rad/s): ", aktualna_rychlost_vlavo, " | ", aktualna_rychlost_vpravo)
                print("SMA rychlost vlavo | vpravo (rad/s): ", SMA_rychlost_vlavo, " | ", SMA_rychlost_vpravo)
#                print("")
                posledny_cas_vypisu = time() # aktualizujeme cas posledneho vypisu
            
            reset_tikov() # resetujeme tiky pre enkodery, aby sme mali ciste hodnoty pre dalsie meranie
            zmerana_perioda_T = time()

        if not pauza(cas_pred_spracovanim, interval_pauzy):
            print("Chyba pri citani tikov. Zrychlite periodu citania tikov alebo spomalte robota.")
            break # ukoncime program, ak sa neda citat tiky v danom intervale - chyba pri citani tikov alebo vypocte rychlosti
        else: # pokracujeme v programe
            cas_pred_spracovanim = monotonic_ns() # aktualizujeme cas pred spracovanim uloh