import heapq

# Graful (lista vecini)
graf = {
    1:  [2, 10], 
    2:  [1, 3, 5],
    3:  [2, 15],
    4:  [5, 11],
    5:  [2, 4, 6, 8],
    6:  [5, 14],
    7:  [8, 12],
    8:  [5, 7, 9],
    9:  [8, 13],
    10: [1, 22, 11],
    11: [10, 19, 4, 12],
    12: [11, 7, 16],
    13: [14, 18, 9],
    14: [6, 15, 21, 13],
    15: [3, 24, 14],
    16: [12, 17],
    17: [20, 16, 18],
    18: [17, 13],
    19: [20, 11],
    20: [23, 21, 19, 17],
    21: [14, 20],
    22: [23, 10],
    23: [24, 20, 22],
    24: [15, 23]
}

# Noduri pe inele
#    0 - exterior, 1 - mijloc, 2 - interior
# Avem 8 pozitii pe inel, de la 0 la 7, fiecare pozitie corespunzand unui nod.
# Fiecare pereche (inel, pozitie) corespunde unui nod.
mapare_inel = {
    # Inel 0 (exterior)
    1:  (0, 0), 2:  (0, 1), 3:  (0, 2), 15: (0, 3), 
    24: (0, 4), 23: (0, 5), 22: (0, 6), 10: (0, 7),

    # Inel 1 (mijloc)
    4:  (1, 0), 5:  (1, 1), 6:  (1, 2), 14: (1, 3), 
    21: (1, 4), 20: (1, 5), 19: (1, 6), 11: (1, 7),

    # Inel 2 (interior)
    7:  (2, 0), 8:  (2, 1), 9:  (2, 2), 13: (2, 3),
    18: (2, 4), 17: (2, 5), 16: (2, 6), 12: (2, 7)
}
RING_SIZE = 8  # nr pozitii pe inel

# Cost muchie
def get_cost(u, v):
    """
    Cost de la u la v:
      - acelasi inel:
          * inel 0: cost = 3
          * inel 1: cost = 2
          * inel 2: cost = 1
      - inele dif: cost = 1
    """
    inel_u, _ = mapare_inel[u]
    inel_v, _ = mapare_inel[v]
    
    if inel_u == inel_v:
        if inel_u == 0:
            return 3
        elif inel_u == 1:
            return 2
        else:
            return 1
    else:
        return 1

# Euristica
def euristica_ineluri(nod, scopuri):
    """
    Calculeaza euristica pt nod:
      - dif radiala: nr inele de traversat
      - dif unghiulara: dist circulara daca sunt pe acelasi inel
    Returneaza minimul dintre toate valorile
    """
    best = 9999999
    inel_nod, poz_nod = mapare_inel[nod]
    for scop in scopuri:
        inel_scop, poz_scop = mapare_inel[scop]
        diff_radial = abs(inel_nod - inel_scop)
        aux = abs(poz_nod - poz_scop)
        diff_angular = min(aux , RING_SIZE - aux)
        diff_angular = diff_angular *  (min(3 - inel_scop, 3 - inel_nod))
        valoare_curenta = diff_radial + diff_angular

        if valoare_curenta < best:
            best = valoare_curenta
    return best

# A* cu nr fix de pasi
def a_star_n_pasi(nod_start, scopuri, nr_pasi):
    """
    A* care se opreste dupa nr_pasi
    Returneaza:
      - "Nod scop atins: <ID>" daca gaseste
      - lista open cu noduri si f daca nu gaseste
    """
    open_lista = []   # (f, nod, cost_g)
    g_start = 0
    f_start = g_start + euristica_ineluri(nod_start, scopuri)
    mesaj = "Lista open dupa " + str(nr_pasi) + " pasi:\n"
    heapq.heappush(open_lista, (f_start, nod_start, g_start))
    inchis = set()
    pasi = 0

    while open_lista and pasi < nr_pasi:
        f_curent, nod_curent, g_curent = heapq.heappop(open_lista)
        if nod_curent in inchis:
            continue
        inchis.add(nod_curent)

        if nod_curent in scopuri:
            mesaj = "Nod scop atins: " + str(nod_curent)
            return mesaj

        for vecin in graf[nod_curent]:
            if vecin in inchis:
                continue
            cost_edge = get_cost(nod_curent, vecin)
            g_nou = g_curent + cost_edge
            f_nou = g_nou + euristica_ineluri(vecin, scopuri)
            heapq.heappush(open_lista, (f_nou, vecin, g_nou))
        pasi = pasi + 1

    if len(open_lista) == 0:
        return "Nu mai exista noduri de explorat in lista open."
    
    def sort_key(item):
        return (item[0], item[1])
    lista_sortata = sorted(open_lista, key=sort_key)
    for element in lista_sortata:
        mesaj = mesaj + "  Nod: " + str(element[1]) + ", f: " + str(element[0]) + "\n"
    return mesaj

# IDA* cu limita de pasi
nr_expansiuni = 0

def ida_search(drum, g, limita, scopuri, nr_pasi):
    global nr_expansiuni
    nod_curent = drum[-1]
    f = g + euristica_ineluri(nod_curent, scopuri)
    
    if f > limita:
        return (f, None)  # trebuie sa crestem limita
    if nod_curent in scopuri:
        return (0, drum)  # solutie gasita
    if nr_expansiuni >= nr_pasi:
        return (-1, drum)  # limita atinsa
        
    min_f = float('inf')
    for vecin in graf[nod_curent]:
        if vecin in drum:
            continue
        nr_expansiuni += 1
        cost_edge = get_cost(nod_curent, vecin)
        f_nou, drum_nou = ida_search(drum + [vecin], g + cost_edge, limita, scopuri, nr_pasi)
        
        if drum_nou is not None:  # am gasit solutie sau limita
            return (f_nou, drum_nou)
        min_f = min(min_f, f_nou)
            
    return (min_f, None)

def ida_star_n_pasi(nod_start, scopuri, nr_pasi):
    limita = euristica_ineluri(nod_start, scopuri)
    while True:
        global nr_expansiuni
        nr_expansiuni = 0
        f, drum = ida_search([nod_start], 0, limita, scopuri, nr_pasi)
        
        if drum is not None:
            if f == 0:  # solutie
                mesaj = "Nod scop atins: " + str(drum[-1]) + "\nDrumul gasit este:\n"
                for nod in drum:
                    mesaj = mesaj + "  " + str(nod) + "\n"
                return mesaj
            if f == -1:  # limita
                mesaj = "Limita de pasi (" + str(nr_pasi) + ") atinsa.\nDrumul curent este:\n"
                for nod in drum:
                    mesaj = mesaj + "  " + str(nod) + "\n"
                return mesaj
        if f == float('inf'):
            return "Nu exista solutie."
        limita = f

#Functia principala
def rezolvare_problema(id_datapoint, nod_start, lista_scop, nr_pasi, algoritm):
    mesaj_final = "Rezolvare pentru ID = " + str(id_datapoint) + ":\n"
    if algoritm.upper() == "A*":
        rezultat = a_star_n_pasi(nod_start, lista_scop, nr_pasi)
        mesaj_final = mesaj_final + "Algoritmul A* a returnat:\n" + rezultat
    elif algoritm.upper() == "IDA*":
        rezultat = ida_star_n_pasi(nod_start, lista_scop, nr_pasi)
        mesaj_final = mesaj_final + "Algoritmul IDA* a returnat:\n" + rezultat    
    return mesaj_final

if __name__ == "__main__":
    # Test pt ID = 620, nod_start = 12, lista_scop = [1, 20], nr_pasi = 2, algoritm = "A*"
    id_datapoint = 620
    nod_start = 12
    lista_scop = [1, 20]
    nr_pasi = 4
    algoritm = "A*"  # sau "IDA*"
    
    rezultat = rezolvare_problema(id_datapoint, nod_start, lista_scop, nr_pasi, algoritm)
    print(rezultat)
