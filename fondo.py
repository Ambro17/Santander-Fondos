import urllib.request
from bs4 import BeautifulSoup
import time
import io
import os
from dateutil import parser
# Constantes para facilitar la lectura y mantenimiento del codigo y los campos.
VALCUOTPARTE=0
VARDIARIA=1
LAST30=2
LAST90=3
VARANUAL=4
# EXCEPCIONES
class NoNewData(Exception):
    pass
# ================= CLASES del dominio ================= #
class RendimientoDiario:
    def __init__(self, tablapes, tabladolar, tablaletes):
        tablapesos = tablapes
        tabladolares = tabladolar
        assert isinstance(tablaletes, FondosDeMoneda), "El argumento ingresado es invalido. No es una instancia de TablaFondo"
        tablaletras = tablaletes

class FondosDeMoneda:
    headers = [0,0,0,0,0 ] # headers se reciben o los tiene la clase? si los tiene la clase que parece lo mas logico. De donde los saca, harcodea por conocimiento y estudio del problema? eso es correcto?..
    def __init__(self,fech, tipomoneda, losfondos):
        self.fecha = fech
        self.moneda = tipomoneda  
        self.fondos = losfondos
    # debe contener los headers.
    def mostrarTabla(self):
        return 1

class Fondo:
    def __init__(self, nombre, los_indicadores, fecha_referencia):
        self.name = nombre
        self.indicadores = los_indicadores
        self.fecha = fecha_referencia

# ================= FUNCIONES auxiliares ================= #

def capturarFecha(web_sincols):
    # capturo el string fecha en row 0, parseo la string y la convierto a formato dd/mm/aaaa. Considerar normalizar el formato de fechas (on filename)
    textoFecha = web_sincols.div.table.tr.th.string
    return parser.parse(textoFecha,fuzzy=True).strftime("%Y/%m/%d")

def removeColTags(a_web):
    cant_col_tags = len(a_web.find_all("col"))
    for i in range(0,cant_col_tags):
        a_web.col.unwrap()
    return a_web


def esCampoIndicador(td):
    return td.name == "td" and td["align"] == "right" and td.has_attr('class') #encapsulado pues es sensible a cambios

def getCamposIndicadores(amotherrow):
    return amotherrow.find_all(esCampoIndicador)

def getName(arow):
    strCelda = arow.td.table.tr.td.string
    return strCelda.strip()

def isNegative(str):
    return '(' in str and ')' in str
def parseNegative(str):
    return str.replace("(","-").replace(")","") # (3.5) --> -3.5
def dfloat(string):
    if isNegative(string):
        string = parseNegative(string)
    return float(string.replace(".","").replace(",",".")) # thanks obama

def getIndicadores(amotherrow):
    indicadores = []
    td_valores = getCamposIndicadores(amotherrow)
    for td in td_valores:
        valor_num = dfloat(td.string)
        indicadores.append(valor_num)
    return indicadores

def existe(obj):
    return obj != None
def esEncabezado(row):
    lo_es = False
    if existe(row.find("th",{"class": "th2"})):
        lo_es = True
    return lo_es
    # Probar: return True if existe(row.find("th",{"class": "th2"})) else False

def lastWord(row):
    return row.th.string.split()[-1] # obtiene la ultima palabra de un row header

def dirPadre():
    return os.path.dirname(os.path.abspath(__file__)) # __file__ es una constante global unica a cada proceso de ejecucion.

def directorio(folderStr):
    return os.path.join(dirPadre(),folderStr) #dado un subdirectorio de la carpeta raiz del directorio, devuelve el path completo hacia él.

def getHistoryDates(): # todo: resolver despues de implementar las instancias de clase. PRobablemente sea mas efectivo consultar la abstraccion que almacene esos datos mas inteligentes que un texto crudo (y de paso respeta el concepto de backup)
    dir_datos = directorio("Data")
    all_files = os.listdir(dir_datos)
    pass
    #print(all_files)

def fechaRepetida(fecha):
    historial_fechas = getHistoryDates()
    pass
    #return fecha in historial_fechas
    ### Considerando.. crear un backup consultable, con cierto poder de respuesta ante tuFecha::file->fecha. Porque por dos lados estoy consultando la fecha, al archivo tokenizado y al historial.

def esCategoria(row,strCat):
    return lastWord(row) == strCat

def filtrarFondos(rows):
    fpesos=rows[1:20]
    fdol=rows[20:29]
    fletes=rows[29:40]
    return (fpesos,fdol,fletes) # comienzan por header categoria/headers/rowsfondos al mismo nivel de row.


def procesarFondos(rows, fecha):
    true_rows = rows[1:]
    fondosPesos, fondosDol, fondosletes = filtrarFondos(true_rows)
    print("##################################Pes")
    print(fondosPesos)
    print("##################################Dol")
    print(fondosDol)
    print("##################################Let")
    print(fondosLetes)
    # creacion de objetos

def procesarTabla(unaWeb):
    web = removeColTags(unaWeb)
    fecha = capturarFecha(web) # dd/mm/aaaa
    print("La fecha del dia de hoy es: " + fecha)
    rows = web.div.table.find_all("tr", recursive=False)
    procesarFondos(rows,fecha)

def backupSourceFile(webrio): #TODO: agregar logica de que si la tabla contiene la misma fecha elimina/no backupea el archivo (info duplicada)
    try:
        # *Considerar guardar el archivo html sin embellecer para menor dependencia y mayor confianza en la integridad de los datos.**
        stringfecha = time.strftime("%Y%m%d")
        file_name = 'Fondos-%s.dat' % stringfecha
        data_dir = os.path.join(dirPadre(), "Data")
        html_file = io.open(os.path.join(data_dir,file_name), 'w', encoding="UTF-8")
        # le escribo el arbol del html webrio prettified (tabulado)
        html_tokenizado = BeautifulSoup(webrio, "html.parser")
        # TODO: escribir sólo si la fecha no coincide con la del dia anterior. (function TableDate :: Tabla->String->Bool)
        html_file.write(html_tokenizado.prettify())
        return html_tokenizado
    except FileExistsError:
        print("Excepcion: ARCHIVO_YA_PROCESADO")
        print("Los datos de rendimiento del día de hoy ya han sido procesados.")
        exit(-1)



""" ######### COMIENZO PROGRAMA ######### """
#   abro página que contiene la tabla a la que llama el html original con ajax
url = "http://www.santanderrio.com.ar/ConectorPortalStore/Rendimiento"
webrio = urllib.request.urlopen(url).read()
# Guardo archivo html y obtengo el html tokenizado
bsweb = backupSourceFile(webrio)
procesarTabla(bsweb)
