"""
Detector dinámico de items configurables.
Cada item tiene su propio rango HSV.
"""

import cv2
import numpy as np
import mss
import json
import os


class ROItemDetector:
    def __init__(self, config_path='ro_items_config.json'):
        self.sct = mss.mss()
        self.items_config = self.load_items_config(config_path)
        self.min_contour_area = 50
        self.max_contour_area = 2000

    def load_items_config(self, config_path):
        """Carga la configuración de items desde JSON."""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        print(f"Advertencia: No se encontró {config_path}")
        return {}

    def capture_screen(self, region=None):
        """Captura pantalla."""
        if region is None:
            region = self.sct.monitors[1]
        
        screenshot = self.sct.grab(region)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def detect_item_type(self, frame, item_name):
        """
        Detecta un tipo específico de item por su rango de color HSV.
        
        Args:
            frame: Imagen capturada
            item_name: Nombre del item (debe estar en ro_items_config.json)
        
        Returns:
            Lista de items detectados: [{'center': (x, y), 'confidence': 0.9}, ...]
        """
        if item_name not in self.items_config:
            return []
        
        item_config = self.items_config[item_name]
        
        if not item_config.get('enabled', True):
            return []
        
        lower = np.array(item_config['lower'])
        upper = np.array(item_config['upper'])
        
        # Convertir a HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Crear máscara
        mask = cv2.inRange(hsv, lower, upper)
        
        # Operaciones morfológicas
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        items = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if area < self.min_contour_area or area > self.max_contour_area:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            center = (x + w // 2, y + h // 2)
            
            # Calcular confianza basada en el área
            confidence = min(area / self.max_contour_area, 1.0)
            
            items.append({
                'center': center,
                'confidence': confidence,
                'x': x,
                'y': y,
                'w': w,
                'h': h
            })
        
        return items

    def detect_all_items(self, frame):
        """
        Detecta todos los items configurados en la pantalla.
        
        Returns:
            Dict con items encontrados y su información
        """
        all_items = {}
        
        for item_name in self.items_config:
            items = self.detect_item_type(frame, item_name)
            if items:
                all_items[item_name] = items
        
        return all_items

    def get_nearest_item_by_type(self, frame, item_name, center_x=640, center_y=480):
        """
        Obtiene el item más cercano de un tipo específico.
        
        Returns:
            Dict con el item más cercano o None
        """
        items = self.detect_item_type(frame, item_name)
        
        if not items:
            return None
        
        # Calcular distancia desde el centro
        for item in items:
            ix, iy = item['center']
            distance = np.sqrt((ix - center_x)**2 + (iy - center_y)**2)
            item['distance'] = distance
        
        # Retornar el más cercano
        items.sort(key=lambda i: i['distance'])
        return items[0]

    def debug_visualization(self, frame, output_path="debug_items.png"):
        """Crea imagen de debug mostrando items detectados."""
        debug_frame = frame.copy()
        
        all_items = self.detect_all_items(frame)
        
        colors = {
            'Jellopy': (255, 0, 0),      # Azul
            'Carta': (0, 255, 255),      # Amarillo
            'Poción': (0, 0, 255),       # Rojo
            'Empty_Bottle': (255, 255, 0),  # Cyan
            'Apple': (0, 165, 255)       # Naranja
        }
        
        for item_name, items in all_items.items():
            color = colors.get(item_name, (0, 255, 0))
            
            for i, item in enumerate(items):
                center = item['center']
                x, y, w, h = item['x'], item['y'], item['w'], item['h']
                
                # Dibujar bounding box
                cv2.rectangle(debug_frame, (x, y), (x+w, y+h), color, 2)
                
                # Dibujar centro
                cv2.circle(debug_frame, center, 3, color, -1)
                
                # Etiqueta
                label = f"{item_name} ({item['confidence']:.2f})"
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
    all_items = detector.detect_all_items(frame)
    
    print(f"\n✓ Items detectados:")
    for item_name, items in all_items.items():
        print(f"  {item_name}: {len(items)} encontrados")
        for i, item in enumerate(items):
            print(f"    #{i+1}: Posición={item['center']}, Confianza={item['confidence']:.2f}")
    
    detector.debug_visualization(frame)
