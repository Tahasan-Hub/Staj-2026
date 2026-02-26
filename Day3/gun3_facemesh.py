import cv2
import mediapipe as mp
import math

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces = 1)

sol_goz = [33,160,158,133,153,144]
sag_goz = [362,385,387,263,373,380]

kamera = cv2.VideoCapture(0)

def oklid_mesafe(p1,p2):
    x_fark = p2[0] - p1[0]
    y_fark = p2[1] - p1[1]

    toplam = (x_fark ** 2 ) + (y_fark ** 2 )
    karekok = math.sqrt(toplam)
    return karekok
def ear_hesapla(goz_noktalari):
    p1 = goz_noktalari[0] #Sol Köşe
    p2 = goz_noktalari[1] #Üst Sol
    p3 = goz_noktalari[2] #Üst Sağ
    p4 = goz_noktalari[3] #Sağ Köşe
    p5 = goz_noktalari[4] #Alt Sağ
    p6 = goz_noktalari[5] #Alt Sol

    sol_dikey = oklid_mesafe(p2,p6)
    sag_dikey = oklid_mesafe(p3,p5)
    yatay = oklid_mesafe(p1,p4)

    ear_degeri = (sol_dikey + sag_dikey) / (2 * yatay)
    return ear_degeri

while True:

    ret,frame = kamera.read()
    rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    sonuclar = face_mesh.process(rgb_frame)

    if sonuclar.multi_face_landmarks: 
        for face_landmarks in sonuclar.multi_face_landmarks:
            h,w,c = frame.shape
            sol_goz_koordinatlar = []
            sag_goz_koordinatlar = []
            for i in sol_goz:
                nokta = face_landmarks.landmark[i]
                x_piksel = int(nokta.x * w)
                y_piksel = int(nokta.y * h)
                sol_goz_koordinatlar.append((x_piksel,y_piksel))
            for i in sag_goz:
                nokta = face_landmarks.landmark[i]
                x_piksel = int(nokta.x * w)
                y_piksel = int(nokta.y * h)
                sag_goz_koordinatlar.append((x_piksel,y_piksel))    
            sol_ear = ear_hesapla(sol_goz_koordinatlar)
            sag_ear = ear_hesapla(sag_goz_koordinatlar)   
            ort_ear = (sol_ear + sag_ear) / 2.0
            print("Ortalama EAR:",ort_ear)
        for id,landmark in enumerate(face_landmarks.landmark):
                piksel_x = int(landmark.x * w)
                piksel_y = int(landmark.y * h)

                if id in sol_goz:
                    cv2.circle(frame, (piksel_x,piksel_y),3,(0,255,0),-1)
                elif id in sag_goz:
                    cv2.circle(frame,(piksel_x,piksel_y),3,(0,0,255),-1)
                else:
                    cv2.circle(frame,(piksel_x,piksel_y),1,(255,255,255),-1)    
    cv2.imshow("FaceMesh",frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):    
        break                
kamera.release()
cv2.destroyAllWindows()