# 🚦 Sistema de Visualización Balizas V16

Sistema en Python para visualizar incidencias de tráfico de la DGT (Dirección General de Tráfico) en un mapa interactivo con estadísticas por provincia.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Folium](https://img.shields.io/badge/Folium-0.19+-green)

## ✨ Características

- 📡 **Datos en tiempo real** desde el feed DATEX2 de la DGT
- 🗺️ **Mapa interactivo** con Folium y clustering de marcadores
- 🎨 **Colores por severidad**: verde (baja), naranja (media), rojo (alta), rojo oscuro (muy alta)
- 📊 **Estadísticas** por provincia, comunidad autónoma y tipo de incidencia
- 📄 **Reportes HTML** con diseño moderno y responsive

## 📋 Requisitos

- Python 3.12+
- uv (gestor de paquetes)

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/jrcosio/balizav16.git
cd balizav16

# Instalar dependencias con uv
uv sync
```

## 💻 Uso

### Datos en tiempo real de la DGT

```bash
uv run python main.py
```

### Con archivo XML local

```bash
uv run python main.py --local
```

### Generar reporte HTML de estadísticas

```bash
uv run python main.py --stats-html
```

### Todas las opciones

```bash
uv run python main.py --help
```

| Opción | Descripción |
|--------|-------------|
| `--local` | Usar archivo local `datex2_v36.xml` |
| `--no-stats` | No mostrar estadísticas en consola |
| `--stats-html` | Generar reporte HTML de estadísticas |
| `--output FILE` | Nombre del archivo de salida del mapa |

## 📁 Estructura del Proyecto

```
v16/
├── main.py              # Script principal
├── datex2_parser.py     # Parser XML DATEX2
├── map_visualizer.py    # Visualización con Folium
├── stats_generator.py   # Generador de estadísticas
├── datex2_v36.xml       # Archivo de datos de ejemplo
├── pyproject.toml       # Configuración del proyecto
└── README.md
```

## 📊 Salida

El sistema genera:

- **`mapa_v16.html`** - Mapa interactivo con todas las incidencias
- **`estadisticas_v16.html`** - Reporte visual de estadísticas (opcional)

### Ejemplo de Estadísticas en Consola

```
============================================================
📊 REPORTE DE INCIDENCIAS DE TRÁFICO - BALIZAS V16
============================================================

📈 RESUMEN GENERAL
   • Total de incidencias: 674
   • Provincias afectadas: 50
   • CCAA afectadas: 17
   • Municipios afectados: 542

⚠️ DISTRIBUCIÓN POR SEVERIDAD
   • Sin especificar: 531 (78.8%)
   • Alta: 68 (10.1%)
   • Media: 43 (6.4%)
   • Muy Alta: 27 (4.0%)
   • Baja: 5 (0.7%)

🏛️ TOP 10 PROVINCIAS CON MÁS INCIDENCIAS
    1. Pontevedra: 45 incidencias (34 municipios)
    2. Asturias: 44 incidencias (28 municipios)
    3. León: 37 incidencias (32 municipios)
    ...
```

## 🔧 API de Módulos

### Datex2Parser

```python
from datex2_parser import Datex2Parser

parser = Datex2Parser()
parser.fetch_data()  # Descargar de la DGT
# o parser.load_from_file("archivo.xml")
parser.parse_xml()
situations = parser.get_situations()
```

### MapVisualizer

```python
from map_visualizer import MapVisualizer

visualizer = MapVisualizer(situations)
visualizer.create_map(use_clustering=True)
visualizer.save("mi_mapa.html")
```

### StatisticsGenerator

```python
from stats_generator import StatisticsGenerator

stats = StatisticsGenerator(situations)
stats.print_report()
stats.generate_html_report("estadisticas.html")
```

## 📡 Fuente de Datos

Los datos provienen del **Punto de Acceso Nacional (NAP)** de la DGT:

- **URL**: https://nap.dgt.es/datex2/v3/dgt/SituationPublication/datex2_v36.xml
- **Formato**: DATEX II v3
- **Actualización**: Tiempo real

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
