# Learning to use sqlite databases
import sqlite3
conexion = sqlite3.connect('dummy.db')
c = conexion.cursor()
# c.execute('''CREATE TABLE goles
#                 (minuto integer, goleador text)''') #minuto, goleador
# c.execute("INSERT INTO goles VALUES (90,'Ronaldo')")
# conexion.commit()
# conexion.close()
goles = [(15,'Messi'),
         (35,'Messi'),
         (55,'Ronaldo'),
         ]
    # c = conexion.cursor()
    # c.executemany('INSERT INTO goles VALUES (?,?)', goles)
    # for reg in c.execute('SELECT *  FROM goles ORDER BY minuto'):
    #     print(reg)
    # conexion.commit()
    # conexion.close()
