import cv2
import math 
import time 
from ultralytics import YOLO
import mediapipe as mp

model = YOLO("yolov8n.pt")
kamera = cv2.VideoCapture(0)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces = 1,min_detection_confidence = 0.5)

sonraki_id = 0
takip_listesi = {}

kisi_durumlari = {}

def oklid_hesapla(p1,p2):
    fark_x = p2[0] - p1[0]
    fark_y = p2[1] - p1[1]
    toplam = (fark_x ** 2) + (fark_y ** 2)
    karekok = math.sqrt(toplam)
    return karekok

def ear_hesapla(goz_koordinatları):
    p1 = goz_koordinatları[0] #Sol Köşe
    p2 = goz_koordinatları[1] #Sol Üst
    p3 = goz_koordinatları[2] #Sağ Üst
    p4 = goz_koordinatları[3] #Sağ Köşe
    p5 = goz_koordinatları[4] # Sağ Alt
    p6 = goz_koordinatları[5] # Sol Alt

    sol_dik = oklid_hesapla(p2,p6)
    sag_dik = oklid_hesapla(p3,p5)
    yatay = oklid_hesapla(p1,p4)

    ear_degeri = (sol_dik + sag_dik) / (2 * yatay)
    return ear_degeri

def tracker_guncelle(tespitler , takip_listesi , sonraki_id , max_mesafe=100):
    guncel_nesneler = []
    for kutu in tespitler:
        x1,y1,x2,y2 = kutu
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        guncel_nesneler.append({"merkez": (cx,cy), "kutu":(x1,y1,x2,y2)})
        if len(takip_listesi) == 0:
            for nesne in guncel_nesneler:
                takip_listesi[sonraki_id] = nesne
                sonraki_id += 1
        else:
            yeni_takip_listesi = {}
            for nesne in guncel_nesneler:
                yeni_merkez = nesne["merkez"]
                en_kisa_mesafe = max_mesafe
                eslesen_id = None
                for eski_id ,eski_bilgi in takip_listesi.items():
                    eski_merkez = eski_bilgi["merkez"]
                    mesafe = oklid_hesapla(eski_merkez,yeni_merkez)
                    if mesafe < en_kisa_mesafe:
                        en_kisa_mesafe = mesafe
                        eslesen_id = eski_id
                if eslesen_id is not None:
                    yeni_takip_listesi[eslesen_id] = nesne
                    del takip_listesi[eslesen_id]
                else:
                    yeni_takip_listesi[sonraki_id] = nesne
                    sonraki_id += 1
            takip_listesi = yeni_takip_listesi.copy()
    return takip_listesi,sonraki_id              

while True:
    ret,frame = kamera.read()
    if not ret:
        break
    results = model(frame,classes = [0],verbose = False)

    tespitler = []
    for r in results:
        for box in r.boxes:
            x1,y1,x2,y2 = map(int,box.xyxy[0])
            tespitler.append((x1,y1,x2,y2))
    takip_listesi , sonraki_id = tracker_guncelle(tespitler,takip_listesi,sonraki_id)      
    for kisi_id , bilgi in takip_listesi.items():
        x1,y1,x2,y2 = bilgi["kutu"]
        if kisi_id not in kisi_durumlari:
            kisi_durumlari[kisi_id] = {
                "goz_baslangic": None,
                "hareketsiz_baslangic":None
            }
        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
        cv2.putText(frame,f"ID: {kisi_id}",(x1,y1-10),cv2.FONT_HERSHEY_SIMPLEX,0.9,(0,255,0),2) 
        x1,y1 = max(0,x1) , max(0,y1)
        x2,y2 = max(0,x2) , max(0,y2)

        kisi_resmi = frame[y1:y2,x1:x2]

        if kisi_resmi.size == 0:
            continue
        rgb_resim = cv2.cvtColor(kisi_resmi , cv2.COLOR_BGR2RGB)
        sonuclar = face_mesh.process(rgb_resim)   
        if sonuclar.multi_face_landmarks:
            for yuz_noktalari in sonuclar.multi_face_landmarks:
                sol_goz_koordinatlari = [33,160,158,133,153,144]
                sag_goz_koordinatlari = [362,385,387,263,373,380]
                sol_goz = []
                for i in sol_goz_koordinatlari:
                    nokta = yuz_noktalari.landmark[i]
                    sol_goz.append((nokta.x,nokta.y))
                sag_goz = []
                for i in sag_goz_koordinatlari:
                    nokta = yuz_noktalari.landmark[i]
                    sag_goz.append((nokta.x,nokta.y))
                sol_ear = ear_hesapla(sol_goz)
                sag_ear = ear_hesapla(sag_goz)        
                ortalama_ear = (sol_ear + sag_ear) / 2.0

                cv2.putText(frame,f"EAR: {ortalama_ear:.2f}",(x1,y2+20),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,0),2)
                
                EAR_ESIK = 0.20
                UYKU_SURE_SINIRI = 3.0

                if ortalama_ear < EAR_ESIK:
                    if kisi_durumlari[kisi_id]["goz_baslangic"] is None:
                        kisi_durumlari[kisi_id]["goz_baslangic"] = time.time()
                    else:
                        gecen_sure = time.time() - kisi_durumlari[kisi_id]["goz_baslangic"]    

                        if gecen_sure > UYKU_SURE_SINIRI:
                            cv2.putText(frame,f"UYARI! UYKU: KISI {kisi_id}",(x1,y1-20),cv2.FONT_HERSHEY_SIMPLEX,1.2,(0,0,255),3)
                else:
                    kisi_durumlari[kisi_id]["goz_baslangic"] = None
    cv2.imshow("Uyku Sistemi",frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
kamera.release()
cv2.destroyAllWindows()                                