import tkinter as tk
#from tkinter import ttk
from tkinter import messagebox

from Controls import *
from Forms import *

class temporal(Form):
    """
        Clase de inicio de la aplicación con el nombre que lo contiene
    """

    def __init__(self, hcaller, name=''):
        """ Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos app y el name que le da el caller
        """
        super().__init__(hcaller, name)
        self.title("APLICACION EN DESARROLLO")
        # Definimos self.container no incluido en el Form (clase base)
        self.container=tk.Frame(self)
        
        self.contimage = tk.Frame(self.container)
        self.contitulo = tk.Frame(self.container)
        # Frame contimage (A la izquierda de la pantalla dentro de self.container)
        self.imgoil = tk.PhotoImage(file='img/enConstruccion400.png')
        self.lblimg = tk.Label(self.contimage, image=self.imgoil)
        self.lblimg.pack(fill=tk.BOTH, padx=3, pady=3, expand=True)
        # Frame contitulo
        txttitulo='ACCESO\nTEMPORALMENTE\nINHABILITADO'
        self.cab = tk.Label(self.contitulo, text=txttitulo, font=['helvetica',18,'bold'], justify=tk.CENTER)
        
        explica='\nEsta pantalla impide el acceso a la aplicación'
        explica+='\nSe encuentra en proceso de desarrollo'
        explica+='\nPulse [Alt-S] o seleccione botón Salir'
        explica+='\npara cerrar este formulario'
        self.lineas = tk.Label(self.contitulo, text=explica, width=60, justify=tk.CENTER)
        
        # La empaquetamos despues de mostrar la barra de botones de 
        # acceso rapido.

        # Empaquetado
        self.contimage.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.contitulo.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.cab.pack(side=tk.TOP, fill=tk.X, padx=3, pady=3)
        self.lineas.pack(side=tk.TOP, fill=tk.X, padx=3, pady=3)
        #self.htmltit.pack(side=tk.TOP, fill=tk.BOTH, padx=3, pady=3)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.center()
    # Eventos 
        


        
        
