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
    tabla = [[0 for i in range(6)] for j in range(21)]
    # capturo la tr que contiene los nombres de las columnas para los valores del fondo
    rowTags = rows[2]
    i=0
    for th in rowTags.find_all("th"):
        tabla[0][i] = th.string
        i+=1
    return tabla


def procesarFondos(rows):
    tabla = inicializarTablaFondos(rows)
    rowFondos = rows[3:] # elimino la row fecha,categoria, y tags cuyos datos ya fueron capturados
    i = 1
    for row in islice(rowFondos,35): # limito fondo pesos TODO: agregar el resto
        if row.contents: # si tiene contenido
            j = 0
            for valor in valores:
                tabla[i][j] = valor
                j+=1
            print("Check solo quedan valores")
            print(row)
            i+=1
    return -1

def procesarTabla(unaWeb,fecha):
    rows = web.find_all("tr")
    fecha = capturarFecha(rows)
    categoria = capturarCat(rows)
    procesarFondos(rows)



""" ######### COMIENZO PROGRAMA ######### """
#   abro página que contiene la tabla a la que llama el html original con ajax
urltabla = "http://www.santanderrio.com.ar/ConectorPortalStore/Rendimiento"
webrio = urllib.request.urlopen(urltabla).read()
# Guardo archivo html
timestr = time.strftime("%Y%m%d")
archivo_html = io.open('Fondos-%s.dat' % timestr, 'w+', encoding="UTF-8")
web = BeautifulSoup(webrio,"html.parser")
archivo_html.write(web.prettify())
fecha = ""
procesarTabla(web,fecha)
