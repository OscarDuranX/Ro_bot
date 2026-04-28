# Guía de Configuración Óptima para RO_Bot - Detección de Jellopy

## 📋 RESUMEN EJECUTIVO

Tu bot ahora tiene un **detector especializado de Jellopy** que combina:
- ✅ Detección por **color HSV** (altamente confiable para items azules)
- ✅ Validación con **template matching** como método secundario
- ✅ Filtrado de ruido y duplicados
- ✅ Rango de detección limitado a **50px del centro** de pantalla

---

## 🎮 CONFIGURACIÓN DEL JUEGO

### Resolución
- **Ventana del juego**: 1280 x 960 (✅ Ya es correcta)
- **Modo**: Ventana (NO pantalla completa)
- **Escala de UI**: 100% (no cambiar)

### Posicionamiento de la ventana
1. Abre Ragnarok Online
2. Posiciona la ventana en la **esquina superior izquierda** (0,0)
3. Redimensiona a **exactamente 1280x960**

#### ✅ Cómo verificar en Windows:
```
Click derecho en ventana → Propiedades
Verificar que tenga exactamente 1280x960
```

### Gráficos recomendados
Para una detección óptima:

| Configuración | Valor | Razón |
|---|---|---|
| **Efectos de partículas** | BAJO/DESACTIVADO | Evita ruido de color |
| **Sombras** | DESACTIVADO | Sombras no afectan items |
| **Iluminación dinámica** | DESACTIVADO | Consistencia de color |
| **Calidad de sprites** | NORMAL | Detecta bien Jellopy azul |
| **Renderizado** | OpenGL o DirectX 9+ | Suficiente |

---

## 🎯 ESTRUCTURA DE ARCHIVOS

Asegúrate de que tu carpeta está así:

```
Ro_bot/
├── ro_main.py
├── ro_bot_logic.py
├── ro_jellopy_detector.py         ← NUEVO: Detector especializado
├── ro_detector.py
├── ro_controller.py
├── ro_config.json                 ← ACTUALIZADO
├── assets/
│   ├── items/
│   │   ├── jellopy.png           ← CRÍTICO: Imagen del Jellopy
│   │   ├── empty_bottle.png
│   │   └── apple.png
│   └── monsters/
│       ├── poring.png
│       └── fabre.png
└── dataset/
    └── raw/
```

---

## 📸 PREPARACIÓN DEL TEMPLATE DE JELLOPY

### Paso 1: Capturar la imagen correcta

1. Mata algunos monstruos y deja que caigan Jellopy
2. **IMPORTANTE**: Asegúrate de que el Jellopy está **limpio** (sin sombras de otros items encima)
3. Toma una captura de pantalla completa

### Paso 2: Extraer el icono

Usa Python para hacer crop exacto:

```python
import cv2
import numpy as np

# Cargar la captura
img = cv2.imread('screenshot.png')

# Aproximadamente donde ves un Jellopy
# (Reemplaza con las coordenadas exactas de tu captura)
x1, y1, x2, y2 = 570, 480, 595, 505  # Ejemplo: 25x25 píxeles

jellopy_crop = img[y1:y2, x1:x2]
cv2.imwrite('./assets/items/jellopy.png', jellopy_crop)

print(f"Template guardado. Tamaño: {jellopy_crop.shape}")
```

### Paso 3: Verificar el template

```python
import cv2

template = cv2.imread('./assets/items/jellopy.png')
if template is not None:
    print(f"✓ Template cargado correctamente")
    print(f"  Tamaño: {template.shape}")
    print(f"  Mostrar para verificar que es azul")
else:
    print("✗ Error al cargar template")
```

---

## 🧪 PROBAR EL DETECTOR

### Test 1: Verificar que captura la pantalla

```bash
python -c "
from ro_detector import RODetector
detector = RODetector()
frame = detector.capture_screen()
print(f'Captura OK: {frame.shape}')
"
```

**Resultado esperado**: `Captura OK: (960, 1280, 3)` o similar

### Test 2: Probar detector de Jellopy

```bash
python -c "
from ro_jellopy_detector import ROJellopyDetector
detector = ROJellopyDetector()
frame = detector.capture_screen()
detections = detector.detect_jellopy(frame, max_distance=50)
print(f'Jellopy encontrados: {len(detections)}')
for d in detections:
    print(f'  - Centro: {d[\"center\"]}, Confianza: {d[\"confidence\"]:.2f}')
"
```

**Resultado esperado**: Encuentra Jellopy si están en pantalla

### Test 3: Generar imagen de debug

```bash
python ro_jellopy_detector.py
```

Esto generará `debug_jellopy.png` mostrando:
- 🟢 Círculo verde de 50px (rango de detección)
- 🔴 Rectángulos rojos alrededor de Jellopy detectados
- 🔵 Puntos azules en los centros

---

## 🔧 AJUSTES FINOS

Si el detector no funciona bien, prueba estos cambios en `ro_jellopy_detector.py`:

### Problema: No detecta Jellopy
```python
# En ROJellopyDetector.__init__()
self.lower_blue = np.array([85, 80, 80])       # ← Más amplio
self.upper_blue = np.array([135, 255, 255])   # ← Más amplio
```

### Problema: Detecta ruido azul (no es Jellopy)
```python
self.min_contour_area = 100      # ← Aumentar
self.max_contour_area = 1000     # ← Disminuir
```

### Problema: Detecta items demasiado lejanos
```python
# En ro_bot_logic.py, en __init__()
self.jellopy_pickup_distance = 30  # ← Disminuir de 50
```

---

## 📊 MONITOREO Y DEBUGGING

### Ver logs en tiempo real
```python
# En ro_bot_logic.py, línea ~55
# Ya hay prints de debug, mira la consola
```

### Generar screenshots de debug cada frame
```python
# En ro_bot_logic.py, añade en el bucle:
if jellopy_detections:
    self.jellopy_detector.debug_visualization(frame, jellopy_detections)
```

---

## ⚠️ CHECKLIST ANTES DE EJECUTAR

- [ ] Ventana Ragnarok: 1280x960, modo ventana
- [ ] Ventana posicionada en esquina superior izquierda
- [ ] Archivo `./assets/items/jellopy.png` existe
- [ ] Template de Jellopy es **solo el icono azul** (25-40px)
- [ ] Ejecuté `python ro_jellopy_detector.py` y veo detecciones en debug
- [ ] `ro_config.json` actualizado con `jellopy_template`
- [ ] Gráficos del juego en LOW para evitar ruido

---

## 🚀 PRIMERA EJECUCIÓN

```bash
# 1. Abre el juego
# 2. Mata un monstruo y espera a que caiga Jellopy
# 3. Ejecuta:
python ro_main.py

# 4. Mira la consola para ver:
# [JELLOPY] Detectado en (X, Y) - Confianza: 0.95
```

---

## 📞 TROUBLESHOOTING

| Problema | Solución |
|---|---|
| No detecta Jellopy | Ampliar rango HSV, verificar template |
| Detecta ruido azul | Reducir área de contorno, mejorar template |
| Clicks no funcionan | Verificar posición de ventana |
| HP bar no detecta | Ajustar `hp_roi` en `ro_detector.py` |

---

## 🎨 PARÁMETROS CLAVE EN `ro_jellopy_detector.py`

```python
# Rango de color HSV para azul (Jellopy)
self.lower_blue = np.array([90, 100, 80])
self.upper_blue = np.array([130, 255, 255])

# Tamaño mínimo/máximo de objeto en píxeles
self.min_contour_area = 50
self.max_contour_area = 2000

# Umbral de confianza para template
self.template_threshold = 0.75

# Distancia máxima desde centro de pantalla (EN EL BOT: 50px)
max_distance = 50
```

---

## 📌 PRÓXIMOS PASOS

1. **Crea el template de Jellopy** (lo más importante)
2. **Prueba el detector** con `python ro_jellopy_detector.py`
3. **Ejecuta el bot** y verifica logs
4. **Ajusta parámetros** según necesites

¿Necesitas ayuda con algo específico? 🎯
