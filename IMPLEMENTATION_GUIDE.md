# 🎮 RO_Bot V2.0 - GUÍA PROFESIONAL DE IMPLEMENTACIÓN

## ✅ LO QUE HE HECHO POR TI

He creado **4 detectores profesionales completamente nuevos** que solucionan todos los problemas:

### 1. **ro_hp_detector.py** ✓
- **Lectura de HP por OCR** (lee el porcentaje numérico)
- **Detección de color verde** (barra visual)
- Validación de ambos métodos para mayor precisión
- Posición fija: esquina superior izquierda (25, 55)

### 2. **ro_monster_detector.py** ✓
- **Detecta barras de HP roja/amarilla** debajo de los monstruos
- Calcula HP aproximado por ancho de barra
- **Prioriza el monstruo más cercano automáticamente**
- Ordena por distancia al centro de pantalla

### 3. **ro_obstacle_detector.py** ✓
- **Detecta muros/obstáculos oscuros**
- Valida si un punto es caminable
- **Busca punto seguro cercano** si objetivo está bloqueado
- Evita que el bot clickee en paredes

### 4. **ro_item_detector.py** ✓
- **Sistema dinámico de items** basado en color
- Items configurables en `ro_items_config.json`
- Detección de Jellopy, Cartas, Pociones, etc.
- Fácil de añadir nuevos items

### 5. **ro_bot_v2.py** ✓
Bot mejorado con **sistema de prioridades inteligente**:
```
1. ❤️  SALUD (HP < 50% → usar poción)
2. 💎 JELLOPY (recoger si está cerca)
3. 📦 ITEMS (recoger otros items)
4. ⚔️  MONSTRUOS (atacar el más cercano)
5. 🗺️ EXPLORACIÓN (moverse si está inactivo)
```

---

## 🔧 INSTALACIÓN Y SETUP

### **PASO 1: Instalar dependencias**
```bash
pip install -r requirements.txt
```

**⚠️ IMPORTANTE:** También necesitas Tesseract OCR para lectura de HP:
- **Windows:** Descargar e instalar desde https://github.com/UB-Mannheim/tesseract/wiki
- **Linux:** `sudo apt install tesseract-ocr`
- **Mac:** `brew install tesseract`

### **PASO 2: Configurar el juego**
- Resolución: **1280 x 960** (ventana)
- Posición: Esquina superior izquierda **(0, 0)**
- Modo: **VENTANA** (no pantalla completa)
- Ejecutar bot como **ADMINISTRADOR** (Windows)

### **PASO 3: Configurar items a recoger**
Edita `ro_items_config.json`:
```json
{
    "Jellopy": {
        "lower": [90, 100, 80],      // Rango HSV inferior
        "upper": [130, 255, 255],    // Rango HSV superior
        "color_name": "blue",
        "enabled": true
    },
    "Carta": {
        "lower": [15, 100, 100],
        "upper": [45, 255, 255],
        "color_name": "yellow",
        "enabled": true
    }
}
```

**¿Cómo saber el rango HSV de un item?**
Ejecuta este script para detectar colores:
```bash
python detect_item_colors.py
```

### **PASO 4: Ajustar delays según anti-bot**
En `ro_config.json`:
```json
{
    "click_delay": 1.0,      // Espera 1s entre clicks
    "attack_delay": 1.0,     // Espera 1s entre ataques
    "pickup_delay": 1.0      // Espera 1s después de recoger
}
```

Si el juego es muy restrictivo, aumenta estos valores.

---

## 🚀 EJECUTAR EL BOT

```bash
python ro_main.py
```

**Salida esperada:**
```
╔═══════════════════════════════════════════════════════════╗
║         🎮 RO_BOT V2.0 - RAGNAROK ONLINE AUTOMATION      ║
║              Por: Oscar Duran (XEstoyProgramando)         ║
║     ⭐ Swordman Edition - Optimizado para Farmeo ⭐     ║
╚═══════════════════════════════════════════════════════════╝

🔧 CONFIGURACIÓN DEL BOT:
──────────────────────────────────────────────────────────
  HP Crítico: 50%
  Tecla Poción: f1
  Tecla Teleportación: f5
  Delay de Click: 1.0s
  Modo Debug: ON ✓

⏳ El bot iniciará en 5 segundos...

[1] 📊 HP Actual: 100.0%
[2] ⚔️  Atacando monstruo en (640, 480) HP:100% Dist:150px
[3] 💎 Jellopy detectado en (700, 500) - Confianza: 0.95
```

---

## 🔍 TROUBLESHOOTING

### ❌ "El HP no se detecta"
**Solución:**
1. Verifica que Tesseract esté instalado
2. En Windows, edita `ro_hp_detector.py` y asegúrate de que la ruta es correcta:
```python
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```
3. Ejecuta el test:
```bash
python ro_hp_detector.py
```

### ❌ "Los clicks no funcionan"
1. ¿Ejecutas como administrador? (Windows)
2. ¿La ventana del juego está en (0,0)?
3. ¿Está en MODO VENTANA (no pantalla completa)?
4. Prueba con un clic manual:
```bash
python -c "from ro_controller import ROController; c = ROController(); c.click(640, 480)"
```

### ❌ "No detecta monstruos"
1. Ejecuta test del detector:
```bash
python ro_monster_detector.py
```
2. Revisa `debug_monsters.png` para ver qué se detectó
3. Si ves las barras de HP, está bien. Si no, puede ser:
   - Lighting muy oscuro (ajusta gráficos)
   - Rango de HSV incorrecto (modifica `lower_red` y `upper_red`)

### ❌ "El bot se atasca en muros"
1. Verifica `debug_obstacles.png` (ejecuta `ro_obstacle_detector.py`)
2. Aumenta el radio de búsqueda de punto seguro en `ro_bot_v2.py`:
```python
safe_point = self.obstacle_detector.find_safe_zone_near(
    frame, center[0], center[1], radius=50  # Aumentar de 30 a 50
)
```

---

## 📊 ESTADÍSTICAS Y LOGS

El bot genera automáticamente:
- **Console logs** con cada acción en tiempo real
- **Imágenes de debug** (al final de cada sesión):
  - `debug_hp.png` - Detección de HP
  - `debug_monsters.png` - Monstruos detectados
  - `debug_items.png` - Items detectados
  - `debug_obstacles.png` - Obstáculos del mapa

**Al detener el bot (Ctrl+C):**
```
📊 ESTADÍSTICAS FINALES:
────────────────────────────────────────────────────
⏱️  Tiempo de ejecución: 2h 15m 30s
💎 Jellopy recogidos: 1250
📦 Items recogidos: 430
⚔️  Monstruos matados: 890
💊 Pociones usadas: 12
────────────────────────────────────────────────────
```

---

## 🎯 PRÓXIMAS MEJORAS (OPCIONAL)

### Cambiar a YOLOv8 para detección más precisa
```python
# En ro_config.json
"use_yolo": true
```

### Añadir soporte para más clases de personaje
Crear archivos separados:
- `ro_bot_archer.py` (Archer/Ranger)
- `ro_bot_mage.py` (Mago/Sage)
- `ro_bot_merchant.py` (Merchant/Alchemist)

### Sistema de aprendizaje de mapas
El bot ya graba automáticamente donde spawnan monstruos en:
```
map_data/{map_name}_spawns.json
```

---

## ⚖️ NOTAS LEGALES

⚠️ **IMPORTANTE:** Este bot es para uso personal y educativo. Algunos servidores de RO pueden violar términos de servicio. Úsalo bajo tu propio riesgo.

---

## 📞 SOPORTE

¿Problemas?

1. Revisa los logs en consola (incluyen línea exacta del error)
2. Genera imágenes de debug:
   ```bash
   python ro_hp_detector.py
   python ro_monster_detector.py
   python ro_item_detector.py
   python ro_obstacle_detector.py
   ```
3. Abre un issue en GitHub con:
   - Screenshot del juego
   - Las imágenes de debug
   - El log completo del error

---

## 🏆 ¿LISTO PARA FARMEAR?

```bash
python ro_main.py
```

**¡Que disfrutes del bot! 🎮**

---

*Creado por Oscar Duran - XEstoyProgramando*
*RO_Bot V2.0 - Mayo 2026*
