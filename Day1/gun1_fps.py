import cv2
import time

onceki_zaman = time.time()
kamera = cv2.VideoCapture(0)
fps_liste = []

while True:
    ret,frame = kamera.read()
    suanki_zaman = time.time()
    gecen_sure = suanki_zaman - onceki_zaman
    onceki_zaman = suanki_zaman
    fps = 1/gecen_sure
    fps_liste.append(fps)
    if len(fps_liste) > 10:
        fps_liste.pop(0)
    ortalama_fps = sum(fps_liste) / len(fps_liste)
    yazi = f"FPS: {int(ortalama_fps)}"
    cv2.putText(frame,yazi,(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),2)
    cv2.imshow("FPS BASTIRMA",frame)
    if cv2.waitKey(1) == ord('q'):
        break
kamera.release()
cv2.destroyAllWindows()    
