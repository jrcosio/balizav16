"""
Sistema de Visualización de Balizas V16
========================================

Visualiza incidencias de tráfico de la DGT en un mapa interactivo
y genera estadísticas por provincia.

Por JR Blanco

Uso:
    python main.py              # Descarga datos en tiempo real
    python main.py --local      # Usa archivo local datex2_v36.xml
"""

import argparse
import sys
from datex2_parser import Datex2Parser
from map_visualizer import MapVisualizer
from stats_generator import StatisticsGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Visualización de balizas V16 de la DGT"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Usar archivo local datex2_v36.xml en lugar de descargar"
    )
    parser.add_argument(
        "--no-stats",
        action="store_true",
        help="No mostrar estadísticas en consola"
    )
    parser.add_argument(
        "--stats-html",
        action="store_true",
        help="Generar reporte HTML de estadísticas"
    )
    parser.add_argument(
        "--output",
        default="mapa_v16.html",
        help="Nombre del archivo de salida para el mapa (default: mapa_v16.html)"
    )
    
    args = parser.parse_args()
    
    # 1. Cargar datos
    print("🚀 Iniciando sistema de visualización V16...")
    datex_parser = Datex2Parser()
    
    try:
        if args.local:
            print("📂 Cargando datos desde archivo local...")
            datex_parser.load_from_file("datex2_v36.xml")
        else:
            print("🌐 Descargando datos de la DGT...")
            datex_parser.fetch_data()
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        sys.exit(1)
    
    # 2. Parsear XML
    print("📄 Parseando XML DATEX2...")
    datex_parser.parse_xml()
    situations = datex_parser.get_situations()
    print(f"✅ Se encontraron {len(situations)} situaciones")
    
    if not situations:
        print("⚠️ No se encontraron situaciones. Saliendo...")
        sys.exit(0)
    
    # 3. Generar estadísticas
    if not args.no_stats:
        stats = StatisticsGenerator(situations)
        stats.print_report()
        
        if args.stats_html:
            stats_file = stats.generate_html_report()
            print(f"\n📊 Reporte HTML guardado en: {stats_file}")
    
    # 4. Crear mapa
    print(f"\n🗺️ Generando mapa interactivo...")
    visualizer = MapVisualizer(situations)
    visualizer.create_map(use_clustering=True)
    map_file = visualizer.save(args.output)
    print(f"✅ Mapa guardado en: {map_file}")
    
    print("\n🎉 ¡Proceso completado!")
    print(f"   Abre {map_file} en tu navegador para ver el mapa.")


if __name__ == "__main__":
    main()
