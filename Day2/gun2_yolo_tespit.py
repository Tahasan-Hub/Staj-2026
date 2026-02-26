import cv2
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

kamera = cv2.VideoCapture(0)

while True:
    ret,frame = kamera.read()
    results = model(frame,classes=[0],conf = 0.8)
    for box in results[0].boxes:
        koordinatlar=box.xyxy[0]
        x1 = int(koordinatlar[0])
        y1 = int(koordinatlar[1])
        x2 = int(koordinatlar[2])
        y2 = int(koordinatlar[3])
        skor = float(box.conf[0])
        yuzde = int(skor * 100) #Conf u yüzdelikli hale çevirdik.
        kutu = cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),3)
        cv2.putText(frame,f"Kisi: %{yuzde}",(x1,y1-10),cv2.FONT_HERSHEY_PLAIN,1,(0,255,0),3)

    kisi_sayisi = len(results[0].boxes)    
    cv2.putText(frame,f"Toplam Kisi Sayisi: {kisi_sayisi}",(35,40),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
    cv2.imshow("YOLO",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
kamera.release() 
cv2.destroyAllWindows()    
