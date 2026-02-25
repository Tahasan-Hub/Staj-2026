import cv2

kamera = cv2.VideoCapture(0)

while True:
    kontrol,frame = kamera.read()
    yukseklik = frame.shape[0]
    genislik = frame.shape[1]
    yazi = f"{genislik}x{yukseklik}"
    cv2.putText(frame,yazi,(10,40),cv2.FONT_HERSHEY_PLAIN,1,(0,0,255),3)
    cv2.rectangle(frame,(65,50),(150,200),(255,0,255),3)#Dikdörtgen
    cv2.circle(frame,(400,300),45,(0,255,0),-1)#Daire
    cv2.putText(frame,"DENEME OYLESİNE",(200,100),cv2.FONT_HERSHEY_SCRIPT_COMPLEX,2,(150,240,30),3)#Ekrana yazı yazar.
    cv2.imshow("Yeni Pencere",frame)
    if cv2.waitKey(1) == ord('q'):
        break
kamera.release()
cv2.destroyAllWindows()


