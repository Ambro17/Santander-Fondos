import urllib.request
from bs4 import BeautifulSoup
import time
import io
import os
from dateutil import parser
import jsonpickle

# ================= EXCEPCIONES ================= #
class NoNewData(Exception):
    pass

# ================= CLASES del dominio ================= #
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
    def getName(self):
        return self.name
    def getIndicadores(self):
        return self.indicadores
# ================= FUNCIONES auxiliares ================= #

def removeColTags(a_web):
    col_tags = a_web.find_all("col")
    [col_tag.unwrap() for col_tag in col_tags]
    return a_web
    # parametrizar estas dos funciones con orden sup/parametros (str y funcion la complican, podria hacer "col" una funcion dummy pero parece forzado)

def removeEmptyTags(unaweb):
    empty_tags = unaweb.find_all(lambda tag: not tag.contents) # si le paso un html string no elimina los <tr></tr> vaya uno a saber xq'
    [empty_tag.extract() for empty_tag in empty_tags]
    return unaweb

def esCampoIndicador(td):
    return td.name == "td" and td["align"] == "right" and td.has_attr('class') #encapsulado pues es sensible a cambios

def getCamposIndicadores(amotherrow):
    return amotherrow.find_all(esCampoIndicador)

def getName(arow):
    strCelda = arow.td.table.tr.td.string
    # funciona solo para el primero, corregir para dollar y letes
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

def esCategoria(row,strCat):
    return lastWord(row) == strCat

def getHeaders(row):
    headers=[]
    [headers.append(th.string.strip()) for th in row.find_all("th")]
    return headers

def rowValida(row):
    # hay html basura en el codigo, incluyendo un <tr><td></td></tr> que se disfraza de row
    return row.td.has_attr("class")

# ================= FIN FUNCIONES auxiliares ================= #

def objectsToJSON(rend_diario,fecha_vig):
    json_str = jsonpickle.pickler.encode(rend_diario)
    json_dir = os.path.join(dirPadre(), "JSON")
    file_name = "Fondos-%s.json" % fecha_vig
    print(json_dir)
    json_file = io.open(os.path.join(json_dir, file_name), "w+")
    json_file.write(json_str)
    print("FIN")

def instanciarFondo(rowsfondo):
    Fondos = []
    moneda = lastWord(rowsfondo[0])
    headers = getHeaders(rowsfondo[1]) # armar dicc?
    onlyfondosrows = rowsfondo[2:] # me quedo solo con row de fondos
    for row in onlyfondosrows:
        if rowValida(row):
            fondo = Fondo(getName(row), getIndicadores(row))
            Fondos.append(fondo)
    return FondosDeMoneda(moneda,Fondos)

def obtenerRendimientoDelDia(fecha_vigencia,fpes,fdol,flet):
    fondo_pesos = instanciarFondo(fpes)
    fondo_dollars = instanciarFondo(fdol)
    fondo_letras = instanciarFondo(flet)
    return RendimientoDiario(fecha_vigencia,fondo_pesos,fondo_dollars,fondo_letras)
    # todo: Historico.addRendimiento( rd ) o eso va directo e json..

def filtrarFondos(prerows):
    rows = prerows[1:] # fecha ya extraida
    fpesos=rows[0:19]
    fdol=rows[19:26]
    fletes=rows[26:40]
    return (fpesos,fdol,fletes) # comienzan por header categoria/headers/rowsfondos al mismo nivel de row.

def procesarFondos(rows, fecha):
    fondosPesos, fondosDol, fondosLetes = filtrarFondos(rows)
    rend_diario = obtenerRendimientoDelDia(fecha,fondosPesos,fondosDol,fondosLetes)
    objectsToJSON(rend_diario,fecha)

def limpiarWeb(absweb):
    return removeEmptyTags(removeColTags(absweb))

def capturarFecha(web_sincols):
    textoFecha = web_sincols.div.table.tr.th.string
    return parser.parse(textoFecha,fuzzy=True).strftime("%Y-%m-%d")

def procesarDatos(webcruda):
    web_tokenizada = BeautifulSoup(webcruda, "html.parser")
    web = limpiarWeb(web_tokenizada)
    fecha = capturarFecha(web)
    rows = web.div.table.find_all("tr", recursive=False)
    rend_diario = procesarFondos(rows,fecha)

def backupSourceFile(webrio):
    try:
        # backupea el archivo, independientemente que la fecha de la tabla a parsear sea identica a la del dia anterior. Proteccion ante errores de la pagina
        stringfecha = time.strftime("%Y%m%d")
        file_name = 'Fondos-%s.dat' % stringfecha
        data_dir = os.path.join(dirPadre(), "Data")
        html_file = io.open(os.path.join(data_dir,file_name), 'w', encoding="UTF-8")
        web_str = str(webrio, 'utf-8')
        html_file.write(web_str.strip())
    except FileExistsError:
        print("ARCHIVO_YA_PROCESADO.")
        print("Los datos de rendimiento del día de hoy ya han sido procesados.")
        exit(-1)



# ================= MAIN  ================= #
x =""""

"""
#backupSourceFile(webrio)
procesarDatos(x)


# 1. Imprimir tabla de valores del día--> Desde JSON o valores en t. de ejecucion?
# 2. Imprimir historico de fondo--> JSON FIND in many files by name.
# 3. Sugerir un fondo según móvil de inversion(anti-inflacion, ahorro, ganancia) y aversión al riesgo (r.fija, variable, m.dinero) definidas por el usuario
# 4. --help con correspondencia entre Tipo de Renta y perfil de inversor, con comentario.
# 1.2 Exportar Tabla historico, puntual a excel
# 3.2 Asociar tipo de renta a perfil de aversion.


