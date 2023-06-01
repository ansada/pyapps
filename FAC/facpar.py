import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from Propiedades import *
from DBsql import *
from Controls import *
from Forms import *
import datetime

class frmparam(Form):
    """
        Formulario Parámetros aplicación

    """

    def __init__(self, hcaller, name=''):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario Toplevel
        """
        self.hcaller = hcaller

        super().__init__(hcaller, name)
        self.title("PARAMETROS APLICACION OIL")

        self.setIcon('img/settings32.gif')
        # Solo para debug (inicializamos tamaño)
        # self.geometry("1000x480+200+200")
        # Cargamos propiedades existentes en fichero de parametros
        self.prop=cmvar.properties
        
        # Boton Guardar 
        self.imgsave = tk.PhotoImage(file='img/save32.png')
        self.btnsave = tk.Button(self.buttonbar, image=self.imgsave, command=self.on_savepar)
        self.btnsave.pack(side=tk.RIGHT, fill=tk.X, padx=3, pady=3)
        self.statusbar.createTip(self.btnsave, "Guardar datos modificados [F3]")
        self.bind('<F3>', self.on_savepar)
        # Boton Recargar
        self.imgundo = tk.PhotoImage(file='img/reload32.png')
        self.btnundo = tk.Button(self.buttonbar, image=self.imgundo, command=self.on_loadpar)
        self.btnundo.pack(side=tk.RIGHT, fill=tk.X, padx=3, pady=3)
        self.statusbar.createTip(self.btnundo, "Deshacer cambio y recargar [Alt-U]")
        self.bind('<Alt-u>', self.on_loadpar)
        
        # Area de contenido
        self.contenido=tk.Frame(self, pady=10, highlightbackground="black", highlightthickness=1)

        # Mostramos datos titular de las aplicaciones (NO MODIFICABLE EN este formulario)
        tk.Label(self.contenido, text="Titular:").grid(row=0, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="DNI:").grid(row=0, column=3, sticky=tk.E)
        tk.Label(self.contenido, text="Dirección:").grid(row=1, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="Distrito:").grid(row=1, column=3, sticky=tk.E)
        tk.Label(self.contenido, text="Población:").grid(row=2, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="Provincia:").grid(row=2, column=3, sticky=tk.E)
        tk.Label(self.contenido, text="Teléfonos:").grid(row=3, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="Mail:").grid(row=3, column=3, sticky=tk.E)
        self.txttitular=tk.Entry(self.contenido, takefocus=0, readonlybackground='white')
        self.txttitular.grid(row=0, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtdni=tk.Entry(self.contenido, width=9,  takefocus=0, readonlybackground='white')
        self.txtdni.grid(row=0, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtdireccion=tk.Entry(self.contenido,  takefocus=0, readonlybackground='white')
        self.txtdireccion.grid(row=1, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtdistrito=tk.Entry(self.contenido,  takefocus=0, readonlybackground='white', width=5)
        self.txtdistrito.grid(row=1, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtpoblacion=tk.Entry(self.contenido, takefocus=0, readonlybackground='white')
        self.txtpoblacion.grid(row=2, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtprovincia=tk.Entry(self.contenido,  takefocus=0, readonlybackground='white')
        self.txtprovincia.grid(row=2, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttlf1 = tk.Entry(self.contenido, takefocus=0, readonlybackground='white', width=9)
        self.txttlf1.grid(row=3, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttlf2 = tk.Entry(self.contenido,  takefocus=0, readonlybackground='white', width=9)
        self.txttlf2.grid(row=3, column=2, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtemail = tk.Entry(self.contenido,  takefocus=0, readonlybackground='white', width=40)
        self.txtemail.grid(row=3, column=4, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        
        self.contenido.grid_rowconfigure(8, weight=1)
        self.contenido.grid_columnconfigure(1, weight=1)
        self.contenido.grid_columnconfigure(2, weight=1)
        self.contenido.grid_columnconfigure(4, weight=1)
        
        self.contenido.pack(side=tk.TOP, fill=tk.X)

        # Area detalle de parametros de Fac
        self.detalle=tk.Frame(self, pady=10, highlightbackground="black", highlightthickness=1)

        # Mostramos datos titular de las aplicaciones (NO MODIFICABLE EN este formulario)
        tk.Label(self.detalle, text="IVA por defecto:").grid(row=0, column=1, sticky=tk.E)
        tk.Label(self.detalle, text="IRPF por defecto:").grid(row=0, column=3, sticky=tk.E)
        tk.Label(self.detalle, text="Porcentaje gastos dificil justificación:").grid(row=1, column=0, columnspan=2, sticky=tk.E)
        tk.Label(self.detalle, text="Con un límite máximo de gastos:").grid(row=1, column=3,sticky=tk.E)
        tk.Label(self.detalle, text="Porcentaje Cálculo Rendimiento Neto:").grid(row=2, column=0, columnspan=2, sticky=tk.E)
        tk.Label(self.detalle, text="Ultimo cierre Año-Periodo:").grid(row=2, column=3, sticky=tk.E)

        self.txtiva=Numbox(self.detalle, width=5, decimales=2, background='white')
        self.txtiva.grid(row=0, column=2, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtirpf=Numbox(self.detalle, width=5, decimales=2, background='white')
        self.txtirpf.grid(row=0, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtgastos=Numbox(self.detalle, width=5, decimales=2, bg='white')
        self.txtgastos.grid(row=1, column=2, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtlimite=Numbox(self.detalle, width=5,background='white')
        self.txtlimite.grid(row=1, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtrdoneto = Numbox(self.detalle, width=5, decimales=2, background='white')
        self.txtrdoneto.grid(row=2, column=2, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtultimo=tk.Entry(self.detalle, width=5, bg='white', takefocus=0, readonlybackground='white')
        self.txtultimo.grid(row=2, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)

        self.detalle.columnconfigure(1, weight=1)
        self.detalle.columnconfigure(3, weight=1)

        self.detalle.pack(side=tk.BOTTOM, fill=tk.X)

        self.showFields()
        self.showDetalle()
        # No centramos porque parece que sale correcto sin mover ventana
        # self.center()
        # Hacemos que sea el form superior hasta que se cierre
        # y no acepte eventos en otros formularios
        # self.grab_set()
        # y siempre se muestre encima de todas
        # self.attributes('-topmost', 'true')

    def center(self):
        self.update_idletasks()
        altoScreen = int(self.winfo_screenheight())
        anchoScreen = int(self.winfo_screenwidth())
        altoWin = int(self.winfo_height())
        anchoWin = int(self.winfo_width())
        posx = int((anchoScreen - anchoWin) / 2)
        posy = int((altoScreen - altoWin) / 4)

        posicion = str(anchoWin) + "x" + str(altoWin) + \
            "+" + str(posx) + "+" + str(posy)
        self.geometry(posicion)

    # Eventos

    def on_savepar(self, *args):
        # Actualizamos valores
        self.prop.setProperty('defiva', float(self.txtiva.get()))
        self.prop.setProperty('defirpf', float(self.txtirpf.get()))
        self.prop.setProperty('rdoneto', float(self.txtrdoneto.get()))
        self.prop.setProperty('porcentajeGastos', float(self.txtgastos.get()))
        self.prop.setProperty('limiteGtos', int(self.txtlimite.get()))
    
        self.prop.saveProperties()
        messagebox.showinfo(
            "Parametros FAC", "Guardados datos modificados", parent=self)
        self.closer()

    def on_loadpar(self, *args):

        self.clearFields()
        self.showFields()

    # Metodos
    def clearFields(self):
        #  Limpiar value de los entry
        for w in self.detalle.winfo_children():
            if w.winfo_class()=='Entry':
                if w['state']=='readonly':
                    w['state']='normal'
                    w.delete(0,'end')
            # if Entry in w.mro():
            #     w.delete(0, 'end')
            
    def showFields(self, event=""):
        self.txttitular["state"]='normal'
        self.txtdni["state"]='normal'
        self.txtdireccion["state"]='normal'
        self.txtdistrito["state"]='normal'
        self.txtpoblacion["state"]='normal'
        self.txtprovincia["state"]='normal'
        self.txttlf1["state"]='normal'
        self.txttlf2["state"]='normal'
        self.txtemail["state"]='normal'
        self.txttitular.insert(0, self.prop.getProperty("titular"))
        self.txtdni.insert(0, self.prop.getProperty("dni"))
        self.txtdireccion.insert(0, self.prop.getProperty("direccion"))
        self.txtdistrito.insert(0, self.prop.getProperty("distrito"))
        self.txtpoblacion.insert(0, self.prop.getProperty("poblacion"))
        self.txtprovincia.insert(0, self.prop.getProperty("provincia"))
        self.txttlf1.insert(0, self.prop.getProperty("telefono1"))
        self.txttlf2.insert(0, self.prop.getProperty("telefono2"))
        self.txtemail.insert(0, self.prop.getProperty("mail"))
        self.txttitular["state"]='readonly'
        self.txtdni["state"]='readonly'
        self.txtdireccion["state"]='readonly'
        self.txtdistrito["state"]='readonly'
        self.txtpoblacion["state"]='readonly'
        self.txtprovincia["state"]='readonly'
        self.txttlf1["state"]='readonly'
        self.txttlf2["state"]='readonly'
        self.txtemail["state"]='readonly'

    def showDetalle(self):
        # Porcentaje IVA por defecto
        if self.prop.existProperty('defiva'):
            iva = self.prop.getProperty('defiva')
        else:
            iva = 21.00

        self.txtiva.set_texto(f'{iva:5.2f}')
        # Porcentaje IRPF por defecto
        if self.prop.existProperty('defirpf'):
            irpf = self.prop.getProperty('defirpf')
        else:
            irpf = 15.00

        self.txtirpf.set_texto(f'{irpf:5.2f}')
        # Porcentaje rendimiento neto
        if self.prop.existProperty('rdoNeto'):
            rdoNeto = self.prop.getProperty('rdoNeto')
        else:
            rdoNeto = 20.00
        
        self.txtrdoneto.set_texto(f'{rdoNeto:5.2f}')
        # Porcentaje gastos dificil justificación
        if self.prop.existProperty('porcentajeGastos'):
            prcGastos = self.prop.getProperty('porcentajeGastos')
        else:
            prcGastos = 5
        
        self.txtgastos.set_texto(f'{prcGastos:5.2f}')
        # Limite de gastos de dificil justificación
        if self.prop.existProperty('limiteGtos'):
            limite = self.prop.getProperty('limiteGtos')
        else:
            limite = 2000
        
        self.txtlimite.set_value(limite)
        # Ultimo Cierre realizado
        if self.prop.existProperty('ultimoCierre'):
            cierre = self.prop.getProperty('ultimoCierre')
        else:
            # Si no existe el del ultimo trimestre.
            periodo= int((datetime.date.today().month + 2) / 3)
            if periodo == 1:
                cierre = (datetime.date.today().year - 1) * 10 + 4
            else:
                cierre = datetime.date.today().year * 10 + periodo

        self.txtultimo.insert(0, str(cierre))
        self.txtultimo['state']='readonly'
        
        self.txtiva.focus()
        