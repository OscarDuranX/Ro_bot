import time
import random
from ro_jellopy_detector import ROJellopyDetector
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
        
        # Detector especializado para Jellopy
        self.jellopy_detector = ROJellopyDetector()
        
        self.controller = ROController()
        self.running = False
        self.state = "IDLE"  # Estados: IDLE, BUSCANDO, ATACANDO, RECOGIENDO, CURANDO, RECOGIENDO_JELLOPY
        self.hp_threshold = 50  # Porcentaje de HP para usar poción
        self.potion_key = 'f1'
        self.jellopy_pickup_distance = 50  # Distancia máxima para recoger Jellopy

    def run(self):
        """Bucle principal del bot."""
        print("═" * 60)
        print("Iniciando el asistente de IA para Ragnarok Online...")
        print("═" * 60)
        self.running = True
        self.start_time = time.time()
        self.last_break = time.time()
        
        iteration = 0
        
        while self.running:
            iteration += 1
            
            # Simular descansos humanos aleatorios
            current_time = time.time()
            if current_time - self.last_break > random.randint(1800, 3600):  # Descanso cada 30-60 min
                break_duration = random.randint(60, 300)  # Descanso de 1-5 min
                print(f"\n⏰ Tomando un descanso humano de {break_duration} segundos...")
                time.sleep(break_duration)
                self.last_break = time.time()
                continue

            frame = self.detector.capture_screen()
            
            # 1. Verificar Salud (Prioridad Máxima)
            hp_info = self.detector.detect_hp_bar(frame)
            if hp_info and hp_info['percent'] < self.hp_threshold:
                self.state = "CURANDO"
                print(f"[{iteration}] ❤️ HP BAJO ({hp_info['percent']:.1f}%) - Usando poción...")
                self.controller.use_potion(self.potion_key)
                time.sleep(0.5)
                continue
            
            # 2. Buscar Jellopy (Prioridad Alta) ⭐
            jellopy_list = self.jellopy_detector.detect_jellopy(frame, max_distance=self.jellopy_pickup_distance)
            if jellopy_list:
                self.state = "RECOGIENDO_JELLOPY"
                target_jellopy = jellopy_list[0]  # Coger el más cercano/confiable
                print(f"[{iteration}] 💎 JELLOPY detectado en ({target_jellopy['center'][0]}, {target_jellopy['center'][1]}) "
                      f"- Confianza: {target_jellopy['confidence']:.2f}")
                self.map_intel.record_spawn("Jellopy", target_jellopy['center'][0], target_jellopy['center'][1])
                self.controller.pick_up(target_jellopy['center'][0], target_jellopy['center'][1])
                time.sleep(1.0)
                continue
            
            # 3. Buscar Ítems genéricos (Prioridad Media)
            items = self.detector.detect_items(frame) if hasattr(self.detector, 'detect_items') else []
            if items:
                self.state = "RECOGIENDO"
                target_item = items[0]
                print(f"[{iteration}] 📦 Item ({target_item['label']}) en ({target_item['center'][0]}, {target_item['center'][1]})")
                self.map_intel.record_spawn(target_item['label'], target_item['center'][0], target_item['center'][1])
                self.controller.pick_up(target_item['center'][0], target_item['center'][1])
                time.sleep(1.0)
                continue
            
            # 4. Buscar Monstruos (Prioridad Baja)
            monsters = self.detector.detect_monsters(frame) if hasattr(self.detector, 'detect_monsters') else self.detector.detect_objects(frame)
            if monsters:
                self.state = "ATACANDO"
                target_monster = monsters[0]
                print(f"[{iteration}] ⚔️  Atacando {target_monster['label']} en ({target_monster['center'][0]}, {target_monster['center'][1]})")
                self.map_intel.record_spawn(target_monster['label'], target_monster['center'][0], target_monster['center'][1])
                self.controller.attack(target_monster['center'][0], target_monster['center'][1])
                time.sleep(2.0)
                continue
            
            # 5. Si no hay nada, moverse a la mejor zona de farmeo o aleatoriamente
            self.state = "BUSCANDO"
            best_spot = self.map_intel.get_best_farming_spot()
            
            if best_spot:
                print(f"[{iteration}] 🔍 No hay objetivos. Moviendo a zona de alta densidad: {best_spot}")
                self.controller.move_character(best_spot[0], best_spot[1])
            else:
                print(f"[{iteration}] 🗺️  No se detectaron objetivos. Explorando...")
                screen_w, screen_h = frame.shape[1], frame.shape[0]
                rand_x = random.randint(int(screen_w * 0.3), int(screen_w * 0.7))
                rand_y = random.randint(int(screen_h * 0.3), int(screen_h * 0.7))
                self.controller.move_character(rand_x, rand_y)
            
            time.sleep(3.0)

    def stop(self):
        self.running = False
        print("\n" + "═" * 60)
        print("✓ Asistente detenido.")
        print("═" * 60)


if __name__ == "__main__":
    # Para ejecutar el bot, se necesitarían los templates de imágenes
    # bot = ROBot(monster_templates=['monster1.png'], item_templates=['item1.png'])
    # bot.run()
    print("Lógica del bot cargada. Se requieren imágenes de referencia para funcionar.")
