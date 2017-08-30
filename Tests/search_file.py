import os
import io
def retrieveFile():

    try:
        with open("filetosearch", "x") as fout:
            print("Archivo creado con éxito")
    except FileExistsError:
        # obtener el directorio padre del path absoluto de mi archivo
        parent_path = os.path.dirname(os.path.abspath(__file__))
        existing_file = io.open(parent_path + "/filetosearch", "r+", encoding="UTF-8")
        read_file = existing_file.read()
        print(read_file)
retrieveFile()