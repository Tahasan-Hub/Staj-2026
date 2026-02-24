import time
import random

# krono_süre = None

# while True:
#     if krono_süre is None:
#         kmt = input("Kronometre şuan saymıyor.Lütfen başlatmak için 'baslat' yazın yada çıkmak için 'cikis'yazını: ")
#     else:
#         kmt = input("Kronometre şuan sayıyor.Durdurmak için 'durdur' yazınız: ")

#     if kmt == "baslat":
#         if krono_süre is None:
#             krono_süre = time.time()
#             print("Kronometre saymaya başladı!")
#         else:
#             print("Kronometre zaten çalışıyor tekrardan çalıştıramazsın!") 

#     elif kmt == "durdur":
#         if krono_süre is not None:
#             süre = time.time() - krono_süre
#             print(f"Kronometre {süre:.2f} saniye saydı.")
#             krono_süre = None
#         else:
#             print("Kronometre zaten kapalı önce çalıştırmalısın!")    
#     elif kmt == "cikis":
#         print("Kronometreden çıkılıyor...!")
#         break        




print("Hazır ol.'ŞİMDİ BAS' yazısını görünce hemen ENTER tuşuna basınız.")

bekleme_suresi = random.randint(1,15)

time.sleep(bekleme_suresi)

print("ŞİMDİ BAS")

baslangic = time.time()

input()
bitis = time.time()

gecen_sure = bitis - baslangic

print(f"Reaksiyon Süreniz: {gecen_sure:.2f}")



