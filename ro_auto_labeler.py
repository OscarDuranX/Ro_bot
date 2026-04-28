import os
import cv2
import yaml

class ROAutoLabeler:
    def __init__(self, processed_path="/home/ubuntu/dataset/processed", yolo_dataset_path="/home/ubuntu/dataset/yolo"):
        self.processed_path = processed_path
        self.yolo_dataset_path = yolo_dataset_path
        self.classes = []
        self._ensure_dirs()

    def _ensure_dirs(self):
        for split in ['train', 'val']:
            os.makedirs(os.path.join(self.yolo_dataset_path, split, 'images'), exist_ok=True)
            os.makedirs(os.path.join(self.yolo_dataset_path, split, 'labels'), exist_ok=True)

    def generate_labels(self):
        """Genera etiquetas YOLOv8 basadas en las carpetas de imágenes procesadas."""
        # Obtener clases de las carpetas en processed_path
        self.classes = sorted([d for d in os.listdir(self.processed_path) if os.path.isdir(os.path.join(self.processed_path, d))])
        class_to_id = {cls: i for i, cls in enumerate(self.classes)}
        
        print(f"Clases detectadas: {self.classes}")
        
        all_files = []
        for cls in self.classes:
            cls_dir = os.path.join(self.processed_path, cls)
            for img_name in os.listdir(cls_dir):
                if img_name.endswith('.png'):
                    all_files.append((cls, img_name))
        
        if not all_files:
            print("No hay imágenes para etiquetar.")
            return

        # Dividir en train (80%) y val (20%)
        import random
        random.shuffle(all_files)
        split_idx = int(len(all_files) * 0.8)
        train_files = all_files[:split_idx]
        val_files = all_files[split_idx:]

        self._process_split(train_files, 'train', class_to_id)
        self._process_split(val_files, 'val', class_to_id)
        
        self._create_yaml()
        print("Etiquetado automático completado.")

    def _process_split(self, files, split, class_to_id):
        for cls, img_name in files:
            src_path = os.path.join(self.processed_path, cls, img_name)
            img = cv2.imread(src_path)
            if img is None: continue
            
            h, w = img.shape[:2]
            
            # Como son recortes del objeto, el objeto ocupa casi toda la imagen
            # En formato YOLO: class_id x_center y_center width height (normalizado 0-1)
            # Usamos 0.5 0.5 0.9 0.9 para que el cuadro cubra el objeto en el recorte
            label_content = f"{class_to_id[cls]} 0.5 0.5 0.9 0.9\n"
            
            # Copiar imagen al dataset YOLO
            dst_img_path = os.path.join(self.yolo_dataset_path, split, 'images', img_name)
            cv2.imwrite(dst_img_path, img)
            
            # Crear archivo de etiqueta
            label_name = img_name.rsplit('.', 1)[0] + '.txt'
            dst_label_path = os.path.join(self.yolo_dataset_path, split, 'labels', label_name)
            with open(dst_label_path, 'w') as f:
                f.write(label_content)

    def _create_yaml(self):
        data = {
            'path': self.yolo_dataset_path,
            'train': 'train/images',
            'val': 'val/images',
            'names': {i: cls for i, cls in enumerate(self.classes)}
        }
        with open(os.path.join(self.yolo_dataset_path, 'data.yaml'), 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

if __name__ == "__main__":
    labeler = ROAutoLabeler()
    labeler.generate_labels()
