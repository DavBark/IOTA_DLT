# ETS2021 | Gruppenmitglieder: David Barkmeyer, Luca Görke, Leo Drees, Matthias Grafe, Pascal Hartmann und Daniel Winner | 17.01.2023 
# Bearbeiter: David Barkmeyer und Leo Drees
"""
Aufgabenstellung:
    - Gibt es für jede Transportstation jeweils einen Eintrag für das Ein-bzw. Auschecken? 
    - Sind die Einträge zeitlich sinnvoll geordnet?  
"""
#---------------| v. 1.0 |---------------#
import iota_client
from datetime import datetime
import json
from termcolor import colored

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

client = iota_client.Client(
    nodes_name_password= [['https://api.lb-0.h.chrysalis-devnet.iota.cafe']])   # Link

# ---- Datensätze empfangen

messages = client.find_messages(indexation_keys=['Food Solution Hildesheim'])   # indexation = der Message search key

# ---- Alle IDs durcharbeiten

for transportID in transportIDs:

    # reset/set für jede neue ID
    target=[]
    failText=[[],[],[]]
    invalidDirection=False
    invalidCooling=False
    invalidDuration=False
    invalidID=False
    count = 0
    checkOutTimedate=0
    checkInTimedate=0

    # durchsuche alle Datensätze und füge die Datensätzte mit der benötigten ID in die target Liste ein
    for messageRead in messages:
        message=messageRead['payload']['indexation'][0]['data']
        messageUTF8 = ''.join(chr(val) for val in message)
        messageJSON=json.loads(messageUTF8)
        if int(messageJSON['transportid'])==transportID:
            target.append(messageJSON)

    # sortiere die Datensätze nach Zeit
    def bydatetime(elem):           # Funktion für die Sortierung nach timestamp
        return elem['timestamp']
    target.sort(key=bydatetime)     # Sortiere nach der Funktion bydatetime



    if target!=[]:                  # sind Datensätze der zu überprüfenden ID zugeordnet?

        for targetValid in target:  # lese jeden Datensatz der ID
        
            if count%2==0:          # Der ein aund Ausgang aus kühlungen ist abwechselnd und fängt mit Eingängen an
                if targetValid['direction']=='in':  # Dadurch muss bei geradem Index die direction in sein
                    
                    if checkOutTimedate !=0:        # hat es schon ein Zeitpunkt für die letzte Auslagerung gegeben?

                                                        # timestamp vom Datensatz, Formatierung des Datensatzes
                        checkInTimedate=datetime.strptime(targetValid['timestamp'],'%d.%m.%Y %H:%M:%S')     # formatiere Timestamp aus datensatz zu einem Zeitpunkt
                        
                        if (checkInTimedate-checkOutTimedate).total_seconds()>(maxMinutesOutFridge*60):     # prüfe ob der Auslagerungszeitpunkt einen größeren abstand als gewünscht zur nächsten Einlagerung hat
                            invalidCooling=True
                            failText[1].append(str(int((checkInTimedate-checkOutTimedate).total_seconds()-maxMinutesOutFridge*60))+'s before '+ str(targetValid['transportstation']))


                else:               # ist der Index gerade aber die direction ist nicht in gibt es einen Fehler bei Ein und Auslagern
                    invalidDirection=True
                    failText[0].append(str('missing In at '+targetValid['transportstation']))
                    count+=1


            else:                   # für Ausgänge muss der Index in der Liste ungerade sein
                if targetValid['direction']=='out':
                    checkOutTimedate=datetime.strptime(targetValid['timestamp'],'%d.%m.%Y %H:%M:%S')    # letzten Auslagerungszeitpunkt überschreiben
                    
                else:               # ist der Index ungerade aber die direction ist nicht out gibt es einen Fehler bei Ein und Auslagern
                    invalidDirection=True
                    failText[0].append(str('missing Out at '+targetValid['transportstation']))
                    count+=1

            
            count+=1

        
    # ---- Gesamttransportdauer prüfen
        firstInFridge=datetime.strptime(target[0]['timestamp'],'%d.%m.%Y %H:%M:%S')     # wandel timestamp vom ersten Event zu einem Zeitpunkt um
        lastOutFridge=datetime.strptime(target[-1]['timestamp'],'%d.%m.%Y %H:%M:%S')    # wandel timestamp vom letzten Event zu einem Zeitpunkt um

        if (lastOutFridge-firstInFridge).total_seconds()>(maxHoursTransportDuration*60*60):     # liegt zwischen dem ersten und letztm Event mehr als gewünscht?
            invalidDuration=True

        #if invalidDirection or invalidCooling or invalidDuration:
            #print(target)

    else:
        invalidID=True

    # --- Ausgabe des Ergebnisses der Überprüfung

    if not invalidDirection and not invalidCooling and not invalidDuration  and not invalidID:   # keine Fehler gefunden
        print(colored('ID: '+str(transportID)+u' \u2705','green'))
    else:
        print(colored('ID: '+str(transportID)+ u' \u274c ','red'),end= '')
        if invalidDirection:    # fehler in der Ein und Auslagerungs reihenfolge
            print(colored(' | '+str(failText[0])[1:-1].replace("'",""),'red'),end='')
        if invalidCooling:      # fehler durch zulange ohne kühlung zwischen Kühlungen
            print(colored(' | no cooling over 10 min for '+str(failText[1])[1:-1].replace("'",""),'red'),end='')
        if invalidDuration:     # fehler durch Überschreitung der gesamt Transportdauer
            print(colored(' | invalid Duration','red'),end='')
        if invalidID:           # unbekannte ID
            print(colored(' | ID not found','red'),end='')
        print(colored(' | ','red'))

    
    