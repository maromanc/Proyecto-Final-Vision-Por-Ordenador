import cv2
import numpy as np

# -----------------------------------------
# CONTADOR DE USOS DEL MÓVIL (IGUAL)
# -----------------------------------------
phone_count = 0
tracking = False        # indica si el tracker está activo
tracker = None          # objeto tracker
no_phone_frames = 0     # frames sin móvil detectado tras fallar
NO_PHONE_THRESHOLD = 10 # frames necesarios para confirmar desaparición


# -----------------------------------------
# FUNCIÓN PRINCIPAL DEL TRACKER
# -----------------------------------------
def update_mobile_tracker(frame):
    global phone_count, tracking, tracker, no_phone_frames

    # =============================
    # SI NO ESTAMOS TRACKING -> DETECTAR MÓVIL ROJO
    # =============================
    if not tracking:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # ROJO HSV
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)

        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        mask = mask1 | mask2
        mask = cv2.medianBlur(mask, 7)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        phone_detected = False
        phone_box = None

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 5000:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            ar = h / float(w)

            # filtro de forma tipo móvil vertical
            if 1.4 < ar < 2.5:
                phone_detected = True
                phone_box = (x, y, w, h)

                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                cv2.putText(
                    frame,
                    "Movil detectado (inicio tracker)",
                    (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0,255,0),
                    2
                )
                break

        if phone_detected:
            tracker = cv2.TrackerCSRT_create()
            tracker.init(frame, phone_box)
            tracking = True
            print("TRACKER iniciado.")

    # =============================
    # SI ESTAMOS TRACKING -> SEGUIR AL OBJETO
    # =============================
    else:
        ok, bbox = tracker.update(frame)

        if ok:
            x, y, w, h = tuple(map(int, bbox))
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 3)
            cv2.putText(
                frame,
                "TRACKING...",
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255,255,0),
                2
            )
        else:
            no_phone_frames += 1

            if no_phone_frames >= NO_PHONE_THRESHOLD:
                phone_count += 1
                print("Movil desaparecido -> contador:", phone_count)

                tracking = False
                no_phone_frames = 0
                tracker = None

        if not ok:
            cv2.putText(
                frame,
                "Buscando desaparicion...",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0,0,255),
                2
            )

    # ==================================
    # MOSTRAR CONTADOR EN PANTALLA
    # ==================================
    cv2.putText(
        frame,
        f"Veces que coges el movil: {phone_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0,255,0),
        2
    )

    return frame
