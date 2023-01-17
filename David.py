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
print(timestamps[0],"   |   ", timestamps[-1])
print(timestamps[0][:10])
print(timestamps[0][11:])

tag = timestamps[0][:2]
monat = timestamps[0][3:5]
jahr = timestamps[0][6:10]

print(tag, "|", monat, "|", jahr)

from datetime import date


dt1 = datetime.datetime(int(jahr),int(monat),int(tag)) 
dt2 = datetime.datetime(2022,9,6) 
tdelta = dt2 - dt1 
print(tdelta) 
print(type(tdelta)) 
