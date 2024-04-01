import cv2
import os

imagesPath = "C:/Users/peris/OneDrive/Documentos/Stefa/programacion/probando_face_recognition/Projecto-0/images/input_images"

if not os.path.exists("images/faces"):
    os.makedirs("faces")
    print("Nueva carpeta: faces")

#Detector facial 
faceClassif = cv2.CascadeClassifier("frontalface_classifier.xml")

def capture_photo():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: No se pudo abrir la camara")
        return
    
    last_frame = None
    while True:
        # Mostrar el frame en una ventana
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar el frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceClassif.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("frame", frame)

        last_frame = frame.copy()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Guardar la imagen capturada en el directorio de imágenes
    username = input("Escribe el nombre de la persona capturada: ").capitalize()
    cv2.imwrite(os.path.join(imagesPath, username + ".jpg"), frame)
    print(f"Foto guardada como {username}.jpg")

    
answer = input("Quieres añadir una nueva cara mediante la camara? [si/no] ").lower()
if answer == "si":
    capture_photo()
elif answer != "no":
    print("Respuesta invalida")
    exit(1)



#Iteracion por las caras de cada imagen para luego guardarlas
count = 0
for imageName in os.listdir(imagesPath):
    print(imageName)
    image = cv2.imread(imagesPath + "/" + imageName)
    faces = faceClassif.detectMultiScale(image, 1.1, 5)
    for (x, y, w, h) in faces:
        #Deja seccion de la cara y le cambia el tamaño
        face = image[y:y + h, x:x + w]
        face = cv2.resize(face, (150, 150))
        
        cv2.imwrite("faces/" + str(count) + ".jpg", face)
        count += 1
  
  
                       