"""
Módulo para visualización de situaciones en mapa con Folium.
"""

import folium
from folium.plugins import MarkerCluster
from datex2_parser import Situation


class MapVisualizer:
    """Genera mapas interactivos con Folium."""
    
    # Centro de España (aproximado)
    SPAIN_CENTER = [40.4168, -3.7038]
    DEFAULT_ZOOM = 6
    
    # Colores por severidad
    SEVERITY_COLORS = {
        'low': 'green',
        'medium': 'orange',
        'high': 'red',
        'highest': 'darkred',
        None: 'blue'
    }
    
    # Iconos por severidad
    SEVERITY_ICONS = {
        'low': 'info-sign',
        'medium': 'warning-sign',
        'high': 'exclamation-sign',
        'highest': 'remove-sign',
        None: 'question-sign'
    }
    
    def __init__(self, situations: list[Situation]):
        self.situations = situations
        self.map = None
    
    def create_map(self, use_clustering: bool = True) -> folium.Map:
        """Crea el mapa base con todos los marcadores."""
        self.map = folium.Map(
            location=self.SPAIN_CENTER,
            zoom_start=self.DEFAULT_ZOOM,
            tiles='OpenStreetMap'
        )
        
        # Añadir capa de tiles alternativa
        folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(self.map)
        
        if use_clustering:
            marker_cluster = MarkerCluster(name='Incidencias').add_to(self.map)
            container = marker_cluster
        else:
            container = self.map
        
        for sit in self.situations:
            self._add_marker(sit, container)
        
        # Añadir control de capas
        folium.LayerControl().add_to(self.map)
        
        # Añadir leyenda
        self._add_legend()
        
        return self.map
    
    def _add_marker(self, situation: Situation, container) -> None:
        """Añade un marcador para una situación."""
        color = self.SEVERITY_COLORS.get(situation.severity, 'blue')
        icon_name = self.SEVERITY_ICONS.get(situation.severity, 'question-sign')
        
        # Crear popup con información
        popup_html = self._create_popup_html(situation)
        
        marker = folium.Marker(
            location=[situation.latitude, situation.longitude],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{situation.road_name or 'Sin nombre'} - {situation.severity or 'Sin severidad'}",
            icon=folium.Icon(color=color, icon=icon_name, prefix='glyphicon')
        )
        marker.add_to(container)
    
    def _create_popup_html(self, situation: Situation) -> str:
        """Crea el HTML para el popup de un marcador."""
        severity_es = {
            'low': 'Baja',
            'medium': 'Media',
            'high': 'Alta',
            'highest': 'Muy Alta',
            None: 'No especificada'
        }
        
        management_es = {
            'laneClosures': 'Cierre de carril',
            'roadClosed': 'Carretera cerrada',
            'singleAlternateLineTraffic': 'Tráfico alterno',
            'other': 'Otro',
            None: 'No especificado'
        }
        
        cause_es = {
            'roadMaintenance': 'Mantenimiento de vía',
            'roadOrCarriagewayOrLaneManagement': 'Gestión de tráfico',
            None: 'No especificada'
        }
        
        html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 250px;">
            <h4 style="margin: 0 0 10px 0; color: #333; border-bottom: 2px solid #007bff; padding-bottom: 5px;">
                🚧 {situation.road_name or 'Carretera sin nombre'}
            </h4>
            <table style="width: 100%; font-size: 13px;">
                <tr>
                    <td style="padding: 3px 0;"><strong>📍 Ubicación:</strong></td>
                    <td>{situation.municipality or 'N/A'}, {situation.province or 'N/A'}</td>
                </tr>
                <tr>
                    <td style="padding: 3px 0;"><strong>🏛️ CCAA:</strong></td>
                    <td>{situation.autonomous_community or 'N/A'}</td>
                </tr>
                <tr>
                    <td style="padding: 3px 0;"><strong>⚠️ Severidad:</strong></td>
                    <td><span style="color: {self.SEVERITY_COLORS.get(situation.severity, 'blue')}; font-weight: bold;">
                        {severity_es.get(situation.severity, 'N/A')}
                    </span></td>
                </tr>
                <tr>
                    <td style="padding: 3px 0;"><strong>🔧 Tipo:</strong></td>
                    <td>{management_es.get(situation.management_type, situation.management_type or 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 3px 0;"><strong>📋 Causa:</strong></td>
                    <td>{cause_es.get(situation.cause_type, situation.cause_type or 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 3px 0;"><strong>📏 PK:</strong></td>
                    <td>{situation.km_point if situation.km_point else 'N/A'}</td>
                </tr>
            </table>
            <div style="margin-top: 8px; font-size: 11px; color: #666;">
                ID: {situation.id}
            </div>
        </div>
        """
        return html
    
    def _add_legend(self) -> None:
        """Añade una leyenda al mapa."""
        legend_html = """
        <div style="
            position: fixed;
            bottom: 50px;
            left: 50px;
            z-index: 1000;
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            font-family: Arial, sans-serif;
            font-size: 13px;
        ">
            <h4 style="margin: 0 0 10px 0; font-size: 14px;">🚦 Severidad</h4>
            <div style="margin: 5px 0;">
                <span style="background-color: green; width: 15px; height: 15px; display: inline-block; border-radius: 50%; margin-right: 8px;"></span>
                Baja
            </div>
            <div style="margin: 5px 0;">
                <span style="background-color: orange; width: 15px; height: 15px; display: inline-block; border-radius: 50%; margin-right: 8px;"></span>
                Media
            </div>
            <div style="margin: 5px 0;">
                <span style="background-color: red; width: 15px; height: 15px; display: inline-block; border-radius: 50%; margin-right: 8px;"></span>
                Alta
            </div>
            <div style="margin: 5px 0;">
                <span style="background-color: darkred; width: 15px; height: 15px; display: inline-block; border-radius: 50%; margin-right: 8px;"></span>
                Muy Alta
            </div>
        </div>
        """
        self.map.get_root().html.add_child(folium.Element(legend_html))
    
    def save(self, filepath: str = "mapa_v16.html") -> str:
        """Guarda el mapa como archivo HTML."""
        if self.map is None:
            self.create_map()
        self.map.save(filepath)
        return filepath


if __name__ == "__main__":
    from datex2_parser import Datex2Parser
    
    # Test del visualizador
    parser = Datex2Parser()
    parser.load_from_file("datex2_v36.xml")
    parser.parse_xml()
    situations = parser.get_situations()
    
    print(f"Creando mapa con {len(situations)} situaciones...")
    visualizer = MapVisualizer(situations)
    visualizer.create_map()
    filepath = visualizer.save()
    print(f"Mapa guardado en: {filepath}")
