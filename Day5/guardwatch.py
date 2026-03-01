import math
import cv2
import json
from ultralytics import YOLO
import os
import mediapipe as mp
import time
import pygame
import logging


logging.basicConfig(filename="guvenlik.log",level=logging.INFO,format = "%(asctime)s - %(message)s") #Log dosyamızın ayarlarını yapıyoruz.(Tarih - Mesaj formatında yazacak)
logging.info("Sistem basladi") #Sistem çalışır çalışmaz ilk kaydımızı düşüyoruz
loglanmis_ihlaller = {} #İhlallerin dosyaya saniyede 30 kez yazılmasını engellemek için hafıza sözlüğü
pygame.mixer.init() #Pygame'in ses motorunu başlatıyoruz (Bunu yapmazsak ses çalışmaz)

alarm_sesi = pygame.mixer.Sound("beep.wav") #Alarmı dosya koduna yükleyip alarm_sesi adını veriyoruz
son_alarm_zamani = 0.0 #Bekleme süresini hesaplamak için son çalma saatini tutacağımız hafıza

def ayarları_yukle(dosya_yolu = "config.json"):
    try:
        with open(dosya_yolu,"r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"yolo_confidence":0.4 , "tracker_max_mesafe":100}    
CONFIG = ayarları_yukle()
CONFIDENCE_THRESHOLD = CONFIG["yolo_confidence"]    

model = YOLO("yolov8n.pt")
kamera = cv2.VideoCapture(0)

uyku_zamanlayicilari = {} #Hangi ID'nin saat kaçtan beri uyuduğunu tutacağımız hafıza

son_bilinen_konumlar = {} #Hangi ID'nin en son hangi (x,y) koordinatında olduğunu tutar
hareketsizlik_zamanlayicilari = {} #Hangi ID'nin saat kaçtan beri yerinden kıpırdamadığını tutar

mp_face_mesh = mp.solutions.face_mesh # MediaPipe Face Mesh modelini hazırlıyoruz
face_mesh = mp_face_mesh.FaceMesh(max_num_faces = 10,refine_landmarks=True)#refine landmarks ayarı gözleri daha hassas taramasını sağlar

def oklid_hesapla(p1,p2):
    fark_x = p2[0] - p1[0]
    fark_y = p2[1] - p1[1]

    toplam = (fark_x ** 2) + (fark_y ** 2)
    karekok = math.sqrt(toplam)
    return karekok

def ear_hesapla(goz_koordinatlari):
    p1 = goz_koordinatlari[0] #Sol Köşe
    p2 = goz_koordinatlari[1] #Sol Üst
    p3 = goz_koordinatlari[2] #Sağ Üst
    p4 = goz_koordinatlari[3] #Sağ Köşe
    p5 = goz_koordinatlari[4] #Sağ Alt
    p6 = goz_koordinatlari[5] #Sol Alt

    sol_dik = oklid_hesapla(p2,p6)
    sag_dik = oklid_hesapla(p3,p5)
    yatay = oklid_hesapla(p1,p4) 

    ear_degeri = (sol_dik + sag_dik) / (2 * yatay)
    return ear_degeri

def merkez_hesapla(kutu):
# kutu[0] = x1    kutu[1] = y1  kutu[2] = x2  kutu[3] = y2
    
    merkez_x = int((kutu[0] + kutu[2]) / 2)
    merkez_y = int((kutu[1] + kutu[3]) / 2)
    return (merkez_x,merkez_y)

takip_listesi = {} #Ekranda takip ettiğimiz kişilerin merkez noktalarını tutacağımız boş sözlük
siradaki_id = 0 #Yeni tespit edilen kişilere vereceğimiz ilk ID

def tracker_guncelle(yeni_merkezler):
    global siradaki_id #Dışarıda tanımladığımız id değişkenini içeride değiştirebilmek için izin alıyoz
    guncel_takip = {} #Sadece bu framede ekranda olan kişileri tutacağımız geçici liste

    for yeni_m in yeni_merkezler:#YOLO'nun bulduğu her bir yeni merkez noktası için sırayla dönüyoruz
        eslesti_mi = False #Başlangıçta bu yeni merkezin eski biriyle eşleşmediğini varsayıyoruz

        for obje_id , eski_m in takip_listesi.items():#Hafızadaki(önceki karedeki) kayıtlı ID'leri ve onların eski merkezlerini kontrol ediyoruz
            mesafe = oklid_hesapla(yeni_m,eski_m)#Yeni bulduğumuz nokta ile hafızadaki eski nokta arasındaki mesafeyi ölçüyoruz

            if mesafe < CONFIG["tracker_max_mesafe"]:#Eğer aralarındaki mesafe configdeki sınırımızdan küçükse
                guncel_takip[obje_id] = yeni_m #BU aynı kişi ID'sini koruyup yeni merkez koordinatını kaydediyoruz
                eslesti_mi = True #Eşleşme sağlandığı için durumu True yapıyoruz
                break # Bu kişi ile işimiz bitti hafızadaki diğer eski kişilere bakmaya gerek yok döngüden çık
        if not eslesti_mi: # Eğer hafızadaki kimseyle eşleşmediyse (mesafe hep büyük çıktıysa veya hafıza boşsa)
            guncel_takip[siradaki_id] = yeni_m # Bu yepyeni birisi.Ona sıradaki boş ID'yi veriyoruz ve merkezini kaydediyoruz
            siradaki_id += 1 #Bir sonraki yeni kişi için ID sayacını 1 arttırıyoruz(0 ise 1 , 1 ise 2)
    takip_listesi.clear() #Ana hafızamızı(eski listeyi) tamamen temizliyoruz ki ekrandan çıkanlar silinsin            
    takip_listesi.update(guncel_takip) #Sadece bu karede eşleştirdiğimiz ve yeni eklediğimiz kişileri (taze listeyi) ana hafızaya yazıyoruz
    return takip_listesi # Güncellenmiş takip listesini ana döngüde kullanmak üzere geri gönderiyoruz

def yolo_kutulari_bul(frame):#Görüntüdeki nesnelerin kutu koordinatlarını bulur ve liste olarak döndürür
    bulunan_kutular = [] #YOLO'nun bulacağı kutuları içine atacağımız boş bir liste oluşturuyoruz
    sonuclar = model(frame,verbose = False)#Görüntüyü YOLO modeline verip sonuçları alıyoruz(verbose=False ekrana gereksiz log yazmasını engeller)
    for sonuc in sonuclar: # YOLO'dan gelen sonuçların içinde sırayla geziniyoruz
        for kutu in sonuc.boxes:#O sonucun içindeki her bir dikdörtgen kutuya tek tek bakıyoruz
            guven_skoru = float(kutu.conf[0])#Yapay zekanın bu kutudaki nesneden yüzde kaç emin olduğunu alıyoruz
            if guven_skoru > CONFIG["yolo_confidence"]:#Eğer güven skoru bizim configdeki eşiğimizden büyükse bu kutuyu kabul ediyoruz
                x1,y1,x2,y2 = map(int,kutu.xyxy[0])#Kutunun 4 köşesinin koordinatlarını tam sayı olarak alıyoruz
                bulunan_kutular.append([x1,y1,x2,y2])#Koordinatları bir liste yapıp,ana listemize ekliyoruz
    return bulunan_kutular#Bulduğumuz tüm geçerli kutuların listesini dışarıya gönderiyoruz

def kare_isle(frame):#Bir fotoğrafı alır,işler,üzerine çizim yapıp geri döndürür.
    global son_alarm_zamani #Dışarıda tanımladığımız alarm sayacını içeride değiştirebilmek için izin alıyoruz
    kutular = yolo_kutulari_bul(frame)#Resimdeki tüm kutuları alıyoruz
    merkezler = [] #Merkez noktalarını tutacağımız boş bir liste hazırlıyoruz
    rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)# Görüntüyü RGB formatına çeviriyoruz
    ear_degeri = uyku_durumu_bul(rgb_frame) #Ear Değerini alıyoruz
    for kutu in kutular: #YOLO'nun bulduğu her bir kutu için döngüye giriyoruz
        cv2.rectangle(frame,(kutu[0],kutu[1]), (kutu[2],kutu[3]),(255,0,0),2)
        merkez_noktasi = merkez_hesapla(kutu) #Kutunun tam ortasını buluyoruz
        merkezler.append(merkez_noktasi) #Bulduğumuz bu merkez noktasını listemize ekliyoruz
    aktif_kisiler = tracker_guncelle(merkezler) #Merkez noktalarını Trackera gönderip güncel ID'leri alıyoruz
    genel_tehlike_durumu =False #Bütün kişileri kontrol etmeden önce genel tehlike durumunu Yok(False) sayıyoruz
    for k_id,k_merkez in aktif_kisiler.items():#Ekranda aktif olan her bir kişi için çizim yapmaya başlıyoruz
        goz_tehlikede = False
        hareket_tehlikede = False
        cv2.circle(frame,k_merkez,5,(0,0,255),-1)#Kişinin tam merkez noktasına küçük kırmızı bir nokta çiziyoruz
        cv2.putText(frame,f"ID: {k_id}",(k_merkez[0]-25 , k_merkez[1] - 230),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,0),2)#Kişinin merkez noktasının biraz üstüne yeşil renkle ID numarasını yazıyoruz

        if ear_degeri is not None: # Eğer MediaPipe bir yüz veya göz bulabildiyse hesaplamaya başla
            if ear_degeri < CONFIG["ear_threshold"]: #Göz kapalıysa EAR değeri CONFİG de ki eşiğimizden küçük mü?
                if k_id not in uyku_zamanlayicilari:#Bu kişi hafızada yoksa yani gözünü ilk defa tam şuanda kapattıysa
                    uyku_zamanlayicilari[k_id] = time.time() #Şuanki saati/saniyeyi al ve bu kişinin ID'siyle hafızaya kaydet Kronometreyi başlat
                else: #Bu kişi zaten hafızada varsa yani gözü bir süredir kapalıysa
                    gecen_sure = time.time() - uyku_zamanlayicilari[k_id] #Şuanki zamandan gözünü ilk kapattığı zamanı çıkar
                    if gecen_sure > CONFIG["goz_kapali_limit_sn"]: #Eğer geçen süre configde ki limitten (2.0 sn) büyükse
                        genel_tehlike_durumu = True #Biri uyuduğu için tehlike bayrağını kaldır
                        goz_tehlikede = True

                        if loglanmis_ihlaller.get(f"{k_id}_uyku") != True: #Eğer bu adamın uykusunu daha önce dosyaya YAZMADIYSAK
                            logging.info(f"IHLAL BASLADİ (ID={k_id},tur = goz_kapali)")
                            loglanmis_ihlaller[f"{k_id}_uyku"] = True #Artık yazıldı olarak işaretle
            else: #Göz Açıksa EAR değeri eşikten büyükse
                if k_id in uyku_zamanlayicilari:
                    del uyku_zamanlayicilari[k_id] #Göz açıldığı an tehlike geçmiştir.Bu kişinin kaydını hafızadan sil (Kronometreyi sıfırla)             
                    
                    if loglanmis_ihlaller.get(f"{k_id}_uyku") == True: #Bu adamın uyuduğunu daha önce log'a bildirmiş miydik
                        logging.info(f"IHLAL BITTI (ID = {k_id},tur=goz_kapali)")
                        loglanmis_ihlaller[f"{k_id}_uyku"] = False
        if k_id in son_bilinen_konumlar: #Bu kişinin daha önceki bir konumunu hafızaya kaydetmiş miydik diye bakıyoruz
            hareket_miktari = oklid_hesapla(k_merkez,son_bilinen_konumlar[k_id]) #Öklid hesapla ile eski konumu ile şuanki konumu arasındaki farkı ölçüyoruz
            if hareket_miktari < CONFIG["hareket_piksel_esigi"]: #Eğer 20 pikselden az hareket ettiyse -> ADAM DURUYOR
                if k_id not in hareketsizlik_zamanlayicilari: #Adam daha yeni durmaya başladıysa o anki saati kronometreye başlangıç olarak kaydediyoruz
                    hareketsizlik_zamanlayicilari[k_id] = time.time()
                else: #Adam zaten bir süredir duruyorsa , aradan kaç saniye geçmiş onu hesaplıyoruz
                    gecen_hareketsiz_sure = time.time() - hareketsizlik_zamanlayicilari[k_id]
                    if gecen_hareketsiz_sure > CONFIG["hareketsizlik_limit_sn"]: #Eğer durduğu süre 2.0 saniyeyi geçtiyse tehlike çanları çalar
                        genel_tehlike_durumu = True #Biri donup kaldığı için tehlike bayrağını kaldır                       
                        hareket_tehlikede = True

                        if loglanmis_ihlaller.get(f"{k_id}_hareketsiz") != True: #Eğer bu adamın hareketsizliğini daha önce dosyaya YAZMADIYSAK
                            logging.info(f"IHLAL BASLADI (ID={k_id},tur = hareketsiz)")
                            loglanmis_ihlaller[f"{k_id}_hareketsiz"] = True #Artık yazıldı olarak işaretle
            else: #Eğer 20 pikselden FAZLA hareket ettiyse Adam canlandı , yer değiştirdi
                son_bilinen_konumlar[k_id] = k_merkez #Adam hareket ettiği için yeni konumunu güncel olarak hafızaya yazıyoruz
                if k_id in hareketsizlik_zamanlayicilari: #Tehlike geçtiği için eğer donma kronometresi çalışıyorsa onu sıfırlıyoruz
                    del hareketsizlik_zamanlayicilari[k_id]                

                    if loglanmis_ihlaller.get(f"{k_id}_hareketsiz") == True:
                        logging.info(f"IHLAL BITTI (ID = {k_id},tur=hareketsiz)")
                        loglanmis_ihlaller[f"{k_id}_hareketsiz"] = False
        else: #Eğer bu kişiyi ekranda ilk defa görüyorsak:
            son_bilinen_konumlar[k_id] = k_merkez #Sadece o anki konumunu alıyoruz ki bir saniye sonraki karede karşılaştırabilelim 
            logging.info(f"Kisi tespit edildi (ID = {k_id})") #Yeni kişi hafızaya eklendiği an kara kutuya yaz

        if goz_tehlikede == True and hareket_tehlikede == True:
            cv2.putText(frame,"UYKU IHLALI",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
        elif goz_tehlikede == True:
            cv2.putText(frame,"GOZ KAPALI",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),3)
        elif hareket_tehlikede == True:
            cv2.putText(frame,"HAREKETSIZ",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),3)
        else:
            cv2.putText(frame,"NORMAL",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)                
    if genel_tehlike_durumu == True : #Bütün kişiler kontrol edildikten sonra bayrağın son durumuna bakıyoruz
        if time.time() - son_alarm_zamani > 3.0: #Eğer tehlike varsa ve son çalmanın üzerinden 3 saniye(cooldown) geçtiyse çal
            alarm_sesi.play()
            son_alarm_zamani = time.time()
    else:
        alarm_sesi.stop() #Hiçbir tehlike yoksa (Bayrak False kaldıysa) sesi anında kes           
    return frame #İşlemleri biten ve üzerine çizim yapılan resmi geri gönderiyoruz         

def uyku_durumu_bul(rgb_frame):#MediaPipe ile göz noktalarını bulur ve EAR değerini hesaplayıp döndürür
    sonuclar = face_mesh.process(rgb_frame)#Resmi MediaPipe'a veriyoruz ve yüz noktalarını taramasını istiyoruz
    if not sonuclar.multi_face_landmarks:#Eğer ekranda hiçbir yüz bulamadıysa işlem yapmadan None döndürüyoruz
        return None
    yuz_noktalari = sonuclar.multi_face_landmarks[0].landmark #Ekranda yüz varsa ilk bulduğu yüzün noktalarını alıyoruz
    sol_goz_indeksleri = [33,160,158,133,153,144] #Sol gözün etrafındaki 6 noktanın MediaPipedaki sabit numaraları
    h,w,_ = rgb_frame.shape #Resmin yüksekliğini ve genişliğini alıyoruz ki noktaları piksele çevirebilelim
    goz_koordinatlari = [] #Göz koordinatlarını biriktireceğimiz boş bir liste açıyoruz
    for i in sol_goz_indeksleri: #Sadece sol gözün 6 noktası için döngüye giriyoruz
        nokta = yuz_noktalari[i] #Haritadan o numaralı noktayı alıyoruz
        x_piksel = int(nokta.x * w)
        y_piksel = int(nokta.y * h) #Noktalar 0 ile 1 arasında gelir.Bunu resmin eni ve boyuyla çarpıp tam sayı (piksel) yapıyoruz
        goz_koordinatlari.append((x_piksel,y_piksel)) #Bulduğumuz piksel koordinatını listeye ekliyoruz
    ear_degeri = ear_hesapla(goz_koordinatlari) #Bulduğumuz bu 6 noktayı ear_hesapla fonksiyonuna gönderip EAR değerini alıyoruz
    return ear_degeri #Hesaplanan EAR değerini geri gönderiyoruz    


def main(): #Kamerayı başlatır,görüntüleri okur ve işleyerek ekranda gösterir.
    if not kamera.isOpened(): #Kamera başarıyla açıldı mı diye kontrol ediyoruz
        print("HATA: Kamera açılmadı!Lütfen bağlantıyı kontrol edin.")
        return
    print("GuardWatch Başladı... Çıkmak için klavyeden 'q' tuşuna basın.")
    
    while True: #Sonsuz bir döngü başlatıyoruz
        ret,frame = kamera.read() 
        if not ret: #Eğer fotoğraf okunamadıysa döngüyü kırıp çıkıyoruz
            print("Kameradan görüntü alınamıyor.Kapatılıyor...")
            break 

        islenmis_frame = kare_isle(frame) #Okuduğumuz ham fotoğrafı,o yazdığımız dev fonksiyona yollayıp işlenmiş halini alıyoruz
        cv2.imshow("GuardWatch Kamera",islenmis_frame) #Üzerine kutular ve yazılar çizilmiş olan bu yeni fotoğrafı ekranda gösteriyoruz
        if cv2.waitKey(1) & 0xFF == ord('q'): #Klavyeyi dinle 1 milisaniye bekle ve basılan tuş 'q' ise döngüyü bitir
            break    

    kamera.release() # Döngü bitince kamerayı donanımsal olarak serbest bırakıyoruz
    cv2.destroyAllWindows() #Ekranda açık kalan tüm OpenCV pencerelerini temizleyip kapatıyoruz
if __name__ == "__main__": #Eğer bu dosya (guardwatch.py) doğrudan çalıştırıldıysa main() fonksiyonunu tetikle
    main()        

