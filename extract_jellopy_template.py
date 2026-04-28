"""
Herramienta para extraer automáticamente el template de Jellopy.
Ofrece 3 opciones:
1. GUI interactiva (click en Jellopy)
2. Coordenadas manuales
3. Ver template actual
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path


class JellopyTemplateExtractor:
    def __init__(self):
        self.template_path = "./assets/items/jellopy.png"
        self.screenshot_path = None
        self.mouse_x = None
        self.mouse_y = None
        self.dragging = False
        self.start_x = None
        self.start_y = None
    
    def create_assets_dir(self):
        """Crea la carpeta assets/items si no existe."""
        Path("./assets/items").mkdir(parents=True, exist_ok=True)
    
    def mouse_callback(self, event, x, y, flags, param):
        """Callback para eventos del mouse."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start_x = x
            self.start_y = y
            self.dragging = True
            print(f"📍 Inicio: ({x}, {y})")
        
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            self.mouse_x = x
            self.mouse_y = y
        
        elif event == cv2.EVENT_LBUTTONUP:
            self.mouse_x = x
            self.mouse_y = y
            self.dragging = False
            print(f"📍 Fin: ({x}, {y})")
    
    def extract_by_gui(self):
        """Opción 1: Extrae Jellopy usando interfaz gráfica (drag to select)."""
        print("\n" + "="*60)
        print("OPCIÓN 1: Extracción por GUI")
        print("="*60)
        
        screenshot_file = input("Ruta de la screenshot (ej: screenshot.png): ").strip()
        
        if not os.path.exists(screenshot_file):
            print(f"✗ Error: Archivo no encontrado: {screenshot_file}")
            return False
        
        img = cv2.imread(screenshot_file)
        if img is None:
            print(f"✗ Error: No se pudo cargar la imagen")
            return False
        
        print(f"\n✓ Imagen cargada: {img.shape}")
        print("\nInstrucciones:")
        print("1. Haz clic y arrastra para seleccionar el Jellopy azul")
        print("2. Presiona ESPACIO para confirmar o ESC para cancelar")
        
        display = img.copy()
        cv2.namedWindow("Selecciona el Jellopy", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Selecciona el Jellopy", self.mouse_callback)
        
        while True:
            frame = display.copy()
            
            # Dibujar rectángulo mientras se arrastra
            if self.dragging and self.mouse_x and self.mouse_y:
                cv2.rectangle(frame, (self.start_x, self.start_y), 
                            (self.mouse_x, self.mouse_y), (0, 255, 0), 2)
                cv2.putText(frame, f"({self.mouse_x}, {self.mouse_y})", 
                           (self.mouse_x + 10, self.mouse_y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            cv2.imshow("Selecciona el Jellopy", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # ESPACIO
                if self.start_x and self.mouse_x and self.start_y and self.mouse_y:
                    x1, y1 = min(self.start_x, self.mouse_x), min(self.start_y, self.mouse_y)
                    x2, y2 = max(self.start_x, self.mouse_x), max(self.start_y, self.mouse_y)
                    
                    jellopy = img[y1:y2, x1:x2]
                    cv2.destroyAllWindows()
                    return self.save_template(jellopy, f"({x1},{y1})-({x2},{y2})")
                else:
                    print("✗ Error: Debes seleccionar un área")
            
            elif key == 27:  # ESC
                print("⊘ Cancelado")
                cv2.destroyAllWindows()
                return False
    
    def extract_by_coordinates(self):
        """Opción 2: Extrae Jellopy usando coordenadas manuales."""
        print("\n" + "="*60)
        print("OPCIÓN 2: Extracción por Coordenadas")
        print("="*60)
        
        screenshot_file = input("Ruta de la screenshot (ej: screenshot.png): ").strip()
        
        if not os.path.exists(screenshot_file):
            print(f"✗ Error: Archivo no encontrado: {screenshot_file}")
            return False
        
        img = cv2.imread(screenshot_file)
        if img is None:
            print(f"✗ Error: No se pudo cargar la imagen")
            return False
        
        print(f"\n✓ Imagen cargada: {img.shape} (Alto x Ancho)")
        print("\nIntroduce las coordenadas de la esquina superior-izquierda y inferior-derecha del Jellopy")
        
        try:
            x1 = int(input("X inicial (columna izquierda): "))
            y1 = int(input("Y inicial (fila superior): "))
            x2 = int(input("X final (columna derecha): "))
            y2 = int(input("Y final (fila inferior): "))
        except ValueError:
            print("✗ Error: Las coordenadas deben ser números")
            return False
        
        # Validar coordenadas
        if x1 >= x2 or y1 >= y2:
            print("✗ Error: Coordenadas inválidas (x1 < x2 y y1 < y2)")
            return False
        
        if x2 > img.shape[1] or y2 > img.shape[0]:
            print("✗ Error: Coordenadas fuera de rango")
            return False
        
        jellopy = img[y1:y2, x1:x2]
        
        # Mostrar preview
        print(f"\nTamaño del template: {jellopy.shape}")
        print("Mostrando preview (cierra la ventana para continuar)...")
        cv2.imshow("Preview de Jellopy", jellopy)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return self.save_template(jellopy, f"({x1},{y1})-({x2},{y2})")
    
    def view_current_template(self):
        """Opción 3: Visualiza el template actual."""
        print("\n" + "="*60)
        print("OPCIÓN 3: Ver Template Actual")
        print("="*60)
        
        if not os.path.exists(self.template_path):
            print(f"✗ No hay template guardado en: {self.template_path}")
            return
        
        template = cv2.imread(self.template_path)
        if template is None:
            print(f"✗ Error al cargar: {self.template_path}")
            return
        
        print(f"✓ Template encontrado:")
        print(f"  Ruta: {self.template_path}")
        print(f"  Tamaño: {template.shape} (Alto x Ancho x Canales)")
        print(f"  Tamaño en píxeles: {template.shape[1]}x{template.shape[0]}")
        
        print("\nMostrando preview...")
        cv2.imshow("Template Jellopy Actual", template)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def save_template(self, jellopy_crop, coordinates):
        """Guarda el template extraído."""
        self.create_assets_dir()
        
        # Validar tamaño
        if jellopy_crop.shape[0] < 10 or jellopy_crop.shape[1] < 10:
            print("✗ Error: El tamaño es muy pequeño (mínimo 10x10 píxeles)")
            return False
        
        if jellopy_crop.shape[0] > 100 or jellopy_crop.shape[1] > 100:
            print("⚠ Advertencia: El tamaño es muy grande para un item")
            confirm = input("¿Continuar? (s/n): ").strip().lower()
            if confirm != 's':
                return False
        
        cv2.imwrite(self.template_path, jellopy_crop)
        
        print(f"\n✓ Template guardado exitosamente:")
        print(f"  Ruta: {self.template_path}")
        print(f"  Tamaño: {jellopy_crop.shape[0]}x{jellopy_crop.shape[1]} píxeles")
        print(f"  Coordenadas: {coordinates}")
        
        return True
    
    def run(self):
        """Menú principal."""
        while True:
            print("\n" + "="*60)
            print("🎮 EXTRACTOR DE TEMPLATE - JELLOPY")
            print("="*60)
            print("\n¿Cómo deseas extraer el template?")
            print("\n1. 🖱️  GUI Interactiva (drag to select)")
            print("2. ⌨️  Coordenadas Manuales")
            print("3. 👁️  Ver Template Actual")
            print("4. ❌ Salir")
            
            choice = input("\nOpción (1-4): ").strip()
            
            if choice == '1':
                if self.extract_by_gui():
                    print("\n✓ Template extraído correctamente")
                    break
            
            elif choice == '2':
                if self.extract_by_coordinates():
                    print("\n✓ Template extraído correctamente")
                    break
            
            elif choice == '3':
                self.view_current_template()
            
            elif choice == '4':
                print("\n✓ Saliendo...")
                sys.exit(0)
            
            else:
                print("✗ Opción inválida")


def main():
    print("\n")
    print("█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + "  🎮 HERRAMIENTA PARA EXTRAER TEMPLATE DE JELLOPY  ".center(58) + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60)
    
    extractor = JellopyTemplateExtractor()
    extractor.run()


if __name__ == "__main__":
    main()
