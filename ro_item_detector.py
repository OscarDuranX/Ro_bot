"""
Detector especializado para items basado en color HSV.
Detecta items dinámicamente según configuración en ro_items_config.json
"""

import cv2
import numpy as np
import mss
import json
import os


class ROItemDetector:
    def __init__(self, config_path="ro_items_config.json"):
        self.sct = mss.mss()
        self.config_path = config_path
        self.items_config = self._load_config()
        
        self.center_x = 640
        self.center_y = 480

    def _load_config(self):
        """Carga la configuración de items desde JSON."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def capture_screen(self, region=None):
        """Captura pantalla."""
        if region is None:
            region = self.sct.monitors[1]
        
        screenshot = self.sct.grab(region)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def detect_items(self, frame, max_distance=200):
        """
        Detecta todos los items configurados.
        
        Args:
            frame: Imagen capturada
            max_distance: Distancia máxima desde el centro (píxeles)
        
        Returns:
            Lista de items detectados, ordenados por distancia
        """
        all_items = []
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        for item_name, item_config in self.items_config.items():
            if not item_config.get("enabled", True):
                continue
            
            lower = np.array(item_config.get("lower", [0, 0, 0]))
            upper = np.array(item_config.get("upper", [180, 255, 255]))
            
            mask = cv2.inRange(hsv, lower, upper)
            
            # Operaciones morfológicas
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filtrar por área (item mínimo 50px², máximo 2000px²)
                if area < 50 or area > 2000:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2
                
                # Calcular distancia desde centro de pantalla
                distance = np.sqrt((center_x - self.center_x)**2 + (center_y - self.center_y)**2)
                
                if distance > max_distance:
                    continue
                
                item = {
                    "name": item_name,
                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h,
                    "center": (center_x, center_y),
                    "distance": distance,
                    "area": area,
                    "confidence": 0.90,
                    "priority": item_config.get("priority", 5)
                }
                
                all_items.append(item)
        
        # Eliminar duplicados (items muy cercanos)
        all_items = self._remove_duplicates(all_items)
        
        # Ordenar por prioridad (menor número = más prioritario), luego por distancia
        all_items.sort(key=lambda x: (x['priority'], x['distance']))
        
        return all_items

    def _remove_duplicates(self, items, threshold=20):
        """Elimina detecciones duplicadas muy cercanas."""
        if not items:
            return items
        
        filtered = []
        for item in items:
            is_duplicate = False
            for existing in filtered:
                dist = np.sqrt((item['center'][0] - existing['center'][0])**2 + 
                             (item['center'][1] - existing['center'][1])**2)
                if dist < threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(item)
        
        return filtered

    def get_nearest_item(self, frame, max_distance=200):
        """Retorna el item más cercano o None."""
        items = self.detect_items(frame, max_distance)
        
        if items:
            return items[0]
        
        return None

    def get_items_by_name(self, frame, item_name, max_distance=200):
        """Retorna todos los items de un tipo específico."""
        items = self.detect_items(frame, max_distance)
        return [item for item in items if item['name'] == item_name]

    def debug_visualization(self, frame, items, output_path="debug_items.png"):
        """Crea imagen de debug mostrando items detectados."""
        debug_frame = frame.copy()
        
        # Dibujar centro de pantalla
        center = (self.center_x, self.center_y)
        cv2.circle(debug_frame, center, 5, (0, 255, 0), -1)
        cv2.circle(debug_frame, center, 200, (0, 255, 0), 2)
        
        # Colores para debug
        colors = [
            (0, 255, 0),    # Verde
            (0, 165, 255),  # Naranja
            (255, 0, 0),    # Azul
            (255, 255, 0),  # Cyan
            (255, 0, 255)   # Magenta
        ]
        
        # Dibujar cada item
        for i, item in enumerate(items):
            x, y, w, h = item['x'], item['y'], item['w'], item['h']
            center_item = item['center']
            
            color = colors[i % len(colors)]
            
            # Bounding box
            cv2.rectangle(debug_frame, (x, y), (x+w, y+h), color, 2)
            
            # Centro
            cv2.circle(debug_frame, center_item, 3, color, -1)
            
            # Línea hacia el centro
            cv2.line(debug_frame, center, center_item, color, 1)
            
            # Etiqueta
            label = f"{item['name']}#{i+1} D:{item['distance']:.0f}px"
            cv2.putText(debug_frame, label, (x, y-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        cv2.imwrite(output_path, debug_frame)
        print(f"Debug items image saved: {output_path}")
        
        return debug_frame


if __name__ == "__main__":
    detector = ROItemDetector()
    
    print("Capturando pantalla...")
    frame = detector.capture_screen()
    
    print("Detectando items...")
    items = detector.detect_items(frame)
    
    print(f"\n✓ Se encontraron {len(items)} items:")
    for i, item in enumerate(items):
        print(f"  #{i+1}: {item['name']} en ({item['center'][0]}, {item['center'][1]}), "
              f"Distancia={item['distance']:.0f}px, Prioridad={item['priority']}")
    
    if items:
        detector.debug_visualization(frame, items)
