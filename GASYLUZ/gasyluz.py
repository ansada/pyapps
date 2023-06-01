import tkinter as tk
from tkinter import messagebox

from Propiedades import *
from DBsql import *
from Controls import *
from Forms import *
from GASYLUZ.Gestores import gestores
from GASYLUZ.Clientes import clientes
from GASYLUZ.Parametros import parametros
from GASYLUZ.Contratos import contratoluz, contratogas
from GASYLUZ.Tarifas import tarifas
from GASYLUZ.Facturacion import facturacion
from GASYLUZ.Facturacion import OrdenFacturacion

from Editor import frmEditor
import Dialogo as dlg

class app(Form):
    """
        Clase de inicio de la aplicación con el nombre que lo contiene
    """
    def __init__(self, hcaller, name=''):
        """ Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos app
        """
        Form.__init__(self, hcaller, name)
        self.title("CONTRATOS ELECTRICIDAD y GAS")
        self.setIcon('img/plug32.gif')
        # Referenciamos propiedades existentes en fichero de parametros
        # que están cargadas en el modulo cmvar - variable properties
        self.prop=cmvar.properties
        # Conexión a datos
        # self.conbd = self.prop.getProperty("host") + "/oil.db"
        conbd = os.path.join(self.prop.getProperty('host'),'gasyluz.db')

        if not db.conecta("GYL", conbd):
            ok = messagebox.askokcancel('ERROR DE CONEXION','No se ha podido conectar a\n'+conbd+"\nContinuar?")
            if ok == False:
                self.closer()
        else:
            self.cnn='GYL'
        
        # Boton Parametros/Settings particulares de LUZ
        self.imgsettings = tk.PhotoImage(file='img/settings32.png')
        self.btnsettings = tk.Button(self.buttonbar, image=self.imgsettings,command=lambda: self.openForm(parametros))
        self.statusbar.createTip(self.btnsettings, "Parámetros Aplicación LUZ [Alt-P]")
        self.btnsettings.pack(side=tk.RIGHT, fill=tk.Y, padx=3, pady=3)
        
        # Definimos self.container no incluido en el Form (clase base)
        self.container=tk.Frame(self)
        
        self.contimage = tk.Frame(self.container)
        self.contitulo = tk.Frame(self.container)
        # Frame contimage (A la izquierda de la pantalla dentro de self.container)
        #self.imgluz = tk.PhotoImage(file='img/icon-electric-power.png')
        self.imgluz = tk.PhotoImage(file='img/gasyluz.png')
        self.lblimg = tk.Label(self.contimage, image=self.imgluz)
        self.lblimg.pack(fill=tk.BOTH, padx=3, pady=3, expand=True)
        # Frame contitulo
        self.cabecera = tk.Label(self.contitulo, text="CONTRATOS Y COMISIONES DE ELECTRICIDAD", font=['helvetica',18,'bold'], justify=tk.CENTER)
        explica='\nRegistro y Consulta de Contratos'
        explica+='\nRenovaciones y Modificaciones'
        explica+='\nFacturación de Comisiones'
        explica+='\nLiquidación de Gestores Colaboradores'
        self.lineas = tk.Label(self.contitulo, text=explica, width=60, justify=tk.CENTER)
        self.cabecera.pack(side=tk.TOP, fill=tk.X, padx=3, pady=3)
        self.lineas.pack(side=tk.TOP, fill=tk.X, padx=3, pady=3)

        # Separador de acceso dentro de contitulo
        # Barra de acceso directo (Añadir height=50 ?)
        self.acceso = tk.Frame(self.contitulo)
        self.prueba=Textbox(self.acceso)
        # Botones Acceso directo
        self.imgcli = tk.PhotoImage(file='img/avatar32.png')
        #self.imgcontratos = tk.PhotoImage(file='img/editArea32.png')
        self.imgconluz = tk.PhotoImage(file='img/plug32.png')
        self.imgcongas = tk.PhotoImage(file='img/gas32.png')
        self.imgadmin = tk.PhotoImage(file='img/iconoUser.png')
        self.btncli = tk.Button(self.acceso, image=self.imgcli,command=lambda: self.openForm(clientes, 'clientes'))
        self.btncli.pack(side=tk.LEFT, padx=3, pady=3)
        self.statusbar.createTip(self.btncli, "Consulta de Clientes [ALT-C]")
        self.btnconluz = tk.Button(self.acceso, image=self.imgconluz, command=lambda: self.openForm(contratoluz, 'contratoluz'))
        self.btnconluz.pack(side=tk.LEFT, padx=3, pady=3)
        self.statusbar.createTip(self.btnconluz, "Consulta/Registro de Contratos Electricidad [ALT-R]")
        self.btncongas = tk.Button(self.acceso, image=self.imgcongas, command=lambda: self.openForm(contratogas, 'contratogas'))
        self.btncongas.pack(side=tk.LEFT, padx=3, pady=3)
        self.statusbar.createTip(self.btncongas, "Consulta/Registro de Contratos de GAS [ALT-A]")
        self.btnges = tk.Button(self.acceso, image=self.imgadmin, command=lambda: self.openForm(gestores, 'gestores'))
        self.btnges.pack(side=tk.LEFT, padx=3, pady=3)
        self.statusbar.createTip(self.btnges, "Consulta de Gestores de Clientes [ALT-G]")


        # Empaquetado
        self.contimage.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.contitulo.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.acceso.pack(side=tk.BOTTOM, fill=tk.X, padx=3, pady=3)
        tk.Frame(self.contitulo, background='black', height=1).pack(side=tk.BOTTOM, fill=tk.X)
        #self.htmltit.pack(side=tk.TOP, fill=tk.BOTH, padx=3, pady=3)
        self.container.pack(fill=tk.BOTH, expand=True)
        #
        tk.Frame(self.contitulo, height=1, bg='black').pack(side=tk.BOTTOM, fill=tk.X)
        #self.center()
       
        self.defineMenu()
        self.defineAceleradoras()

    def defineMenu(self):
        # Menu ventana
        self.menubar = tk.Menu(self)
        self.mnuArch = tk.Menu(self.menubar, tearoff=False)
        self.mnuCont = tk.Menu(self.menubar, tearoff=False)
        self.mnuFact = tk.Menu(self.menubar, tearoff=False)
        self.mnuUtil = tk.Menu(self.menubar, tearoff=False)
        # Menu Archivo
        self.menubar.add_cascade(label="Ficheros", underline=0, menu=self.mnuArch)
        self.mnuArch.add_command(label="Clientes", underline=0, accelerator="Alt-C",command=lambda: self.openForm(clientes, 'clientes'))
        self.mnuArch.add_command(label="Gestores", underline=0, accelerator="Alt-G",command=lambda: self.openForm(gestores,'gestores'))
        self.mnuArch.add_command(label="Tarifas", command=lambda: self.openForm(tarifas, 'tarifas'))
        self.mnuArch.add_separator()
        self.mnuArch.add_command(label="Salir", underline=0, command=self.closer, accelerator="Alt-S")

        # Menu Contrato
        self.menubar.add_cascade(label="Contratos", underline=2, menu=self.mnuCont)
        self.mnuCont.add_command(label="Registro Electridad", underline=0, accelerator="Alt-R", command=lambda: self.openForm(contratoluz, 'contratoluz'))
        self.mnuCont.add_command(label="Registro GAS", underline=0, accelerator="Alt-A", command=lambda: self.openForm(contratogas, 'contratogas'))
        self.mnuCont.add_command(label="Consulta", underline=5, accelerator="Alt-L", command=self.on_Opcion)
        self.mnuCont.add_command(label="Cambios", underline=2, accelerator="Alt-M", command=self.on_Opcion)
        self.mnuCont.add_separator()
        self.mnuCont.add_command(label="Ofertas", command=self.on_Opcion)
        
        # Menu Facturacion
        self.menubar.add_cascade(label="Facturación", underline=8, menu=self.mnuFact)
        self.mnuFact.add_command(label="Orden Facturación", underline=0, accelerator="Alt-O",command=lambda: self.openForm(OrdenFacturacion, 'ordenfac'))
        self.mnuFact.add_command(label="Consulta Facturas Emitidas", underline=6, accelerator="Alt-T",command=lambda: self.openForm(facturacion,'facturacion'))
        self.mnuFact.add_command(label="Comisiones por Gestión", command=self.on_Opcion)

        # Menu Utilidad
        self.menubar.add_cascade(label="Utilidad", underline=0, menu=self.mnuUtil)
        self.mnuUtil.add_command(label="Parametros-Settings", underline=6, accelerator="Alt-P", command=self.on_Opcion)
        self.mnuUtil.add_command(label="Editar Texto", underline=0, accelerator="Alt-E", command=lambda: self.openForm(frmEditor,'Editor'))
        self.mnuUtil.add_command(label="Acerca de ...", command=self.on_Acerca)

        self.config(menu=self.menubar)

    def defineAceleradoras(self):
        # Shortcuts - ventana principal
        # command=lambda: self.openForm('frmadmin', frmadmin)
        self.bind("<Alt-p>", lambda e: self.openForm(parametros))
        self.bind("<Alt-P>", lambda e: self.openForm(parametros))
        self.bind("<Alt-G>", lambda e: self.openForm(gestores,'gestores'))
        self.bind("<Alt-g>", lambda e: self.openForm(gestores,'gestores'))
        self.bind("<Alt-c>", lambda e: self.openForm(clientes, 'clientes'))
        self.bind("<Alt-C>", lambda e: self.openForm(clientes, 'clientes'))
        self.bind("<Alt-e>", lambda e: self.openForm(frmEditor, 'editor'))
        self.bind("<Alt-E>", lambda e: self.openForm(frmEditor, 'editor'))
        self.bind("<Alt-a>", lambda e: self.openForm(contratogas,'contratogas'))
        self.bind("<Alt-A>", lambda e: self.openForm(contratogas,'contratogas'))
        self.bind("<Alt-r>", lambda e: self.openForm(contratoluz,'contratoluz'))
        self.bind("<Alt-R>", lambda e: self.openForm(contratoluz,'contratoluz'))
        # self.bind("<Alt-G>", lambda e: self.verPedFra0)
        # self.bind("<Alt-g>", lambda e: self.verPedFra0)

    def on_Opcion(self, event=""):
        messagebox.showinfo("MENU", "Seleccionada Opción de Menu",parent=self)

    def on_Acerca(self, event=""):
        strmsg="\t\tGAS Y LUZ\n"
        strmsg+="\nRegistro y control de contratos de ELECTRICIDAD y GAS"
        strmsg+="\nRenovaciones y Modificaciones de contratos"
        strmsg+="\nFacturación de comisiones"
        strmsg+="\nControl de liquidaciones por contrato a colaboradores"
        
        # messagebox.showinfo("APLICACION LUZ", strmsg, parent=self)
        acercade = dlg.dialogo(self, 'APLICACION LUZ', strmsg, ['ACEPTAR'], dlg.INFO).showmodal()
        
    
    def closer(self, evt=None):
        # Como estamos en punto de entrada a la aplicación oil
        # cerramos bases de datos que podrían estar abiertas
        db.close("GYL")
        db.close("FAC")
        # self.hcaller.show()
        # Llamamos al método que sobrecargamos en esta instancia de Form
        super().closer()

    # def on_facturas(self, *args):
    #     pass