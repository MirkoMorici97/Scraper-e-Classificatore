import sys
import scipy.stats
from scipy.stats import ranksums
import statistics

fileMax = open('Profiling-UD_output/1075max.csv',"r")
fileMedio = open('Profiling-UD_output/1076medio.csv',"r")
fileMin = open('Profiling-UD_output/1079min.csv',"r")

#nomi_colonne = []

line=fileMax.readline()
linesMax=line.strip()
nomi_colonneMax=linesMax.split("\t")

lineMedio=fileMedio.readline()
linesMedio=lineMedio.strip()
nomi_colonneMedio=linesMedio.split("\t")

lineMin=fileMin.readline()
linesMin=lineMin.strip()
nomi_colonneMin=linesMin.split("\t")

#creo un dizionario con solo i nomi delle features
Dict_colonne = {}
Dict_colonne_min = {}
n = 1
m = 1
for nomi in nomi_colonneMax[1:]:
    Dict_colonne[n] = nomi
    n = n + 1

for nomi_min in nomi_colonneMin[1:]:
    Dict_colonne_min[m] = nomi_min
    m = m + 1


#funzione per creare il dizoinario da dove costruisco le matrici
def crea_dizionario(filex):
    Dict = {}
    #scorro ogni riga del file
    for riga in filex:
        righe=riga.strip()
        lista_riga=righe.split("\t")
         #il contatore c serve indicare la chiave del dizionario così da poter dividere il dizionario di ogni file in
         # chiavi valore dove la chiave è il nome della features e il valore tutti i dati corrispondenti a quella features
         # di una sola fascia di prezzo
        c = 1
        #scorro le righe di
        for ele in lista_riga[1:]:
            #controllo se il nome della features è già presente nel mio dizionario che rappresenta il documento
            # se lo è, allora semplicemente appendo il valore alla chiave 
            if Dict_colonne[c] in Dict:
                Dict[Dict_colonne[c]].append(float(ele))
            else:
            # se non lo è allora creo la chiave con quel nome della features e appendo l'elemento
                Dict[Dict_colonne[c]] = []
                Dict[Dict_colonne[c]].append(float(ele))
            if c < len(Dict_colonne):
                c = c + 1
    return Dict

def crea_dizionario_min(fileMin):
    DictMin = {}
    for riga in fileMin:
        righe=riga.strip()
        lista_riga=righe.split("\t")
        c = 1
        for ele in lista_riga[1:]:
            if Dict_colonne_min[c] in DictMin:
                DictMin[Dict_colonne_min[c]].append(float(ele))
            else:
                DictMin[Dict_colonne_min[c]] = []
                DictMin[Dict_colonne_min[c]].append(float(ele))
            if c < len(Dict_colonne_min):
                c = c + 1
    return DictMin


def controlla_dizionario(Dict_max, Dict_medio, Dict_min):
    chiavi_max = list(Dict_max.keys())
    chiavi_medio = list(Dict_medio.keys())
    chiavi_min = list(Dict_min.keys())
    print("Chiavi max", len(chiavi_max))
    print("Chiavi medio", len(chiavi_medio))
    print("Chiavi min", len(chiavi_min))
    for chiave in range(len(chiavi_max)):
        if chiavi_max[chiave] == chiavi_medio[chiave] and chiavi_max[chiave] == chiavi_min[chiave] and chiavi_medio[chiave] == chiavi_min[chiave]:
            print("Chiave: ", chiavi_max[chiave], " E' uguale per tutti i file: ", chiavi_max[chiave], chiavi_medio[chiave], chiavi_min[chiave])
        else:
            print("ATTENZIONE!! Chiave: ", chiavi_max[chiave], "Non è ugule per i file")
            print("Chiave max: ", chiavi_max[chiave])
            print("Chiave medio: ", chiavi_medio[chiave])
            print("Chiave min: ", chiavi_min[chiave])
            chiave_da_eliminare = chiavi_min[chiave]
            break
    print("\n\n")
    print("Eliminare: ", chiave_da_eliminare)
    print("\n\n")
    Dict_min.pop(chiave_da_eliminare, None)
    chiavi_min2 = list(Dict_min.keys())
    print("Chiavi min aggiornato: ", len(chiavi_min2))
    for chiave in range(len(chiavi_max)):
        if chiavi_max[chiave] == chiavi_medio[chiave] and chiavi_max[chiave] == chiavi_min2[chiave] and chiavi_medio[chiave] == chiavi_min2[chiave]:
            print("Chiave: ", chiavi_max[chiave], " E' uguale per tutti i file: ", chiavi_max[chiave], chiavi_medio[chiave], chiavi_min2[chiave])
        else:
            print("ATTENZIONE!! Chiave: ", chiavi_max[chiave], "Non è ugule per i file")
            print("Chiave max: ", chiavi_max[chiave])
            print("Chiave medio: ", chiavi_medio[chiave])
            print("Chiave min: ", chiavi_min2[chiave])
            chiave_da_eliminare = chiavi_min2[chiave]
            break
    return Dict_min
    


def main():
    dati = []

    Dict_max = crea_dizionario(fileMax)
    Dict_medio = crea_dizionario(fileMedio)
    Dict_min = crea_dizionario_min(fileMin)
    Dict_min = controlla_dizionario(Dict_max, Dict_medio, Dict_min)

    parole_file_max = sum(Dict_max[Dict_colonne[2]])
    parole_file_medio = sum(Dict_medio[Dict_colonne[2]])
    parole_file_min = sum(Dict_min[Dict_colonne[2]])

    frasi_file_max = sum(Dict_max[Dict_colonne[1]])
    frasi_file_medio = sum(Dict_medio[Dict_colonne[1]])
    frasi_file_min = sum(Dict_min[Dict_colonne[1]])

    parole_totali = parole_file_max + parole_file_medio + parole_file_min
    frasi_totali = frasi_file_max + frasi_file_medio + frasi_file_min

    print("Totale parole file max = ", parole_file_max)
    print("Totale parole file medio = ", parole_file_medio)
    print("Totale parole file min = ", parole_file_min)
    print("Totale parole nei file = ", parole_totali)
    print("Totale frasi file max = ", frasi_file_max)
    print("Totale frasi file medio = ", frasi_file_medio)
    print("Totale frasi file min = ", frasi_file_min)
    print("Totale frasi nei file = ", frasi_totali)

    for n in range(1,143):

        rank_Max_Medio = ranksums(Dict_max[Dict_colonne[n]],Dict_medio[Dict_colonne[n]])
        rank_Medio_Min = ranksums(Dict_medio[Dict_colonne[n]],Dict_min[Dict_colonne[n]])
        rank_Min_Max = ranksums(Dict_min[Dict_colonne[n]],Dict_max[Dict_colonne[n]])
        
        #calcolo la media
        mediaMax = statistics.mean(Dict_max[Dict_colonne[n]])
        mediaMedio = statistics.mean(Dict_medio[Dict_colonne[n]])
        mediaMin = statistics.mean(Dict_min[Dict_colonne[n]])
        
        #camcolo la deviazione standard
        deviazioneMax = statistics.stdev(Dict_max[Dict_colonne[n]])
        deviazioneMedio = statistics.stdev(Dict_medio[Dict_colonne[n]])
        deviazioneMin = statistics.stdev(Dict_min[Dict_colonne[n]])
        
        print(Dict_colonne[n])
        if rank_Max_Medio[1] < 0.05:
            print("Max-Medio: ", rank_Max_Medio, ",  Media Max: ", mediaMax, ", Media Medio: ", mediaMedio, ", Deviazione standard Max: ", deviazioneMax, ", Deviazione standard Medio: ", deviazioneMedio)
            #print(max(Dict_max[Dict_colonne[n]]))
            #print(max(Dict_medio[Dict_colonne[n]]))
            if rank_Max_Medio[1] < 0.001:
                print("Fortemente significativa")
            else:
                print("Mediamente significativa")
            print("\n")
        if rank_Medio_Min[1] < 0.05:
            print("Medio-Min: ", rank_Medio_Min, ",  Media Medio: ", mediaMedio, ", Media Min: ", mediaMin, ", Deviazione standard Medio: ", deviazioneMedio, ", Deviazione standard Min: ", deviazioneMin)
            #print(max(Dict_medio[Dict_colonne[n]]))
            #print(max(Dict_min[Dict_colonne[n]]))
            if rank_Medio_Min[1] < 0.001:
                print("Fortemente significativa")
            else:
                print("Mediamente significativa")
            print("\n")
        if rank_Min_Max[1] < 0.05:
            print("Min-Max: ", rank_Min_Max, ",  Media Min: ", mediaMin, ", Media Max: ", mediaMax, ", Deviazione standard Min: ", deviazioneMin, ", Deviazione standard Max: ", deviazioneMax)
            #print(max(Dict_min[Dict_colonne[n]]))
            #print(max(Dict_max[Dict_colonne[n]]))
            if rank_Min_Max[1] < 0.001:
                print("Fortemente significativa")
            else:
                print("Mediamente significativa")
            print("\n")
    print("\n\n\n")

if __name__ == "__main__":
    main()