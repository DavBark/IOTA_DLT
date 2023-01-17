# IOTA_DLT
## Aufgabenbeschreibung
Erstellen Sie ein Programm, dass die benötigten Daten anhand der übergebenen TransportId aus dem IOTATangle ausliest 
und die Einhaltung der drei Bedingungen:
- „Stimmigkeit der Kühlketteninformationen“
- „Zeiträume ohne Kühlung“ 
- und „Transportdauer“ überprüft. 

Das Programm soll dem Anwender die Information zurückgeben, ob alle Bedingungen an die Kühlkette erfüllt wurden oder nicht.
Falls nicht, soll eine eindeutige Fehlerbeschreibung ausgegeben werden.


## Scenario
Der Hersteller „Food Solution Hildesheim“ des Dönerspießes bietet seinen Endkunden eine 
zertifizierte Kühlkette für alle Produkte an. Diese kann vom Endkunden leicht über einen QR-Code 
abgefragt werden. 

- Jeder Dönerspieß bekommt vom Logistikunternehmen eine **eindeutige** Identifikationsnummer als QR-Code. 
- Jeder Dönerspieß durchläuft während des Transports verschiedene Stationen in der Kühlkette. 


## Beispiel:
Ein beispielhafter Transportweg könnte folgendermaßen aussehen: 

- Der Kühltransporter (KT) holt die Ware ab und transportiert sie zum
- lokalen Kühlhaus im Güterverteilzentrum (GVZ) 
- Ein Kühltransporter (KT) bringt die Ware in ein  
- Güterverteilzentrum (GVZ) in der Nähe desEndkunden 
- Ein Kühltransporter (KT) bringt die Ware zum Endkunden.  


## Weitere Infos
Der Endkunde kann die Einhaltung der Kühlkette  berprüfen, indem er den QR-Code einscannt.
