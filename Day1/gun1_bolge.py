import cv2

kamera = cv2.VideoCapture(0)

ret,frame = kamera.read()

r = cv2.selectROI("Bölge Seç",frame)

x,y,w,h = r
print(f"Koordinatlar: X:{x}, Y:{y}, GENİŞLİK:{w}, YÜKSEKLİK: {h}")

kesilen_bolge = frame[y:y+h , x:x+w]

cv2.imshow("Kesilen Fotoğraf",kesilen_bolge)

cv2.waitKey(0)

kamera.release()
cv2.destroyAllWindows()