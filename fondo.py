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
class Historico:
    'Registro histórico de los rendimientos de los fondos'
    RendimientosDiarios=[]
    def addRendimiento(self,renddiario):
        RendimientoDiario.append(renddiario)

class RendimientoDiario:
    'La instancia de RendimientoDiario contiene las tablas de fondos en pesos, dolares y letes.'
    def __init__(self, a_fecha, tablapes, tabladolar, tablaletras):
        self.fecha= a_fecha
        self.tablapesos = tablapes
        self.tabladolares = tabladolar
        assert isinstance(tablaletras, FondosDeMoneda), "El argumento ingresado es invalido. No es una instancia de TablaFondo"
        self.tablaletes = tablaletras

class FondosDeMoneda:
    'Representa una lista de fondos de cierta moneda'
    headers = [0,0,0,0,0 ] # headers se reciben o los tiene la clase? si los tiene la clase que parece lo mas logico. De donde los saca, harcodea por conocimiento y estudio del problema? eso es correcto?..
    def __init__(self, tipomoneda, losfondos):
        self.moneda = tipomoneda  
        self.fondos = losfondos
    # debe contener los headers.
    def mostrarTabla(self):
        return 1

class Fondo:
    'Representa un fondo y sus indicadores'
    def __init__(self, nombre, los_indicadores):
        self.name = nombre
        self.indicadores = los_indicadores

# ================= FUNCIONES auxiliares ================= #

def esCampoIndicador(td):
    return td.name == "td" and td["align"] == "right" and td.has_attr('class') #encapsulado pues es sensible a cambios

def getCamposIndicadores(amotherrow):
    return amotherrow.find_all(esCampoIndicador)

def getName(arow):
    strCelda = arow.td.table.tr.td.string
    return strCelda.strip()

def getIndicadores(amotherrow):
    indicadores = []
    td_valores = getCamposIndicadores(amotherrow)
    for td in td_valores:
        valor_num = dfloat(td.string)
        indicadores.append(valor_num)
    return indicadores

def isNegative(str):
    return '(' in str and ')' in str
def parseNegative(str):
    return str.replace("(","-").replace(")","") # (3.5) --> -3.5
def dfloat(string):
    if isNegative(string):
        string = parseNegative(string)
    return float(string.replace(".","").replace(",",".")) # thanks obama


def existe(obj):
    return obj != None
def esEncabezado(row):
    lo_es = False
    if existe(row.find("th",{"class": "th2"})):
        lo_es = True
    return lo_es
    # Probar: return (True if) existe(row.find("th",{"class": "th2"})) (or/elswe) False

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
    fpesos=rows[0:19]
    fdol=rows[19:29]
    fletes=rows[29:40]
    return (fpesos,fdol,fletes) # comienzan por header categoria/headers/rowsfondos al mismo nivel de row.

def getHeaders(row):
    headers=[]
    [headers.append(th.string) for th in row.find_all("th")]
    return headers

def storeData(rowsfondo):
    Fondos = []
    moneda = lastWord(rowsfondo[0])
    headers = getHeaders(rowsfondo[1]) # armar dicc?
    onlyfondosrows = rowsfondo[2:] # me quedo solo con row de fondos
    for row in onlyfondosrows:
        fondo = Fondo(getName(row), getIndicadores(row))
        Fondos.append(fondo)
    return FondosDeMoneda(moneda,Fondos)

def guardarRendimiento(fecha,fpes,fdol,flet):
    fondo_pesos = storeData(fpes)
    fondo_dollars = storeData(fdol)
    fondo_letras = storeData(flet)
    RendimientoDiario(fecha,fondo_pesos,fondo_dollars,fondo_letras)

def procesarFondos(rows, fecha):
    true_rows = rows[1:]
    fondosPesos, fondosDol, fondosLetes = filtrarFondos(true_rows)
    guardarRendimiento(fecha,fondosPesos,fondosDol,fondosLetes)

def removeColTags(a_web):
    col_tags = a_web.find_all("col")
    [col_tag.unwrap() for col_tag in col_tags]
    return a_web
# parametrizar estas dos funciones con orden sup/parametros (str y funcion la complican, podria hacer "col" una funcion dummy pero parece forzado)
def removeEmptyTags(unaweb):
    empty_tags = unaweb.find_all(lambda tag: not tag.contents)
    [empty_tag.extract() for empty_tag in empty_tags]
    return unaweb

def limpiarWeb(absweb):
    return removeEmptyTags(removeColTags(absweb))

def capturarFecha(web_sincols):
    textoFecha = web_sincols.div.table.tr.th.string
    return parser.parse(textoFecha,fuzzy=True).strftime("%Y/%m/%d")

def procesarDatos(unaWeb):
    web = limpiarWeb(unaWeb)
    fecha = capturarFecha(web)
    rows = web.div.table.find_all("tr", recursive=False)
    procesarFondos(rows,fecha)

def backupSourceFile(webrio):
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
        print("ARCHIVO_YA_PROCESADO.")
        print("Los datos de rendimiento del día de hoy ya han sido procesados.")
        exit(-1)


# ================= MAIN  ================= #
url = "http://www.santanderrio.com.ar/ConectorPortalStore/Rendimiento"
webrio = urllib.request.urlopen(url).read()
bsweb = backupSourceFile(webrio)
procesarDatos(bsweb)
# 1. Imprimir tabla de valores del día
# 2. Imprimir historico de fondo
# 3. Sugerir un fondo según móvil de inversion y aversión al riesgo definidas por el usuario
# 4. --help con correspondencia entre Tipo de Renta y perfil de inversor, con comentario.
# 1.2 Exportar Tabla historico, puntual a excel
# 3.2 Asociar tipo de renta a perfil de aversion.


