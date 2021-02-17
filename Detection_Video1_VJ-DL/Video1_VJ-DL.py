# IMPORTATION DES LIBRAIRIES NECESSAIRES
import cv2
import os
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import numpy as np

# ............................................................................

# IMPORTATION DES MODELES
# Cascade Viola Jones pour la détection des visages
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')

# Modèle de Deep Learning : réseau de neurones pour la détection des masques
model = load_model("mask_recog_ver2.h5")

# ............................................................................

# Taille de la vidéo
WIDTH = 640
HEIGHT = 480


# LANCEMENT DE LA VIDEO
video_capture = cv2.VideoCapture(0)

# Emplacement de la vidéo sauvegardée
out = cv2.VideoWriter('/Users/clair/Desktop/FaceMaskDetect_Output.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (WIDTH,HEIGHT))

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    
    # Passage en noir et blanc pour l'analyse
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # DETECTION DES VISAGES EN TEMPS REEL (HAARCASCADE VIOLA ET JONES)
    faces = faceCascade.detectMultiScale(gray,
                                         scaleFactor=1.1,
                                         minNeighbors=5,
                                         minSize=(60, 60),
                                         flags=cv2.CASCADE_SCALE_IMAGE)    
    faces_list=[]
    preds=[]
    
    # Paramétrage des cadres à afficher sur la vidéo
    for (x, y, w, h) in faces:
        face_frame = frame[y:y+h,x:x+w]
        face_frame = cv2.cvtColor(face_frame, cv2.COLOR_BGR2RGB)
        face_frame = cv2.resize(face_frame, (224, 224))
        face_frame = img_to_array(face_frame)
        face_frame = np.expand_dims(face_frame, axis=0)
        face_frame =  preprocess_input(face_frame)
        faces_list.append(face_frame)
        
        # PREDICTION DU PORT OU NON DU MASQUE EN TEMPS REEL (RESEAU DE NEURONES)    
        if len(faces_list)>0:
            preds = model.predict(faces_list)
        for pred in preds:
            (mask, withoutMask) = pred
            
        # Légende des cadres sur la vidéo
        label = "Mask" if mask > withoutMask else "No Mask"
        color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
        label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)
        cv2.putText(frame, label, (x, y- 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)

        cv2.rectangle(frame, (x, y), (x + w, y + h),color, 2)
        
        # AFFICHAGE DU RESULTAT SOUS FORME DE CADRE LEGENDE EN TEMPS REEL (MASK OU NO MASK)  
    cv2.imshow('Video', frame) 
    out.write(frame)
    
    if cv2.waitKey(33) & 0xFF == ord('q'): # quitter l'enregistrement en appuyant sur la touche q
        break
    
# ARRET ET SAUVEGARDE DE LA VIDEO     
video_capture.release()
out.release()
cv2.destroyAllWindows()