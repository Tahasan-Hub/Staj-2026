import json

with open("ayarlar.json" , "r" , encoding="utf-8") as dosya: # utf-8 yazma sebebim eğer ayarlar.json dosyasında türkçe karakter varsa abuk sabuk şekilde yazmasın diye onu yazdım.
    veri = json.load(dosya)

print(veri)