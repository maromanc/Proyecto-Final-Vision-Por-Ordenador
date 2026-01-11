import cv2
import numpy as np
import glob
import os

# === CONFIGURACIÓN ===========================================
IMAGES_DIR = "calibration_images"
OUTPUT_CORNERS_DIR = "detected_corners"  # <--- Guardar esquinas
CHESSBOARD_COLS = 7
CHESSBOARD_ROWS = 5
SQUARE_SIZE = 0.025

OUTPUT_FILE_NPZ = "calibration_data.npz"
OUTPUT_FILE_YAML = "calibration.yaml"
# ===============================================================


def calibrate_camera_from_folder(images_dir):

    # Crear carpeta si no existe
    if not os.path.exists(OUTPUT_CORNERS_DIR):
        os.makedirs(OUTPUT_CORNERS_DIR)

    objp = np.zeros((CHESSBOARD_ROWS * CHESSBOARD_COLS, 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHESSBOARD_COLS, 0:CHESSBOARD_ROWS].T.reshape(-1, 2)
    objp *= SQUARE_SIZE

    objpoints = []
    imgpoints = []

    pattern_list = ["*.png", "*.jpg", "*.jpeg"]
    images = []
    for pat in pattern_list:
        images.extend(glob.glob(os.path.join(images_dir, pat)))

    images = sorted(images)

    if not images:
        print(f"❌ No se han encontrado imágenes en: {images_dir}")
        return None, None, None, None

    print(f"🖼  Encontradas {len(images)} imágenes de calibración")

    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        30,
        0.001
    )

    gray = None

    for fname in images:
        img = cv2.imread(fname)
        if img is None:
            print(f"⚠️  No se pudo leer {fname}")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(
            gray,
            (CHESSBOARD_COLS, CHESSBOARD_ROWS),
            None
        )

        if ret:
            corners_subpix = cv2.cornerSubPix(
                gray,
                corners,
                (11, 11),
                (-1, -1),
                criteria
            )

            objpoints.append(objp)
            imgpoints.append(corners_subpix)

            cv2.drawChessboardCorners(
                img,
                (CHESSBOARD_COLS, CHESSBOARD_ROWS),
                corners_subpix,
                ret
            )

            # === GUARDAR IMAGEN CON ESQUINAS DETECTADAS ===
            out_name = os.path.basename(fname)
            out_path = os.path.join(OUTPUT_CORNERS_DIR, out_name)
            cv2.imwrite(out_path, img)
            print(f"💾 Guardada (esquinas): {out_path}")

            cv2.imshow("Esquinas detectadas", img)
            cv2.waitKey(150)

        else:
            print(f"⚠️ No se detectó patrón en: {fname}")

    cv2.destroyAllWindows()

    if gray is None or len(objpoints) < 3:
        print("❌ No hay suficientes imágenes válidas para calibrar.")
        return None, None, None, None

    image_size = gray.shape[::-1]
    print("\n📏 Calibrando cámara…")

    rms, K, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints,
        imgpoints,
        image_size,
        None,
        None
    )

    print("\n✅ Calibración completada")
    print("RMS:", rms)
    print("K:\n", K)
    print("dist:\n", dist)

    # Guardar datos
    np.savez(
        OUTPUT_FILE_NPZ,
        K=K,
        dist=dist,
        rvecs=rvecs,
        tvecs=tvecs,
        rms=rms,
        image_size=image_size
    )

    cv_file = cv2.FileStorage(OUTPUT_FILE_YAML, cv2.FILE_STORAGE_WRITE)
    cv_file.write("K", K)
    cv_file.write("dist", dist)
    cv_file.write("rms", float(rms))
    cv_file.release()

    print(f"💾 Parámetros guardados en {OUTPUT_FILE_NPZ} y {OUTPUT_FILE_YAML}")

    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(
            objpoints[i], rvecs[i], tvecs[i], K, dist
        )
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
        mean_error += error

    mean_error /= len(objpoints)
    print("Error medio de reproyección:", mean_error)

    return K, dist, image_size, rms


if __name__ == "__main__":
    calibrate_camera_from_folder(IMAGES_DIR)
