import pydirectinput
import time
import random

class ROController:
    def __init__(self):
        # Configuración de tiempos de espera aleatorios para humanización
        self.min_delay = 0.1
        self.max_delay = 0.3
        # Desactivar el fail-safe de PyAutoGUI si es necesario (usar con precaución)
        # pydirectinput.FAILSAFE = False

    def human_delay(self):
        """Añade un retraso aleatorio para simular comportamiento humano."""
        time.sleep(random.uniform(self.min_delay, self.max_delay))

    def move_to(self, x, y):
        """Mueve el ratón a una posición específica con un pequeño offset aleatorio y velocidad variable."""
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        target_x, target_y = x + offset_x, y + offset_y
        
        # Simular movimiento curvo o velocidad variable
        # PyDirectInput no soporta curvas nativas, pero podemos usar duraciones aleatorias
        duration = random.uniform(0.1, 0.4)
        pydirectinput.moveTo(target_x, target_y, duration=duration)
        self.human_delay()

    def click(self, x, y, button='left'):
        """Realiza un clic en una posición específica."""
        self.move_to(x, y)
        pydirectinput.click(button=button)
        self.human_delay()

    def attack(self, x, y):
        """Simula un ataque haciendo clic sobre el monstruo."""
        print(f"Atacando en ({x}, {y})")
        self.click(x, y)

    def pick_up(self, x, y):
        """Simula la recogida de un ítem haciendo clic sobre él."""
        print(f"Recogiendo ítem en ({x}, {y})")
        self.click(x, y)

    def use_potion(self, key='f1'):
        """Usa una poción presionando una tecla de acceso rápido."""
        print(f"Usando poción con la tecla {key}")
        pydirectinput.press(key)
        self.human_delay()

    def move_character(self, x, y):
        """Mueve al personaje haciendo clic en el suelo."""
        print(f"Moviendo personaje a ({x}, {y})")
        self.click(x, y)

if __name__ == "__main__":
    # Ejemplo de uso básico (solo para pruebas, no ejecutar sin el juego abierto)
    controller = ROController()
    print("Controlador inicializado.")
    # controller.use_potion('f1') # Ejemplo de uso
