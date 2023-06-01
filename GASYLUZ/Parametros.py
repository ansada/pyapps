import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from Propiedades import *
from DBsql import *
from Controls import *
from Forms import *
#from tkhtmlview import HTMLLabel


class parametros(Form):
    """
        Formulario Parámetros aplicación

    """

    def __init__(self, hcaller, name=''):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario Toplevel
        """
        self.hcaller = hcaller

        super().__init__(hcaller, name)
        self.title("PARAMETROS APLICACION LUZ")

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
        self.txttlf1 =tk.Entry(self.contenido, takefocus=0, readonlybackground='white', width=9)
        self.txttlf1.grid(row=3, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttlf2 =tk.Entry(self.contenido,  takefocus=0, readonlybackground='white', width=9)
        self.txttlf2.grid(row=3, column=2, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtemail =tk.Entry(self.contenido,  takefocus=0, readonlybackground='white', width=40)
        self.txtemail.grid(row=3, column=4, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.contenido, text="Cliente Facturación:").grid(row=4, column=0, sticky=tk.E)
        clientesfac = self.qryClientesFac()
        self.cmbclifac = ttk.Combobox(self.contenido, state="readonly", values=clientesfac)
        self.cmbclifac.grid(row=4, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        
        self.contenido.grid_rowconfigure(8, weight=1)
        self.contenido.grid_columnconfigure(1, weight=1)
        self.contenido.grid_columnconfigure(2, weight=1)
        self.contenido.grid_columnconfigure(4, weight=1)
        
        self.contenido.pack(fill=tk.BOTH, expand=True)

        self.showFields()


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
        self.prop.setProperty('clifacluz', self.idCliFac())
        self.prop.saveProperties()
        messagebox.showinfo(
            "Parametros LUZ", "Guardados datos modificados", parent=self)
        self.closer()

    def on_loadpar(self, *args):

        self.clearFields()
        self.showFields()

    # Metodos
    def clearFields(self):
        #  Limpiar value de los entry
        for w in self.contenido.winfo_children():
            if w.winfo_class()=='Entry':
                w.delete(0,'end')
                if w['state']=='readonly':
                    w['state']='normal'
                    w.delete(0,'end')
                    w['state']='readonly'
                    
            
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
        # Nos situamos y mostramos el cliente facturación
        cliente = self.nomCliFac(self.prop.getProperty("clifacluz", 0))
        if cliente == 0:
            self.cmbclifac.current(0)
        else:
            for n in range(len(self.cmbclifac["values"])):
                if self.cmbclifac["values"][n] == cliente:
                    self.cmbclifac.current(n)
                    break 

        # Enfocamos en campo que se acepta primero
        self.cmbclifac.focus_force()

    def idCliFac(self):
        bd = self.prop.getProperty("host") + "/fac.db"
        idCliente = 0
        if db.conecta("FAC", bd):
            strsql = 'SELECT id FROM clientes WHERE empcli=?'
            rst = db.consultar(strsql, (self.cmbclifac.get(),), con="FAC")
            if len(rst) > 0:    # Quiere decir que ha devuelto un registro
                idCliente = rst[0]["id"]

        return idCliente

    def nomCliFac(self, idCliente):
        bd = self.prop.getProperty("host") + "/fac.db"
        Cliente = ""
        if db.conecta("FAC", bd):
            strsql = 'SELECT empcli FROM clientes WHERE id=?'
            rst = db.consultar(strsql, par=(idCliente,), con="FAC")
            if len(rst) > 0:    # Quiere decir que ha devuelto un registro
                Cliente = rst[0]["empcli"]

        return Cliente

    def qryClientesFac(self):
        bd = self.prop.getProperty("host") + "/fac.db"
        clientes=tuple()
        if db.conecta("FAC", bd):
            strsql = 'SELECT * FROM clientes ORDER BY empcli'
            rst = db.consultar(strsql, con="FAC")
            nombres = []
            for registro in rst:
                nombres.append(registro["empcli"])
                clientes=tuple(nombres)
        else:
            clientes = list("ERROR",)

        return clientes