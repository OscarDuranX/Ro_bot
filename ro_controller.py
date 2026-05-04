"""
Controlador mejorado con soporte para teclas adicionales.
"""

import pydirectinput
import time
import random


class ROController:
    def __init__(self):
        self.min_delay = 0.1
        self.max_delay = 0.3

    def human_delay(self):
        """Añade retraso aleatorio para humanización."""
        time.sleep(random.uniform(self.min_delay, self.max_delay))

    def move_to(self, x, y):
        """Mueve el ratón con velocidad variable."""
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        target_x, target_y = x + offset_x, y + offset_y
        
        duration = random.uniform(0.1, 0.4)
        pydirectinput.moveTo(target_x, target_y, duration=duration)
        self.human_delay()

    def click(self, x, y, button='left'):
        """Realiza un clic en posición específica."""
        self.move_to(x, y)
        pydirectinput.click(button=button)
        self.human_delay()

    def attack(self, x, y):
        """Simula un ataque."""
        print(f"Atacando en ({x}, {y})")
        self.click(x, y)

    def pick_up(self, x, y):
        """Recoge un ítem."""
        print(f"Recogiendo ítem en ({x}, {y})")
        self.click(x, y)

    def use_potion(self, key='f1'):
        """Usa una poción."""
        print(f"Usando poción con tecla {key}")
        pydirectinput.press(key)
        self.human_delay()
    
    def key_press(self, key):
        """Presiona una tecla."""
        pydirectinput.press(key)
        self.human_delay()
    
    def key_down(self, key):
        """Mantiene una tecla presionada."""
        pydirectinput.keyDown(key)
    
    def key_up(self, key):
        """Suelta una tecla."""
        pydirectinput.keyUp(key)

    def move_character(self, x, y):
        """Mueve el personaje."""
        print(f"Moviendo personaje a ({x}, {y})")
        self.click(x, y)
