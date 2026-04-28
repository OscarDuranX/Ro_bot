import cv2
import numpy as np
import mss
import time
import os

# Nota: Para usar este script, el usuario debe instalar ultralytics: pip install ultralytics
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

class ROYoloDetector:
    def __init__(self, model_path="/home/ubuntu/models/ro_best.pt"):
        self.sct = mss.mss()
        self.model_path = model_path
        self.model = None
        if YOLO and os.path.exists(self.model_path):
            self.model = YOLO(self.model_path)
            print(f"Modelo YOLOv8 cargado desde {self.model_path}")
        else:
            print("Aviso: YOLOv8 no instalado o modelo no encontrado. Usando modo de espera.")

    def capture_screen(self, region=None):
        if region is None:
            region = self.sct.monitors[1]
        screenshot = self.sct.grab(region)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def detect_objects(self, frame):
        """Detecta objetos usando el modelo YOLOv8 entrenado."""
        if not self.model:
            return []
            
        results = self.model(frame, verbose=False)
        detections = []
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Obtener coordenadas, confianza y clase
                x1, y1, x2, y2 = box.xyxy[0]
                conf = box.conf[0]
                cls = int(box.cls[0])
                label = self.model.names[cls]
                
                detections.append({
                    'label': label,
                    'x': int(x1),
                    'y': int(y1),
                    'w': int(x2 - x1),
                    'h': int(y2 - y1),
                    'center': (int((x1 + x2) / 2), int((y1 + y2) / 2)),
                    'confidence': float(conf)
                })
        return detections

if __name__ == "__main__":
    detector = ROYoloDetector()
    print("Detector YOLOv8 inicializado.")
