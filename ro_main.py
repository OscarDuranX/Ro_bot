"""
Script principal del RO_Bot V2.0
Ejecutar con: python ro_main.py
"""

import json
import os
import sys
import time

# Intentar importar el bot
try:
    from ro_bot_v2 import ROBotV2
except ImportError as e:
    print(f"Error: No se pudo importar ro_bot_v2.py")
    print(f"Detalle: {e}")
    sys.exit(1)


def check_requirements():
    """Verifica que estén instaladas todas las dependencias necesarias."""
    print("🔍 Verificando dependencias...\n")
    
    required_modules = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'mss': 'mss',
        'pydirectinput': 'pydirectinput'
    }
    
    missing = []
    
    for module, package in required_modules.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NO INSTALADO")
            missing.append(package)
    
    # Verificar pytesseract (opcional pero recomendado)
    try:
        import pytesseract
        print(f"  ✓ pytesseract (OCR para HP)")
    except ImportError:
        print(f"  ⚠ pytesseract (OCR) - NO INSTALADO (recomendado para mejor detección de HP)")
    
    print()
    
    if missing:
        print("❌ FALTAN DEPENDENCIAS:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True


def check_config_files():
    """Verifica que existan los archivos de configuración."""
    print("📁 Verificando archivos de configuración...\n")
    
    required_files = [
        'ro_config.json',
        'ro_items_config.json'
    ]
    
    missing = []
    
    for filename in required_files:
        if os.path.exists(filename):
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} - NO ENCONTRADO")
            missing.append(filename)
    
    print()
    
    if missing:
        print(f"❌ FALTAN ARCHIVOS DE CONFIGURACIÓN")
        return False
    
    return True


def main():
    print("\n" + "="*60)
    print("🎮 RO_BOT V2.0 - SETUP INICIAL")
    print("="*60 + "\n")
    
    # Verificar dependencias
    if not check_requirements():
        print("❌ Por favor instala las dependencias:")
        print("   pip install -r requirements.txt")
        print("   (También necesitas Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki)")
        return
    
    # Verificar archivos de configuración
    if not check_config_files():
        print("❌ Por favor descarga los archivos de configuración faltantes")
        return
    
    print("✓ Todas las verificaciones pasaron correctamente!\n")
    
    # Iniciar el bot
    try:
        bot = ROBotV2()
        bot.run()
    except KeyboardInterrupt:
        print("\n\n❌ Bot detenido por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error en el bot: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
