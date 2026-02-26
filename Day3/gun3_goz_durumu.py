import cv2
import mediapipe as mp
import math

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces = 1)

sol_goz = [33,160,158,133,153,144]
sag_goz = [362,385,387,263,373,380]

esik_degeri = 0.25

kamera = cv2.VideoCapture(0)

def oklid_mesafe(p1,p2):
    fark_x = p2[0] - p1[0]
    fark_y = p2[1] - p1[1]

    toplam = (fark_x ** 2) + (fark_y ** 2)
    karekok = math.sqrt(toplam)
    return karekok

def ear_hesapla(goz_noktalari):
    p1 = goz_noktalari[0] # Sol Köşe
    p2 = goz_noktalari[1] # Sol Üst
    p3 = goz_noktalari[2] # Sağ Üst
    p4 = goz_noktalari[3] # Sağ Köşe
    p5 = goz_noktalari[4] # Sağ Alt
    p6 = goz_noktalari[5] # Sol Alt

    sol_dik = oklid_mesafe(p2,p6)
    sag_dik = oklid_mesafe(p3,p5)
    yatay = oklid_mesafe(p1,p4)

    ear_degeri = (sol_dik + sag_dik) / (2 * yatay)
    return ear_degeri

while True:
    ret,frame = kamera.read()
    rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    sonuclar = face_mesh.process(rgb_frame)

    if sonuclar.multi_face_landmarks:
        for face_landmarks in sonuclar.multi_face_landmarks:
            h,w,c = frame.shape
            sol_goz_koor = []
            sag_goz_koor = []

            for i in sol_goz:
                nokta = face_landmarks.landmark[i]
                piksel_x = int(nokta.x * w)
                piksel_y = int(nokta.y * h)
                sol_goz_koor.append((piksel_x,piksel_y))

            for i in sag_goz:
                nokta = face_landmarks.landmark[i]
                piksel_x = int(nokta.x * w)
                piksel_y = int(nokta.y * h)    
                sag_goz_koor.append((piksel_x,piksel_y))

            sol_ear = ear_hesapla(sol_goz_koor)
            sag_ear = ear_hesapla(sag_goz_koor)
            ort = (sol_ear + sag_ear) / 2.0
            sol_ear = round(sol_ear,3)
            sag_ear = round(sag_ear,3)
            ort = round(ort,3)
            if ort >= esik_degeri:
                cv2.rectangle(frame,(20,20),(350,80),(0,255,0),2)
                cv2.putText(frame,"GOZ ACIK",(40,60),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
            else:
                cv2.rectangle(frame,(20,20),(350,80),(0,0,255),-1)
                cv2.putText(frame,"GOZ KAPALI",(40,60),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)  
            cv2.putText(frame,f"Sol Ear: {sol_ear}",(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
            cv2.putText(frame,f"Sag Ear: {sag_ear}",(30,90),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2) 
            cv2.putText(frame,f"Ortalama: {ort}",(30,130),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        for id,landmark in enumerate(face_landmarks.landmark):
            piksel_x = int(landmark.x * w)
            piksel_y = int(landmark.y * h)

            if id in sol_goz:
                cv2.circle(frame,(piksel_x,piksel_y),3,(0,255,0),-1)
            elif id in sag_goz:
                cv2.circle(frame,(piksel_x,piksel_y),3,(0,0,255),-1)
            else:
                cv2.circle(frame,(piksel_x,piksel_y),1,(255,255,255),-1) 
    cv2.imshow("Face Mesh",frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
kamera.release()
cv2.destroyAllWindows()                          
