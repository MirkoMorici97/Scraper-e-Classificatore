import sklearn
from sklearn import preprocessing
from sklearn import svm
from sklearn import metrics
import pandas as pd
from pandas import Series
import itertools
from itertools import chain
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import figure
import numpy as np
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import average_precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_recall_fscore_support
from sklearn.ensemble import ExtraTreesClassifier
import random


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
    

    

def crea_corpus(Dict_max, Dict_medio, Dict_min):
    features_da_scalare = []
    lista_scalati = []
    matrice_valori_training_max = []
    matrice_valori_test_max = []

    matrice_valori_training_medio = []
    matrice_valori_test_medio = []

    matrice_valori_training_min = []
    matrice_valori_test_min = []
    
    features_file_training_max = []
    features_file_training_medio = []
    features_file_training_min = []
    
    features_file_test_max = []
    features_file_test_medio = []
    features_file_test_min = []
    
    training_corpus = []
    test_corpus = []

    #per scalare ogni features bisogna unire tutte le features dei tre documenti riguardanti le tre fasce  
    # avvio quindi un ciclo dove unisco di volta in volta in un unica lista tutte le colonne di una features
    # ovvero in un unico array metto la colonna x(una features) del dizionario di tutti e 3 i file andando quindi
    # a creare un array con 210.000 elementi in quanto ogni fetures del file ha 70.000 elementi che corrispondono
    # alle recensioni
    for x in Dict_max:
        features_da_scalare = Dict_max[x] + Dict_medio[x] + Dict_min[x]
        # trasformo la lista delle features da scalare in un dataframe in quanto la funzione MinMaxScaler.fit deve avere
        # in input un array bidimensionale
        features_da_scalare = pd.DataFrame(features_da_scalare)
        MinMaxScaler = preprocessing.MinMaxScaler()
        scalati = MinMaxScaler.fit_transform(features_da_scalare)
        #scalati è quindi una lista contenente i dati di una colonna di features scalate, la sua struttura è un array di 
        # array dove ogni array dentro l'array scalati è un array con un solo elemento, ovvero il valore della feature
        # scalata
        #creo una lista a una dimensione contenente tutta una colonna di features scalate
        for numero in scalati:
            lista_scalati.append(numero[0])
        #ora ho una lista ad una dimensione che contiene un' intera colonna, quindi una features, completamente scalata
        # per poter creare il training corpus ed il test corpus dovrò avere per entrambi un array di array. L'array
        # principale dovrà contenere al suo interno tanti array quante sono le recensioni, ogni array interno dovrà
        # avere tutti i valori delle features scalate per quella recensione.
        #Per fare ciò parto dividendo la lista scalati in 3 gruppi che corrispondono ai valori delle features divisi 
        # per fasce di prezzo del ristorante. Questa divisoine mi porterà ad avere 70.000 alementi per ogni fascia.
        #Siccome si è scelto di dividere il corpus esattamente a metà tra training corpus e test corpus, dovrò
        # dividere ulteriormente questi 70.000 elementi in due gruppu, i primi 35.000 vanno a formare il training,
        # i secondi vanno a formare il test. Questo viene fatto per ogni feature.
        matrice_valori_training_max.append(lista_scalati[0:35000])    
        matrice_valori_training_medio.append(lista_scalati[70000:105000])
        matrice_valori_training_min.append(lista_scalati[140000:175000])
        
        matrice_valori_test_max.append(lista_scalati[35000:70000])
        matrice_valori_test_medio.append(lista_scalati[105000:140000])
        matrice_valori_test_min.append(lista_scalati[175000:210000])
        
        #Fatto questo io avrò 6 matrici(nel caso in cui prenda solo max e min ne avrò 4),
        # ogniuna contiene tutte lefeatures scalate per training e test corpus divise per file
        lista_scalati = []
    #Le matrici saranno qundi commposte da 142 array, ovvero un array per ogni features. Gli array interni avranno
    # 35.000 elementi, ovvero i valori di quella features. Non sono 70.000(ovvero il numero di recensioni per ogni fascia)
    # perché si è scelto di dividere in due parti uguali training e test corpus

    #A questo punto bisogna creare il training corpus e il test corpus
    #Devo creare un array che contenga un array per ogni recensione, questo array avrà tutti i valori delle features
    # scalate per quella recensione
    #Il primo ciclo for serve per scorrere tutti i valori in un unica colonna
    for y in range(len(matrice_valori_training_max [0])):
        #il secondo serve per scorrere le colonne
        for x in range(len(matrice_valori_training_max)):
            #così facendo prendo gli elementi per riga in quanto inizialmente y = 0 e x = 0
            # per 142 vole x aumenterà e y sarà uguale a zero riuscendo a prendere tutte le features dello stesso file
            #features_file_training_max.append(matrice_valori_training_max[x][y])
            features_file_training_medio.append(matrice_valori_training_medio[x][y])
            features_file_training_min.append(matrice_valori_training_min[x][y])
        #appendo il file con le features di un documento
        #training_corpus.append(features_file_training_max)
        training_corpus.append(features_file_training_medio)
        training_corpus.append(features_file_training_min)
        #svuoto gli array così da poterli riempire con le features della recensione successiva
        #features_file_training_max = []
        features_file_training_medio = []
        features_file_training_min = []

    #stesso meccanismo di quello sopra ma applicato al test corpus
    for y2 in range(len(matrice_valori_test_max[0])):
        for x2 in range(len(matrice_valori_test_max)):
            #features_file_test_max.append(matrice_valori_test_max[x2][y2])
            features_file_test_medio.append(matrice_valori_test_medio[x2][y2])
            features_file_test_min.append(matrice_valori_test_min[x2][y2])
        #test_corpus.append(features_file_test_max)
        test_corpus.append(features_file_test_medio)
        test_corpus.append(features_file_test_min)
        #features_file_test_max = []
        features_file_test_medio = []
        features_file_test_min = []
    return training_corpus, test_corpus

def classificatore (training_corpus, test_corpus):
    print("\n\n\n")
    print("Inizio classificatore...")
    #random.shuffle(test_corpus)
    lista_classi = []
    #35.000 perché deve essere lungo quanto il training corpus che è 70.000. 35.000 perché inserisco 2 elementi
    for x in range(35000):
        lista_classi.append(0)
        lista_classi.append(2)
    print("Eventi: ",len(training_corpus))
    print("Classi: ",len(lista_classi))
    print("Test corpus: ", len(test_corpus))
    clf = svm.SVC(kernel='linear', random_state=0, verbose=True)
    clf.fit(training_corpus,lista_classi)
    predict = clf.predict(test_corpus)
    #score_decision = clf.decision_function(test_corpus)
    print("Predict: \n", predict)
    for x in predict:
        print(x)
    cl_0 = 0
    cl_1 = 0
    cl_2 = 0
    for num in predict:
        if num == 0:
            cl_0 = cl_0 + 1
        else:
            cl_2 = cl_2 + 1
    
    print("Accuratezza: ",metrics.accuracy_score(lista_classi, predict))
    print("Numero classi 0: ", cl_0)
    print("Numero classi 2: ", cl_2)

    scores = cross_val_score(clf,training_corpus, lista_classi, cv=StratifiedKFold(5, shuffle= True, random_state = 0), scoring="accuracy")
    print("Accuratezza 2 = %0.2f" % scores.mean())
    
    f_score = f1_score(lista_classi, predict, average = 'macro')
    print("f_score = ", f_score)

    precision_recall_fscore = precision_recall_fscore_support(lista_classi, predict, average = 'macro')
    print("Precision, recall, fscore = ", precision_recall_fscore)
    
    #precision = average_precision_score(lista_classi,predict)
    #print("Precision = ", precision)
    
    #recall = recall_score(lista_classi, predict)
    #print("Recall = ", recall)
    
    print("\n\n")
    print(clf.coef_[0])
    '''forest = ExtraTreesClassifier(n_estimators=1000, random_state=0)
    forest.fit(training_corpus, lista_classi)'''
    return clf.coef_[0]

def importanza_features(coef, nomi_colonne):
    nomi_colonne.pop(0)
    rankingTotFeat = []
    importanza_feat = []
    for i in coef:
        importanza_feat.append(i)
    print("\n\n")
    #indici = np.argsort(importanza_feat)[::-1]
    dict_features = {}
    for c in range(len(nomi_colonne)):
        dict_features[nomi_colonne[c]] = importanza_feat[c]  
        #rankingTotFeat.append(c + 1, nomi_colonne[c], indici[c])
    dict_features = sorted(dict_features.items(), key=lambda x: x[1])
    for x in dict_features:
        print(x)



def main():
    Dict_max = crea_dizionario(fileMax)
    Dict_medio = crea_dizionario(fileMedio)
    Dict_min = crea_dizionario_min(fileMin)
    Dict_min = controlla_dizionario(Dict_max, Dict_medio, Dict_min)
    training_corpus, test_corpus = crea_corpus(Dict_max, Dict_medio, Dict_min)
    coef = classificatore(training_corpus, test_corpus)
    importanza_features(coef, nomi_colonneMax)
    

if __name__ == "__main__":
    main()