import cv2
import numpy as np
import time

prev_time = time.time()

# ===============================
# IMPORTAR MÓDULOS DEL PROYECTO
# ===============================
from secuencia_funciones import check_security_sequence
from deteccion_funciones import update_mobile_tracker

# ===============================
# CARGAR CALIBRACIÓN (OFFLINE)
# ===============================
calib = np.load("calibration_data.npz")
K = calib["K"]
dist = calib["dist"]

# ===============================
# CÁMARA
# ===============================
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: no se pudo abrir la cámara")
    exit()

# ===============================
# ESTADO DEL SISTEMA
# ===============================
acceso_permitido = False

# ===============================
# BUCLE PRINCIPAL
# ===============================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # -------- UNDISTORT --------
    frame = cv2.undistort(frame, K, dist)

    # -------- SISTEMA DE SEGURIDAD --------
    if not acceso_permitido:
        acceso_permitido, frame = check_security_sequence(frame)

    # -------- TRACKER (SOLO SI HAY ACCESO) --------
    else:
        frame = update_mobile_tracker(frame)

    # -------- CALCULAR FPS --------
    current_time = time.time()
    fps = 1.0 / (current_time - prev_time)
    prev_time = current_time

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )
        
    # -------- MOSTRAR VÍDEO --------
    cv2.imshow("Sistema Final", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ===============================
# CIERRE LIMPIO
# ===============================
cap.release()
cv2.destroyAllWindows()
