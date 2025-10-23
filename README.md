# 👁️ İnsan Algılama Sistemi (OpenCV + PyQt6)

Bu proje, **kamera görüntüsünden insan/yüz algılama**, **ekran kaydı alma**, **otomatik fotoğraf kaydetme** ve **e-posta ile uyarı gönderme** özelliklerine sahip bir masaüstü uygulamasıdır.

## 🚀 Özellikler

- ✅ Gerçek zamanlı yüz algılama (OpenCV Haar Cascade)
- 🧠 Performans optimizasyonu (düşük çözünürlükte hızlı tespit)
- 💾 Algılama anında:
  - Anlık fotoğraf kaydı (`kayitlar/` klasörüne)
  - 5 saniyelik kısa video kaydı
  - E-posta ile otomatik uyarı gönderimi
- 🔔 Sesli ve görsel (popup) uyarı sistemi
- 🪟 PyQt6 arayüzü ile kullanıcı dostu tasarım

---

## 🧰 Kullanılan Teknolojiler

| Teknoloji | Açıklama |
|------------|-----------|
| **Python 3.13+** | Ana programlama dili |
| **OpenCV** | Görüntü işleme ve yüz tespiti |
| **PyQt6** | Grafiksel kullanıcı arayüzü |
| **NumPy** | Görüntü verilerini işleme |
| **MSS** | Ekran kaydı oluşturma |
| **smtplib** | E-posta gönderimi için |

---

## 📦 Kurulum

1. Gerekli bağımlılıkları yükleyin:

   ```bash
   pip install opencv-python pyqt6 numpy mss python-dotenv


##🧠 Çalışma Prensibi

Kullanıcı “Kamerayı Başlat” butonuna basar.

Sistem yüz algılarsa:

Anlık fotoğraf ve kısa video kaydı oluşturulur.

İstenirse e-posta gönderilir.

Sesli veya popup uyarı gösterilir.

Kullanıcı isterse kayıt klasörünü değiştirebilir.

##🧩 Geliştirici Notları

Algılama performansı, çözünürlük ve detect_scale parametresiyle ayarlanabilir.

GPU destekli OpenCV (opencv-contrib-python) kurulumu performansı artırabilir.

Kod yapısı modülerdir — yeni algılama modelleri (ör. DNN, YOLO) kolayca eklenebilir.

##👨‍💻 Geliştirici

Barış Koçyiğit