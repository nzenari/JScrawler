# Crawler
Progetto del corso "Analisi dei sistemi informatici", Laurea magistrale "Ingegneria e scienze informatiche", 
Università degli studi di Verona.

## Obiettivo
L'obiettivo del progetto è raccogliere codice JavaScript considerato malevolo attraverso l'esplorazione del web.
Il progetto si avvale di:
* *HpHosts*, un repository di URL ritenuti malevoli da una comunità che viene aggiornato
quotidiamente;
* *Virus Total*, un servizio online di scansione degli URL;
* *Google Safe Browsing*, un servizio che permette di verificare se un URL è da considerarsi malevolo o meno.

## Funzionalità
Il progetto provvede a:
* collezionare gli URL considerati malevoli da *HpHosts*
* effettuare il *crawling* di tali URL
* estrarre il codice JavaScript dalle pagine correttamente scaricate
* interrogare *Virus Total* e *Google Safe Browsing* per etichettare i siti web.

## Requisiti
* Python 3.x
* Librerie Python:
    * json
    * bs4
    * requests
    * warc3
    * gzip
* Chiavi API di Virus Total
* Chiavi API di Google Safe Browsing

## File di configurazione
Prima di avviare il progetto è necessario modificare correttamente il file di configurazione *config.json* sulla
base delle personali necessità. Affinché *Virus Total* e *Google Safe Browsing* funzionino correttamente, è
necessario inserire le proprie chiavi API.

## Comandi per l'esecuzione
1. python3.x getHosts.py
2. avviare *Heritrix*:
    1. $HERITRIX_HOME/bin/heritrix -a utente:password;
    2. copiare il file seeds.txt contentuto nella cartella di out all'interno della cartella del job di *Heritrix*;
    3. avviare il job
3. python3.x warcExtractor.py -s *percorso_al_file_warc_creato_da_heritrix*
4. python3.x jsExtractor.py
5. python3.x vt.py
6. python3.x gsb.py
7. per avere le statistiche:
    1. python3.x vtStata.py
    2. python3.x gsbStata.py
    3. python3.x evalStata.py
    
## Risultati finali
Tutti i risultati sono contenuti all'interno della cartella **out**. Tale directory è così organizzata:
* **out**
    * *seeds.txt*: host riga per riga
    * **gsb**
        * *body0.json*: file necessario a gsb.py per interrogare Google Safe Browsing
        * ...
    * **hosts**
        * **hostname_0**
            * *info.json*: contiene tutte le informazioni relative all'host
            * **heritrix**
                * *files*: tutti i file scaricati da *Heritrix*
                * **javascript**
                    * *files*: tutti i file JavaScript estratti
        * **hostname_1**
            * ...
        * ...
    
## Autori
* Valentina Ceoletta - valentina.ceoletta@studenti.univr.it
* Mattia Zanotti - mattia.zanotti@studenti.univr.it
* Nicolò Zenari - nicolo.zenari@studenti.univr.it