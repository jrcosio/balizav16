"""
Módulo para parsear datos DATEX2 de la DGT.
"""

import requests
from lxml import etree
from typing import Optional
from dataclasses import dataclass


@dataclass
class Situation:
    """Representa una situación/incidencia de tráfico."""
    id: str
    severity: Optional[str]
    latitude: float
    longitude: float
    province: Optional[str]
    municipality: Optional[str]
    autonomous_community: Optional[str]
    road_name: Optional[str]
    management_type: Optional[str]
    cause_type: Optional[str]
    km_point: Optional[float] = None


class Datex2Parser:
    """Parser para datos DATEX2 de la DGT."""
    
    NAMESPACES = {
        'd2': 'http://levelC/schema/3/d2Payload',
        'sit': 'http://levelC/schema/3/situation',
        'loc': 'http://levelC/schema/3/locationReferencing',
        'com': 'http://levelC/schema/3/common',
        'lse': 'http://levelC/schema/3/locationReferencingSpanishExtension',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    DEFAULT_URL = "https://nap.dgt.es/datex2/v3/dgt/SituationPublication/datex2_v36.xml"
    
    def __init__(self, url: Optional[str] = None):
        self.url = url or self.DEFAULT_URL
        self._xml_content: Optional[bytes] = None
        self._root: Optional[etree._Element] = None
    
    def fetch_data(self, timeout: int = 30) -> bytes:
        """Descarga el XML desde la URL de la DGT."""
        response = requests.get(self.url, timeout=timeout)
        response.raise_for_status()
        self._xml_content = response.content
        return self._xml_content
    
    def load_from_file(self, filepath: str) -> bytes:
        """Carga el XML desde un archivo local."""
        with open(filepath, 'rb') as f:
            self._xml_content = f.read()
        return self._xml_content
    
    def parse_xml(self, xml_content: Optional[bytes] = None) -> etree._Element:
        """Parsea el contenido XML."""
        content = xml_content or self._xml_content
        if content is None:
            raise ValueError("No hay contenido XML para parsear. Usa fetch_data() o load_from_file() primero.")
        self._root = etree.fromstring(content)
        return self._root
    
    def _extract_point_info(self, point_elem: etree._Element) -> dict:
        """Extrae información de un punto (coordenadas y extensiones)."""
        info = {
            'latitude': None,
            'longitude': None,
            'province': None,
            'municipality': None,
            'autonomous_community': None,
            'km_point': None
        }
        
        # Coordenadas
        coords = point_elem.find('.//loc:pointCoordinates', self.NAMESPACES)
        if coords is not None:
            lat = coords.find('loc:latitude', self.NAMESPACES)
            lon = coords.find('loc:longitude', self.NAMESPACES)
            if lat is not None and lat.text:
                info['latitude'] = float(lat.text)
            if lon is not None and lon.text:
                info['longitude'] = float(lon.text)
        
        # Extensiones españolas
        ext = point_elem.find('.//loc:extendedTpegNonJunctionPoint', self.NAMESPACES)
        if ext is not None:
            province = ext.find('lse:province', self.NAMESPACES)
            municipality = ext.find('lse:municipality', self.NAMESPACES)
            ac = ext.find('lse:autonomousCommunity', self.NAMESPACES)
            km = ext.find('lse:kilometerPoint', self.NAMESPACES)
            
            if province is not None:
                info['province'] = province.text
            if municipality is not None:
                info['municipality'] = municipality.text
            if ac is not None:
                info['autonomous_community'] = ac.text
            if km is not None and km.text:
                info['km_point'] = float(km.text)
        
        return info
    
    def get_situations(self) -> list[Situation]:
        """Extrae todas las situaciones del XML parseado."""
        if self._root is None:
            raise ValueError("XML no parseado. Usa parse_xml() primero.")
        
        situations = []
        
        for sit_elem in self._root.findall('.//sit:situation', self.NAMESPACES):
            sit_id = sit_elem.get('id', '')
            
            # Severidad
            severity_elem = sit_elem.find('sit:overallSeverity', self.NAMESPACES)
            severity = severity_elem.text if severity_elem is not None else None
            
            # Procesar cada situationRecord
            for record in sit_elem.findall('.//sit:situationRecord', self.NAMESPACES):
                # Nombre de carretera
                road_name_elem = record.find('.//loc:roadName', self.NAMESPACES)
                road_name = road_name_elem.text if road_name_elem is not None else None
                
                # Tipo de gestión
                mgmt_elem = record.find('.//sit:roadOrCarriagewayOrLaneManagementType', self.NAMESPACES)
                management_type = mgmt_elem.text if mgmt_elem is not None else None
                
                # Tipo de causa
                cause_elem = record.find('.//sit:causeType', self.NAMESPACES)
                cause_type = cause_elem.text if cause_elem is not None else None
                
                # Buscar puntos de ubicación (from, to, o point)
                location_ref = record.find('sit:locationReference', self.NAMESPACES)
                if location_ref is None:
                    continue
                
                # Intentar obtener punto 'from' (inicio del segmento)
                from_point = location_ref.find('.//loc:from', self.NAMESPACES)
                to_point = location_ref.find('.//loc:to', self.NAMESPACES)
                single_point = location_ref.find('.//loc:point', self.NAMESPACES)
                
                # Usar el primer punto disponible
                point = from_point if from_point is not None else (to_point if to_point is not None else single_point)
                
                if point is None:
                    continue
                
                point_info = self._extract_point_info(point)
                
                if point_info['latitude'] is None or point_info['longitude'] is None:
                    continue
                
                situation = Situation(
                    id=sit_id,
                    severity=severity,
                    latitude=point_info['latitude'],
                    longitude=point_info['longitude'],
                    province=point_info['province'],
                    municipality=point_info['municipality'],
                    autonomous_community=point_info['autonomous_community'],
                    road_name=road_name,
                    management_type=management_type,
                    cause_type=cause_type,
                    km_point=point_info['km_point']
                )
                situations.append(situation)
        
        return situations


if __name__ == "__main__":
    # Test del parser
    parser = Datex2Parser()
    
    # Cargar desde archivo local para pruebas
    parser.load_from_file("datex2_v36.xml")
    parser.parse_xml()
    
    situations = parser.get_situations()
    print(f"Total situaciones encontradas: {len(situations)}")
    
    # Mostrar primeras 5
    for sit in situations[:5]:
        print(f"  - {sit.id}: {sit.road_name} ({sit.province}) - {sit.severity}")
