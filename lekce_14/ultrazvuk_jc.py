from digitalio import Direction 
from time import monotonic_ns
from cas_jc import Cas

class Ultrazvuk:
    def __init__(self, trig, echo):
        self.__trigger = trig
        self.__trigger.direction = Direction.OUTPUT
        self.__echo = echo
        self.__rychlost_zvuku = 343 # m/s
        self.__signal_vyslan = False
        self.__cas_vyslani = -1
        self.__signal_prijat = -1
        self.__konec_signalu = -1
    
    def __vysli_signal(self):
        self.__trigger.value = True
        self.__trigger.value = False
        self.__signal_vyslan = True
        self.__cas_vyslani = monotonic_ns()
    
    def reset(self):
        self.__signal_vyslan = False
        self.__cas_vyslani = -1
        self.__signal_prijat = -1
        self.__konec_signalu = -1

    #timeout je cas vyprseni mereni v sekundach
    def proved_mereni_blokujici(self, timeout = 0.05): 
        self.__vysli_signal()

        start = monotonic_ns()
        while self.__echo.value != 1:
            if Cas.ubehl_cas(monotonic_ns(), start, timeout):
                return -2  # Timeout
            
        start = monotonic_ns()
        while self.__echo.value == 1:
            if Cas.ubehl_cas(monotonic_ns(), start, timeout):
                return -1  # Timeout

        ubehnuty_cas = Cas.rozdil_tiku(monotonic_ns(), start) 

        return ubehnuty_cas*self.__rychlost_zvuku/2.0       # /2.0 tam + spat

#    def proved_mereni_neblokujici(self, timeout = 1):
#        if not self.__signal_vyslan:
#            self.__vysli_signal()
#            return -3
#        else:
#            # signal vyslan, cekame na prijem
#
#            if Cas.ubehl_cas(monotonic_ns(), self.__cas_vyslani, timeout):
#                self.__reset()
#                return -2
#            else: # cas je mensi nez timeout
#                #prijali jsme nabeznou hranu na echo pinu
#                if self.__echo.value == 1 and self.__signal_prijat==-1:
#                    self.__signal_prijat = monotonic_ns()
#                    return -3
#        
#                if self.__signal_prijat != -1 and Cas.ubehl_cas(self.__signal_prijat, monotonic_ns(), timeout):
#                    self.__reset()
#                    return -1
#        
#                if self.__echo.value == 0 and self.__signal_prijat != -1:
#                    self.__konec_signalu = monotonic_ns()
#
#                if self.__signal_prijat != -1 and self.__konec_signalu != -1:
#                    ubehnuty_cas = Cas.rozdil_tiku(self.__konec_signalu, self.__signal_prijat)
#                    self.__reset()
#                    return ubehnuty_cas*self.__rychlost_zvuku/2.0
#                
#                return -3 # cas je mensi nez timeout, echo je porad nula
#        
#        return -4 #tenhle by nikdy nemel nastat