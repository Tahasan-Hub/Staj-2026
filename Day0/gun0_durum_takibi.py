import time
isik_acilma_zamani = None

while True:
    if isik_acilma_zamani is None:
        şalter = input("Işık şuan KAPALI açmak için 'ac' yaz: ")
    else:
        şalter = input("Işık şuan AÇIK kapatmak için 'kapa' yaz: ")  

    if şalter == "ac":
        if isik_acilma_zamani is None:
            isik_acilma_zamani = time.time()
            print("Işık açıldı! Elektrik Faturasına Dikkat Ediniz!")
        else:
            print("UYARI Işık zaten AÇIK tekrar açamazsın!")

    elif şalter == "kapa":
        if isik_acilma_zamani is not None:
            zaman = time.time() - isik_acilma_zamani
            print(f"Işık {zaman:.1f} saniye açık kaldı!")    
            isik_acilma_zamani = None 
    else:
         print("Hatalı Komut! Lütfen sadece 'ac' ya da 'kapa' yazınız.") 