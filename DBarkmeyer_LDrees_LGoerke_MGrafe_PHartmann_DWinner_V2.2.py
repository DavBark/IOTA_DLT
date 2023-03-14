# ETS2021 | Gruppenmitglieder: David Barkmeyer, Luca Görke, Leo Drees, Matthias Grafe, Pascal Hartmann und Daniel Winner | 14.02.2023 - 14.03.2023
"""
Folgende Kriterien sind für die Einhaltung der Kühlkette zu überprüfen:

    o Stimmigkeit der Kühlketteninformationen
         Gibt es für jede Transportstation jeweils einen Eintrag für das Ein-bzw. Auschecken?
         Sind die Einträge zeitlich sinnvoll geordnet?

    o Zeiträume ohne Kühlung
         Überschreitet die Zeit zwischen dem Auschecken aus einer Transportstation und dem Einchecken in die darauffolgende 10 min?
         Temperaturüberwachung der Kühlstationen

    o Transportdauer
         Überschreitet die Gesamttransportdauer 48 h?

    o Verschlüsselung
         Verschlüsselung der Daten auf dem Tangle     

    o Reparationszahlung
         Reparationszahlung bei Verletzung der Kühlkette

"""
#---------------| v. 2.2 |---------------#
import iota_client
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import time
import json



transportIDs = [72359278599178561029675,
                15668407856331648336231,
                73491878556297128760578,
                99346757838434834886542,
                46204863139457546291334,
                77631003455214677542311,
                34778534098134729847267,
                64296734612883933474299,
                84356113249506843372979,
                23964376768701928340034,
                55638471099438572108556,
                84552276793340958450995,
                96853785349211053482893,
                68345254400506854834562,
                67424886737245693583645,
                85746762813849598680239,
                56993454245564893300000,
                95662334024905944384522,
                13456783852887496020345,
                76381745965049879836902]

maxMinutesOutFridge=10
maxHoursTransportDuration=48
tempKuehlhausMax=4.0
tempKuehlhausMin=2.0
tempkuehlhausTiming=15

richtig=0
unbekannt=0
falsch=0

# ---- Log Tabelle für Überprüfungsergebnis erstellen inkl. Zeitstempel in dem Dateinamen

timestamp=datetime.now()
timestamp=timestamp.strftime('%d-%m-%y_%H-%M-%S')       # Zeitstempel für Erstellung des Logs
logDat = open(str('log_'+timestamp+'.csv'),'x')    # wird im Projektordner abgespeichert

    # Titelzeile für CSV Tabelle
logDat.writelines('ID,i.O.,Unbekannte ID,48h gesamt Lieferzeit überschritten,10 min ohne Kühlung überschritten,Reihenfolge Problem,Kühltemperatur fehlerhaft\n')

client = iota_client.Client(
    nodes_name_password= [['https://api.lb-0.h.chrysalis-devnet.iota.cafe']])

# ---- Datensätze empfangen

print('\nDatensätze werden gesucht....',end='\n\n')

messages = client.find_messages(indexation_keys=['Food Solution Hildesheim encrypted'])   # indexation = der Message search key
messageDecrypted=[]

print(str(len(messages))+' Datensätze gefunden', end='\n\n')

# ---- Sortierfunktionen

def bydatetime(elem):            # Funktion für die Sortierung nach timestamp
    return elem['timestamp']
def byDirection(elem):           # Funktion für die Sortierung nach direction
    return elem['direction']

def decryptTangle():
    '''Verschlüsselte Tangles entschlüsseln'''
    key = b'mysecretpassword'
    iv = b'passwort-salzen!'

    for messageDecrypt in messages:
        message=bytes(messageDecrypt['payload']['indexation'][0]['data'])
        cipher = AES.new(key, AES.MODE_CBC, iv)
        dataDecrypted = unpad(cipher.decrypt(message), AES.block_size)
        dataDecrypted=dataDecrypted.decode("utf8")
        messageJSON=json.loads(dataDecrypted)
        messageDecrypted.append(messageJSON)


def kuehltemp(kuehlhaus,checkInTime,checkOutTime):
    '''
    Prüfen ob in dem kuehlhaus(str) zwischen checkInTime(timetuple) und checkOutTime(timetuble) die Kühltemperatur die Grenzen nicht verlassen hat

    return(Liste) mit Fehlertexten
    '''
    target=[]
    failtextTemp=[]
    messages = client.find_messages(indexation_keys=[kuehlhaus])
    for messageRead in messages:
        message=messageRead['payload']['indexation'][0]['data']
        messageUTF8 = ''.join(chr(val) for val in message)
        messageJSON=json.loads(messageUTF8)
        target.append(messageJSON)
    target.sort(key=bydatetime)
    for targetTemp in target:
        targetTempTimestamp=datetime.strptime(targetTemp['timestamp'],'%d.%m.%Y %H:%M:%S')
        if (targetTempTimestamp-checkInTimedate).total_seconds()>=tempkuehlhausTiming*60-1 and (targetTempTimestamp-checkOutTimedate).total_seconds()<=tempkuehlhausTiming*60+1:
            if targetTemp['temperature']<tempKuehlhausMin or targetTemp['temperature']>tempKuehlhausMax:
                failtextTemp.append(str(str(targetTemp['temperature'])+u'\xb0''C um '+str(targetTempTimestamp.strftime('%H:%M:%S'))+' bei '+kuehlhaus))
    return failtextTemp


def checkMoney(DEBUG=False):
    '''
    Prüfen, wie viel Geld sich auf den Konten befindet
    
    DEBUG=Bool / wenn true wird im Terminal Debug ausgegeben
    '''
    # Seed zum Signieren der Transaktion (selbst generiert)
    LOGISTIK_IOTA_SEED_SECRET = "71ba735e4957cf56d2c498e8a06e3ed534b022529220c90403b0a52ed5d6179a"
    FOODSOLUTION_SEED_SECRET = "b397d3b1e214e20c247daa6fd9cb0ab0a1d9dc76d73babe05eb7d6b28c8fc2e3"

    # Client-Objekt erzeugen
    client = iota_client.Client()
    # Kontostand für die Seeds abfragen
    LOGISTIK_balance = client.get_balance(seed=LOGISTIK_IOTA_SEED_SECRET, account_index=0,
    initial_address_index=0) / 1000000
    
    FOODSOLUTION_balance = client.get_balance(seed=FOODSOLUTION_SEED_SECRET, account_index=0,
    initial_address_index=0) / 1000000
    

    # Ausgabe Deebug
    if DEBUG:
        print()
        print('----------------------------------------------------------------------------------')
        print("Kontostand Logistikunternhemen: ", LOGISTIK_balance, " MIOTA")
        print("Kontostand FoodSolution GmbH: ", FOODSOLUTION_balance, " MIOTA")
        print('----------------------------------------------------------------------------------') 

    return [FOODSOLUTION_balance, LOGISTIK_balance]


def sendMoneyback(DEBUG=False):
    '''
    Sendet vorhandenes Geld wieder zurück aufs Logistik Konto.
    Für Testzwecke, damit das Konto des Logistikunternehmen einen Geldbetrag besitzt.
    
    DEBUG=Bool / wenn true wird im Terminal Debug ausgegeben
    '''
    kontostand_FS = int(checkMoney()[0])
    print("Sende alles vohandene Geld des Foot Solution Konto auf das Logistik Konto zurück. FÜR TESTZWECKE!")
    if kontostand_FS > 0: # Prüfen ob Geld zum Zurückschicken vorhanden ist
    
        print("Zurück zum Absender!")
        try:
            # Generierte Seed-Adressen 
            FOODSOLUTION_SEED_SECRET = "b397d3b1e214e20c247daa6fd9cb0ab0a1d9dc76d73babe05eb7d6b28c8fc2e3"
        
            # Generierte Adresse
            LOGISTIK_Adresse = [('atoi1qqr58tqg2xhn4knn6vdf4743j9dvww66ajxz78ku3745ynvenmsgj0hzt27', False), 
            ('atoi1qryd0a66p26qr5t3vlr5xeuw9znxjjld3tfm2k2gce9vn8xuvjaqza3nw28', True)]
            
            # Client-Objekt erzeugen
            client = iota_client.Client()
            # Überweisung druchführen
            message = client.message(
                seed=FOODSOLUTION_SEED_SECRET,
                outputs=[
                    {
                    'address': LOGISTIK_Adresse[0][0],
                    'amount': kontostand_FS * 1_000_000
                    }
                    ]
                )

            # Ausgabe Deebug
            if DEBUG:
                print()
                print ('----------------------------------------------------------------------------------')
                print(message)
                print ('----------------------------------------------------------------------------------') 
            print("Geld Überwiesen")

        except:
            print("Fehler beim Ausführen.")
    else:
        print("Kein Betrag auf dem Food Solution Konto vohanden.")


def sendMoney(Betrag, DEBUG=False):
    '''Sende Geld von Logistikunternehmen nach Foodsolution 
    Betrag=Int / wieviel überwiesen werden soll

    DEBUG=Bool / wenn true wird im Terminal Debug ausgegeben'''
    kontostand_LU = int(checkMoney()[1])
    if kontostand_LU >= Betrag:         # Überprüfen, ob genügend Geld auf dem Konto LogistikUnternhemen ist

        print(f"Betrag von {Betrag} MIOTA wird dem Food Solution Konto überwiesen")
        try:
            # Generierte Seed-Adressen
            LOGISTIK_IOTA_SEED_SECRET = "71ba735e4957cf56d2c498e8a06e3ed534b022529220c90403b0a52ed5d6179a"  
            # IOTA-Adresse von Food Solution
            FOODSOLUTION_Adresse = [('atoi1qq8kky79rcjm6ck70d39t0xnfltzypk43869vslh22crmd2pjkhzv4rx663', False),
            ('atoi1qrp5pnxf0wahme0m6whru2385lxjuw9wu49e5kymymg990x9l4j5yrqkjzt', True)]

            # Client-Objekt erzeugen
            client = iota_client.Client()
            # Überweisung druchführen
            message = client.message(
                seed=LOGISTIK_IOTA_SEED_SECRET,
                outputs=[
                    {
                    'address': FOODSOLUTION_Adresse[0][0],
                    'amount': Betrag*1_000_000
                    } 
                ]
            )

            # Ausgabe Deebug
            if DEBUG:
                print()
                print ('----------------------------------------------------------------------------------')
                print(message)
                print ('----------------------------------------------------------------------------------') 
                
            print("Geld Überwiesen")

        except:
            print("Fehler beim Ausführen")
    else:
        print("Nicht genügend Geld auf dem Logistik Konto")


"""--------------------------------------------------------------------------------------------------"""
#-----------------------------------------| Programm Start |-------------------------------------------#
"""--------------------------------------------------------------------------------------------------"""
checkMoney(True)
sendMoneyback()     # Empfangenes Geld zurück senden um wieder überweisen zu können
print()

decryptTangle()     # Entschlüsselung des Tangels

# ---- Alle IDs durcharbeiten

for transportID in transportIDs:

    # reset/set vin Parametern für jede neue ID
    target=[]
    failText=[[],[],[],[]]
    invalidDirection=False
    invalidCooling=False
    invalidDuration=False
    invalidID=False
    invalidCoolingTemp=False
    count = 0
    checkOutTimedate=0
    checkInTimedate=0
    letztestation=''

    # durchsuche alle Datensätze und füge die Datensätzte mit der benötigten ID in die target Liste ein
    for messageRead in messageDecrypted:
        if int(messageRead['transportid'])==transportID:
            target.append(messageRead)

    # sortiere die Datensätze nach Zeit
    target.sort(key=byDirection,reverse=True)   # Sortiere nach der Direction
    target.sort(key=bydatetime )    # Sortiere nach der Funktion bydatetime

    if target!=[]:                  # sind Datensätze der zu überprüfenden ID zugeordnet?

        for targetValid in target:  # lese jeden Datensatz der ID
        
            if count%2==0:          # Der ein aund Ausgang aus kühlungen ist abwechselnd und fängt mit Eingängen an
                if targetValid['direction']=='in':  # Dadurch muss bei geradem Index die direction in sein
                    letztestation=targetValid['transportstation']
                    checkInTimedate=datetime.strptime(targetValid['timestamp'],'%d.%m.%Y %H:%M:%S')     # formatiere Timestamp aus datensatz zu einem Zeitpunkt
                    
                    if checkOutTimedate !=0:        # hat es schon ein Zeitpunkt für die letzte Auslagerung gegeben?

                                                            # timestamp vom Datensatz, Formatierung des Datensatzes
                        
                        if (checkInTimedate-checkOutTimedate).total_seconds()>(maxMinutesOutFridge*60):     # prüfe ob der Auslagerungszeitpunkt einen größeren abstand als gewünscht zur nächsten Einlagerung hat
                            invalidCooling=True
                            failText[1].append(str(time.strftime('%H:%M:%S', time.gmtime(int((checkInTimedate-checkOutTimedate).total_seconds()-maxMinutesOutFridge*60))))+' bevor '+ str(targetValid['transportstation']))


                else:               # ist der Index gerade aber die direction ist nicht in gibt es einen Fehler bei Ein und Auslagern
                    invalidDirection=True
                    failText[0].append(str('Fehlendes In bei '+targetValid['transportstation']))
                    count+=1


            else:                   # für Ausgänge muss der Index in der Liste ungerade sein
                if targetValid['direction']=='out':
                    if str(letztestation)==str(targetValid['transportstation']):
                        checkOutTimedate=datetime.strptime(targetValid['timestamp'],'%d.%m.%Y %H:%M:%S')    # letzten Auslagerungszeitpunkt überschreiben

                        # print(kuehltemp(letztestation,checkInTimedate,checkOutTimedate))
                        failTextTemp = kuehltemp(letztestation,checkInTimedate,checkOutTimedate)
                        if failTextTemp!=[]:
                            failText[3].append(failTextTemp)
                            if not invalidCoolingTemp:
                                invalidCoolingTemp=True
                        

                        

                    else:
                        failText[0].append(str('Fehlendes Out bei '+letztestation))
                        failText[0].append(str('Fehlendes In bei '+targetValid['transportstation']))
                        invalidDirection=True
                    
                else:               # ist der Index ungerade aber die direction ist nicht out gibt es einen Fehler bei Ein und Auslagern
                    invalidDirection=True
                    failText[0].append(str('Fehelendes Out bei '+targetValid['transportstation']))
                    count+=1

            
            count+=1

        
    # ---- Gesamttransportdauer prüfen
        firstInFridge=datetime.strptime(target[0]['timestamp'],'%d.%m.%Y %H:%M:%S')     # wandel timestamp vom ersten Event zu einem Zeitpunkt um
        lastOutFridge=datetime.strptime(target[-1]['timestamp'],'%d.%m.%Y %H:%M:%S')    # wandel timestamp vom letzten Event zu einem Zeitpunkt um

        if (lastOutFridge-firstInFridge).total_seconds()>(maxHoursTransportDuration*60*60):     # liegt zwischen dem ersten und letztm Event mehr als gewünscht?
            invalidDuration=True
            failText[2]=time.strftime('%H:%M:%S', time.gmtime(int((lastOutFridge-firstInFridge).total_seconds()-maxHoursTransportDuration*60*60)))      # speichern der überschrittenen Zeit

        #if invalidDirection or invalidCooling or invalidDuration:
            #print(target)

    else:
        invalidID=True

    # --- Ausgabe des Ergebnisses der Überprüfung

    if not invalidDirection and not invalidCooling and not invalidDuration  and not invalidID and not invalidCoolingTemp:   # keine Fehler gefunden
        logDat.writelines(str(transportID)+',OK'+"\n")
        print("\033[0;32m"+'ID: '+str(transportID)+' OK')
        richtig+=1

    elif invalidID:
        logDat.writelines(str(transportID)+',Unbekannt,ID unbekannt\n')
        print("\033[0;33mID: "+str(transportID)+" \033[1;33m ? \033[0;33m | unbekannte ID")
        unbekannt+=1

    else:
        logDat.writelines(str(transportID)+',FAIL,')
        print("\033[0;31m"+'ID: '+str(transportID)+ ' FAIL',end= '')

        if invalidDuration:     # fehler durch Überschreitung der gesamt Transportdauer
            logDat.writelines(',um '+str(failText[2])+' überschritten')
            print("\033[0;31m"+' | max 48 Stunden Kühlkette mit '+str(failText[2])+' überschritten',end='')
        else:
            logDat.writelines(',')

        if invalidCooling:      # fehler durch zulange ohne kühlung zwischen Kühlungen
            logDat.writelines(','+str('mit '+str(failText[1])[1:-1].replace("'","")).replace(',',' |'))
            print("\033[0;31m"+' | ohne Kühlung über 10 minuten von '+str(failText[1])[1:-1].replace("'",""),end='')
        else:
            logDat.writelines(',')

        if invalidDirection:    # fehler in der Ein und Auslagerungs reihenfolge
            logDat.writelines(','+str(str(failText[0])[1:-1].replace("'","")).replace(',',' |'))
            print("\033[0;31m"+' | '+str(failText[0])[1:-1].replace("'",""),end='')
        else:
            logDat.writelines(',')

        if invalidCoolingTemp:
            logDat.writelines(','+str(str(failText[3])[2:-2].replace("'","")+'\n').replace(',',' |'))
            print("\033[0;31m"+' | '+str(failText[3])[2:-2].replace("'",""),end='')
        else:
            logDat.writelines(',\n')

        print("\033[1;31m"+' | ')
        falsch+=1


logDat.close()
print('\n\033[0;32mIn Ordnung: ' + str(richtig)+'\033[0;33m Unbekannt: '+str(unbekannt)+'\033[0;31m Fehlerhaft: '+ str(falsch))
sendMoney(falsch)   # Anzahl der zu senden MIOTA auf das Food Solution Konto