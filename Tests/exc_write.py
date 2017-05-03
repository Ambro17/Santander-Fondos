try:
    with open("fname", "x") as fout:
        print("Archivo creado con éxito")
except FileExistsError:
    print("El archivo ya existe")