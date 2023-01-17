# ETS2021 | Gruppenmitglieder: David Barkmeyer, Luca Görke, Leo Drees, Matthias Grafe, Pascal Hartmann und Daniel Winner | 17.01.2023 
# Bearbeiter: Matthias Grafe und Pascal Hartmann
"""
Aufgabenstellung:
    - Überschreitet die Gesamttransportdauer 48 h? 
"""
#---------------| v. 1.0 |---------------#
import iota_client
from datetime import datetime
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
print(target)