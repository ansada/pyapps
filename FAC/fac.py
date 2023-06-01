import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from Propiedades import *
from DBsql import *
from Controls import *
from Forms import *
from FAC.facpar import frmparam
from Editor import frmEditor
import Dialogo
from Dialogo import dialogo
from FAC.Proveedores import frmAcreedor
from FAC.Clientes import frmCliente
from FAC.Tipos import frmtipgto, frmtiping
from FAC.Facturacion import facturar

class app(Form):
    """
        Clase de inicio de la aplicación con el nombre que lo contiene
    """
    def __init__(self, hcaller, name=''):
        """ Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos app
        """
        Form.__init__(self, hcaller, name)
        self.title("FACTURACION E IMPUESTOS")
        self.setIcon('img/conta32.gif')
        # Referenciamos propiedades existentes en fichero de parametros
        # que están cargadas en el modulo cmvar - variable properties
        self.prop=cmvar.properties
        # Conexión a datos
        # self.conbd = self.prop.getProperty("host") + "/oil.db"
        conbd = os.path.join(self.prop.getProperty('host'),'fac.db')
        self.cnn='FAC'

        if not db.conecta(self.cnn, conbd):
            ok = messagebox.askokcancel('ERROR DE CONEXION','No se ha podido conectar a\n'+conbd+"\nContinuar?")
            if ok == False:
                self.closer()
    
        # Boton Parametros/Settings particulares de LUZ
        self.imgsettings = tk.PhotoImage(file='img/settings32.png')
        self.btnsettings = tk.Button(self.buttonbar, image=self.imgsettings,command=lambda: self.openForm(frmparam))
        self.statusbar.createTip(self.btnsettings, "Parámetros Aplicación LUZ [Alt-P]")
        self.btnsettings.pack(side=tk.RIGHT, fill=tk.Y, padx=3, pady=3)
        
        # Definimos self.container no incluido en el Form (clase base)
        self.container=tk.Frame(self)
        
        self.contimage = tk.Frame(self.container)
        self.contitulo = tk.Frame(self.container)
        # Frame contimage (A la izquierda de la pantalla dentro de self.container)
        self.imgluz = tk.PhotoImage(file='img/conta425.png')
        self.lblimg = tk.Label(self.contimage, image=self.imgluz)
        self.lblimg.pack(fill=tk.BOTH, padx=3, pady=3, expand=True)
        # Frame contitulo
        txttitulo='\nGESTION DE FACTURACION E IMPUESTOS'
        self.cab = tk.Label(self.contitulo, text=txttitulo, font=['helvetica',18,'bold'], justify=tk.CENTER)
        
        explica='\nDeclaración de IVA modelo 303'
        explica+='\nDeclaración de IRPF modelo 110'
        explica+='\nEstadística Ingresos y Gastos'
        explica+='\nControl de amortización de compras'
        self.lineas = tk.Label(self.contitulo, text=explica, width=60, justify=tk.CENTER)
        # La empaquetamos despues de mostrar la barra de botones de 
        # acceso rapido.

        # Separador de acceso dentro de contitulo
        # Barra de acceso directo (Añadir height=50 ?)
        self.acceso = tk.Frame(self.contitulo)
        self.prueba=Textbox(self.acceso)
        # Botones Acceso directo
        self.imgfac = tk.PhotoImage(file='img/factura-icon.png')
        # self.imgcontratos = tk.PhotoImage(file='img/editArea32.png')
        # self.imgadmin = tk.PhotoImage(file='img/iconoUser.png')
        self.btnfac = tk.Button(self.acceso, image=self.imgfac, command=lambda: self.openForm(facturar,'frmfactura'))
        self.btnfac.pack(side=tk.LEFT, padx=3, pady=3)
        self.statusbar.createTip(self.btnfac, "Registro-Orden nueva factura [ALT-O]")
        # self.btncon = tk.Button(self.acceso, image=self.imgcontratos)#, command=lambda: self.openForm(frmcontr, 'frmcontr'))
        # self.btncon.pack(side=tk.LEFT, padx=3, pady=3)
        # self.statusbar.createTip(self.btncon, "Consulta/Registro de Contratos [ALT-R]")
        # self.btnges = tk.Button(self.acceso, image=self.imgadmin)#, command=lambda: self.openForm(frmgest, 'frmgestor'))
        # self.btnges.pack(side=tk.LEFT, padx=3, pady=3)
        # self.statusbar.createTip(self.btnges, "Consulta de Gestores de Clientes [ALT-G]")

        # Empaquetado
        self.contimage.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.contitulo.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.acceso.pack(side=tk.BOTTOM, fill=tk.X, padx=3, pady=3)
        tk.Frame(self.contitulo, background='black', height=1).pack(side=tk.BOTTOM, fill=tk.X)
        #self.htmltit.pack(side=tk.TOP, fill=tk.BOTH, padx=3, pady=3)
        self.cab.pack(side=tk.TOP, fill=tk.X, padx=3, pady=3)
        self.lineas.pack(side=tk.TOP, fill=tk.X, padx=3, pady=3)
        self.container.pack(fill=tk.BOTH, expand=True)
        #
        tk.Frame(self.contitulo, height=1, bg='black').pack(side=tk.BOTTOM, fill=tk.X)
        #
        self.defineMenu()
        self.defineAceleradoras()
        # self.center()

    def defineMenu(self):
        # Menu ventana
        self.menubar = tk.Menu(self)
        self.mnuArch = tk.Menu(self.menubar, tearoff=False)
        self.mnuFact = tk.Menu(self.menubar, tearoff=False)
        self.mnuGast = tk.Menu(self.menubar, tearoff=False)
        self.mnuUtil = tk.Menu(self.menubar, tearoff=False)
        # Menu Archivo
        self.menubar.add_cascade(label="Archivos", underline=0, menu=self.mnuArch)
        self.mnuArch.add_command(label="Clientes", underline=0, accelerator="Alt-C",command=lambda: self.openForm(frmCliente, 'frmCliente'))
        #,command=lambda: self.openForm(frmcli, 'frmluzcli'))
        self.mnuArch.add_command(label="Acreedores", command=lambda: self.openForm(frmAcreedor, 'frmAcreedor'))
        self.mnuArch.add_separator()
        self.mnuArch.add_command(label="Tipos de GASTO", command=lambda: self.openForm(frmtipgto, 'frmTipogasto'))
        self.mnuArch.add_command(label="Tipos de INGRESO", command=lambda: self.openForm(frmtiping, 'frmTipoingreso'))
        self.mnuArch.add_separator()
        self.mnuArch.add_command(label="Salir", underline=0, command=self.closer, accelerator="Alt-S")

        # Menu Facturacion
        self.menubar.add_cascade(label="Facturación", underline=0, menu=self.mnuFact)
        self.mnuFact.add_command(label="Ordenes de Facturación", underline=0, accelerator="Alt-O", 
                                 command=lambda: self.openForm(facturar,'frmfactura'))
        self.mnuFact.add_command(label="Consulta Facturación", underline=9, accelerator="Alt-F", 
                                 command=self.on_Opcion)
        self.mnuFact.add_command(label="Listado Ingresos - Facturas Expedidas - IVA REPERCUTIDO", 
                                 command=self.on_Opcion)
        self.mnuFact.add_command(label="Listado Retenciones Soportadas - IRPF", 
                                 command=self.on_Opcion)
        self.mnuFact.add_command(label="Informe Resumen Anual por Trimestres IRPF - MOD 130", 
                                 command=self.on_Opcion)
        # Menu Gastos
        self.menubar.add_cascade(label="Gastos", underline=4, menu=self.mnuGast)
        self.mnuGast.add_command(label="Gastos CON IVA", command=self.on_Opcion)
        self.mnuGast.add_command(label="Gastos SIN IVA", command=self.on_Opcion)
        self.mnuGast.add_command(label="Listado Gastos - Facturas Recibidas - IVA SOPORTADO", 
                                 command=self.on_Opcion)
        self.mnuGast.add_command(label="Listado Libro de Gastos - CON y SIN IVA", 
                                 command=self.on_Opcion)
        self.mnuGast.add_command(label="Listado Resumen Anual por Tipo de Gasto", 
                                 command=self.on_Opcion)
        self.mnuGast.add_command(label="Liquidación IVA trimestral - MOD 303", 
                                 command=self.on_Opcion)
        
        self.mnuGast.add_separator()
        self.mnuGast.add_command(label="Ofertas", underline=0, command=self.on_Opcion)
        # Menu Utilidad
        self.menubar.add_cascade(label="Utilidad", underline=0, menu=self.mnuUtil)
        self.mnuUtil.add_command(label="Cierre Trimestral - 130/303", 
                                 command=self.on_Opcion)
        self.mnuUtil.add_command(label="Parametros-Settings", underline=0, accelerator="Alt-P", 
                                 command=lambda: self.openForm(frmparam))
        self.mnuUtil.add_command(label="Editar Texto", underline=0, accelerator="Alt-E",
                                 command=lambda: self.openForm(frmEditor,'Editor'))
        self.mnuUtil.add_command(label="Acerca de ...", command=self.on_Acerca)

        self.config(menu=self.menubar)

    def defineAceleradoras(self):
        # Shortcuts - ventana principal
        # command=lambda: self.openForm('frmadmin', frmadmin)
        self.bind("<Alt-p>", lambda e: self.openForm(frmparam))
        self.bind("<Alt-P>", lambda e: self.openForm(frmparam))
        # self.bind("<Alt-G>", lambda e: self.openForm(frmgest,'frmgestor'))
        # self.bind("<Alt-g>", lambda e: self.openForm(frmgest,'frmgestor'))
        # self.bind("<Alt-c>", lambda e: self.openForm(frmcli, "frmcli"))
        # self.bind("<Alt-C>", lambda e: self.openForm(frmcli, "frmcli"))
        # self.bind("<Alt-d>", lambda e: self.openForm(frmpro,"frmpro"))
        # self.bind("<Alt-D>", lambda e: self.openForm(frmpro, "frmpro"))
        # self.bind("<Alt-r>", lambda e: self.openForm(frmped, 'frmped'))
        # self.bind("<Alt-R>", lambda e: self.openForm(frmped, 'frmped'))
        self.bind("<Alt-O>", lambda e: self.openForm(facturar,'frmfactura'))
        self.bind("<Alt-o>", lambda e: self.openForm(facturar,'frmfactura'))

    def on_Opcion(self, event=""):
        messagebox.showinfo("MENU", "Seleccionada Opción de Menu",parent=self)

    def on_Acerca(self, event=""):
        strmsg="\tF A C"
        strmsg+="\n- Ordenes de facturación"
        strmsg+="\n- Control de ingresos - IRPF"
        strmsg+="\n- Control de Gastos - IVA"
        strmsg+="\n- Liquidación trimestral - anual"
        strmsg+="\n\nPARA LA DECLARACIÓN DE \nMOD. 130(IRPF) y 303(IVA)"
        
        # messagebox.showinfo("APLICACION FAC", strmsg, parent=self)
        aviso = dialogo(self, 'ACERCA DE FAC', strmsg, ['Aceptar'], Dialogo.INFO)
        aviso.showmodal()
        # messagebox.showinfo("MENU", "Seleccionada Opción de Menu", parent=self)
        self.show()
        
    
    def closer(self, *args):
        # Como estamos en punto de entrada a la aplicación oil
        # cerramos bases de datos que podrían estar abiertas
        db.close("FAC")
        # self.hcaller.show()
        # Llamamos al método que sobrecargamos en esta instancia de Form
        super().closer()

    def on_seleccion(self, evt=None):
        strmsg="SELECIONADO - ORDEN DE FACTURACION"
        dialogo(self, 'APLICACION FAC', strmsg, ['ACEPTAR'], Dialogo.INFO).showmodal()