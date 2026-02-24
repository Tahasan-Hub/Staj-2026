#Dictionary
###Telefon Rehberi
tel_rehber = {}

tel_rehber["Ali"] = "0541 486 8596"
tel_rehber["Zeynep"] = "0536 456 7891"
tel_rehber["Taha"] = "0523 125 4586"
tel_rehber["Osman"] = "548 741 4263"
tel_rehber["Buse"] = "0512 236 1425"

#print(tel_rehber)



#Silme işlemi
del tel_rehber["Osman"]
#print(tel_rehber)



#Güncelleme işlemi
tel_rehber.update({
    "Ali":"0543 856 7182",
    "Yusuf":"0536 695 1838"
})
#print(tel_rehber)

#Hepsini beraber bastırma...2 yöntem var!

#Yöntem 1
#print(tel_rehber)

#Yöntem 2
#Bu for döngüsünü ilk çalıştırdığımda items yazmamıştım ve hata aldım.Hatanın sebebini bana GEMİNİ söyledi.
for isim,numara in tel_rehber.items():
    print(f"İsim:{isim}   Numara:{numara}")


###Öğrenci Not Sistemi
not_sistemi = {}

not_sistemi["Taha"] = [50,60,70]
not_sistemi["Elif"] = [80,90,60]
not_sistemi["Hakan"] = [40,80,75]
not_sistemi["Ayşe"] = [70,90,20]
not_sistemi["Mustafa"] = [45,95,85]

#print(not_sistemi)

for isim,notlar in not_sistemi.items():
    toplam = sum(notlar)

    ort = toplam / len(notlar)

    print(f"{isim} adlı öğrencinin ortalaması {ort:.2f}") # .2f ile ortalamada virgülden sonra sadece 2 rakamı gösterecek!



#KELİME SAYACI

cumle = "Python Java C# C# Python Java HTML CSS PHP HTML Java Python C# CSS CSS SQL HTML SQL"
kelime_sayac = {}
yeni = cumle.split()#Split kullanarak cümleyi kelimelere böldük.parantez içinin boş olması space boşluktan böl demek yani.
for kelime in yeni:
    kelime_sayac[kelime] = kelime_sayac.get(kelime , 0) + 1
print(kelime_sayac)    










