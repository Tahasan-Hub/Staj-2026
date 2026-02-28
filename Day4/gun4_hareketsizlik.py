import cv2
import math
import time
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

kamera = cv2.VideoCapture(0)

eski_merkez = None
hareketsizligin_basladigi_an = None

def oklid_hesapla(p1,p2):
    fark_x = p2[0] - p1[0]
    fark_y = p2[1] - p1[1]

    toplam = (fark_x ** 2) + (fark_y ** 2)
    karekok = math.sqrt(toplam)
    return karekok 
 
while True:
    ret,frame = kamera.read()
    results = model(frame,classes = [0])

    for r in results:
        if len(r.boxes) > 0:
            box = r.boxes[0]
            x1,y1,x2,y2 = box.xyxy[0]
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)
            guncel_merkez = (cx,cy)

            if eski_merkez is not None:
                mesafe = oklid_hesapla(eski_merkez,guncel_merkez)

                if mesafe < 20:
                    if hareketsizligin_basladigi_an is None:
                        hareketsizligin_basladigi_an = time.time()    
                    gecen_sure = time.time() - hareketsizligin_basladigi_an

                    cv2.putText(frame,f"Sure: {gecen_sure:.1f} sn",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),3)
                    if gecen_sure >= 2.0:
                        cv2.putText(frame,"HAREKETSIZ",(100,150),cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,0,255),3)
                     
                else:
                    hareketsizligin_basladigi_an = None  
                    
            eski_merkez = guncel_merkez
    cv2.imshow("Hareketsizlik",frame)
    if cv2.waitKey(1) & 0xFF == ord ('q'):
        break                      
kamera.release()
cv2.destroyAllWindows()