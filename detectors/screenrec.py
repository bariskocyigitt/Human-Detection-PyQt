import cv2
import numpy as np
import mss
import time
import os
from datetime import datetime

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
    return path

def record_screen(duration=5, save_dir="kayitlar", fps=20, use_xvid_fallback=False):
    """
    Tüm ekranı duration(sn) kadar kaydeder.
    Varsayılan: MP4 (mp4v). Eğer player açmazsa use_xvid_fallback=True ile AVI(XVID) yaz.
    Dönüş: kaydedilen dosyanın tam yolu.
    """
    _ensure_dir(save_dir)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Codec ve uzantı seçimi
    if use_xvid_fallback:
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        ext = "avi"
    else:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        ext = "mp4"

    filename = os.path.join(save_dir, f"screenrec_{ts}.{ext}")

    with mss.mss() as sct:
        monitor = sct.monitors[1]  # primary ekran
        width, height = monitor["width"], monitor["height"]

        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        if not out.isOpened():
            # mp4 açılmadıysa otomatik XVID'e düş
            if not use_xvid_fallback:
                return record_screen(duration, save_dir, fps, use_xvid_fallback=True)
            else:
                raise RuntimeError("VideoWriter açılamadı (XVID).")

        start = time.time()
        frame_interval = 1.0 / float(fps)
        next_ts = start

        while True:
            img = np.array(sct.grab(monitor))         # BGRA
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # BGR
            out.write(frame)

            next_ts += frame_interval
            sleep_for = next_ts - time.time()
            if sleep_for > 0:
                time.sleep(sleep_for)

            if time.time() - start >= duration:
                break

        out.release()

    return filename
