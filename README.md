# 🎮 RO_Bot - Asistente de IA para Ragnarok Online

**Un bot inteligente para farmear automáticamente Jellopy y otros items en Ragnarok Online.**

## 📋 Descripción

RO_Bot es un asistente de visión por computadora que:
- ✅ Detecta y recoge **Jellopy** automáticamente
- ✅ Mata monstruos (Poring, Fabre, etc.)
- ✅ Gestiona automáticamente pociones de vida
- ✅ Navega por el mapa de forma inteligente
- ✅ Aprende sobre el mapa conforme juega

**Tecnologías:**
- `OpenCV` - Visión por computadora
- `PyDirectInput` - Control del juego
- `MSS` - Captura de pantalla
- `NumPy` - Procesamiento de imágenes

---

## 🚀 Guía Rápida

### 1️⃣ Preparación (5 minutos)

```bash
# Clonar el repositorio
git clone https://github.com/OscarDuranX/Ro_bot.git
cd Ro_bot

# Instalar dependencias
pip install -r requirements.txt

# Crear carpetas necesarias
mkdir -p assets/{items,monsters}
mkdir -p dataset/raw
```

### 2️⃣ Extraer Template de Jellopy (IMPORTANTE)

```bash
python extract_jellopy_template.py
```

**Opciones:**
- **1** - GUI: Haz drag sobre el Jellopy azul en una captura
- **2** - Coordenadas: Introduce manualmente (x1, y1, x2, y2)
- **3** - Ver: Visualiza el template guardado

### 3️⃣ Configurar el Juego

**Resolución:**
- Ventana: `1280 x 960`
- Modo: Ventana (NO pantalla completa)
- Posición: Esquina superior izquierda (0, 0)

**Gráficos (opcional pero recomendado):**
- Efectos de partículas: BAJO
- Sombras: DESACTIVADO
- Iluminación dinámica: DESACTIVADO

### 4️⃣ Ejecutar el Bot

```bash
python ro_main.py
```

**Consola esperada:**
```
════════════════════════════════════════════════════════════════
Iniciando el asistente de IA para Ragnarok Online...
════════════════════════════════════════════════════════════════

[1] 💎 JELLOPY detectado en (640, 480) - Confianza: 0.95
[1] Recogiendo ítem en (640, 480)
[2] ⚔️ Atacando Poring en (500, 350)
```

---

## 📁 Estructura del Proyecto

```
Ro_bot/
├── ro_main.py                    # Punto de entrada
├── ro_bot_logic.py               # Lógica principal del bot
├── ro_jellopy_detector.py        # ⭐ Detector especializado para Jellopy
├── ro_detector.py                # Detector genérico (monstruos, items)
├── ro_yolo_detector.py           # Detector YOLOv8 (opcional)
├── ro_controller.py              # Control del ratón/teclado
├── ro_map_intelligence.py        # Sistema de inteligencia del mapa
├── extract_jellopy_template.py   # 🛠️ Herramienta para extraer templates
├── ro_config.json                # Configuración del bot
├── requirements.txt              # Dependencias
├── assets/
│   ├── items/
│   │   ├── jellopy.png          # ⭐ CRÍTICO: Template de Jellopy
│   │   ├── empty_bottle.png
│   │   └── apple.png
│   └── monsters/
│       ├── poring.png
│       └── fabre.png
└── dataset/
    └── raw/                      # Dataset para aprendizaje
```

---

## ⚙️ Configuración

### `ro_config.json`

```json
{
    "jellopy_template": "./assets/items/jellopy.png",
    "jellopy_pickup_distance": 50,
    "hp_threshold": 49,
    "potion_key": "f1",
    "attack_delay": 2.0,
    "pickup_delay": 1.0,
    "game_resolution": {
        "width": 1280,
        "height": 960,
        "mode": "windowed"
    },
    "debug_mode": true
}
```

| Parámetro | Valor | Descripción |
|---|---|---|
| `jellopy_template` | Path | Ruta del template de Jellopy |
| `jellopy_pickup_distance` | 50 | Distancia máxima para recoger Jellopy (px) |
| `hp_threshold` | 49 | % de HP para usar poción |
| `potion_key` | "f1" | Tecla de atajo para poción |
| `debug_mode` | true | Mostrar logs detallados |

---

## 🧠 Prioridades del Bot

El bot ejecuta en este orden de prioridad:

1. **❤️ Salud** - Si HP < 49%, usa poción
2. **💎 Jellopy** - Busca y recoge Jellopy (distancia < 50px)
3. **📦 Items** - Recoge otros items (Empty Bottle, Apple)
4. **⚔️ Monstruos** - Ataca Poring, Fabre, etc.
5. **🗺️ Exploración** - Se mueve a zonas de alta densidad

---

## 🛠️ Herramientas Incluidas

### `extract_jellopy_template.py` - Extraer Templates

```bash
python extract_jellopy_template.py
```

3 métodos:
- GUI drag-to-select
- Coordenadas manuales
- Ver template actual

### `ro_jellopy_detector.py` - Test del Detector

```bash
python ro_jellopy_detector.py
```

Genera `debug_jellopy.png` mostrando:
- 🟢 Círculo de detección (50px)
- 🔴 Jellopy encontrados
- 🔵 Centros de detección

---

## 🐛 Troubleshooting

### "No detecta Jellopy"

**Solución 1:** Verifica el template
```bash
python extract_jellopy_template.py
# Opción 3: Ver template actual
```

**Solución 2:** Amplía el rango de color en `ro_jellopy_detector.py`
```python
self.lower_blue = np.array([85, 80, 80])      # Más amplio
self.upper_blue = np.array([135, 255, 255])  # Más amplio
```

**Solución 3:** Ajusta la distancia de detección
```json
"jellopy_pickup_distance": 75  // Aumentar de 50
```

### "Los clicks no funcionan"

1. Verifica que la ventana está en (0, 0)
2. Ejecuta como administrador (Windows)
3. Desactiva focus-stealing protection

### "El bot ataca muy lentamente"

Ajusta `attack_delay` en `ro_config.json`:
```json
"attack_delay": 1.5  // Reducir de 2.0
```

---

## 📊 Detección de Jellopy

El sistema usa **detección híbrida**:

1. **Color HSV** (primario) - Busca píxeles azules
2. **Template Matching** (secundario) - Valida con template
3. **Filtrado** - Elimina ruido y duplicados

### Parámetros en `ro_jellopy_detector.py`

```python
# Rango de color para Jellopy azul
lower_blue = np.array([90, 100, 80])
upper_blue = np.array([130, 255, 255])

# Tamaño de objeto (píxeles)
min_contour_area = 50
max_contour_area = 2000

# Confianza
template_threshold = 0.75

# Distancia máxima
max_distance = 50
```

---

## 📈 Mejoras Futuras

- [ ] Soporte para más items
- [ ] Detección de otros monstruos
- [ ] Sistema de rutas más inteligente
- [ ] YOLOv8 mejorado
- [ ] Detección de drop de items más rápida
- [ ] Interfaz gráfica

---

## 📞 Soporte

¿Problemas o dudas?

- 📧 Email: xoscarduranx@gmail.com
- 🐙 GitHub Issues: [Crear issue](https://github.com/OscarDuranX/Ro_bot/issues)

---

## ⚖️ Licencia

MIT License - Úsalo libremente

---

## ⚠️ Disclaimer

Este bot es para **uso personal y educativo**. El uso de bots puede violar los términos de servicio de Ragnarok Online. Úsalo bajo tu propio riesgo.

---

**Made with ❤️ by Oscar Duran**
