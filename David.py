# ETS2021 | Gruppenmitglieder: David Barkmeyer, Luca Görke, Leo Drees, Matthias Grafe, Pascal Hartmann und Daniel Winner | 17.01.2023 
# Bearbeiter: David Barkmeyer und Leo Drees
"""
Aufgabenstellung:
    - Gibt es für jede Transportstation jeweils einen Eintrag für das Ein-bzw. Auschecken? 
    - Sind die Einträge zeitlich sinnvoll geordnet?  
"""
#---------------| v. 1.0 |---------------#
from ctypes.wintypes import tagMSG
import datetime
import iota_client
#from datetime import datetime
import json

transportID = 72359278599178561029675
target=[]

client = iota_client.Client(
    nodes_name_password= [['https://api.lb-0.h.chrysalis-devnet.iota.cafe']])   # Link

messages = client.find_messages(indexation_keys=['Food Solution Hildesheim'])   # indexation = der Message search key
# Schleife über alle gefundenen Messages


for messageRead in messages:
    message=messageRead['payload']['indexation'][0]['data']
    messageUTF8 = ''.join(chr(val) for val in message)
    messageJSON=json.loads(messageUTF8)
    if int(messageJSON['transportid'])==transportID:
        target.append(messageJSON)

timestamps = []
for timeStamp in target:
    timestamps.append(timeStamp['timestamp'])

#print(timestamps)

timestamps.sort()
#print(timestamps)
erster_tag = timestamps[0][:2]
erster_monat = timestamps[0][3:5]
erster_jahr = timestamps[0][6:10]
erster_stunde = timestamps[0][11:13]
erster_minute = timestamps[0][14:16]
erster_sekunde = timestamps[0][17:]


letzte_tag = timestamps[-1][:2]
letzte_monat = timestamps[-1][3:5]
letzte_jahr = timestamps[-1][6:10]
letzte_stunde = timestamps[-1][11:13]
letzte_minute = timestamps[-1][14:16]
letzte_sekunde = timestamps[-1][17:]

from datetime import date

dt1 = datetime.datetime(int(erster_jahr),int(erster_monat),int(erster_tag),int(erster_stunde),int(erster_minute),int(erster_sekunde)) 
dt2 = datetime.datetime(int(letzte_jahr),int(letzte_monat),int(letzte_tag),int(letzte_stunde),int(letzte_minute),int(letzte_sekunde))
print(dt1, " | ", dt2) 
tdelta = dt2 - dt1 

Anzahl_tage = str(tdelta)[:1]
if Anzahl_tage >= '2':
    print("Zeit überschritten")

else:
    print("Zeit eingehalten")