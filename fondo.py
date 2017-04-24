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

def procesarFondos(rows):
    rowsFondos = rows[2:] # perdon dios de la programación

    return -1
def procesarTabla(unaWeb,fecha, tabla):
    rows = web.find_all("tr")
    fecha = capturarFecha(rows)
    categoria = capturarCat(rows)
    procesarFondos(rows)



""" ######### COMIENZO PROGRAMA ######### """
#abro página que contiene la tabla a la que llama el html original con ajax
tabla = [[0 for i in range(6)] for j in range(21)] #matriz de 8 columnas y 17 filas
urltabla = "http://www.santanderrio.com.ar/ConectorPortalStore/Rendimiento"
webrio = urllib.request.urlopen(urltabla).read()
# Guardo archivo html
timestr = time.strftime("%Y%m%d")
archivo_html = io.open('Fondos-%s.dat' % timestr, 'w+', encoding="UTF-8")
web = BeautifulSoup(webrio,"html.parser")
archivo_html.write(web.prettify())
fecha = ""
procesarTabla(web,fecha,tabla)
