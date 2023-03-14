# Bibliotheken
import os
import hashlib
from time import sleep
import iota_client

"""LOGISTIK_Adresse = [('atoi1qqr58tqg2xhn4knn6vdf4743j9dvww66ajxz78ku3745ynvenmsgj0hzt27', False), 
('atoi1qryd0a66p26qr5t3vlr5xeuw9znxjjld3tfm2k2gce9vn8xuvjaqza3nw28', True)]

FOODSOLUTION_Adresse = [('atoi1qq8kky79rcjm6ck70d39t0xnfltzypk43869vslh22crmd2pjkhzv4rx663', False),
 ('atoi1qrp5pnxf0wahme0m6whru2385lxjuw9wu49e5kymymg990x9l4j5yrqkjzt', True)]
""" 

def haslib():
    # Seed mit 64 Hex-Stellen erzeugen => 264 Bit
    # 2^64 = 18.446.744.073.709.551.616 = 18.446 Billiarden verschiedene Werte
    rnd_seed = hashlib.sha256(os.urandom(256)).hexdigest()
    # Ausgabe
    print ('----------------------------------------------------------------------------------')
    print ("Seed: ", rnd_seed)
    print ('----------------------------------------------------------------------------------')
    # Seed für Anna und Bob merken
    return rnd_seed

def generateClient():
    LOGISTIK_IOTA_SEED_SECRET = "71ba735e4957cf56d2c498e8a06e3ed534b022529220c90403b0a52ed5d6179a"  
    FOODSOLUTION_SEED_SECRET = "b397d3b1e214e20c247daa6fd9cb0ab0a1d9dc76d73babe05eb7d6b28c8fc2e3"

    IOTA_SEED_SECRET = FOODSOLUTION_SEED_SECRET
    # Client-Objekt erzeugen

    client = iota_client.Client()
    # Iota-Adresse erzeugen

    address_changed_list = client.get_addresses(
    seed=IOTA_SEED_SECRET,
    account_index=0,
    input_range_begin=0,
    input_range_end=1,
    get_all=True
    )

    #Ausgabe
    print ('----------------------------------------------------------------------------------') 
    print("Iota-Adresse: ", address_changed_list)
    print ('----------------------------------------------------------------------------------') # Adressen merken (False=Public-Address, True=Internal Address)

def checkMoney(DEBUG):
    LOGISTIK_IOTA_SEED_SECRET = "71ba735e4957cf56d2c498e8a06e3ed534b022529220c90403b0a52ed5d6179a"  
    FOODSOLUTION_SEED_SECRET = "b397d3b1e214e20c247daa6fd9cb0ab0a1d9dc76d73babe05eb7d6b28c8fc2e3"

    # Client-Objekt erzeugen
    client = iota_client.Client()
    # Kontostand für die Seeds abfragen
    LOGISTIK_balance = client.get_balance(seed=LOGISTIK_IOTA_SEED_SECRET, account_index=0,
    initial_address_index=0) / 1000000
    FOODSOLUTION_balance = client.get_balance(seed=FOODSOLUTION_SEED_SECRET, account_index=0,
    initial_address_index=0) / 1000000
    # Ausgabe
    if DEBUG:
        print("Debug")
        print('----------------------------------------------------------------------------------')
        print("Kontostand Logistikunternhemen: ", LOGISTIK_balance, " MIOTA")
        print("Kontostand FoodSolution GmbH: ", FOODSOLUTION_balance, " MIOTA")
        print('----------------------------------------------------------------------------------') 

    return [FOODSOLUTION_balance, LOGISTIK_balance]

def sendMoneyback(DEBUG): 
 #Sende alles Geld zurück (test Anwendung) 
    kontostand_FS = int(checkMoney(False)[0]*1000000)
    print("Zurück zum Absender")
    if kontostand_FS > 0:
        try:
            #Generierte Seed-Adressen 
            FOODSOLUTION_SEED_SECRET = "b397d3b1e214e20c247daa6fd9cb0ab0a1d9dc76d73babe05eb7d6b28c8fc2e3"

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
                    'amount': kontostand_FS
                    }
                    ]
                )

            if DEBUG:
                # Ausgabe
                print("Debug")
                print ('----------------------------------------------------------------------------------')
                print(message)
                print ('----------------------------------------------------------------------------------') 
            print("Geld Überwiesen")

        except:
            print("Fehler beim Ausführen")
    else:
        print("Kein Betrag auf Food Solution Konto vohanden")

def sendMoney(Betrag, DEBUG): 
    #Sende Geld von Logistikunternehmen nach Foodsolution 
    # Überprüfen, ob genügend geld auf dem Konto LogistikUnternhemen ist
    kontostand_LU = int(checkMoney(False)[1]*1000000)

    print(f"Betrag von {Betrag} MIOTA wird dem Food Solution Konto überwiesen")
    if kontostand_LU >= Betrag:

        try:
            #Generierte Seed-Adressen
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
                    'amount': Betrag*1000000
                    } 
                ]
            )

            if DEBUG:
                # Ausgabe
                print("Debug")
                print ('----------------------------------------------------------------------------------')
                print(message)
                print ('----------------------------------------------------------------------------------') 
            print("Geld Überwiesen")

        except:
            print("Fehler beim Ausführen")
    else:
        print("Nicht genügend Geld auf dem Logistik Konto")



checkMoney(True)
#sendMoneyback(False)
print()
sendMoney(6, False)


print()
sleep(20)
checkMoney(True)

