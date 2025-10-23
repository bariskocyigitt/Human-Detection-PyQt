import sys, time, os, platform
from datetime import datetime
import cv2
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox, QCheckBox, QSpinBox, QGroupBox, QSystemTrayIcon, QStyle
)

from detectors.screenrec import record_screen

# E-posta yardımcı fonksiyonunu dosya adına göre içe aktar (alerts.py / alert.py)
try:
    from utils.alerts import send_mail  # alerts.py
except ImportError:
    from utils.alerts import send_mail   # alert.py (tekil dosya adı)

def beep():
    if platform.system() == "Windows":
        import winsound
        winsound.Beep(1000, 150)
    else:
        print("[BEEP] Birisi göründü!")

class DetectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("İnsan Algılama (OpenCV + PyQt)")
        self.resize(900, 650)

        # Görüntü alanı
        self.video_label = QLabel("Kamera kapalı")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background:#111; color:#bbb; font-size:16px;")

        # Butonlar
        self.btn_start = QPushButton("Kamerayı Başlat")
        self.btn_stop  = QPushButton("Durdur")
        self.btn_snap  = QPushButton("Anlık Foto Kaydet")
        self.btn_folder= QPushButton("Kayıt Klasörü Seç")

        # Ayarlar
        self.chk_sound = QCheckBox("Sesli Uyarı")
        self.chk_sound.setChecked(True)
        self.chk_popup = QCheckBox("Popup Uyarı")
        self.chk_popup.setChecked(True)
        self.chk_auto_snap = QCheckBox("Algılamada Otomatik Foto Kaydet")
        self.chk_auto_snap.setChecked(True)

        self.cooldown_box = QSpinBox()
        self.cooldown_box.setRange(1, 30)
        self.cooldown_box.setValue(3)
        self.cooldown_box.setSuffix(" sn bekleme")

        # Varsayılan klasör
        self.save_dir = os.path.join(os.getcwd(), "kayitlar")
        os.makedirs(self.save_dir, exist_ok=True)

        # Layout
        controls1 = QHBoxLayout()
        controls1.addWidget(self.btn_start)
        controls1.addWidget(self.btn_stop)
        controls1.addWidget(self.btn_snap)
        controls1.addWidget(self.btn_folder)

        options = QHBoxLayout()
        options.addWidget(self.chk_sound)
        options.addWidget(self.chk_popup)
        options.addWidget(self.chk_auto_snap)
        options.addWidget(self.cooldown_box)

        group = QGroupBox("Ayarlar")
        gvl = QVBoxLayout()
        gvl.addLayout(options)
        group.setLayout(gvl)

        main = QVBoxLayout()
        main.addWidget(self.video_label, stretch=1)
        main.addLayout(controls1)
        main.addWidget(group)
        self.setLayout(main)

        # Sistem tepsisi (bildirimler için)
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tray.setVisible(True)

        # OpenCV
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face = cv2.CascadeClassifier(cascade_path)
        self.last_alert_ts = 0.0

        # Buton eventleri
        self.btn_start.clicked.connect(self.start_camera)
        self.btn_stop.clicked.connect(self.stop_camera)
        self.btn_snap.clicked.connect(self.manual_snapshot)
        self.btn_folder.clicked.connect(self.pick_folder)

    def start_camera(self):
        if self.cap is not None:
            return
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Hata", "Kamera açılamadı!")
            return
        self.timer.start(30)
        self.video_label.setText("Kamera açıldı...")

    def stop_camera(self):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.video_label.setText("Kamera kapalı")

    def pick_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Kayıt klasörü seç", self.save_dir)
        if d:
            self.save_dir = d

    def manual_snapshot(self):
        if not hasattr(self, "last_frame"):
            QMessageBox.information(self, "Bilgi", "Henüz canlı kare yok.")
            return
        self.save_snapshot(self.last_frame)

    def save_snapshot(self, frame):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self.save_dir, f"snapshot_{ts}.jpg")
        cv2.imwrite(path, frame)
        self.tray.showMessage("Kayıt", f"Foto kaydedildi: {os.path.basename(path)}",
                              QSystemTrayIcon.MessageIcon.Information, 2000)
        return path  # önemli: dosya yolunu döndür

    def notify(self):
        if self.chk_sound.isChecked():
            beep()
        if self.chk_popup.isChecked():
            self.tray.showMessage("Uyarı", "Birisi göründü!",
                                  QSystemTrayIcon.MessageIcon.Information, 2000)

    def send_alert_email(self, filepath):
        """Algılama sonrası foto veya videoyu e-posta ile gönder"""
        try:
            if not filepath or not os.path.exists(filepath):
                return
            subject = "İnsan Algılama Uyarısı"
            body = "Bir kişi tespit edildi. Ek dosyada görüntü/video mevcuttur."
            success = send_mail(subject, body, attachment_path=filepath)
            if success:
                self.tray.showMessage(
                    "E-posta",
                    "Uyarı e-postası gönderildi.",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )
        except Exception as e:
            print("E-posta gönderim hatası:", e)

    def record_short_video(self):
        """Algılamada kısa bir ekran kaydı alır (5 sn) ve dosya yolunu döndürür."""
        try:
            filename = record_screen(duration=5, save_dir=self.save_dir)
            self.tray.showMessage(
                "Ekran Kaydı",
                "5 saniyelik video kaydedildi.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
            return filename
        except Exception as e:
            print("Ekran kaydı hatası:", e)
            return None

    def update_frame(self):
        ok, frame = self.cap.read()
        if not ok:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face.detectMultiScale(gray, 1.2, 5, minSize=(60, 60))
        detected = len(faces) > 0

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        now = time.time()
        cooldown = float(self.cooldown_box.value())

        if detected and (now - self.last_alert_ts) > cooldown:
            self.notify()
            photo_path = None
            video_path = None
            if self.chk_auto_snap.isChecked():
                photo_path = self.save_snapshot(frame)
                video_path = self.record_short_video()
                # Video varsa onu, yoksa fotoğrafı e-posta ile gönder
                self.send_alert_email(video_path or photo_path)
            self.last_alert_ts = now

        # Ekrana görüntü yansıt
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))
        self.last_frame = frame

    def closeEvent(self, e):
        self.stop_camera()
        super().closeEvent(e)

def main():
    app = QApplication(sys.argv)
    w = DetectorApp()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
