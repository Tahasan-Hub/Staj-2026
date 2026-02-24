import random
import time
import math

def mesafe_hesapla(p1,p2):
    x_fark = p2[0] - p1[0]
    y_fark = p2[1] - p2[1]

    toplam = (x_fark **2) + (y_fark **2)

    karekok = math.sqrt(toplam)
    
    return karekok

nesne={
    "Araba":(100,200),
    "Kisi":(300,150),
    "Top":(50,50)
}

for tur in range(1,11):
    print(f"\n-- {tur}. Tur--")

    for nesne_adi,eski_konum in nesne.items():
        dx=random.randint(-30,30)
        dy=random.randint(-30,30)

        yeni_x = eski_konum[0] + dx
        yeni_y = eski_konum[1] + dy
        yeni_konum = (yeni_x , yeni_y)

        mesafe = mesafe_hesapla(eski_konum,yeni_konum)

        if mesafe < 10:
            durum = "Hareketsiz"
        else:    
            durum = "Hareket Ediyor"

        print(f"{nesne_adi} nesnesi {mesafe} birim hareket etti.Durum: {durum}")

        nesne[nesne_adi] = yeni_konum

        time.sleep(1)    


