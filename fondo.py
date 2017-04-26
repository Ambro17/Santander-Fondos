import urllib.request
from bs4 import BeautifulSoup
from itertools import islice
import time
import io
from dateutil import parser
# Nombres identificadores para facilitar la lectura/acceso a la matriz
COLFONDONAME = 0
COLVALFECHA  = 1
COLVARDIARIA = 2
COLLAST30    = 3
COLLAST90    = 4
COLVARANUAL  = 5

def capturarFecha(rows):
    # capturo el string fecha en row 0, parseo la string y la convierto a formato dd/mm/aaaa
    textoFecha = rows[0].th.string
    return parser.parse(textoFecha,fuzzy=True).strftime("%d/%m/%Y")

def capturarCat(rows):
     return rows[1].th.string

def inicializarTablaFondos(rows):
    cant_campos = 6
    cant_fondos_pesos = 21
    tabla = [[0 for i in range(cant_campos)] for j in range(cant_fondos_pesos)]
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

# def getName(anrow):
#     return anrow
#
# def getIndicadores(arow):
#     indicadores = []
#     arow = arow.find_all("td")
#     celdasValores = arow[1:] # la primera tiene el nombre
#     for celda in celdasValores:
#         valor_numerico = celda.string
#         indicadores.append(valor_numerico)
#     return indicadores
# def getData(arow):
#     nombre = arow.td.strings
#     #indicators= getIndicadores(arow)
#     return -1
def getName(arow):
    a = arow.td
    return a

def procesarFondos(rows,fecha):
    # pongo nombres de columnas en primera fila como headers.
    tabla = inicializarTablaFondos(rows)
    rowFondos = rows[3:] # elimino la row fecha,categoria, y tags cuyos datos ya fueron capturados
    i = 1
    for row in islice(rowFondos,35): # limito fondo pesos TODO: agregar el resto
        if row.contents: # if no esta vacìa
            nombre = getName(row)
            #print(name+"\n"+repr(indicadores)+"\n****")
    return -1

def procesarTabla(unaWeb):
    web = removeColTags(unaWeb)
    rows = web.div.table.find_all("tr", recursive=False)
    fecha = capturarFecha(rows)
    categoria = capturarCat(rows)
    procesarFondos(rows,fecha)



""" ######### COMIENZO PROGRAMA ######### """
#   abro página que contiene la tabla a la que llama el html original con ajax
urltabla = "http://www.santanderrio.com.ar/ConectorPortalStore/Rendimiento"
webrio = urllib.request.urlopen(urltabla).read()
# Guardo archivo html
timestr = time.strftime("%Y%m%d")
archivo_html = io.open('Fondos-%s.dat' % timestr, 'w+', encoding="UTF-8")
bsweb = BeautifulSoup(webrio,"html.parser")
archivo_html.write(bsweb.prettify())
fecha = ""
procesarTabla(bsweb)
