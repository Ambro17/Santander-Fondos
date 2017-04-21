import urllib.request
from bs4 import BeautifulSoup
from itertools import islice
import time
import io
# Nombres identificadores para facilitar la lectura/acceso a la matriz
COLFONDONAME = 0
COLVALFECHA  = 1
COLVARDIARIA = 2
COLLAST30    = 3
COLLAST90    = 4
COLVARANUAL  = 5

def esHeader(arow):
    return arow.find("th") is not None


def procesarTabla(unaWeb,matriz):
    #capturar headers (fecha), inicializar tabla.
    rows = web.find_all("tr")
    finTablaPesos = 38 # para no capturar la tabla dolares aun TODO: feature innecesaria
    for row in islice(rows,finTablaPesos): # row 39 muestra Dol ? ##genera problemas de iteraciones excesivas artificiales? chequear con zip
        i = 0
        if (esHeader(row)): #limita a los 3 headers
            print(row)
            try:
                if row.th["class"] == 'th2':
                    print("Hola")
                    print(row.string)
            except KeyError:
                print("El elemento '" + row.name + "' no tiene una clase.") #aaaah es por la tercera. Evitar que caiga acá simplemente



            #else: ## Trato los namefondo y relleno los campos en matriz
        #    print("no soy header :(, soy un fondo con mmis valores para cada campo header")
        #celda = row.find_all("td")
        #print("Valor de Celda:\n")
        #print(celda)
        #print("**************************************")


""" ######### COMIENZO PROGRAMA ######### """
#abro página que contiene la tabla a la que llama el html original con ajax
matriz = [[0 for i in range(6)] for j in range(21)] #matriz de 8 columnas y 17 filas
urltabla = "http://www.santanderrio.com.ar/ConectorPortalStore/Rendimiento"
webrio = urllib.request.urlopen(urltabla).read()
# Guardo archivo html
timestr = time.strftime("%Y%m%d")
archivo_html = io.open('Fondos-%s.dat' % timestr, 'w+', encoding="UTF-8")
web = BeautifulSoup(webrio,"html.parser")
archivo_html.write(web.prettify())
#procesarTabla(web,matriz)
