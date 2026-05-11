"""
RO_Bot V2.0 - Bot principal con sistema de prioridades inteligente.
Swordman Edition - Optimizado para farmeo.
"""

import time
import cv2
import numpy as np
from datetime import datetime
from ro_hp_detector import ROHPDetector
from ro_monster_detector import ROMonsterDetector
from ro_item_detector import ROItemDetector
from ro_obstacle_detector import ROObstacleDetector
from ro_controller import ROController


class ROBotV2:
    def __init__(self):
        print("\n" + "="*60)
        print("🎮 RO_BOT V2.0 - RAGNAROK ONLINE AUTOMATION")
        print("⭐ Swordman Edition - Optimizado para Farmeo ⭐")
        print("="*60 + "\n")
        
        # Inicializar detectores
        self.hp_detector = ROHPDetector()
        self.monster_detector = ROMonsterDetector()
        self.item_detector = ROItemDetector()
        self.obstacle_detector = ROObstacleDetector()
        self.controller = ROController()
        
        # Configuración
        self.hp_threshold = 50
        self.potion_key = 'f1'
        self.teleport_key = 'f5'
        self.click_delay = 1.0
        self.max_monster_distance = 300
        
        # Estados
        self.running = True
        self.last_action_time = time.time()
        self.inactivity_threshold = 10  # segundos
        self.teleport_threshold = 20  # segundos
        
        # Estadísticas
        self.stats = {
            'start_time': datetime.now(),
            'monsters_killed': 0,
            'jellopy_collected': 0,
            'items_collected': 0,
            'potions_used': 0
        }
        
        print("🔧 CONFIGURACIÓN DEL BOT:")
        print(f"  HP Crítico: {self.hp_threshold}%")
        print(f"  Tecla Poción: {self.potion_key}")
        print(f"  Tecla Teleportación: {self.teleport_key}")
        print(f"  Delay de Click: {self.click_delay}s")
        print(f"  Distancia Ataque: {self.max_monster_distance}px")
        print(f"  Modo Debug: ON ✓")
        print("\n⏳ El bot iniciará en 5 segundos...\n")
        
        time.sleep(5)

    def check_and_use_potion(self, frame):
        """Verifica HP y usa poción si es necesario."""
        hp_info = self.hp_detector.get_hp_percentage(frame)
        
        if hp_info and hp_info['is_low']:
            print(f"❤️ HP CRÍTICO: {hp_info['percent']:.1f}% - Usando poción...")
            self.controller.use_potion(self.potion_key)
            self.stats['potions_used'] += 1
            self.last_action_time = time.time()
            return True
        
        return False

    def handle_jellopy(self, frame):
        """Busca y recoge Jellopy."""
        jellopy = self.item_detector.get_nearest_item_by_type(frame, 'Jellopy')
        
        if jellopy:
            print(f"💎 Jellopy detectado en {jellopy['center']} - Recogiendo...")
            self.controller.pick_up(jellopy['center'][0], jellopy['center'][1])
            self.stats['jellopy_collected'] += 1
            self.last_action_time = time.time()
            return True
        
        return False

    def handle_items(self, frame):
        """Recoge otros items."""
        all_items = self.item_detector.detect_all_items(frame)
        
        for item_name, items in all_items.items():
            if item_name == 'Jellopy':
                continue  # Ya se maneja en handle_jellopy
            
            if items:
                item = items[0]  # Primer item del tipo
                print(f"📦 {item_name} detectado en {item['center']} - Recogiendo...")
                self.controller.pick_up(item['center'][0], item['center'][1])
                self.stats['items_collected'] += 1
                self.last_action_time = time.time()
                return True
        
        return False

    def handle_monsters(self, frame):
        """Ataca el monstruo más cercano."""
        monster = self.monster_detector.get_nearest_monster(frame, self.max_monster_distance)
        
        if monster:
            center = monster['center']
            print(f"⚔️ Atacando monstruo en {center} HP:{monster['hp_percent']:.0f}% Dist:{monster['distance']:.0f}px")
            
            # Verificar obstáculos antes de atacar
            safe_point = self.obstacle_detector.find_safe_zone_near(frame, center[0], center[1], radius=50)
            
            if safe_point:
                self.controller.attack(safe_point[0], safe_point[1])
            else:
                self.controller.attack(center[0], center[1])
            
            self.stats['monsters_killed'] += 1
            self.last_action_time = time.time()
            time.sleep(self.click_delay)  # Esperar antes de siguiente ataque
            return True
        
        return False

    def handle_exploration(self, frame):
        """Se mueve si está inactivo."""
        inactivity_time = time.time() - self.last_action_time
        
        if inactivity_time > self.teleport_threshold:
            # Si lleva mucho tiempo inactivo, teleportarse
            print(f"🌀 Inactivo {inactivity_time:.0f}s - Teleportando (F5)...")
            self.controller.key_press(self.teleport_key)
            self.last_action_time = time.time()
            time.sleep(2)  # Esperar a que se complete el teleporte
            return True
        
        elif inactivity_time > self.inactivity_threshold:
            # Si lleva un tiempo inactivo, moverse a zona aleatoria
            print(f"🗺️ Inactivo {inactivity_time:.0f}s - Explorando...")
            random_x = np.random.randint(200, 1200)
            random_y = np.random.randint(200, 900)
            self.controller.move_character(random_x, random_y)
            self.last_action_time = time.time()
            time.sleep(self.click_delay)
            return True
        
        return False

    def run(self):
        """Loop principal del bot."""
        print("\n🚀 BOT INICIADO - Presiona Ctrl+C para detener\n")
        
        try:
            action_count = 0
            
            while self.running:
                # Capturar pantalla
                frame = self.hp_detector.capture_screen()
                
                # Sistema de prioridades
                action_taken = False
                
                # 1. SALUD CRÍTICA
                if self.check_and_use_potion(frame):
                    action_taken = True
                
                # 2. JELLOPY
                elif self.handle_jellopy(frame):
                    action_taken = True
                
                # 3. OTROS ITEMS
                elif self.handle_items(frame):
                    action_taken = True
                
                # 4. MONSTRUOS
                elif self.handle_monsters(frame):
                    action_taken = True
                
                # 5. EXPLORACIÓN
                else:
                    self.handle_exploration(frame)
                
                # Pequeña pausa para no saturar CPU
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.running = False
            self.print_statistics()

    def print_statistics(self):
        """Imprime estadísticas finales del bot."""
        elapsed = datetime.now() - self.stats['start_time']
        hours = elapsed.total_seconds() // 3600
        minutes = (elapsed.total_seconds() % 3600) // 60
        seconds = elapsed.total_seconds() % 60
        
        print("\n\n" + "="*60)
        print("📊 ESTADÍSTICAS FINALES")
        print("="*60)
        print(f"⏱️  Tiempo: {int(hours)}h {int(minutes)}m {int(seconds)}s")
        print(f"💎 Jellopy: {self.stats['jellopy_collected']}")
        print(f"📦 Items: {self.stats['items_collected']}")
        print(f"⚔️  Monstruos: {self.stats['monsters_killed']}")
        print(f"💊 Pociones: {self.stats['potions_used']}")
        print("="*60 + "\n")


if __name__ == "__main__":
    bot = ROBotV2()
    bot.run()
