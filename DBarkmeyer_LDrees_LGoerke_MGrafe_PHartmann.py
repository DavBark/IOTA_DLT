# ETS2021 | Gruppenmitglieder: David Barkmeyer, Luca Görke, Leo Drees, Matthias Grafe, Pascal Hartmann und Daniel Winner | 17.01.2023 - 13.02.2023
"""
Folgende Kriterien sind für die Einhaltung der Kühlkette zu überprüfen:

    o Stimmigkeit der Kühlketteninformationen
         Gibt es für jede Transportstation jeweils einen Eintrag für das Ein-bzw. Auschecken?
         Sind die Einträge zeitlich sinnvoll geordnet?

    o Zeiträume ohne Kühlung
         Überschreitet die Zeit zwischen dem Auschecken aus einer Transportstation und dem Einchecken in die darauffolgende 10 min?

    o Transportdauer
         Überschreitet die Gesamttransportdauer 48 h?
"""
#---------------| v. 2.1 |---------------#

import iota_client
from datetime import datetime
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

richtig=0
unbekannt=0
falsch=0

# ---- Log Tabelle für Überprüfungsergebnis erstellen inkl. Zeitstempel in dem Dateinamen

timestamp=datetime.now()
timestamp=timestamp.strftime('%d-%m-%y_%H-%M-%S')       # Zeitstempel für Erstellung des Logs
logDat = open(str('log_'+timestamp+'.csv'),'x')    # wird im Projektordner abgespeichert

    # Titelzeile für CSV Tabelle
logDat.writelines('ID,i.O.,Unbekannte ID,48h gesamt Lieferzeit überschritten,10 min ohne Kühlung überschritten,Reihenfolge Problem\n')

client = iota_client.Client(
    nodes_name_password= [['https://api.lb-0.h.chrysalis-devnet.iota.cafe']])

# ---- Datensätze empfangen

print('\nDatensätze werden gesucht....',end='\n\n')

messages = client.find_messages(indexation_keys=['Food Solution Hildesheim'])   # indexation = der Message search key


print(str(len(messages))+' Datensätze gefunden', end='\n\n')

# ---- Sortierfunktionen

def bydatetime(elem):           # Funktion für die Sortierung nach timestamp
    return elem['timestamp']
def byDirection(elem):           # Funktion für die Sortierung nach direction
    return elem['direction']

# ---- Alle IDs durcharbeiten

for transportID in transportIDs:

    # reset/set vin Parametern für jede neue ID
    target=[]
    failText=[[],[],[]]
    invalidDirection=False
    invalidCooling=False
    invalidDuration=False
    invalidID=False
    count = 0
    checkOutTimedate=0
    checkInTimedate=0
    letztestation=''

    # durchsuche alle Datensätze und füge die Datensätzte mit der benötigten ID in die target Liste ein
    for messageRead in messages:
        message=messageRead['payload']['indexation'][0]['data']
        messageUTF8 = ''.join(chr(val) for val in message)
        messageJSON=json.loads(messageUTF8)
        if int(messageJSON['transportid'])==transportID:
            target.append(messageJSON)

    # sortiere die Datensätze nach Zeit
    target.sort(key=byDirection,reverse=True)   # Sortiere nach der Direction
    target.sort(key=bydatetime )     # Sortiere nach der Funktion bydatetime

    if target!=[]:                  # sind Datensätze der zu überprüfenden ID zugeordnet?

        for targetValid in target:  # lese jeden Datensatz der ID
        
            if count%2==0:          # Der ein aund Ausgang aus kühlungen ist abwechselnd und fängt mit Eingängen an
                if targetValid['direction']=='in':  # Dadurch muss bei geradem Index die direction in sein
                    letztestation=targetValid['transportstation']
                    if checkOutTimedate !=0:        # hat es schon ein Zeitpunkt für die letzte Auslagerung gegeben?

                                                        # timestamp vom Datensatz, Formatierung des Datensatzes
                        checkInTimedate=datetime.strptime(targetValid['timestamp'],'%d.%m.%Y %H:%M:%S')     # formatiere Timestamp aus datensatz zu einem Zeitpunkt
                        
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

    if not invalidDirection and not invalidCooling and not invalidDuration  and not invalidID:   # keine Fehler gefunden
        logDat.writelines(str(transportID)+','u' \u2705'+"\n")
        print("\033[0;32m"+'ID: '+str(transportID)+u' \u2705')
        richtig+=1

    elif invalidID:
        logDat.writelines(str(transportID)+',' u' \u2753,ID unbekannt\n')
        print("\033[0;33mID: "+str(transportID)+"\033[1;33m ? \033[0;33m | unbekannte ID")
        unbekannt+=1

    else:
        logDat.writelines(str(transportID)+',' u' \u274c,')
        print("\033[0;31m"+'ID: '+str(transportID)+ u' \u274c',end= '')

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
            logDat.writelines(','+str(str(failText[0])[1:-1].replace("'","")+'\n').replace(',',' |'))
            print("\033[0;31m"+' | '+str(failText[0])[1:-1].replace("'",""),end='')
        else:
            logDat.writelines(',\n')

        print("\033[1;31m"+' | ')
        falsch+=1


logDat.close()
print('\n\033[0;32mIn Ordnung: ' + str(richtig)+'\033[0;33m Unbekannt: '+str(unbekannt)+'\033[0;31m Fehlerhaft: '+ str(falsch))

    
    