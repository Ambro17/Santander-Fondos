import urllib.request
from bs4 import BeautifulSoup
import time
import io
import os
from dateutil import parser

# EXTENSION DOL-LETES
class TablaDiaria:
    def __init__(self,tablapes,tabladolar,tablaletes):
        tablapesos = tablapes
        tabladolares = tabladolar
        assert isinstance(tablaletes, TablaFondo), "El argumento ingresado es invalido. No es una instancia de TablaFondo"
        tablaletras = tablaletes

class TablaFondo:
    headers = [] # headers se reciben o los tiene la clase? si los tiene la clase que parece lo mas logico. De donde los saca, harcodea por conocimiento y estudio del problema? eso es correcto?..
    def __init__(self,fech, tipomoneda, losfondos):
        self.fecha = fecha
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
# maestro lista fondos por moneda.

def capturarFecha(rows):
    # capturo el string fecha en row 0, parseo la string y la convierto a formato dd/mm/aaaa
    textoFecha = rows[0].th.string
    return parser.parse(textoFecha,fuzzy=True).strftime("%d/%m/%Y")

def capturarCat(rows):
     return rows[1].th.string

def inicializarTablaFondos(rows):
    cant_campos = 6
    cant_fondos_pesos = 21
    tabla = [[0 for i in range(cant_campos)] for j in range(cant_fondos_pesos)] #todo modify limit
    # capturo la tr que contiene los nombres de las columnas para los valores del fondo
    rowTags = rows[2]
    i=0
    for th in rowTags.find_all("th"):
        tabla[0][i] = th.string
        i+=1
    return tabla

def removeColTags(a_web):
    cant_col_tags = len(a_web.find_all("col"))
    for i in range(0,cant_col_tags):
        a_web.col.unwrap()
    return a_web

def filtrarFondosPesos(rows):
    return rows[3:21]

def esCampoValor(td):
    return td.name == "td" and td["align"] == "right" and td.has_attr('class') #encapsulado pues es sensible a cambios

def getCamposIndicadores(amotherrow):
    var = amotherrow.find_all(esCampoValor)
    return var

def getName(arow):
    strCelda = arow.td.table.tr.td.string
    return strCelda.strip()

def getIndicadores(amotherrow):
    indicadores = []
    td_valores = getCamposIndicadores(amotherrow)
    for td in td_valores:
        indicadores.append(td.string)
    return indicadores

def procesarFondos(rows,fecha):
    # pongo nombres de columnas en primera fila como headers.
    tabla = inicializarTablaFondos(rows)
    rowsPesos = filtrarFondosPesos(rows)
    for row in rowsPesos:
        if row.contents: # si tiene algo dentro
            nombre = getName(row)
            indicadores = getIndicadores(row)
            print(indicadores)
            #print(name+"\n"+repr(indicadores)+"\n****")
    return -1

def procesarTabla(unaWeb):
    web = removeColTags(unaWeb)
    rows = web.div.table.find_all("tr", recursive=False)
    fecha = capturarFecha(rows)
    procesarFondos(rows,fecha)

def tableDate(web_tokenizada):
    simple_web = removeColTags(web_tokenizada)
    return simple_web.div.table.tr.th.string

def tokenizarWeb(web_cruda):
    return
def backupSourceFile(webrio): #TODO: agregar logica de que si la tabla contiene la misma fecha elimina/no backupea el archivo (info duplicada)
    try:
        # MAL, EL BACKUP DEBE GUARDARLO CRUDO, NO IMPORTA QUE YO LO VEA MAL, LO PONGO EN UN FORMATTER, PERO PARA NO PERDER NADA LO DEJO SIN MANIPULAR.
        # UNA VEZ QUE LO TENGO CRUDO A WEB, LO [def tokenizarWeb(web_cruda):: web->web_tokenizada]
        # web de urllib debe responder igual (una bsweb) que  (nooo) file from html. No  xq una vez que tengo los datos procesados no lo debo hacer de vuelta.
        # creo (si no existe) un archivo con un nombre asociado a la fecha
        stringfecha = time.strftime("%Y%m%d")
        file_name = 'Fondos-%s.dat' % stringfecha
        html_file = io.open(file_name, 'x', encoding="UTF-8")
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
print(webrio)
# Guardo archivo html y obtengo el html tokenizado
bsweb = backupSourceFile(webrio)
fecha = ""
procesarTabla(bsweb)
tableDate(bsweb)
