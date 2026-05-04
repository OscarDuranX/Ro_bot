"""
Detector especializado para monstruos basado en barras de HP.
Detecta las barras HP roja/amarilla debajo de los monstruos.
Prioriza el monstruo más cercano al personaje.
"""

import cv2
import numpy as np
import mss


class ROMonsterDetector:
    def __init__(self):
        self.sct = mss.mss()
        
        # Rango de color para barra HP (rojo/amarillo)
        # En BGR: Rojo es (0, 0, 255)
        self.lower_red = np.array([0, 0, 150])
        self.upper_red = np.array([100, 100, 255])
        
        # Parámetros de detección
        self.min_bar_width = 20     # Ancho mínimo de barra
        self.max_bar_width = 100    # Ancho máximo de barra
        self.min_bar_height = 3     # Altura mínima de barra
        self.max_bar_height = 8     # Altura máxima de barra
        
        self.center_x = 640  # Centro de pantalla (1280/2)
        self.center_y = 480  # Centro de pantalla (960/2)

    def capture_screen(self, region=None):
        """Captura pantalla."""
        if region is None:
            region = self.sct.monitors[1]
        
        screenshot = self.sct.grab(region)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def detect_monsters(self, frame, max_distance=300):
        """
        Detecta monstruos buscando barras de HP roja/amarilla.
        
        Args:
            frame: Imagen capturada
            max_distance: Distancia máxima desde el centro (en píxeles)
        
        Returns:
            Lista de monstruos detectados, ordenados por distancia
        """
        monsters = []
        
        # Convertir a HSV para mejor detección de rojo
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Crear máscara para rojo
        # El rojo en HSV puede estar en dos rangos
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        
        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Aplicar operaciones morfológicas
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 2))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return monsters
        
        # Procesar contornos como barras de HP
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filtrar por tamaño (debe parecer una barra)
            if w < self.min_bar_width or w > self.max_bar_width:
                continue
            if h < self.min_bar_height or h > self.max_bar_height:
                continue
            
            # Centro de la barra
            bar_center_x = x + w // 2
            bar_center_y = y + h // 2
            
            # Calcular distancia desde el centro de pantalla
            distance = np.sqrt((bar_center_x - self.center_x)**2 + (bar_center_y - self.center_y)**2)
            
            if distance > max_distance:
                continue
            
            # Calcular HP aproximado (por ancho de barra verde restante)
            # Buscar parte verde de la barra (HP restante)
            roi = frame[max(0, y-10):min(frame.shape[0], y+h+10), 
                       max(0, x):min(frame.shape[1], x+w)]
            
            if roi.size == 0:
                hp_percent = 50  # Default
            else:
                # Contar píxeles verdes en la región (HP actual)
                hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                lower_green = np.array([35, 40, 40])
                upper_green = np.array([90, 255, 255])
                mask_green = cv2.inRange(hsv_roi, lower_green, upper_green)
                green_pixels = cv2.countNonZero(mask_green)
                total_pixels = mask_green.shape[0] * mask_green.shape[1]
                
                if total_pixels > 0:
                    hp_percent = (green_pixels / total_pixels) * 100
                else:
                    hp_percent = 50
            
            monster = {
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "center": (bar_center_x, bar_center_y),
                "distance": distance,
                "hp_percent": max(0, min(100, hp_percent)),
                "confidence": 0.85
            }
            
            monsters.append(monster)
        
        # Ordenar por distancia (más cercano primero)
        monsters.sort(key=lambda m: m['distance'])
        
        return monsters

    def get_nearest_monster(self, frame, max_distance=300):
        """
        Retorna el monstruo más cercano o None.
        
        Returns:
            Dict con datos del monstruo más cercano o None
        """
        monsters = self.detect_monsters(frame, max_distance)
        
        if monsters:
            return monsters[0]
        
        return None

    def debug_visualization(self, frame, monsters, output_path="debug_monsters.png"):
        """Crea imagen de debug mostrando los monstruos detectados."""
        debug_frame = frame.copy()
        
        # Dibujar centro de pantalla
        center = (self.center_x, self.center_y)
        cv2.circle(debug_frame, center, 5, (0, 255, 0), -1)
        cv2.circle(debug_frame, center, 300, (0, 255, 0), 2)  # Radio máximo
        
        # Dibujar cada monstruo
        for i, monster in enumerate(monsters):
            x, y, w, h = monster['x'], monster['y'], monster['w'], monster['h']
            center_mon = monster['center']
            distance = monster['distance']
            hp = monster['hp_percent']
            
            # Bounding box
            color = (0, 255, 0) if i == 0 else (0, 165, 255)  # Verde si es el más cercano, naranja si no
            cv2.rectangle(debug_frame, (x, y), (x+w, y+h), color, 2)
            
            # Centro
            cv2.circle(debug_frame, center_mon, 3, color, -1)
            
            # Línea hacia el centro
            cv2.line(debug_frame, center, center_mon, color, 1)
            
            # Etiqueta
            label = f"M#{i+1} HP:{hp:.0f}% D:{distance:.0f}px"
            cv2.putText(debug_frame, label, (x, y-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        cv2.imwrite(output_path, debug_frame)
        print(f"Debug monsters image saved: {output_path}")
        
        return debug_frame


if __name__ == "__main__":
    detector = ROMonsterDetector()
    
    print("Capturando pantalla...")
    frame = detector.capture_screen()
    
    print("Detectando monstruos...")
    monsters = detector.detect_monsters(frame)
    
    print(f"\n✓ Se encontraron {len(monsters)} monstruos:")
    for i, m in enumerate(monsters):
        print(f"  #{i+1}: Posición=({m['center'][0]}, {m['center'][1]}), "
              f"HP={m['hp_percent']:.0f}%, Distancia={m['distance']:.0f}px")
    
    if monsters:
        detector.debug_visualization(frame, monsters)
