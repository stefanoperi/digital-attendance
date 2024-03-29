import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("No se pudo abrir la camara")
    exit()

side_face_classif = cv2.CascadeClassifier('profileface_classifier.xml')
face_classif = cv2.CascadeClassifier("frontalface_classifier.xml")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_classif.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)


    side_faces = side_face_classif.detectMultiScale(gray, 1.3, 3)
    for (x, y, w, h) in side_faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
