"""
Detector especializado para Jellopy y otros items con color específico.
Utiliza detección de color HSV + template matching híbrido.
Optimizado para items de tamaño fijo que caen al suelo.
"""

import cv2
import numpy as np
import mss
import time
import os


class ROJellopyDetector:
    """
    Detector especializado para Jellopy (items azules).
    Combina:
    1. Detección por color HSV (muy confiable para items azules)
    2. Template matching como validación secundaria
    3. Filtrado de ruido y duplicados
    """
    
    def __init__(self, jellopy_template_path="./assets/items/jellopy.png"):
        self.sct = mss.mss()
        self.jellopy_template_path = jellopy_template_path
        self.jellopy_template = None
        
        # Cargar template
        if os.path.exists(jellopy_template_path):
            self.jellopy_template = cv2.imread(jellopy_template_path, cv2.IMREAD_COLOR)
            if self.jellopy_template is not None:
                print(f"✓ Template de Jellopy cargado: {jellopy_template_path}")
                print(f"  Tamaño: {self.jellopy_template.shape}")
            else:
                print(f"✗ Error: No se pudo cargar la imagen en {jellopy_template_path}")
        else:
            print(f"⚠ Archivo de template no encontrado: {jellopy_template_path}")
        
        # Parámetros HSV para azul (Jellopy)
        # Jellopy es azul, así que nos enfocamos en ese rango
        self.lower_blue = np.array([90, 100, 80])      # Azul más oscuro
        self.upper_blue = np.array([130, 255, 255])    # Azul más claro
        
        # Parámetros de detección
        self.min_contour_area = 50      # Área mínima del contorno
        self.max_contour_area = 2000    # Área máxima del contorno
        self.template_threshold = 0.75  # Umbral para template matching
        
    def capture_screen(self, region=None):
        """Captura una región de la pantalla o la pantalla completa."""
        if region is None:
            region = self.sct.monitors[1]
        
        screenshot = self.sct.grab(region)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img
    
    def detect_by_color(self, frame, max_distance=50):
        """
        Detecta Jellopy usando filtro de color HSV.
        
        Args:
            frame: Imagen capturada
            max_distance: Distancia máxima en píxeles desde el centro (50px)
        
        Returns:
            Lista de detecciones encontradas
        """
        detections = []
        
        # Convertir a HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Crear máscara de azules
        mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        
        # Aplicar operaciones morfológicas para limpiar
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return detections
        
        # Procesar cada contorno
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filtrar por área
            if area < self.min_contour_area or area > self.max_contour_area:
                continue
            
            # Obtener bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calcular centro
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Verificar que esté dentro de la distancia máxima del centro de pantalla
            screen_center_x = frame.shape[1] // 2
            screen_center_y = frame.shape[0] // 2
            distance = np.sqrt((center_x - screen_center_x)**2 + (center_y - screen_center_y)**2)
            
            if distance > max_distance:
                continue
            
            # Calcular cirularidad (items suelen ser más redondos)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter ** 2)
            
            # Items azules suelen tener circularity entre 0.5 y 1.0
            # Si es muy alargado (< 0.3) o extraño, lo descartamos
            if circularity < 0.3:
                continue
            
            # Crear detección
            detection = {
                "label": "Jellopy",
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "center": (center_x, center_y),
                "area": area,
                "circularity": circularity,
                "distance": distance,
                "confidence": 0.95,  # Alta confianza al ser por color
                "method": "color_hsv"
            }
            
            detections.append(detection)
        
        return detections
    
    def detect_by_template(self, frame, max_distance=50):
        """
        Detecta Jellopy usando template matching como método secundario.
        
        Args:
            frame: Imagen capturada
            max_distance: Distancia máxima en píxeles
        
        Returns:
            Lista de detecciones encontradas
        """
        detections = []
        
        if self.jellopy_template is None:
            return detections
        
        template = self.jellopy_template
        h, w = template.shape[:2]
        
        # Template matching
        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= self.template_threshold)
        
        if len(locations[0]) == 0:
            return detections
        
        # Procesar matches
        screen_center_x = frame.shape[1] // 2
        screen_center_y = frame.shape[0] // 2
        
        for pt in zip(*locations[::-1]):
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2
            
            # Verificar distancia
            distance = np.sqrt((center_x - screen_center_x)**2 + (center_y - screen_center_y)**2)
            if distance > max_distance:
                continue
            
            confidence = result[pt[1], pt[0]]
            
            detection = {
                "label": "Jellopy",
                "x": pt[0],
                "y": pt[1],
                "w": w,
                "h": h,
                "center": (center_x, center_y),
                "confidence": float(confidence),
                "distance": distance,
                "method": "template_matching"
            }
            
            detections.append(detection)
        
        return detections
    
    def remove_duplicates(self, detections, threshold=15):
        """
        Elimina detecciones duplicadas muy cercanas.
        
        Args:
            detections: Lista de detecciones
            threshold: Distancia mínima entre centros para considerarlas diferentes
        
        Returns:
            Lista de detecciones sin duplicados
        """
        if not detections:
            return detections
        
        # Ordenar por confianza (descendente)
        sorted_detections = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        
        filtered = []
        for detection in sorted_detections:
            is_duplicate = False
            
            for existing in filtered:
                dx = detection['center'][0] - existing['center'][0]
                dy = detection['center'][1] - existing['center'][1]
                distance = np.sqrt(dx**2 + dy**2)
                
                if distance < threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(detection)
        
        return filtered
    
    def detect_jellopy(self, frame, max_distance=50, use_hybrid=True):
        """
        Detecta Jellopy usando uno o ambos métodos.
        
        Args:
            frame: Imagen capturada
            max_distance: Distancia máxima desde el centro (50px recomendado)
            use_hybrid: Si True, combina color + template matching
        
        Returns:
            Lista de detecciones Jellopy ordenadas por confianza
        """
        all_detections = []
        
        # Método 1: Detección por color (más confiable)
        color_detections = self.detect_by_color(frame, max_distance)
        all_detections.extend(color_detections)
        
        # Método 2: Template matching (validación adicional)
        if use_hybrid and self.jellopy_template is not None:
            template_detections = self.detect_by_template(frame, max_distance)
            all_detections.extend(template_detections)
        
        # Eliminar duplicados
        unique_detections = self.remove_duplicates(all_detections)
        
        # Ordenar por confianza
        unique_detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        return unique_detections
    
    def debug_visualization(self, frame, detections, output_path="debug_jellopy.png"):
        """
        Crea una imagen de debug mostrando las detecciones encontradas.
        Útil para troubleshooting.
        """
        debug_frame = frame.copy()
        
        # Centro de pantalla (referencia)
        screen_center = (frame.shape[1] // 2, frame.shape[0] // 2)
        cv2.circle(debug_frame, screen_center, 50, (0, 255, 0), 2)  # Círculo de 50px
        cv2.circle(debug_frame, screen_center, 3, (0, 255, 0), -1)  # Centro
        
        # Dibujar detecciones
        for i, det in enumerate(detections):
            x, y, w, h = det['x'], det['y'], det['w'], det['h']
            center = det['center']
            
            # Bounding box rojo
            cv2.rectangle(debug_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            
            # Centro azul
            cv2.circle(debug_frame, center, 3, (255, 0, 0), -1)
            
            # Etiqueta
            label = f"J#{i+1} ({det['confidence']:.2f})"
            cv2.putText(debug_frame, label, (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        cv2.imwrite(output_path, debug_frame)
        print(f"Debug image saved: {output_path}")
        
        return debug_frame


if __name__ == "__main__":
    # Test del detector
    detector = ROJellopyDetector()
    
    print("\nCapturando pantalla de prueba...")
    frame = detector.capture_screen()
    print(f"Tamaño de captura: {frame.shape}")
    
    print("\nDetectando Jellopy...")
    detections = detector.detect_jellopy(frame, max_distance=50)
    
    print(f"\n✓ Se encontraron {len(detections)} Jellopy:")
    for i, det in enumerate(detections):
        print(f"  #{i+1}: Centro=({det['center'][0]}, {det['center'][1]}), "
              f"Confianza={det['confidence']:.2f}, "
              f"Método={det['method']}")
    
    # Generar imagen de debug
    if detections:
        detector.debug_visualization(frame, detections)
