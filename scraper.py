import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import sys
from bs4 import BeautifulSoup
import urllib.request
import pandas
import os.path
import re
import csv


# importo il web driver
driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
caratteri_r = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6})|\[\[(?:[^|\]]*\|)?([^\]]*)]];')


# funzione per controllare se xpath esiste
def controlla_path(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def scrape (url):
    driver.get(url)
    lista_recensioni = []
    lista_utenti = []
    lista_like = []
    lista_punteggio_recensione = []
    elimina = "Mostra meno"

    #fascia prezzo ristorante
    time.sleep(1)
    if controlla_path("/html/body/div[2]/div[1]/div/div[4]/div/div/div[2]/span[3]/a[1]"):
        prezzo_cod = driver.find_element_by_xpath("/html/body/div[2]/div[1]/div/div[4]/div/div/div[2]/span[3]/a[1]")
    elif controlla_path("/html/body/div[3]/div[1]/div/div[4]/div/div/div[2]/span[3]/a[1]"):
        prezzo_cod = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div/div[4]/div/div/div[2]/span[3]/a[1]')
    elif controlla_path("/html/body/div[3]/div[1]/div/div[5]/div/div/div[2]/span[3]/a[1]"): 
        prezzo_cod = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div/div[5]/div/div/div[2]/span[3]/a[1]')
    elif controlla_path("/html/body/div[2]/div[1]/div/div[3]/div/div/div[2]/span[3]/a[1]"):
        prezzo_cod = driver.find_element_by_xpath("/html/body/div[2]/div[1]/div/div[3]/div/div/div[2]/span[3]/a[1]")
    else:
        prezzo_cod = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div/div[3]/div/div/div[2]/span[3]/a[1]')                   
    costo = prezzo_cod.text
    for a in range(0,120):
        if (controlla_path("//span[@class='taLnk ulBlueLinks']")):
            # clicco il pulsante per mostrare di più le recensioni
            driver.find_element_by_xpath("//span[@class='taLnk ulBlueLinks']").click()
            time.sleep(2)

        #nomi utenti
        utenti_code = driver.find_elements_by_class_name("member_info")
        for singolo in utenti_code:
            html = singolo.get_attribute("innerHTML")
            if "info_text pointer_cursor" in html:
                fix1 = html.split('<div class="info_text pointer_cursor"')
                fix2 = re.sub(caratteri_r, '', str(fix1[1]))
                nome = fix2.split('>')
                lista_utenti.append(nome[1])
            else:
                lista_utenti.append("Unknown")

        #recensioni
        rec_code = driver.find_elements_by_xpath("//div[@class='quote']/following-sibling::div[@class='prw_rup prw_reviews_text_summary_hsx']")
        for rec in rec_code:
            testo_rec = rec.text
            lista_recensioni.append(testo_rec.replace(elimina, ""))

        #mi piace recensioni
        like_code = driver.find_elements_by_class_name("numHelp")
        for like in like_code:
            if like.text == "":
                like = 0
                lista_like.append(like)
            else:
                lista_like.append(like.text)

        #voti recensioni
        lista_span = driver.find_elements_by_xpath('//*[@class="ui_column is-9"]/child::span')
        for span in lista_span:
            classe = span.get_attribute("class")
            if classe == "ui_bubble_rating bubble_50":
                voto = 5
                lista_punteggio_recensione.append(voto)
            if classe == "ui_bubble_rating bubble_40":
                voto = 4
                lista_punteggio_recensione.append(voto)
            if classe == "ui_bubble_rating bubble_30":
                voto = 3
                lista_punteggio_recensione.append(voto)
            if classe == "ui_bubble_rating bubble_20":
                voto = 2
                lista_punteggio_recensione.append(voto)
            if classe == "ui_bubble_rating bubble_10":
                voto = 1
                lista_punteggio_recensione.append(voto)
        
        driver.find_element_by_class_name('nav.next.ui_button.primary').click()
        time.sleep(1)
    return lista_recensioni, lista_utenti, lista_like, costo, lista_punteggio_recensione
    #driver.quit()
    

def main (url):
    recensioni, utenti, like, costo, lista_punteggio_recensione = scrape(url)
    print(len(utenti))
    print(len(like))
    print(len(costo))
    print(len(lista_punteggio_recensione))
    while len(recensioni) < len(utenti):
        recensioni.append("NONE")
    print(len(recensioni))
    #if len(recensioni) != len(utenti):
    #    recensioni = recensioni[:-1]
    df = pandas.DataFrame(data = {"Nome Autore recensione": utenti,
                                "Costo ristorante": costo,
                                "Recensione": recensioni, 
                                "Like recensione": like,
                                "Punteggio recensione": lista_punteggio_recensione
                                } )
        #controllo che il file non esista già, nel caso esistesse lo aggiorna aggiungengo le informazioni nuove 
    if os.path.isfile('grayfox.csv'):
        df.to_csv("./grayfox.csv", mode='a', sep='\t', index=False, header=False)
    else:
        df.to_csv("./grayfox.csv", sep='\t', index=False, header=False)

    

main(sys.argv[1])
