import time
import random
from ro_detector import RODetector
from ro_yolo_detector import ROYoloDetector
from ro_controller import ROController
from ro_map_intelligence import ROMapIntelligence
import os

class ROBot:
    def __init__(self, monster_templates=None, item_templates=None, learning_mode=False, use_yolo=False, map_name="default_map"):
        self.map_intel = ROMapIntelligence(map_name=map_name)
        # Intentar cargar YOLO si se solicita y el modelo existe
        model_path = "/home/ubuntu/models/ro_best.pt"
        if use_yolo and os.path.exists(model_path):
            self.detector = ROYoloDetector(model_path)
            print("Usando detector YOLOv8 avanzado.")
        else:
            self.detector = RODetector(monster_templates, item_templates, learning_mode=learning_mode)
            print("Usando detector estándar (Template Matching).")
            
        self.controller = ROController()
        self.running = False
        self.state = "IDLE" # Estados: IDLE, BUSCANDO, ATACANDO, RECOGIENDO, CURANDO
        self.hp_threshold = 50 # Porcentaje de HP para usar poción
        self.potion_key = 'f1'

    def run(self):
        """Bucle principal del bot."""
        print("Iniciando el asistente de IA para Ragnarok Online...")
        self.running = True
        self.start_time = time.time()
        self.last_break = time.time()
        
        while self.running:
            # Simular descansos humanos aleatorios
            current_time = time.time()
            if current_time - self.last_break > random.randint(1800, 3600): # Descanso cada 30-60 min
                break_duration = random.randint(60, 300) # Descanso de 1-5 min
                print(f"Tomando un descanso humano de {break_duration} segundos...")
                time.sleep(break_duration)
                self.last_break = time.time()

            frame = self.detector.capture_screen()
            
            # 1. Verificar Salud (Prioridad Máxima)
            hp_info = self.detector.detect_hp_bar(frame)
            if hp_info and hp_info['percent'] < self.hp_threshold:
                self.state = "CURANDO"
                self.controller.use_potion(self.potion_key)
                time.sleep(0.5) # Pequeña pausa tras curarse
                continue

            # 2. Buscar Ítems (Prioridad Media)
            items = self.detector.detect_items(frame) if hasattr(self.detector, 'detect_items') else []
            if items:
                self.state = "RECOGIENDO"
                target_item = items[0]
                self.map_intel.record_spawn(target_item['label'], target_item['center'][0], target_item['center'][1])
                self.controller.pick_up(target_item['center'][0], target_item['center'][1])
                time.sleep(1.0)
                continue

            # 3. Buscar Monstruos (Prioridad Baja)
            monsters = self.detector.detect_monsters(frame) if hasattr(self.detector, 'detect_monsters') else self.detector.detect_objects(frame)
            if monsters:
                self.state = "ATACANDO"
                target_monster = monsters[0]
                self.map_intel.record_spawn(target_monster['label'], target_monster['center'][0], target_monster['center'][1])
                self.controller.attack(target_monster['center'][0], target_monster['center'][1])
                time.sleep(2.0) 
                continue

            # 4. Si no hay nada, moverse a la mejor zona de farmeo o aleatoriamente
            self.state = "BUSCANDO"
            best_spot = self.map_intel.get_best_farming_spot()
            
            if best_spot:
                print(f"No hay objetivos. Moviendo a zona de alta densidad: {best_spot}")
                self.controller.move_character(best_spot[0], best_spot[1])
            else:
                print("No se detectaron objetivos ni zonas conocidas. Explorando...")
                screen_w, screen_h = frame.shape[1], frame.shape[0]
                rand_x = random.randint(int(screen_w * 0.3), int(screen_w * 0.7))
                rand_y = random.randint(int(screen_h * 0.3), int(screen_h * 0.7))
                self.controller.move_character(rand_x, rand_y)
            
            time.sleep(3.0)

    def stop(self):
        self.running = False
        print("Asistente detenido.")

if __name__ == "__main__":
    # Para ejecutar el bot, se necesitarían los templates de imágenes
    # bot = ROBot(monster_templates=['monster1.png'], item_templates=['item1.png'])
    # bot.run()
    print("Lógica del bot cargada. Se requieren imágenes de referencia para funcionar.")