import xml.etree.ElementTree as ET

class KML:
    def __init__(self, archivo_xml, archivo_kml):
        self.archivo_xml = archivo_xml
        self.archivo_kml = archivo_kml
        self.ns = {'u': 'http://www.uniovi.es'}
        self.arbol = None
        self.raiz = None
        self.coordenadas_linea = []

    def leer_xml(self):
        try:
            self.arbol = ET.parse(self.archivo_xml)
            self.raiz = self.arbol.getroot()
        except Exception as e:
            print(f"Se ha producido un error al leer el archivo XML: {e}")

    def prologo(self, archivo):
        archivo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        archivo.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        archivo.write('     <Document>\n')
        archivo.write('     <name>Planimetría Etapa 6</name>\n')

        estilos = {
            'rojo': 'ff0000ff',
            'verde': 'ff00ff00',
            'azul': 'ffff0000',
            'amarillo': 'ff00ffff',
            'linea': 'b30000ff'
        }

        for id_estilo, color in estilos.items():
            archivo.write(f'    <Style id ="{id_estilo}">\n')
            if id_estilo == 'linea':
                archivo.write('    <LineStyle>\n')
                archivo.write(f'        <color>{color}</color>\n')
                archivo.write('        <width>4</width>\n')
                archivo.write('    </LineStyle>\n')
            else:
                archivo.write('    <IconStyle>\n')
                archivo.write(f'        <color>{color}</color>\n')
                archivo.write('        <Icon>\n')
                archivo.write('            <href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href>\n')
                archivo.write('        </Icon>\n')
                archivo.write('     </IconStyle>\n')
            archivo.write(' </Style>\n')

    def _escribir_punto(self, archivo, nombre, nodo, color, distancia_fija=None):
        longitud = nodo.find('.//u:longitud_geo', self.ns).text
        latitud = nodo.find('.//u:latitud_geo', self.ns).text
        altitud = nodo.find('.//u:altitud', self.ns).text

        if distancia_fija is not None:
            dist = distancia_fija
        else:
            nodo_dist = nodo.find('.//u:distancia', self.ns)
            if nodo_dist is not None:
                dist = float(nodo_dist.text)
            else:
                dist = 0.0

        self.coordenadas_linea.append((dist, f"{longitud},{latitud},{altitud}"))

        archivo.write('         <Placemark>\n')
        archivo.write(f'             <name>{nombre}</name>\n')
        archivo.write(f'             <styleUrl>#{color}</styleUrl>\n')
        archivo.write('             <Point>\n')
        archivo.write(f'                <coordinates>{longitud},{latitud},{altitud}</coordinates>\n')
        archivo.write('             </Point>\n')
        archivo.write('         </Placemark>\n')

    def coordenadas(self, archivo):
        salida = self.raiz.find('.//u:salida', self.ns)
        if salida is not None:
            self._escribir_punto(archivo, "Salida - Alcossebre", salida, "rojo", 0.0)

        puntos = self.raiz.findall('.//u:punto_anonimo', self.ns)
        for p in puntos:
            nombre = p.find('u:nombre_punto', self.ns).text
            self._escribir_punto(archivo, nombre, p, "amarillo")

        puertos = self.raiz.findall('.//u:puerto_montana', self.ns)
        for i, p in enumerate(puertos):
            self._escribir_punto(archivo, f"Puerto {i + 1}", p, "verde")

        sprints = self.raiz.findall('.//u:sprint', self.ns)
        for i, s in enumerate(sprints):
            self._escribir_punto(archivo, f"Sprint {i + 1}", s, "azul")

        meta = self.raiz.find('.//u:meta', self.ns)
        if meta is not None:
            self._escribir_punto(archivo, "Meta - Castelló", meta, "rojo", 177.5)

        archivo.write('     <Placemark>\n')
        archivo.write('         <name>Ruta de la Etapa</name>\n')
        archivo.write('         <styleUrl>#linea</styleUrl>\n')
        archivo.write('         <LineString>\n')
        archivo.write('             <extrude>1</extrude>\n')
        archivo.write('             <tessellate>1</tessellate>\n')
        archivo.write('             <coordinates>\n')
        
        def obtener_clave(elemento):
            return elemento[0]

        self.coordenadas_linea.sort(key=obtener_clave)

        for dist, coordinate in self.coordenadas_linea:
            archivo.write(f'            {coordinate}\n')

        archivo.write('        </coordinates>\n')
        archivo.write('    </LineString>\n')
        archivo.write(' </Placemark>\n')

    def epilogo(self, archivo):
        archivo.write('     </Document>\n')
        archivo.write('</kml>\n')

    def generar(self):
        self.leer_xml()
        if self.raiz is None:
            return

        with open(self.archivo_kml, 'w', encoding='utf-8') as archivo:
            self.prologo(archivo)
            self.coordenadas(archivo)
            self.epilogo(archivo)

if __name__ == '__main__':
    app = KML('etapaEsquema.xml', 'etapa.kml')
    app.generar()
    print("El archivo se ha generado de forma correcta")