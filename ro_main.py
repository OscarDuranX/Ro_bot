import json
import os
import time
from ro_bot_logic import ROBot

def load_config(config_path='./ro_config.json'):
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return None

def main():
    print("--- Asistente de IA para Ragnarok Online ---")
    config = load_config()
    
    if not config:
        print("Error: No se encontró el archivo de configuración.")
        return

    # Inicializar el bot con la configuración cargada
    bot = ROBot(
        monster_templates=config.get('monster_templates', []),
        item_templates=config.get('item_templates', []),
        learning_mode=config.get('learning_mode', False),
        use_yolo=config.get('use_yolo', False)
    )
    
    # Aplicar otros parámetros de configuración
    bot.hp_threshold = config.get('hp_threshold', 50)
    bot.potion_key = config.get('potion_key', 'f1')
    
    print("\nConfiguración cargada:")
    print(f"- Monstruos a cazar: {len(bot.detector.monster_templates)}")
    print(f"- Ítems a recoger: {len(bot.detector.item_templates)}")
    print(f"- Umbral de HP: {bot.hp_threshold}%")
    print(f"- Tecla de poción: {bot.potion_key}")
    print(f"- Modo Aprendizaje: {'Activado' if getattr(bot.detector, 'learning_mode', False) else 'Desactivado'}")
    print(f"- Usar YOLOv8: {'Sí' if config.get('use_yolo', False) else 'No'}")
    
    print("\nEl asistente comenzará en 5 segundos. Por favor, abre la ventana de Ragnarok Online.")
    time.sleep(5)
    
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.stop()
        print("\nAsistente detenido por el usuario.")

if __name__ == "__main__":
    main()
