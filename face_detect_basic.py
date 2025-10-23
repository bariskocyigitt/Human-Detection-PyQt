import cv2
import time
import platform

# Basit beep: Windows'ta ses verir, diğerlerinde konsola yazar
def beep():
    if platform.system() == "Windows":
        import winsound
        winsound.Beep(1000, 200)  # 1000 Hz, 200 ms
    else:
        print("[BEEP] Birisi göründü!")

def main():
    # Haar cascade dosya yolu (OpenCV ile birlikte gelir)
    face_cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(face_cascade_path)

    cap = cv2.VideoCapture(0)  # 0: varsayılan webcam
    if not cap.isOpened():
        print("Kamera açılamadı!")
        return

    last_alert_ts = 0.0
    alert_cooldown = 2.0  # saniye (spama düşmemek için)

    print("Çıkmak için pencere aktifken 'q' tuşuna bas.")
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Kare alınamadı.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(60, 60)
        )

        # Dikdörtgen çiz ve uyarı tetikle
        detected = False
        for (x, y, w, h) in faces:
            detected = True
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Uyarı (cooldown ile)
        now = time.time()
        if detected and (now - last_alert_ts) > alert_cooldown:
            print("Birisi göründü!")
            beep()
            last_alert_ts = now

        cv2.imshow("Yuz Algilama - MVP", frame)

        # q ile çık
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
