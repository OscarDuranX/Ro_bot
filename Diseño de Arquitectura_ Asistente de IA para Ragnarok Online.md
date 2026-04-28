# Diseño de Arquitectura: Asistente de IA para Ragnarok Online

## 1. Visión General del Sistema
El asistente de IA para Ragnarok Online operará como un sistema de circuito cerrado, siguiendo el patrón **Capturar -> Procesar -> Decidir -> Actuar**. Su objetivo principal es automatizar la caza de monstruos y la recolección de ítems específicos en el juego, utilizando técnicas de visión artificial para interactuar con la interfaz gráfica del juego.

## 2. Módulos Principales
La arquitectura del asistente se dividirá en los siguientes módulos:

### 2.1. Módulo de Captura de Pantalla
- **Función**: Capturar continuamente fotogramas de la ventana del juego de Ragnarok Online. Se priorizará la eficiencia y baja latencia para un procesamiento en tiempo real.
- **Tecnología Propuesta**: `mss` (para captura rápida de pantalla) o `PyAutoGUI` (si `mss` presenta incompatibilidades o rendimiento inferior en el entorno específico del usuario).
- **Salida**: Un array de NumPy que representa el fotograma actual de la pantalla del juego.

### 2.2. Módulo de Detección de Objetos (Visión Artificial)
- **Función**: Analizar los fotogramas capturados para identificar elementos clave en el juego.
- **Sub-módulos y Tecnologías**:
    - **Detección de Monstruos**: Utilizará **Template Matching** con `OpenCV` para identificar sprites de monstruos predefinidos. Se considerará la variación de animaciones y orientaciones. Para mayor robustez, se podría explorar el uso de clasificadores en cascada o modelos ligeros de detección de objetos si el rendimiento lo permite.
    - **Detección de Ítems**: Similar a la detección de monstruos, se usará **Template Matching** para identificar los iconos de los ítems en el suelo que el usuario desea recolectar. También se podría emplear **filtrado por color (HSV)** para resaltar el texto de los nombres de los ítems si es legible y tiene un color distintivo.
    - **Detección de Interfaz de Usuario (UI)**: Identificación de barras de HP/SP del personaje, minimapa, mensajes de chat (para posibles CAPTCHAs o interacciones), y otros elementos relevantes de la UI.
- **Salida**: Una lista de coordenadas (x, y) y dimensiones (ancho, alto) para cada objeto detectado, junto con su tipo (monstruo, ítem, barra de HP, etc.).

### 2.3. Módulo de Toma de Decisiones (Lógica del Bot)
- **Función**: Interpretar la información del Módulo de Detección de Objetos y determinar la acción más apropiada a realizar en el juego.
- **Lógica**: Implementará una máquina de estados simple (ej. `IDLE`, `ATACANDO`, `RECOGIENDO`, `CURANDO`, `MOVIENDO`).
    - **Prioridades**: La lógica priorizará la supervivencia (curarse si el HP es bajo), luego atacar monstruos, y finalmente recolectar ítems.
    - **Rutas**: Si no hay monstruos o ítems visibles, el bot podría seguir una ruta predefinida en el mapa o moverse aleatoriamente dentro de un área.
- **Entrada**: Información de objetos detectados y estado actual del personaje.
- **Salida**: Una acción específica (ej. `ATACAR(monstruo_coords)`, `RECOGER(item_coords)`, `USAR_POTION`, `MOVER_A(x, y)`).

### 2.4. Módulo de Ejecución de Acciones (Control del Personaje)
- **Función**: Traducir las decisiones del Módulo de Toma de Decisiones en entradas simuladas de teclado y ratón para interactuar con el juego.
- **Tecnología Propuesta**: `PyDirectInput` para simular clics de ratón y pulsaciones de teclas, ya que es más compatible con juegos que utilizan DirectInput y tienen protecciones anti-bot.
- **Humanización**: Se incorporarán retrasos aleatorios (`time.sleep(random.uniform(min_delay, max_delay))`) y pequeñas variaciones en las coordenadas de los clics para simular un comportamiento humano y evitar la detección por sistemas anti-bot.
- **Entrada**: Acciones a ejecutar desde el Módulo de Toma de Decisiones.

### 2.5. Módulo de Configuración de Usuario (Interfaz)
- **Función**: Proporcionar una manera sencilla para que el usuario configure el comportamiento del bot.
- **Características**:
    - **Especificación de Ítems**: El usuario podrá proporcionar imágenes de los ítems que desea recolectar.
    - **Especificación de Monstruos**: El usuario podrá proporcionar imágenes de los monstruos a cazar.
    - **Área de Operación**: Definir un área del mapa donde el bot debe operar.
    - **Parámetros de HP/SP**: Umbrales para usar pociones.
    - **Teclas de Acceso Rápido**: Configuración de las teclas de acceso rápido del juego para habilidades o ítems.
- **Tecnología Propuesta**: Una interfaz de línea de comandos (CLI) simple inicialmente, o una interfaz gráfica de usuario (GUI) básica con `Tkinter` o `PyQt` si el tiempo lo permite y es necesario para la usabilidad.

## 3. Flujo de Operación
1.  El usuario inicia el asistente y carga su configuración.
2.  El Módulo de Captura de Pantalla comienza a capturar fotogramas del juego.
3.  Cada fotograma es enviado al Módulo de Detección de Objetos para identificar monstruos, ítems y el estado del personaje.
4.  La información detectada se pasa al Módulo de Toma de Decisiones.
5.  El Módulo de Toma de Decisiones evalúa la situación y genera una acción.
6.  El Módulo de Ejecución de Acciones simula las entradas necesarias en el juego.
7.  El ciclo se repite continuamente.

## 4. Diagrama de Arquitectura
![Diagrama de Arquitectura](https://private-us-east-1.manuscdn.com/sessionFile/8Q94bSDbwNafH4PMyCbBxF/sandbox/x1YeMrrhauy72bXoakEP2O-images_1775350324031_na1fn_L2hvbWUvdWJ1bnR1L2FycXVpdGVjdHVyYV9yb19ib3Q.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvOFE5NGJTRGJ3TmFmSDRQTXlDYkJ4Ri9zYW5kYm94L3gxWWVNcnJoYXV5NzJiWG9ha0VQMk8taW1hZ2VzXzE3NzUzNTAzMjQwMzFfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyRnljWFZwZEdWamRIVnlZVjl5YjE5aWIzUS5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=MslE6P04qO3xgn~5bmwdnG4rGkDw1oDrXywfzfy1UfRWjiKUVd2HXtbDnItJt8H58QyUydajIsZ2Q6bZiK94gqErJVV1nIsISu~IYVoypwstr577LY1XdE591RKFiTLGOwG3W6qeot3Qzz6991DYPjJBACjO6VqgCRySXsPdSdu-ePf3xjwnerRp7OqcvEME7mqJDSWgzlYoh5i7q33PHyx0J6sGG~d804ie36rubqYwZ2gppLvQFurFzqKuFsaVwiYowN2~OJg5dwOBahqgCvE3F429-y4c961sVM~IUkhE2NQbdLKGALdeKcnvlrozaGr1F3DZbCEdratmD6MADA__)

## 5. Tecnologías Clave
- **Python**: Lenguaje de programación principal.
- **OpenCV**: Para visión artificial y procesamiento de imágenes.
- **mss**: Para captura de pantalla de alto rendimiento.
- **PyDirectInput**: Para simulación de entradas de teclado y ratón a bajo nivel.
- **NumPy**: Para manipulación eficiente de datos de imagen.

Este diseño proporciona una base sólida para el desarrollo del asistente, abordando los requisitos de visión artificial y automatización de manera estructurada y considerando las protecciones anti-bot del juego.
