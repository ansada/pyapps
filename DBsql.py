import sqlite3
import pandas as pd

class db():

    cnn = {}
    current = ""
    dirhost = "."

    # def __init__(self, db = "libros.db"):
    #     """
    #     Conectamos con la base de datos que recibimos
    #     como parámetro
    #     """

    #     try:
    #         self.condb = sqlite3.connect(db)
    #         self.condb.row_factory = sqlite3.Row

    #     except:
    #         # Se ha producido algún error
    #         # No se actualiza current y devuelve none
    #         print("No se ha podido conectar")

    @staticmethod
    def setCurrent(indice: str):
        # Si el indice solicitado existe 
        # se convierte en el conexion actual
        if(indice in db.cnn):
            db.current = indice
        else:
            return False

        return True

    @staticmethod
    def find(tabla:str, con="", donde="",orden=""):
        # Construimos la consulta simple para la tabla solicitada
        # y devolvemos el resultado de consultar() sin parámetros
        # de la conexion solicitada
        strsql = "SELECT * FROM {}".format(tabla)

        if donde:
            strsql=strsql+" WHERE "+donde

        if orden:
            strsql=strsql+' ORDER BY '+orden

        return db.consultar(strsql, "", con)

    @staticmethod
    def conecta(indice: str, fichero: str):

        if(indice not in db.cnn):
            # No existe la conexión, la añado
            try:
                db.cnn[indice] = sqlite3.connect(fichero)
                db.cnn[indice].row_factory = sqlite3.Row
                # Si es la primera conexión esta sera la current conexion
                if len(db.cnn) == 1:
                    db.current=indice

            except:
                # Se ha producido un error y no se ha conectado
                return False
        
        # La conexión ya existía o se ha establecido
        return True

    @staticmethod
    def close(indice):
        if(indice in db.cnn):
            db.cnn[indice].close()
            db.cnn.pop(indice)
            if indice==db.current:
                # Eliminada current conexion
                if len(db.cnn)>0:
                    db.current=list(db.cnn.keys())[0]
                else:
                    #No hay mas conexiones, current nula
                    db.current=""
        else:
            return False
            # print("No existe el índice")

        return True

    @staticmethod
    def closeall():
        for con in db.cnn:
            db.cnn[con].close()

        db.cnn.clear()

        # Cerradas todas las conexiones
        db.current=""
        
        return

    @staticmethod
    def verconexiones():
        # Por depuración mostramos las conexiones abiertas por consola
        print("{:15}     {:50}".format("NOMBRE","CONEXION"))
        print("="*65)
        for conexion in db.cnn:
            cur = db.cnn[conexion].cursor()
            cur.execute("PRAGMA database_list;")
            rst = cur.fetchone()
            print("{}{:15} >>> {:50}".format("#" if conexion==db.current else ">", conexion, rst[-1]))
        

    @staticmethod
    def consultar(strsql, par=(), con=""):

        if con=="":
            con=db.current
            
        if con not in db.cnn:
            # Conexion inexistente, salgo sin consultar
            # y es erronea (False)
            print("conexión no existe o es errónea")
            return [{}]

        cursor = db.cnn[con].cursor()
        strsql = strsql.format(*par)
        rst = cursor.execute(strsql, par)
        result = [dict(row) for row in rst.fetchall()]
        for r in result:
            for campo in r:
                if r[campo] == None:
                    r[campo] = " "

        db.cnn[con].commit()

        return result

    @staticmethod
    def actualiza(strsql, con=""):

        if con=="":
            con=db.current
            
        if con not in db.cnn:
            # Conexion inexistente, salgo sin consultar
            # y es erronea (False)
            print("La conexión no existe o es errónea: " + con)
            return False

        cursor = db.cnn[con].cursor()
        cursor.execute(strsql)

        db.cnn[con].commit()

        return

    @staticmethod
    # def dfquery(strsql, par=(), con="", indice="", fechas=None):
    def dfquery(strsql, par=(), con="", fechas=None):
        ''' Consulta que devuelve un DataFrame Pandas'''
        #
        if con=="":
            dfcon=db.current
            
        if con not in db.cnn:
            # Conexion inexistente, salgo sin consultar
            # y es erronea (False)
            print("conexión no existe o es errónea")
            return pd.DataFrame({})
        else:
            dfcon=db.cnn[con]

        strsql = strsql.format(*par)
        dfrst = pd.read_sql(strsql, dfcon, parse_dates=fechas)
        
        return dfrst
    
    @staticmethod
    def getIndice(result, campo, valor):
        if len(result) == 0:
            print("No hay registros para buscar")
            return -1
        
        encontrado = -1
        for indice in range(len(result)):
            if result[indice][campo]==valor:
                encontrado=indice

        return encontrado
    
    @staticmethod
    def existeValor(tabla, campo, valor, conexion=''):
        '''
        Buscamos una coincidencia de [campo]==[valor]
        dentro de tabla en conexion 
        '''
        rst=db.consultar('SELECT {} FROM {} WHERE {} = "{}"'.format(campo,tabla,campo,valor),(),conexion)

        return len(rst)
    