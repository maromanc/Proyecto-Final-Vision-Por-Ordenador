import cv2
import numpy as np
import os
import time

# ----------------------------
# CONFIG
# ----------------------------
CAM_INDEX = 0
FLIP_MIRROR = True

OUT_DIR = "captures_transformaciones"
os.makedirs(OUT_DIR, exist_ok=True)

def timestamp():
    return time.strftime("%Y%m%d_%H%M%S")

cap = cv2.VideoCapture(CAM_INDEX)

prev_gray = None  # <- FIX: ahora sí, variable normal

# Morfología
kernel = np.ones((5, 5), np.uint8)

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    frame = cv2.resize(frame, (640, 360))
    if FLIP_MIRROR:
        frame = cv2.flip(frame, 1)

    # --- Transformaciones “seguridad” ---
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 60, 150)

    # --- Transformaciones “tracker” (máscaras) ---
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Rango rojo (similar a vuestro deteccion_funciones.py)
    S_MIN = 110
    V_MIN = 40
    lower1 = np.array([0,   S_MIN, V_MIN])
    upper1 = np.array([12,  255,   255])
    lower2 = np.array([168, S_MIN, V_MIN])
    upper2 = np.array([180, 255,   255])

    red_mask = cv2.inRange(hsv, lower1, upper1) | cv2.inRange(hsv, lower2, upper2)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Movimiento por diferencia de frames (para “foto”)
    curr_g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    curr_g = cv2.GaussianBlur(curr_g, (7, 7), 0)

    if prev_gray is None:
        prev_gray = curr_g.copy()

    diff = cv2.absdiff(curr_g, prev_gray)
    prev_gray = curr_g

    MOTION_THRESH = 20
    _, motion = cv2.threshold(diff, MOTION_THRESH, 255, cv2.THRESH_BINARY)
    motion = cv2.morphologyEx(motion, cv2.MORPH_OPEN, kernel, iterations=1)
    motion = cv2.morphologyEx(motion, cv2.MORPH_CLOSE, kernel, iterations=2)

    combo = cv2.bitwise_and(red_mask, motion)

    # ---- Montaje GRID (2x3) ----
    gray_bgr  = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    blur_bgr  = cv2.cvtColor(blur, cv2.COLOR_GRAY2BGR)
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    red_bgr = cv2.cvtColor(red_mask, cv2.COLOR_GRAY2BGR)
    mot_bgr = cv2.cvtColor(motion, cv2.COLOR_GRAY2BGR)

    top = np.hstack([frame, gray_bgr, blur_bgr])
    bottom = np.hstack([edges_bgr, red_bgr, mot_bgr])
    grid = np.vstack([top, bottom])

    # Etiquetas
    cv2.putText(grid, "Original", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    cv2.putText(grid, "Grises", (650, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    cv2.putText(grid, "Gaussiano", (1280, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.putText(grid, "Canny", (10, 385), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    cv2.putText(grid, "Mascara rojo (HSV)", (650, 385), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    cv2.putText(grid, "Mascara movimiento", (1280, 385), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.imshow("Grid Transformaciones (S=guardar, Q=salir)", grid)
    cv2.imshow("Combo (rojo ∩ movimiento)", combo)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

    if key == ord('s'):
        ts = timestamp()
        cv2.imwrite(os.path.join(OUT_DIR, f"{ts}_01_original.png"), frame)
        cv2.imwrite(os.path.join(OUT_DIR, f"{ts}_02_gray.png"), gray)
        cv2.imwrite(os.path.join(OUT_DIR, f"{ts}_03_blur.png"), blur)
        cv2.imwrite(os.path.join(OUT_DIR, f"{ts}_04_canny.png"), edges)
        cv2.imwrite(os.path.join(OUT_DIR, f"{ts}_05_red_mask.png"), red_mask)
        cv2.imwrite(os.path.join(OUT_DIR, f"{ts}_06_motion.png"), motion)
        cv2.imwrite(os.path.join(OUT_DIR, f"{ts}_07_combo.png"), combo)
        print(f"[OK] Capturas guardadas en '{OUT_DIR}' con timestamp {ts}")

cap.release()
cv2.destroyAllWindows()
