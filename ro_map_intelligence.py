import json
import os
import time


class ROMapIntelligence:
    def __init__(self, map_name="default_map", data_path=None):
        # Carpeta base = carpeta donde está este .py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if data_path is None:
            # Guardar los spawns en una carpeta "map_data" al lado de tus scripts
            data_path = os.path.join(base_dir, "map_data")

        self.map_name = map_name
        self.data_path = data_path
        self.spawn_data = []
        self._load_data()

    def _load_data(self):
        file_path = os.path.join(self.data_path, f"{self.map_name}_spawns.json")

        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        # Archivo vacío -> lista vacía
                        self.spawn_data = []
                    else:
                        self.spawn_data = json.loads(content)
            except json.JSONDecodeError:
                print(f"[WARN] Archivo de spawns corrupto: {file_path}. Reiniciando a lista vacía.")
                self.spawn_data = []
        else:
            os.makedirs(self.data_path, exist_ok=True)
            self.spawn_data = []

    def record_spawn(self, label, x, y):
        """Registra la ubicación de un spawn detectado."""
        self.spawn_data.append({
            "label": str(label),
            "x": int(x),
            "y": int(y),
            "timestamp": float(time.time())
        })
        # Guardar cada 10 registros para no saturar el disco
        if len(self.spawn_data) % 10 == 0:
            self.save_data()

    def save_data(self):
        file_path = os.path.join(self.data_path, f"{self.map_name}_spawns.json")
        os.makedirs(self.data_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.spawn_data, f, indent=4)

    def get_best_farming_spot(self):
        """Analiza los datos para encontrar la zona con más densidad de spawns."""
        if not self.spawn_data:
            return None

        # Dividir el mapa en cuadrícula y contar spawns
        grid_size = 100
        grid = {}

        for spawn in self.spawn_data:
            gx, gy = spawn["x"] // grid_size, spawn["y"] // grid_size
            key = (gx, gy)
            grid[key] = grid.get(key, 0) + 1

        if not grid:
            return None

        best_grid = max(grid, key=grid.get)
        return (
            best_grid[0] * grid_size + grid_size // 2,
            best_grid[1] * grid_size + grid_size // 2,
        )


if __name__ == "__main__":
    intel = ROMapIntelligence()
    intel.record_spawn("Poring", 500, 500)
    print(f"Mejor zona de farmeo: {intel.get_best_farming_spot()}")