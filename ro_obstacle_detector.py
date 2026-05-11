"""
Detector de obstáculos (muros) en el mapa.
Evita que el bot clickee en zonas oscuras/negras.
"""

import cv2
import numpy as np
import mss


class ROObstacleDetector:
    def __init__(self):
        self.sct = mss.mss()
        
        # Umbral de oscuridad para detectar obstáculos
        # Los muros son muy oscuros (BGR bajo)
        self.darkness_threshold = 50
        
        # Tamaño del kernel para operaciones morfológicas
        self.kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    def capture_screen(self, region=None):
        """Captura pantalla."""
        if region is None:
            region = self.sct.monitors[1]
        
        screenshot = self.sct.grab(region)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def is_walkable(self, frame, x, y, check_radius=5):
        """
        Verifica si una posición es caminable (no tiene obstáculo).
        Retorna True si es seguro clickear, False si hay muro.
        
        Args:
            frame: Imagen capturada
            x, y: Coordenadas a verificar
            check_radius: Radio de píxeles a verificar alrededor
        """
        h, w = frame.shape[:2]
        
        # Limitar coordenadas
        x1 = max(0, x - check_radius)
        y1 = max(0, y - check_radius)
        x2 = min(w, x + check_radius)
        y2 = min(h, y + check_radius)
        
        roi = frame[y1:y2, x1:x2]
        
        if roi.size == 0:
            return False
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Calcular brillo promedio
        average_brightness = np.mean(gray)
        
        # Si es muy oscuro, probablemente sea un muro
        if average_brightness < self.darkness_threshold:
            return False
        
        return True

    def find_safe_zone_near(self, frame, target_x, target_y, radius=30, step=5):
        """
        Si el objetivo tiene obstáculo, encuentra un punto seguro cercano.
        Busca en espiral alrededor del punto objetivo.
        
        Args:
            frame: Imagen capturada
            target_x, target_y: Punto objetivo
            radius: Radio máximo de búsqueda
            step: Paso de búsqueda
        
        Returns:
            Tupla (x, y) de punto seguro, o None si no encuentra
        """
        # Primero verificar el punto objetivo
        if self.is_walkable(frame, target_x, target_y):
            return (target_x, target_y)
        
        # Buscar en espiral
        for r in range(step, radius, step):
            for angle in range(0, 360, 30):  # 12 direcciones
                rad = np.radians(angle)
                check_x = int(target_x + r * np.cos(rad))
                check_y = int(target_y + r * np.sin(rad))
                
                if self.is_walkable(frame, check_x, check_y):
                    return (check_x, check_y)
        
        return None

    def create_walkable_mask(self, frame):
        """
        Crea una máscara indicando zonas caminables (blancas) vs obstáculos (negras).
        
        Returns:
            Imagen binaria (255=caminable, 0=obstáculo)
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Crear máscara: píxeles oscuros = obstáculos
        _, mask = cv2.threshold(gray, self.darkness_threshold, 255, cv2.THRESH_BINARY)
        
        # Aplicar operaciones morfológicas
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=1)
        
        return mask

    def debug_visualization(self, frame, output_path="debug_obstacles.png"):
        """Crea imagen de debug mostrando obstáculos detectados."""
        debug_frame = frame.copy()
        
        mask = self.create_walkable_mask(frame)
        
        # Convertir máscara a color (verde=caminable, rojo=obstáculo)
        mask_color = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        mask_color[mask == 0] = [0, 0, 255]  # Rojo para obstáculos
        mask_color[mask == 255] = [0, 255, 0]  # Verde para caminable
        
        # Mezclar con frame original
        debug_frame = cv2.addWeighted(debug_frame, 0.5, mask_color, 0.5, 0)
        
        cv2.imwrite(output_path, debug_frame)
        print(f"Debug obstacles image saved: {output_path}")
        
        return debug_frame


if __name__ == "__main__":
    detector = ROObstacleDetector()
    
    print("Capturando pantalla...")
    frame = detector.capture_screen()
    
    print("Analizando obstáculos...")
    
    # Probar algunos puntos
    test_points = [(640, 480), (500, 400), (800, 600)]
    
    for x, y in test_points:
        walkable = detector.is_walkable(frame, x, y)
        print(f"  Punto ({x}, {y}): {'✓ Caminable' if walkable else '✗ Obstáculo'}")
        
        if not walkable:
            safe = detector.find_safe_zone_near(frame, x, y)
            if safe:
                print(f"    Punto seguro cercano: {safe}")
    
    detector.debug_visualization(frame)
