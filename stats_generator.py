"""
Módulo para generar estadísticas de las situaciones.
"""

import pandas as pd
from datex2_parser import Situation


class StatisticsGenerator:
    """Genera estadísticas a partir de las situaciones."""
    
    def __init__(self, situations: list[Situation]):
        self.situations = situations
        self.df = self._to_dataframe()
    
    def _to_dataframe(self) -> pd.DataFrame:
        """Convierte las situaciones a un DataFrame de pandas."""
        data = [
            {
                'id': s.id,
                'severity': s.severity or 'Sin especificar',
                'province': s.province or 'Sin especificar',
                'municipality': s.municipality or 'Sin especificar',
                'autonomous_community': s.autonomous_community or 'Sin especificar',
                'road_name': s.road_name or 'Sin especificar',
                'management_type': s.management_type or 'Sin especificar',
                'cause_type': s.cause_type or 'Sin especificar',
                'latitude': s.latitude,
                'longitude': s.longitude
            }
            for s in self.situations
        ]
        return pd.DataFrame(data)
    
    def by_province(self) -> pd.DataFrame:
        """Retorna conteo de incidencias por provincia."""
        stats = self.df.groupby('province').agg(
            total_incidencias=('id', 'count'),
            municipios_afectados=('municipality', 'nunique')
        ).sort_values('total_incidencias', ascending=False)
        return stats
    
    def by_severity(self) -> pd.DataFrame:
        """Retorna distribución de incidencias por severidad."""
        stats = self.df.groupby('severity').agg(
            total=('id', 'count')
        )
        stats['porcentaje'] = (stats['total'] / stats['total'].sum() * 100).round(1)
        return stats.sort_values('total', ascending=False)
    
    def by_autonomous_community(self) -> pd.DataFrame:
        """Retorna conteo de incidencias por comunidad autónoma."""
        stats = self.df.groupby('autonomous_community').agg(
            total_incidencias=('id', 'count'),
            provincias_afectadas=('province', 'nunique')
        ).sort_values('total_incidencias', ascending=False)
        return stats
    
    def by_management_type(self) -> pd.DataFrame:
        """Retorna distribución por tipo de gestión."""
        type_names = {
            'laneClosures': 'Cierre de carril',
            'roadClosed': 'Carretera cerrada',
            'singleAlternateLineTraffic': 'Tráfico alterno',
            'other': 'Otro',
            'Sin especificar': 'Sin especificar'
        }
        
        stats = self.df.groupby('management_type').agg(
            total=('id', 'count')
        )
        stats['tipo'] = stats.index.map(lambda x: type_names.get(x, x))
        stats['porcentaje'] = (stats['total'] / stats['total'].sum() * 100).round(1)
        return stats.sort_values('total', ascending=False)
    
    def summary(self) -> dict:
        """Retorna un resumen general de las estadísticas."""
        return {
            'total_incidencias': len(self.df),
            'provincias_afectadas': self.df['province'].nunique(),
            'comunidades_afectadas': self.df['autonomous_community'].nunique(),
            'municipios_afectados': self.df['municipality'].nunique()
        }
    
    def print_report(self) -> None:
        """Imprime un reporte completo en consola."""
        print("\n" + "="*60)
        print("📊 REPORTE DE INCIDENCIAS DE TRÁFICO - BALIZAS V16")
        print("="*60)
        
        # Resumen
        summary = self.summary()
        print(f"\n📈 RESUMEN GENERAL")
        print(f"   • Total de incidencias: {summary['total_incidencias']}")
        print(f"   • Provincias afectadas: {summary['provincias_afectadas']}")
        print(f"   • CCAA afectadas: {summary['comunidades_afectadas']}")
        print(f"   • Municipios afectados: {summary['municipios_afectados']}")
        
        # Por severidad
        print(f"\n⚠️ DISTRIBUCIÓN POR SEVERIDAD")
        severity_df = self.by_severity()
        severity_names = {
            'low': 'Baja',
            'medium': 'Media',
            'high': 'Alta',
            'highest': 'Muy Alta',
            'Sin especificar': 'Sin especificar'
        }
        for idx, row in severity_df.iterrows():
            name = severity_names.get(idx, idx)
            print(f"   • {name}: {row['total']} ({row['porcentaje']}%)")
        
        # Top 10 provincias
        print(f"\n🏛️ TOP 10 PROVINCIAS CON MÁS INCIDENCIAS")
        province_df = self.by_province().head(10)
        for i, (idx, row) in enumerate(province_df.iterrows(), 1):
            print(f"   {i:2}. {idx}: {row['total_incidencias']} incidencias ({row['municipios_afectados']} municipios)")
        
        # Por tipo de gestión
        print(f"\n🔧 TIPO DE INCIDENCIA")
        mgmt_df = self.by_management_type()
        for idx, row in mgmt_df.iterrows():
            print(f"   • {row['tipo']}: {row['total']} ({row['porcentaje']}%)")
        
        print("\n" + "="*60)
    
    def generate_html_report(self, filepath: str = "estadisticas_v16.html") -> str:
        """Genera un reporte HTML con las estadísticas."""
        summary = self.summary()
        
        # Construir filas de tablas por separado
        province_rows = ""
        for i, (idx, row) in enumerate(self.by_province().head(15).iterrows()):
            province_rows += f"<tr><td>{i+1}</td><td>{idx}</td><td>{row['total_incidencias']}</td><td>{row['municipios_afectados']}</td></tr>"
        
        severity_names = {'low': 'Baja', 'medium': 'Media', 'high': 'Alta', 'highest': 'Muy Alta', 'Sin especificar': 'Sin especificar'}
        severity_rows = ""
        for idx, row in self.by_severity().iterrows():
            name = severity_names.get(idx, idx)
            severity_rows += f"<tr><td class='severity-{idx}'>{name}</td><td>{row['total']}</td><td>{row['porcentaje']}%</td></tr>"
        
        ccaa_rows = ""
        for idx, row in self.by_autonomous_community().iterrows():
            ccaa_rows += f"<tr><td>{idx}</td><td>{row['total_incidencias']}</td><td>{row['provincias_afectadas']}</td></tr>"
        
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estadísticas Balizas V16</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: #00d4ff;
            margin-bottom: 30px;
            text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .summary-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }}
        .summary-card:hover {{
            transform: translateY(-5px);
        }}
        .summary-card .number {{
            font-size: 3em;
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 10px;
        }}
        .summary-card .label {{
            color: #aaa;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        .section {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .section h2 {{
            color: #00d4ff;
            margin-top: 0;
            border-bottom: 2px solid rgba(0, 212, 255, 0.3);
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        th {{
            background: rgba(0, 212, 255, 0.2);
            color: #00d4ff;
            font-weight: 600;
        }}
        tr:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}
        .severity-low {{ color: #28a745; }}
        .severity-medium {{ color: #ffc107; }}
        .severity-high {{ color: #fd7e14; }}
        .severity-highest {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Estadísticas de Incidencias - Balizas V16</h1>
        
        <div class="summary-grid">
            <div class="summary-card">
                <div class="number">{summary['total_incidencias']}</div>
                <div class="label">Total Incidencias</div>
            </div>
            <div class="summary-card">
                <div class="number">{summary['provincias_afectadas']}</div>
                <div class="label">Provincias Afectadas</div>
            </div>
            <div class="summary-card">
                <div class="number">{summary['comunidades_afectadas']}</div>
                <div class="label">CCAA Afectadas</div>
            </div>
            <div class="summary-card">
                <div class="number">{summary['municipios_afectados']}</div>
                <div class="label">Municipios Afectados</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🏛️ Incidencias por Provincia</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Provincia</th>
                        <th>Total Incidencias</th>
                        <th>Municipios Afectados</th>
                    </tr>
                </thead>
                <tbody>
                    {province_rows}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>⚠️ Distribución por Severidad</h2>
            <table>
                <thead>
                    <tr>
                        <th>Severidad</th>
                        <th>Total</th>
                        <th>Porcentaje</th>
                    </tr>
                </thead>
                <tbody>
                    {severity_rows}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>🗺️ Incidencias por Comunidad Autónoma</h2>
            <table>
                <thead>
                    <tr>
                        <th>Comunidad Autónoma</th>
                        <th>Total Incidencias</th>
                        <th>Provincias Afectadas</th>
                    </tr>
                </thead>
                <tbody>
                    {ccaa_rows}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filepath


if __name__ == "__main__":
    from datex2_parser import Datex2Parser
    
    # Test del generador de estadísticas
    parser = Datex2Parser()
    parser.load_from_file("datex2_v36.xml")
    parser.parse_xml()
    situations = parser.get_situations()
    
    stats = StatisticsGenerator(situations)
    stats.print_report()
