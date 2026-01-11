import cv2
import numpy as np
import time

# ============================================
# CONFIGURACIÓN
# ============================================

TARGET_SEQUENCE = ["circle", "triangle", "square", "pentagon"]
detected_sequence = []

HOLD_TIME = 0.5  # mantener 1 segundo
last_shape = None
start_time = None
waiting_for_disappear = False


# ============================================
# CLASIFICACIÓN DE FORMAS
# ============================================

def classify_shape(cnt):
    area = cv2.contourArea(cnt)
    if area < 2000:
        return None

    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
    sides = len(approx)

    # CÍRCULO por circularidad
    circularity = 4 * np.pi * area / (peri * peri)
    if circularity > 0.80 and sides >= 6:
        return "circle"

    if sides == 3:
        return "triangle"

    if sides == 4:
        x, y, w, h = cv2.boundingRect(approx)
        r = w / float(h)
        if 0.80 <= r <= 1.20:
            return "square"

    if sides == 5:
        return "pentagon"

    return None


# ============================================
# CÁMARA
# ============================================

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # --- MÉTODO FIABLE DE CONTORNOS ---
    edges = cv2.Canny(blur, 60, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    current_shape = None

    if contours:
        # contorno MÁS GRANDE
        cnt = max(contours, key=cv2.contourArea)

        # centro del contorno (obligar a estar en zona útil)
        x, y, w, h = cv2.boundingRect(cnt)
        cx = x + w // 2
        cy = y + h // 2
        H, W = frame.shape[:2]

        if W * 0.20 < cx < W * 0.80 and H * 0.20 < cy < H * 0.80:
            current_shape = classify_shape(cnt)
            if current_shape:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
                cv2.putText(frame, current_shape, (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    # ============================================
    # ESPERAR A QUE LA FIGURA DESAPAREZCA
    # ============================================
    if waiting_for_disappear:
        if current_shape is None:
            waiting_for_disappear = False

        cv2.putText(frame, "Cambia la figura...", (20,80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

        cv2.imshow("Sistema", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    # ============================================
    # DETECCIÓN ESTABLE DURANTE 1 SEGUNDO
    # ============================================

    if current_shape == last_shape and current_shape is not None:
        if start_time is None:
            start_time = time.time()
        else:
            elapsed = time.time() - start_time

            cv2.putText(frame, f"Estable: {elapsed:.1f}s", (20,80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)

            if elapsed >= HOLD_TIME:
                start_time = None
                waiting_for_disappear = True

                next_index = len(detected_sequence)

                # VALIDAR LA SECUENCIA
                if next_index < len(TARGET_SEQUENCE) and current_shape == TARGET_SEQUENCE[next_index]:
                    detected_sequence.append(current_shape)
                else:
                    # ======= ERROR EN LA SECUENCIA ========
                    detected_sequence = []
                    cv2.putText(frame, "ERROR --> Secuencia incorrecta", (20,200),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 3)
                    cv2.imshow("Sistema", frame)
                    cv2.waitKey(1500)

    else:
        start_time = None

    last_shape = current_shape

    # mostrar secuencia actual
    cv2.putText(frame, f"Secuencia: {detected_sequence}",
                (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

    # SI COMPLETÓ LA SECUENCIA
    if detected_sequence == TARGET_SEQUENCE:
        cv2.putText(frame, "ACCESO PERMITIDO", (80,200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0,255,0),3)
        cv2.imshow("Sistema", frame)
        cv2.waitKey(2500)


    cv2.imshow("Sistema", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
