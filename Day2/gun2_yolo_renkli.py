import cv2
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

renkler = [
    (0,255,0), # 0. Kişi için Yeşil
    (255,0,0), # 1. Kişi için Mavi
    (0,0,255), # 2. Kişi için Kırmızı
    (0,255,255), # 3. Kişi için Sarı
    (255,0,255) # 4. Kişi için Mor
]

kamera = cv2.VideoCapture(0)

while True:
    ret,frame = kamera.read()

    results = model(frame,classes = [0],conf = 0.5)

    for i,box in enumerate(results[0].boxes):
        koordinatlar = box.xyxy[0]
        x1 = int(koordinatlar[0])
        y1 = int(koordinatlar[1])
        x2 = int(koordinatlar[2])
        y2 = int(koordinatlar[3])

        secilen_renk = renkler[i % len(renkler)]

        cv2.rectangle(frame,(x1,y1),(x2,y2),secilen_renk,2)
    cv2.imshow("Renk Çalışması",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
kamera.release()
cv2.destroyAllWindows()        