import os
try:
    from ultralytics import YOLO
except ImportError:
    print("Error: ultralytics no instalado. Ejecuta: pip install ultralytics")
    YOLO = None

def train_ro_model(data_yaml="/home/ubuntu/dataset/yolo/data.yaml", epochs=50, imgsz=640):
    if not YOLO:
        return
    
    if not os.path.exists(data_yaml):
        print(f"Error: No se encontró el archivo {data_yaml}. Ejecuta primero ro_auto_labeler.py")
        return

    # Cargar un modelo pre-entrenado (YOLOv8 Nano es ideal por su velocidad)
    model = YOLO('yolov8n.pt')

    print(f"Iniciando entrenamiento por {epochs} épocas...")
    # Entrenar el modelo
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        plots=True,
        device='cpu' # Cambiar a '0' si tienes una GPU NVIDIA
    )
    
    print("Entrenamiento completado.")
    print(f"El mejor modelo se ha guardado en: {results.save_dir}/weights/best.pt")
    
    # Copiar el mejor modelo a la carpeta de modelos del bot
    os.makedirs("/home/ubuntu/models", exist_ok=True)
    import shutil
    shutil.copy(f"{results.save_dir}/weights/best.pt", "/home/ubuntu/models/ro_best.pt")
    print("Modelo copiado a /home/ubuntu/models/ro_best.pt")

if __name__ == "__main__":
    train_ro_model()
