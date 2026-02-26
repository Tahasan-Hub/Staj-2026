import cv2
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

def merkez_bolgede_mi(kutu , bolge):
    x1,y1,x2,y2 = kutu
    bx,by,bx2,by2 = bolge

    merkez_x = int((x1 + x2) / 2)
    merkez_y = int((y1 + y2) / 2)

    if (merkez_x > bx and merkez_x < bx2) and (merkez_y > by and merkez_y < by2):
        return True
    else:
        return False
    
kamera = cv2.VideoCapture(0)

ret,ilk_frame = kamera.read()
secilen_kutu = cv2.selectROI("Odaklanilacak Bölge",ilk_frame)
cv2.destroyWindow("Odaklanilacak Bölge")

bx = int(secilen_kutu[0])
by = int(secilen_kutu[1])
genislik = int(secilen_kutu[2])
yukseklik = int(secilen_kutu[3])

bx2 = bx + genislik
by2 = by + yukseklik

odamiz = (bx,by,bx2,by2)

while True:
    ret,frame = kamera.read()

    results = model(frame,classes = [0],conf = 0.5)
    cv2.rectangle(frame,(bx,by),(bx2,by2),(255,0,0),2)

    for box in results[0].boxes:
        koordinatlar = box.xyxy[0]
        x1 = int(koordinatlar[0])
        y1 = int(koordinatlar[1])
        x2 = int(koordinatlar[2])
        y2 = int(koordinatlar[3])
        kisinin_kutusu =(x1,y1,x2,y2)

        if merkez_bolgede_mi(kisinin_kutusu,odamiz) == True:
            cv2.rectangle(frame,(x1,y1),(x2,y2),(255,0,0),2)
    cv2.imshow("YOLO ROİ",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  
        break
kamera.release()
cv2.destroyAllWindows()          

