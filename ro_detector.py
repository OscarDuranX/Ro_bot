import cv2
import numpy as np
import mss
import time
import os


class RODetector:
    def __init__(self, monster_templates=None, item_templates=None, learning_mode=False):
        self.sct = mss.mss()
        self.monster_templates = monster_templates if monster_templates else []
        self.item_templates = item_templates if item_templates else []
        self.threshold = 0.7  # Umbral de confianza base
        self.learning_mode = learning_mode

        # Carpeta para dataset relativa al proyecto
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.dataset_path = os.path.join(base_dir, "dataset", "raw")
        if self.learning_mode and not os.path.exists(self.dataset_path):
            os.makedirs(self.dataset_path, exist_ok=True)

    def capture_screen(self, region=None):
        """Captura una región de la pantalla o la pantalla completa."""
        # Si no se especifica región, capturar el monitor principal
        if region is None:
            region = self.sct.monitors[1]

        screenshot = self.sct.grab(region)
        # Convertir a formato compatible con OpenCV (BGR)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def detect_objects(self, frame, templates, label="Objeto", base_threshold=None):
        """Detecta objetos en un frame usando Template Matching."""
        detections = []

        # Umbral por defecto
        if base_threshold is None:
            base_threshold = self.threshold

        current_threshold = base_threshold
        # Si quisieras usar learning_mode, puedes bajar un poco el umbral (opcional)
        if self.learning_mode:
            current_threshold = base_threshold * 0.9

        for template_path in templates:
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                print(f"Error: No se pudo cargar el template {template_path}")
                continue

            h, w = template.shape[:2]
            res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= current_threshold)

            for pt in zip(*loc[::-1]):
                # Evitar detecciones duplicadas muy cercanas
                is_duplicate = False
                for d in detections:
                    if abs(d['x'] - pt[0]) < w / 2 and abs(d['y'] - pt[1]) < h / 2:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    conf = res[pt[1], pt[0]]
                    detection = {
                        "label": label,
                        "x": pt[0],
                        "y": pt[1],
                        "w": w,
                        "h": h,
                        "center": (pt[0] + w // 2, pt[1] + h // 2),
                        "confidence": float(conf),
                    }
                    detections.append(detection)

                    # Guardar para el dataset si estamos en modo aprendizaje
                    if self.learning_mode:
                        self._save_to_dataset(frame, detection)

        return detections

    def _save_to_dataset(self, frame, detection):
        """Guarda un recorte del objeto detectado para entrenamiento futuro."""
        x, y, w, h = detection["x"], detection["y"], detection["w"], detection["h"]
        # Añadir un pequeño margen al recorte
        margin = 10
        y1, y2 = max(0, y - margin), min(frame.shape[0], y + h + margin)
        x1, x2 = max(0, x - margin), min(frame.shape[1], x + w + margin)

        crop = frame[y1:y2, x1:x2]
        timestamp = int(time.time() * 1000)
        filename = f"{detection['label']}_{timestamp}_{detection['confidence']:.2f}.png"
        os.makedirs(self.dataset_path, exist_ok=True)
        cv2.imwrite(os.path.join(self.dataset_path, filename), crop)

    def detect_monsters(self, frame):
        # Usar el umbral base para monstruos
        return self.detect_objects(frame, self.monster_templates, label="Monstruo")

    def detect_items(self, frame):
        # Usar un umbral más alto para ítems para reducir falsos positivos
        return self.detect_objects(frame, self.item_templates, label="Item", base_threshold=0.9)

    def detect_hp_bar(self, frame,
                      hp_roi=(298, 58, 511, 119),   # AJUSTA ESTOS VALORES A TU PANTALLA
                      full_hp_width=134):          # ANCHO DE LA BARRA AL 100% HP
        """
        Detecta la barra de HP azul en una región fija de la UI y devuelve
        un porcentaje real de 0 a 100.
        """
        x1, y1, x2, y2 = hp_roi
        hp_region = frame[y1:y2, x1:x2]

        # 1. Pasar a HSV y crear máscara de AZULES
        hsv = cv2.cvtColor(hp_region, cv2.COLOR_BGR2HSV)
        # Rango de azules (ajusta si hace falta según tu barra)
        lower_blue = np.array([90, 80, 80])
        upper_blue = np.array([130, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # 2. Buscar contornos dentro de la región de HP
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Coger el contorno más grande (la barra)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Filtro para evitar ruido
        if w < 10 or h < 4:
            return None

        # 3. Calcular porcentaje real usando el ancho máximo de la barra
        percent = max(0.0, min(100.0, (w / float(full_hp_width)) * 100.0))

        # Debug opcional
        print(f"[HP DEBUG] w={w}, full={full_hp_width}, percent={percent:.1f}%")

        return {
            "x": x1 + x,
            "y": y1 + y,
            "w": w,
            "h": h,
            "percent": percent,
        }


if __name__ == "__main__":
    detector = RODetector()
    print("Iniciando captura de prueba...")
    start_time = time.time()
    frame = detector.capture_screen()
    end_time = time.time()
    print(f"Captura completada en {end_time - start_time:.4f} segundos.")