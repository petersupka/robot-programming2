
from math import fabs

class Cas:
    def rozdil_tiku(posledni_cas_ns: int, cas_ted_ns: int):
        return fabs(cas_ted_ns - posledni_cas_ns)/1000000000.0
    
    def ubehl_cas(posledni_cas_ns, cas_ted_ns, interval_s):
        rozdil_s = Cas.rozdil_tiku(posledni_cas_ns, cas_ted_ns)
        return rozdil_s > interval_s