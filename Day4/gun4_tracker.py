import math
import cv2 
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
kamera = cv2.VideoCapture(0)

def oklid_hesapla(p1,p2):
    fark_x = p2[0] - p1[0]
    fark_y = p2[1] - p1[1]

    toplam = (fark_x ** 2) + (fark_y ** 2)
    karekok = math.sqrt(toplam)
    return karekok

sonraki_id = 0
takip_listesi = {}

def tracker_guncelle(tespitler , takip_listesi , sonraki_id , max_mesafe=100):
    guncel_nesneler = []

    for kutu in tespitler:
        x1,y1,x2,y2 = kutu

        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        guncel_nesneler.append({"merkez": (cx , cy),"kutu": (x1,y1,x2,y2)})

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

            for eski_id , eski_bilgi in takip_listesi.items():
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
    return takip_listesi , sonraki_id            

while True:
    ret,frame = kamera.read()
    if not ret:
        break
    results = model(frame,classes = [0], verbose = False)
    tespitler = []
    for r in results:
        for box in r.boxes:
            x1,y1,x2,y2 = map(int,box.xyxy[0])
            tespitler.append((x1,y1,x2,y2))
    takip_listesi,sonraki_id = tracker_guncelle(tespitler,takip_listesi,sonraki_id)
    for kisi_id,bilgi in takip_listesi.items():
        x1,y1,x2,y2 = bilgi["kutu"]
        merkez = bilgi["merkez"]
        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
        cv2.putText(frame,f"ID: {kisi_id}",(x1,y1-10),cv2.FONT_HERSHEY_SIMPLEX,0.9,(0,0,255),2)
        cv2.circle(frame,merkez,5,(255,0,0),-1)        

    cv2.imshow("Tracker",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
kamera.release()
cv2.destroyAllWindows()     
