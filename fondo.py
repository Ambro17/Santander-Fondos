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
    LAYOUT = "{!s:40} {!s:20} {!s:20} {!s:20} {!s:20} {!s:20}" # para definir la salida
    def __init__(self, a_fecha, tablapes, tabladolar, tablaletras):
        self.fecha= a_fecha
        self.tablapesos = tablapes
        self.tabladolares = tabladolar
        self.tablaletes = tablaletras

    def show(self):
        # muestra el rendimiento del dia en una tabla
        self._printFondosMoneda(self.tablapesos)
        self._printFondosMoneda(self.tabladolares)
        self._printFondosMoneda(self.tablaletes)

    def _printHeader(self):
        print(self.LAYOUT.format("Fondo", "Valor a la fecha", "Var.Diaria", "Var. 30 días", "Var. 60 días", "Var. Anual"))

    def _printFondosMoneda(self,tablamoneda):
        print("\nFondos en " + str(tablamoneda.moneda))
        self._printHeader()
        for fondo in tablamoneda.fondos:
            inds_fondo = fondo.getIndicadores()
            print(self.LAYOUT.format(fondo.getName(), inds_fondo[0], inds_fondo[1], inds_fondo[2], inds_fondo[3], inds_fondo[4]))

    def showminimal(self):
        pass
        # parametrizar show() para poder imprimir solo la la primera y segunda columna. el layout como cambia

class FondosDeMoneda:
    'Representa una lista de fondos de cierta moneda'
    def __init__(self, tipomoneda, losfondos):
        self.moneda = tipomoneda  
        self.fondos = losfondos
    # debe contener los headers.
    def __repr__(self):
        return "<Moneda: %s, Fondos: %s>" % (self.moneda,self.fondos)

class Fondo:
    'Representa un fondo y sus indicadores'
    def __init__(self, nombre, los_indicadores):
        self.name = nombre
        self.indicadores = los_indicadores
    def getName(self):
        return self.name
    def getIndicadores(self):
        return self.indicadores
    def __repr__(self):
        return "<Nombre: %s, Indicadores: %s>" % (self.name, self.indicadores)
    def show(self):
        tableformat = "{0:20}||{0:20}"
        tableformat.format("Fondo", "Indicadores")
        print("<Nombre: %s,\n Indicadores: %s>" % (self.name, self.indicadores))
        # print 2 columns
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

def extraerNombre(arow):
    strCelda = arow.td.table.tr.td.string
    return strCelda.strip()

def extraerIndicadores(amotherrow):
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
    # hay html basura en el codigo, incluyendo un <tr><td></td></tr> que se disfraza de row. Todos los que tienen class, son validos.
    return row.td.has_attr("class")

# ================= FIN FUNCIONES auxiliares ================= #

def objectsToJSON(rend_diario,fecha_vig):
    # convierte las clases a un archivo JSON
    json_str = jsonpickle.pickler.encode(rend_diario)
    json_dir = os.path.join(dirPadre(), "JSON")
    file_name = "Fondos-%s.json" % fecha_vig
    json_file = io.open(os.path.join(json_dir, file_name), "w+")
    json_file.write(json_str)
    #print("EL Backup .JSON ha sido volado con exito")

def instanciarFondo(rowsfondo):
    #fondo html to class
    fondos = []
    moneda = lastWord(rowsfondo[0]) #obtengo nombre de moneda (pesos, dolar, letes)
    # headers = getHeaders(rowsfondo[1]) # armar dicc?
    onlyfondosrows = rowsfondo[2:] # me quedo solo con row de fondos
    for row in onlyfondosrows:
        if rowValida(row):
            # row html a clase Fondo
            fondo = Fondo( extraerNombre(row), extraerIndicadores(row))
            fondos.append(fondo)
    return FondosDeMoneda(moneda,fondos)

def newRendimientoDelDia(fecha_vigencia,fpes,fdol,flet):
    fondo_pesos = instanciarFondo(fpes)
    fondo_dollars = instanciarFondo(fdol)
    fondo_letras = instanciarFondo(flet)
    return RendimientoDiario(fecha_vigencia,fondo_pesos,fondo_dollars,fondo_letras)
    # todo: Historico.addRendimiento( rd ) o eso va directo e json..

def filtrarFondos(prerows):
    rows = prerows[1:] # fecha ya extraida
    fpesos=rows[0:19]
    fdol=rows[19:27]
    fletes=rows[27:40]
    return (fpesos,fdol,fletes) # comienzan por header categoria/headers/rowsfondos al mismo nivel de row.

def procesarFondos(web, fecha):
    rows = web.div.table.find_all("tr", recursive=False)
    fondosPesos, fondosDol, fondosLetes = filtrarFondos(rows)
    dicc = create_dic(fondosPesos,fondosDol,fondosLetes)
    print(dicc)
    rend_diario = newRendimientoDelDia(fecha,fondosPesos,fondosDol,fondosLetes)
    objectsToJSON(rend_diario,fecha)
    return rend_diario
    #objectsToSQL tabla consultable con getRendHoy, getHistoricoFondo (idfondo?)


def limpiarWeb(absweb):
    return removeEmptyTags(removeColTags(absweb))

def capturarFecha(web_sincols):
    textoFecha = web_sincols.div.table.tr.th.string
    t = parser.parse(textoFecha,fuzzy=True,dayfirst=True).strftime("%Y-%m-%d")
    return t
def procesarDatos(webcruda):
    web_tokenizada = BeautifulSoup(webcruda, "html.parser")
    web = limpiarWeb(web_tokenizada)
    fecha = capturarFecha(web)
    rend_diario = procesarFondos(web, fecha)
    return rend_diario

def create_dic(fp,fdol,flet):
    dicc = {}
    solofondos = fp[2:] + fdol[2:] + flet[2:]
    for index, row in enumerate(solofondos):
        if rowValida(row):
            dicc[index] = extraerNombre(row)
    return dicc
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
url = "http://www.santanderrio.com.ar/ConectorPortalStore/Rendimiento"
webrio = urllib.request.urlopen(url).read()
backupSourceFile(webrio)
rendimiento_del_dia = procesarDatos(webrio)
# RESOLVER CREACION DE DICCIONARIO URGENTE, PARA PODER AGILIZAR LAS BUSQUEDAS EN LA TABLA

# 1. Imprimir tabla de valores del día--> Desde JSON o valores en t. de ejecucion?
# 2. Imprimir historico de fondo--> JSON FIND in many files by name.
# 3. Sugerir un fondo según móvil de inversion(anti-inflacion, ahorro, ganancia) y aversión al riesgo (r.fija, variable, m.dinero) definidas por el usuario
# 4. --help con correspondencia entre Tipo de Renta y perfil de inversor, con comentario.
# 1.2 Exportar Tabla historico, puntual a excel
# 3.2 Asociar tipo de renta a perfil de aversion.


