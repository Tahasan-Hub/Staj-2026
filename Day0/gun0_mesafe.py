import math

def mesafe_hesapla(p1,p2):
    x_fark = p2[0] - p1[0]
    y_fark = p2[1] - p1[1]

    toplam = (x_fark ** 2) + (y_fark ** 2)

    karekok = math.sqrt(toplam)

    return karekok

sonuc1 = mesafe_hesapla((0,0),(3,4))
print(f"Test 1 Sonucu: {sonuc1}")


sonuc2 = mesafe_hesapla((1,1),(4,5))
print(f"Test 2 Sonucu: {sonuc2}")



şehirler = {
    "İstanbul":(28.98,41.01),
    "Ankara":(32.86,39.93),
    "İzmir":(27.12,38.42),
    "Antalya":(30.71,36.89),
    "Sakarya":(30.39,40.77)
}

sec_1 = input("Lütfen 1.şehir ismi giriniz? ")
sec_2 = input("Lütfen 2.şehir ismi giriniz? ")

if sec_1 in şehirler and sec_2 in şehirler:
    şehir_1 = şehirler[sec_1]
    şehir_2 = şehirler[sec_2]
    sonuc = mesafe_hesapla(şehir_1,şehir_2)
    km = sonuc * 111
    print(f"{sec_1} ile {sec_2} arası yaklaşık {km:.2f} km.")
else:
    print("Yanlış şehir ismi girdiniz?")    



hedef = (4,8)
adaylar = [(10,4),(8,1),(1,5),(9,7),(3,6)]

en_yakin_nokta = None
en_kisa_mesafe = float('inf')#Pozitif Sonsuzluk

for aday in adaylar:
    o_anki_mesafe = mesafe_hesapla(hedef,aday)

    if o_anki_mesafe < en_kisa_mesafe: #En küçük mesafeyi arıyoruz!Tüm adaylarda kontrol yapıp en küçüğünü alıyoruz.
        en_kisa_mesafe=o_anki_mesafe

        en_yakin_nokta = aday
print(f"Hedefe en yakın nokta {en_yakin_nokta} en yakın mesafe {en_kisa_mesafe:.3f}")#En yakın mesafede virgülden sonra çok küsurat vardı bu yüzden bunu .3f ile virgülden sonra 3 basamak aldım.        


