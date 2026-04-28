# Investigación: Asistente de IA para Ragnarok Online con Visión Artificial

## 1. Captura de Pantalla y Procesamiento de Imágenes
- **Bibliotecas Clave**: `OpenCV` (procesamiento), `PyAutoGUI` o `mss` (captura rápida), `NumPy` (manipulación de arrays).
- **Técnicas de Detección**:
    - **Template Matching**: Útil para iconos estáticos, botones de la interfaz y nombres de ítems en el suelo.
    - **Filtrado por Color (HSV)**: Efectivo para detectar barras de vida (rojas/verdes) o monstruos con colores distintivos.
    - **Modelos Pre-entrenados (YOLO/Cascade Classifiers)**: Para una detección más robusta de sprites de monstruos que cambian de animación. Roboflow tiene modelos para RO.
- **Desafíos**: El movimiento de la cámara y las animaciones de los sprites pueden dificultar el Template Matching simple.

## 2. Simulación de Entradas (Teclado y Ratón)
- **Problema con PyAutoGUI**: Muchos juegos modernos (incluyendo RO Prime con protecciones como Gepard o similares) ignoran los eventos de nivel de usuario de PyAutoGUI.
- **Solución**: `PyDirectInput`. Esta biblioteca utiliza códigos de escaneo de DirectInput, que son más propensos a ser aceptados por los motores de juegos de PC.
- **Interacción**:
    - **Ataque**: Clic izquierdo sobre el monstruo detectado.
    - **Recogida**: Clic sobre el ítem o uso de la tecla de acceso rápido (ej. `Alt+Z` o simplemente clic).
    - **Movimiento**: Clic en áreas vacías del suelo.

## 3. Consideraciones de Seguridad y Anti-Bot
- **Servidor Inn.Game (RO Prime)**: Probablemente utiliza protecciones como **Gepard Shield** o **Easy Anti-Cheat**.
- **Estrategias de Evasión**:
    - **Humanización**: Añadir retrasos aleatorios entre acciones (`time.sleep(random.uniform(0.1, 0.5))`).
    - **Variación de Clics**: No hacer clic siempre en el centro exacto del objeto detectado; añadir un pequeño offset aleatorio.
    - **Movimientos Curvos**: Evitar movimientos de ratón perfectamente rectos.

## 4. Estructura del Bot
- **Bucle Principal**: Capturar -> Procesar -> Decidir -> Actuar.
- **Estados**: `Buscando`, `Atacando`, `Recogiendo`, `Curándose`.
- **Configuración**: Lista de nombres de ítems (imágenes de referencia) y monstruos prioritarios.
