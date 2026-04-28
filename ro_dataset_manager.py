import os
import shutil
import time

class RODatasetManager:
    def __init__(self, raw_path="/home/ubuntu/dataset/raw", processed_path="/home/ubuntu/dataset/processed"):
        self.raw_path = raw_path
        self.processed_path = processed_path
        self._ensure_dirs()

    def _ensure_dirs(self):
        for path in [self.raw_path, self.processed_path]:
            os.makedirs(path, exist_ok=True)

    def organize_dataset(self):
        """Organiza las imágenes capturadas en carpetas por etiqueta."""
        files = [f for f in os.listdir(self.raw_path) if f.endswith('.png')]
        if not files:
            print("No hay nuevas imágenes para organizar.")
            return

        print(f"Organizando {len(files)} imágenes...")
        for filename in files:
            # El formato es: Etiqueta_Timestamp_Confianza.png
            label = filename.split('_')[0]
            label_dir = os.path.join(self.processed_path, label)
            os.makedirs(label_dir, exist_ok=True)
            
            src = os.path.join(self.raw_path, filename)
            dst = os.path.join(label_dir, filename)
            shutil.move(src, dst)
        
        print("Organización completada.")

    def get_stats(self):
        """Muestra estadísticas del dataset actual."""
        stats = {}
        if not os.path.exists(self.processed_path):
            return stats
            
        for label in os.listdir(self.processed_path):
            label_dir = os.path.join(self.processed_path, label)
            if os.path.isdir(label_dir):
                stats[label] = len(os.listdir(label_dir))
        return stats

if __name__ == "__main__":
    manager = RODatasetManager()
    manager.organize_dataset()
    stats = manager.get_stats()
    print("\nEstadísticas del Dataset:")
    for label, count in stats.items():
        print(f"- {label}: {count} imágenes")
