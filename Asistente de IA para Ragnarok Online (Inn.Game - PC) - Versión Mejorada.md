# Asistente de IA para Ragnarok Online (Inn.Game - PC) - Versión Mejorada

Este proyecto proporciona un asistente de IA basado en visión artificial para automatizar la caza de monstruos y la recolección de ítems en Ragnarok Online Prime (Inn.Game) en PC. Esta versión mejorada incluye funcionalidades para la recolección de datos, lo que permitirá entrenar modelos de Deep Learning para una detección de objetos más robusta en el futuro.

## 1. Requisitos Previos

Para que el asistente funcione correctamente, necesitarás instalar las siguientes bibliotecas de Python:

- `opencv-python`
- `numpy`
- `mss`
- `pydirectinput`
- `ultralytics` (para la detección con YOLOv8, opcional por ahora)

Puedes instalarlas usando `pip`:

```bash
pip install opencv-python numpy mss pydirectinput ultralytics
```

**Nota Importante**: `PyDirectInput` es crucial para interactuar con el juego a un nivel más bajo y evitar problemas con las protecciones anti-bot. Asegúrate de que tu juego esté ejecutándose en modo ventana o sin bordes para una mejor compatibilidad con la captura de pantalla.

## 2. Estructura del Proyecto

El proyecto consta de los siguientes archivos:

- `ro_detector.py`: Módulo encargado de la captura de pantalla y la detección de monstruos, ítems y la barra de HP. **Ahora incluye el modo de aprendizaje para recolectar datos.**
- `ro_controller.py`: Módulo para simular las entradas del teclado y el ratón con humanización. **Mejoras en la simulación de movimiento del ratón.**
- `ro_bot_logic.py`: Contiene la lógica principal del bot (máquina de estados: buscar, atacar, recoger, curar). **Soporte para modo de aprendizaje.**
- `ro_config_ui.py`: Una interfaz de línea de comandos simple para gestionar la configuración del bot.
- `ro_config.json`: Archivo de configuración donde se especifican los templates de imágenes, umbrales de HP, etc. **Ahora incluye la opción `learning_mode`.**
- `ro_main.py`: El script principal para iniciar el asistente. **Soporte para modo de aprendizaje.**
- `ro_yolo_detector.py`: **NUEVO** Módulo para la detección de objetos usando YOLOv8 (requiere entrenamiento previo).
- `ro_map_intelligence.py`: **NUEVO** Módulo para registrar y analizar spawns de monstruos.
- `ro_dataset_manager.py`: **NUEVO** Script para organizar las imágenes recolectadas en el modo de aprendizaje.
- `diseno_arquitectura_ro_bot.md`: Documento que detalla la arquitectura del asistente.
- `arquitectura_ro_bot.png`: Diagrama de la arquitectura del asistente.

## 3. Configuración Inicial

Antes de ejecutar el bot, necesitas configurar los templates de imágenes para los monstruos e ítems que deseas que el bot detecte y recoja. Si planeas usar el modo de aprendizaje, esta configuración inicial es menos crítica, ya que el bot recolectará sus propios datos.

### 3.1. Creación de Templates de Imágenes (para detección inicial)

1.  **Crea una carpeta `assets` en el mismo directorio que los scripts.** Dentro de `assets`, crea subcarpetas como `monsters` e `items`.
    ```
    . (directorio raíz del proyecto)
    ├── ro_detector.py
    ├── ...
    ├── assets
    │   ├── monsters
    │   │   └── poring.png
    │   │   └── fabre.png
    │   └── items
    │       └── jellopy.png
    │       └── apple.png
    ```
2.  **Captura imágenes de los monstruos e ítems que quieres que el bot reconozca.** Es crucial que estas imágenes sean pequeñas y representen fielmente el sprite del monstruo o el icono del ítem tal como aparecen en el juego. Asegúrate de que el fondo sea lo más consistente posible o recorta solo el objeto.
3.  **Guarda estas imágenes en las carpetas `assets/monsters` y `assets/items` respectivamente.**

### 3.2. Edición del Archivo `ro_config.json`

Edita el archivo `ro_config.json` para incluir las rutas a tus templates de imágenes y otros parámetros:

```json
{
    "monster_templates": [
        "./assets/monsters/poring.png",
        "./assets/monsters/fabre.png"
    ],
    "item_templates": [
        "./assets/items/jellopy.png",
        "./assets/items/apple.png"
    ],
    "hp_threshold": 50,      // Porcentaje de HP para usar poción (ej. 50 significa 50% o menos)
    "potion_key": "f1",      // Tecla de acceso rápido para usar poción en el juego
    "attack_delay": 2.0,     // Tiempo de espera después de un ataque
    "pickup_delay": 1.0,     // Tiempo de espera después de recoger un ítem
    "exploration_delay": 3.0, // Tiempo de espera después de moverse aleatoriamente
    "region": null,          // Opcional: {"left": 0, "top": 0, "width": 800, "height": 600} para capturar una región específica
    "learning_mode": true    // Establece a `true` para activar la recolección de datos para entrenamiento
}
```

- **`learning_mode`**: Si se establece en `true`, el bot guardará automáticamente recortes de las detecciones (incluso con menor confianza) en la carpeta `/home/ubuntu/dataset/raw`. Esto es esencial para construir tu propio dataset para entrenar un modelo YOLOv8.

## 4. Ejecución del Asistente

1.  Abre Ragnarok Online Prime y asegúrate de que la ventana del juego esté visible.
2.  Ejecuta el script principal desde tu terminal:

    ```bash
    python ro_main.py
    ```

3.  El bot esperará 5 segundos antes de comenzar. Durante este tiempo, asegúrate de que la ventana del juego esté activa y en primer plano.
4.  Para detener el bot, presiona `Ctrl+C` en la terminal.

## 5. Proceso de Entrenamiento (Modo Aprendizaje)

Si `learning_mode` está activado en `ro_config.json`, el bot recolectará imágenes en `/home/ubuntu/dataset/raw`.

### 5.1. Organización del Dataset

Después de recolectar suficientes imágenes, puedes usar el `ro_dataset_manager.py` para organizarlas:

```bash
python ro_dataset_manager.py
```

Este script moverá las imágenes de `/home/ubuntu/dataset/raw` a `/home/ubuntu/dataset/processed` organizadas por la etiqueta detectada (ej. `Monstruo`, `Item`).

### 5.2. Etiquetado y Preparación para YOLOv8

Una vez organizadas, necesitarás etiquetar manualmente estas imágenes para entrenar un modelo YOLOv8. Herramientas como **Roboflow** o **LabelImg** son recomendadas para esta tarea. Deberás crear un archivo de configuración de dataset (`data.yaml`) y luego entrenar el modelo YOLOv8.

### 5.3. Integración de YOLOv8

Una vez que tengas un modelo YOLOv8 entrenado (ej. `best.pt`), guárdalo en `/home/ubuntu/models/ro_best.pt`. Luego, puedes modificar `ro_main.py` para usar `ro_yolo_detector.py` en lugar de `ro_detector.py` para una detección más avanzada.

## 6. Consideraciones y Mejoras Futuras

-   **Detección de HP/SP**: La detección de la barra de HP por color es un ejemplo básico. Para una mayor precisión, se podría entrenar un modelo más robusto o usar OCR para leer los valores numéricos.
-   **Rutas de Movimiento**: El módulo `ro_map_intelligence.py` está diseñado para registrar spawns. En el futuro, se puede integrar con la lógica del bot para que el personaje se mueva a las zonas de farmeo más eficientes.
-   **Anti-Bot**: Las mejoras en `ro_controller.py` ayudan a humanizar el comportamiento. Continuar refinando los patrones de movimiento y los tiempos de espera es crucial.
-   **Interfaz Gráfica**: Para una experiencia de usuario más amigable, se podría desarrollar una GUI completa con `Tkinter` o `PyQt`.

¡Espero que este asistente mejorado te sea de gran utilidad en tus aventuras por Rune-Midgard!
