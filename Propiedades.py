# Propiedades de la aplicación
import os
import pickle

class propiedades():

    def __init__(self, fichero):
        # Directorio de ejecución de la aplicación
        self.pathfile = os.path.join(os.getcwd(), fichero+'.cnf')
        if os.path.isfile(self.pathfile):
            # El fichero EXISTE 
            # Cargamos en el diccionario
            self.loadProperties()

        else:
            # El fichero NO EXISTE')
            # Lo creamos con un diccionario vacío
            self.parametros={'fuente':'Helvetica,12,normal,roman',
                             'iva': 21.00, 'irpf': 15.00 }
            self.saveProperties()
        
    def getProperty(self, clave, defecto=''):
        if clave in self.parametros.keys():
            # Existe la propiedad
            return self.parametros[clave]
        else:
            if defecto != '':
                # Si defecto no es nulo queremos
                # crear si no existe
                self.parametros[clave]=defecto
                # y devolvemos lo creado
                return defecto
            else:
                # No existe devolvemos cadena vacía
                return ''
        
    def setProperty(self, clave, valor):
        # La entrada existe, la modificamos con el valor
        # y si no existiese se crearía con el valor recibido
        self.parametros[clave]=valor

    def existProperty(self, clave:str):
        # Permite comprobar que la clave existe en el dict.
        if clave in self.parametros.keys():
            return True
        else:
            return False

    def getProperties(self):
        # Devolvemos el diccionario completo
        return self.parametros

    def updateProperties(self, param, salvar=False):
        # Esto es para sustituir todo el diccionario
        self.parametros = param
        if salvar == True:
            # Si el parámetro salvar es True
            # actualizamos el fichero
            self.saveProperties()

    def saveProperties(self):
        self.fichero = open(self.pathfile, 'wb')
        pickle.dump(self.parametros, self.fichero)
        self.fichero.close()

    def loadProperties(self):
        self.fichero = open(self.pathfile, 'rb')
        self.parametros = pickle.load(self.fichero)
        self.fichero.close()



