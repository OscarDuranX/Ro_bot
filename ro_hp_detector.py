"""
Detector especializado para la barra de HP del jugador.
Lee tanto por color como por OCR (Tesseract).
La barra está en la esquina superior izquierda.
"""

import cv2
import numpy as np
import mss
import os

try:
    import pytesseract
except ImportError:
    pytesseract = None


class ROHPDetector:
    def __init__(self):
        self.sct = mss.mss()
        
        # Posición de la barra de HP (esquina superior izquierda)
        # Basada en la captura: barra está en aproximadamente x:25-170, y:55-65
        self.hp_bar_region = {"left": 20, "top": 50, "width": 160, "height": 25}
        self.hp_text_region = {"left": 165, "top": 50, "width": 50, "height": 25}
        
        # Rango de color verde para la barra de HP
        self.lower_green = np.array([40, 40, 40])    # Verde oscuro en BGR
        self.upper_green = np.array([100, 255, 100])  # Verde claro en BGR
        
        # Configurar Tesseract si está disponible
        if pytesseract:
            try:
                # Windows
                pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            except:
                pass

    def capture_screen(self, region=None):
        """Captura una región de la pantalla."""
        if region is None:
            region = self.sct.monitors[1]
        
        screenshot = self.sct.grab(region)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def extract_hp_region(self, frame):
        """Extrae la región de la barra de HP."""
        h, w = frame.shape[:2]
        
        x1 = max(0, self.hp_bar_region["left"])
        y1 = max(0, self.hp_bar_region["top"])
        x2 = min(w, self.hp_bar_region["left"] + self.hp_bar_region["width"])
        y2 = min(h, self.hp_bar_region["top"] + self.hp_bar_region["height"])
        
        return frame[y1:y2, x1:x2]

    def extract_hp_text_region(self, frame):
        """Extrae la región del texto de HP (%)."""
        h, w = frame.shape[:2]
        
        x1 = max(0, self.hp_text_region["left"])
        y1 = max(0, self.hp_text_region["top"])
        x2 = min(w, self.hp_text_region["left"] + self.hp_text_region["width"])
        y2 = min(h, self.hp_text_region["top"] + self.hp_text_region["height"])
        
        return frame[y1:y2, x1:x2]

    def get_hp_by_color(self, frame):
        """
        Detecta HP por la proporción de color verde en la barra.
        Retorna: {'percent': float, 'confidence': float}
        """
        hp_region = self.extract_hp_region(frame)
        
        if hp_region.size == 0:
            return None
        
        # Convertir a HSV para mejor detección de verde
        hsv = cv2.cvtColor(hp_region, cv2.COLOR_BGR2HSV)
        
        # Rango verde en HSV
        lower_green_hsv = np.array([35, 40, 40])
        upper_green_hsv = np.array([90, 255, 255])
        
        mask = cv2.inRange(hsv, lower_green_hsv, upper_green_hsv)
        
        # Calcular porcentaje de píxeles verdes
        total_pixels = mask.shape[0] * mask.shape[1]
        green_pixels = cv2.countNonZero(mask)
        
        if total_pixels == 0:
            return None
        
        percentage = (green_pixels / total_pixels) * 100
        
        return {
            "percent": percentage,
            "confidence": 0.85,
            "method": "color"
        }

    def get_hp_by_ocr(self, frame):
        """
        Detecta HP leyendo el número directamente con OCR.
        Retorna: {'percent': float, 'confidence': float}
        """
        if not pytesseract:
            return None
        
        text_region = self.extract_hp_text_region(frame)
        
        if text_region.size == 0:
            return None
        
        # Mejorar contraste para OCR
        gray = cv2.cvtColor(text_region, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        try:
            text = pytesseract.image_to_string(thresh, config='--psm 6')
            text = text.strip()
            
            # Buscar número en el texto
            import re
            numbers = re.findall(r'\d+', text)
            
            if numbers:
                hp_percent = int(numbers[0])
                
                # Validar que sea un porcentaje válido
                if 0 <= hp_percent <= 100:
                    return {
                        "percent": float(hp_percent),
                        "confidence": 0.95,
                        "method": "ocr",
                        "text_read": text
                    }
        except Exception as e:
            print(f"Error en OCR: {e}")
        
        return None

    def get_hp_percentage(self, frame=None):
        """
        Obtiene el porcentaje de HP.
        Prioridad: OCR > Color
        Retorna: {'percent': float, 'method': str, 'confidence': float, 'is_low': bool}
        """
        if frame is None:
            frame = self.capture_screen()
        
        # Intentar OCR primero (más preciso)
        ocr_result = self.get_hp_by_ocr(frame)
        if ocr_result:
            ocr_result['is_low'] = ocr_result['percent'] < 50
            return ocr_result
        
        # Fallback a color
        color_result = self.get_hp_by_color(frame)
        if color_result:
            color_result['is_low'] = color_result['percent'] < 50
            return color_result
        
        return None

    def debug_visualization(self, frame, output_path="debug_hp.png"):
        """Crea imagen de debug mostrando la detección de HP."""
        debug_frame = frame.copy()
        
        # Dibujar región de barra de HP
        hp_region = self.hp_bar_region
        cv2.rectangle(debug_frame,
                     (hp_region["left"], hp_region["top"]),
                     (hp_region["left"] + hp_region["width"], hp_region["top"] + hp_region["height"]),
                     (0, 255, 0), 2)
        
        # Dibujar región de texto
        text_region = self.hp_text_region
        cv2.rectangle(debug_frame,
                     (text_region["left"], text_region["top"]),
                     (text_region["left"] + text_region["width"], text_region["top"] + text_region["height"]),
                     (255, 0, 0), 2)
        
        # Añadir texto con HP actual
        hp_info = self.get_hp_percentage(frame)
        if hp_info:
            label = f"HP: {hp_info['percent']:.1f}% ({hp_info['method']})"
            cv2.putText(debug_frame, label, (30, 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imwrite(output_path, debug_frame)
        print(f"Debug HP image saved: {output_path}")
        
        return debug_frame


if __name__ == "__main__":
    detector = ROHPDetector()
    
    print("Capturando pantalla...")
    frame = detector.capture_screen()
    
    print("Detectando HP...")
    hp_info = detector.get_hp_percentage(frame)
    
    if hp_info:
        print(f"✓ HP Detectado: {hp_info['percent']:.1f}%")
        print(f"  Método: {hp_info['method']}")
        print(f"  Confianza: {hp_info['confidence']:.2f}")
        print(f"  Estado: {'CRÍTICO' if hp_info['is_low'] else 'OK'}")
    else:
        print("✗ No se pudo detectar HP")
    
    detector.debug_visualization(frame)
