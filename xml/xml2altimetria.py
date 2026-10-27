import xml.etree.ElementTree as ET

class Svg:
    def __init__(self, archivo_xml, archivo_svg):
        self.archivo_xml = archivo_xml
        self.archivo_svg = archivo_svg
        self.ns = {'u': 'http://www.uniovi.es'}
        self.arbol = None
        self.raiz = None

    def leer_xml(self):
        try:
            self.arbol = ET.parse(self.archivo_xml)
            self.raiz = self.arbol.getroot()
        except Exception as e:
            print(f"Error al leer el archivo XML: {e}")

    def prologo(self, archivo):
        archivo.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
        archivo.write('<svg xmlns="http://www.w3.org/2000/svg" version="2.0" ')
        archivo.write('viewBox="0 -50 1200 500" width="100%" height="100%">\n')
        archivo.write('    <!-- Fondo blanco -->\n')
        archivo.write('    <rect width="1200" height="500" y="-50" fill="white"/>\n')

        for alt in range(0, 1501, 500):
            y = 400 - (alt / 4) 
            archivo.write(f'    <line x1="40" y1="{y}" x2="1150" y2="{y}" stroke="lightgray" stroke-width="1" stroke-dasharray="5,5"/>\n')
            archivo.write(f'    <text x="5" y="{y+4}" font-family="Arial" font-size="12" fill="gray">{alt}m</text>\n')

    def dibujar_perfil(self, archivo):
        puntos_altimetria = []
        
        salida = self.raiz.find('.//u:salida', self.ns)
        if salida is not None:
            alt = float(salida.find('.//u:altitud', self.ns).text)
            puntos_altimetria.append((0.0, alt))

        nodos_intermedios = self.raiz.findall('.//u:puerto_montana', self.ns) + \
                            self.raiz.findall('.//u:sprint', self.ns) + \
                            self.raiz.findall('.//u:punto_anonimo', self.ns)
        
        for nodo in nodos_intermedios:
            nodo_dist = nodo.find('u:distancia', self.ns)
            if nodo_dist is not None:
                dist = float(nodo_dist.text)
            else:
                dist = 0.0
            alt = float(nodo.find('.//u:altitud', self.ns).text)
            puntos_altimetria.append((dist, alt))

        meta = self.raiz.find('.//u:meta', self.ns)
        if meta is not None:
            alt = float(meta.find('.//u:altitud', self.ns).text)
            puntos_altimetria.append((177.5, alt))

        def ordenar_por_km(elemento):
            return elemento[0]

        puntos_altimetria.sort(key=ordenar_por_km)

        if not puntos_altimetria:
            return

        puntos_polilinea = []
        ancho_total = 1100
        x_inicial = 50
        y_base = 400
        
        if len(puntos_altimetria) > 1:
            paso_x = ancho_total / (len(puntos_altimetria) - 1)
        else:
            paso_x = 0

        puntos_polilinea.append(f"{x_inicial},{y_base}")

        x_actual = x_inicial
        for dist, altitud in puntos_altimetria:
            y_actual = y_base - (altitud / 4) 
            puntos_polilinea.append(f"{x_actual},{y_actual}")
            x_actual += paso_x

        x_final = x_actual - paso_x
        puntos_polilinea.append(f"{x_final},{y_base}")
        puntos_polilinea.append(f"{x_inicial},{y_base}")

        puntos_str = " ".join(puntos_polilinea)
        archivo.write(f'    <polyline points="{puntos_str}" ')
        archivo.write('fill="#e34234" stroke="#b30000" stroke-width="2" />\n')

    def epilogo(self, archivo):
        archivo.write('</svg>\n')

    def generar(self):
        self.leer_xml()
        if self.raiz is None:
            return
        
        with open(self.archivo_svg, 'w', encoding='utf-8') as archivo:
            self.prologo(archivo)
            self.dibujar_perfil(archivo)
            self.epilogo(archivo)

if __name__ == '__main__':
    app = Svg('etapaEsquema.xml', 'altimetria.svg')
    app.generar()
    print("El archivo SVG se ha generado de forma correcta")