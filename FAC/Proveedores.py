import tkinter as tk
from tkinter import messagebox

from Propiedades import *
from Controls import *
from Forms import *
from DBsql import *
import Dialogo as dlg

class frmAcreedor(FormData):
    """
        Formulario Acreedores (Proveedores)

    """
    
    def __init__(self, hcaller, name):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
        """
        self.prop=cmvar.properties
        
        # Conexión a datos
        self.cnn="FAC"
        strsql = "SELECT * FROM proveedores"
        
        super().__init__(hcaller, name, strsql, self.cnn, 'emppro')
        self.title("PROVEEDORES/ACREEDORES DE GASTOS")
        #
        # Aquí diseñamos los widgets que se verán en forma de ficha
        self.declaraControls()
        #
        # Icono que aparece en ventana minimizada (Barra de tareas)
        self.setIcon('img/user32.gif')

        # Ponernos a la escucha de eventos generados por Buttons de Buttonbar
        # Cada vez que el cursor del result cambie
        self.bind('<<cursordata>>', self.showdata)
        # Cuando se editen - añadan - eliminen datos
        self.bind('<<editdata>>', self.on_btnedit)
        self.bind('<<newdata>>', self.on_btnnew)
        self.bind('<<deldata>>', self.on_btndel)
        #
        # Es la primera entrada/exposición de datos
        if self.current.get() >= 0:
            self.showdata()
        # Capturar evento buscar (F5)
        self.bind('<<seledata>>', self.seledata)
        self.center()
        
    # Metodos
    def declaraControls(self):
        # Area de contenido
        self.contenido=tk.Frame(self, pady=10, highlightbackground="black", highlightthickness=1)
        tk.Label(self.contenido, text="ID:").grid(row=0, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="Razón Social:").grid(row=1, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="NIF:").grid(row=2, column=0, sticky=tk.E)
        
        self.idpro=Numbox(self.contenido, width=5)
        self.idpro.grid(row=0, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.emppro=Textbox(self.contenido, width=40, tipo=Textbox.MAYUSCULAS)
        self.emppro.grid(row=1, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.nifpro=Textbox(self.contenido, width=9, tipo=Textbox.TITLE)
        self.nifpro.grid(row=2, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        
        # self.imgGest = tk.PhotoImage(file='img/list32.png')
        # self.btngestionados=tk.Button(self.contenido, image=self.imgGest,text='Gestionados', compound=tk.LEFT, command=self.ver_gestionados)
        # self.btngestionados.grid(row=0, column=4, ipadx=3, ipady=3, padx=3, pady=3)
        # self.statusbar.createTip(self.btngestionados, "Ver Clientes gestionados [F6]")
        # self.bind('<F6>', self.ver_gestionados)

        self.contenido.columnconfigure(1, weight=1)

        self.contenido.pack(fill=tk.BOTH, expand=True)

    def clearFields(self):
        #  Limpiar value de los entry
        try:
            for w in self.contenido.winfo_children():
                if w.winfo_class() == 'Entry':
                    w['state']='normal'
                    w.delete(0, 'end')
                    w['state']='readonly'
        except:
            messagebox.showinfo("ERROR clearFields", "Se ha producido un error")


    def showdata(self, *args):
        
        self.clearFields()
        reg = self.current.get()
        # Hacemos editables los textbox/entry
        for w in self.contenido.winfo_children():
            if w.winfo_class() == 'Entry':
                w['state']='normal'
            
        self.showfield(self.emppro, reg, 'emppro')
        self.showfield(self.idpro, reg, 'id')
        self.showfield(self.nifpro, reg, 'nifpro')
        
        # Revertimos edición y ponemos readonly textbox
        for w in self.contenido.winfo_children():
            if w.winfo_class() == 'Entry':
                w['state']='readonly'

        # Mostramos la posicion en el statusbar
        pos = 'Registro: ' + str(self.current.get()+1) + ' de ' + str(len(self.rst))
        self.statusbar.showMensaje(pos, True)
        # No usamos el metodo showPosicion porque entramos en bucle
        # al generar un evento que llama de nuevo a showData y produce
        # un error de: Abortado('core' generado)
        # Actualizar combobox finder 
        # if self.fieldfind != '':
        #     self.cmbfind.set(self.rst[self.fieldfind][self.current.get()])

        self.updateBar()
        
    def showfield(self, widget, reg, campo):
        # Si el campo no está en blanco mostramos datos
        if self.rst[reg][campo] != None:
            widget.insert(0, self.rst[reg][campo])

    # Respuesta a Eventos escuchados
        
    def on_btnnew(self, *args):
        # Nuevo administrador
        frmeditpro = frmproedit(self)
        self.withdraw()
        self.wait_window(frmeditpro)
        self.show()
        self.loadData()
        self.current.set(len(self.rst)-1)
        self.showdata()

    def on_btnedit(self, *args):
        indice = self.current.get()
        registro=self.rst[indice]
        
        frmeditpro = frmproedit(self, '', registro=registro)
        self.withdraw()
        self.wait_window(frmeditpro)
        self.show()
        self.loadData()
        self.current.set(indice)
        self.showdata()
        self.cmbfind.set(self.emppro.get())
        
    def on_btndel(self, *args):
        indice = self.current.get()
        idPro = self.rst[self.current.get()]['id']
        consulta = 'SELECT COUNT(*) AS registros FROM gastos WHERE progto = {}'.format(str(idPro))
        rstexist = db.consultar(consulta, con=self.cnn)
        if int(rstexist[0]['registros']) > 0:
            #rstclis=db.consultar('SELECT * FROM clientes WHERE admcli =?',(idAdmin,),con=self.cnn)
            strmsg="Este acreedor/Proveedor tiene "+str(rstexist[0]['registros'])+" de gastos registrados\nIMPOSIBLE ELIMINAR"
            dlg.dialogo(self,"ELIMINAR REGISTRO "+str(idPro),strmsg,img=dlg.ERROR)
            return
        else:
            ok=dlg.dialogo(self,"ELIMINAR REGISTRO "+str(idPro),"¿Está ud. seguro?",['Aceptar','Cancelar'],img=dlg.PREGUNTA).showmodal()
            if ok == 0:
                strsql = "DELETE FROM proveedores WHERE id = {}"
                strsql = strsql.format(idPro)
                db.actualiza(strsql, con=self.cnn)
                # messagebox.showinfo("ELIMINADO", "Registro borrado", parent=self)
            else:
                return

        # Volvemos a cargar el DataFrame
        self.loadData()
        # Si la posición anterior era la última ahora
        # será mayor que el tamaño de la Lista, por tanto
        # hacemos que sea el último registro
        if indice >= len(self.rst)-1:
            self.current.set(len(self.rst)-1)
        
        self.showdata()
        self.cmbfind.set(self.emppro.get())
        return

    def seledata(self, *args):

        frmsele = SeleData(self,
                           self.rst,
                           [ {'titulo':'Proveedores',
                              'campo': 'emppro',
                              'ancho': 300,
                              'alineacion': tk.W},
                              {'titulo':'NIF',
                              'campo': 'nifpro',
                              'ancho': 100,
                              'alineacion': tk.W}], self.current, 0)
        
        frmsele.bind('<<gotodata>>', self.on_selected)
        
        # Esperamos a que devuelva el control
        #self.wait_window(frmsele)
        # Y volvemos a mostrar
        #self.show()

    def on_selected(self, *args):
        # self.center()
        self.showPosicion()

    # def ver_gestionados(self, *args):
    #     # Ver clientes gestionados por este administrador/gestor de clientes
    #     # Id del del administrador
    #     idAdmin = self.rst[self.current.get()]['id']
    #     strsqladm = 'SELECT * FROM clientes WHERE admcli={}'.format(idAdmin)
    #     self.rstcli = db.consultar(strsqladm, con=self.con)
        
        # if len(self.rstcli) == 0:
        #     messagebox.showinfo(parent=self, 
        #                         message="Ningún registro está relacionado con este gestor", 
        #                         title="CLIENTES GESTIONADOS")
        # else:
        #     # Declaro puntero intvar usado por seledata
        #     posicioncli = tk.IntVar()
        #     posicioncli.set(0)
        #     # Cargar formulario para selección de registro
        #     # con busqueda por contenido en.
        #     frmsele = SeleData(self,
        #                 self.rstcli,
        #                 [ {'titulo':'Cliente',
        #                     'campo': 'empcli',
        #                     'ancho': 300,
        #                     'alineacion': tk.W},
        #                     {'titulo':'Contacto',
        #                     'campo': 'concli',
        #                     'ancho': 300,
        #                     'alineacion': tk.W},
        #                     {'titulo':'Dirección',
        #                     'campo': 'dircli',
        #                     'ancho': 300,
        #                     'alineacion': tk.W},
        #                     {'titulo':'D.P.',
        #                     'campo': 'discli',
        #                     'ancho': 60,
        #                     'alineacion': tk.E},
        #                     {'titulo':'Población',
        #                     'campo': 'pobcli',
        #                     'ancho': 200,
        #                     'alineacion': tk.W},
        #                     {'titulo':'Telefono',
        #                     'campo': 'tlfcli',
        #                     'ancho': 90,
        #                     'alineacion': tk.E},
        #                     {'titulo':'Movil',
        #                     'campo': 'movcli',
        #                     'ancho': 90,
        #                     'alineacion': tk.E}], posicioncli, 0)
                            
        # return
    

class frmproedit(FormEdit):
    """
        Formulario Edición Administradores

    """
    
    def __init__(self, hcaller, name="", registro={}):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
            El registro es un diccionario con los datos a modificar.
            Si esta vacío es nuevo.
        """
        # La conexión que viene de oil no la pasamos como parámetro
        # por lo menos ahora. La inicializamos para que la tenga en cuenta
        self.cnn = hcaller.cnn
        self.registro=registro
        #
        if len(registro) == 0:
            self.modo = 'INSERT'
            self.idrec = 0
        else:
            self.modo = 'UPDATE'
            self.idrec = registro['id']
        
        super().__init__(hcaller, name)
        #
        # Aquí diseñamos los widgets que se verán en forma de ficha
        #
        self.declaraControls()
        #
        # Icono que aparece en ventana minimizada (Barra de tareas)
        self.setIcon('img/user32.gif')
        # Ponernos a la escucha de eventos generados por Buttons de Buttonbar
        # Cuando queramos grabar el registro
        self.bind('<<savedata>>', self.onsave)

        self.showdata()
        self.emppro.focus_force()


    # Metodos

    def declaraControls(self):
        tk.Label(self.buttonbar, text="ID: ").pack(side=tk.LEFT, padx=20)
        self.idpro=tk.Label(self.buttonbar, bg='white',borderwidth=1,
                           relief="solid", width=5,anchor=tk.E)
        self.idpro.pack(side=tk.LEFT, ipadx=3, ipady=3, padx=3, pady=3)

        # Area de contenido
        self.contenido=tk.Frame(self, pady=10, highlightbackground="black", highlightthickness=1)

        tk.Label(self.contenido, text="Razón Social:").grid(row=1, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="NIF:").grid(row=2, column=0, sticky=tk.E)
        
        self.emppro=Textbox(self.contenido, width=40, tipo=Textbox.MAYUSCULAS)
        self.emppro.grid(row=1, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.nifpro=Textbox(self.contenido, width=9, tipo=Textbox.TITLE)
        self.nifpro.grid(row=2, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        
        self.contenido.columnconfigure(1, weight=1)
        
        self.contenido.pack(fill=tk.BOTH, expand=True)
        
    def showdata(self, *args):
        # Hacemos editables los textbox/entry (Por si acaso)
        for w in self.contenido.winfo_children():
            if w.winfo_class() == 'Entry':
                w['state']='normal'
        
        if self.idrec == 0:
            self.idpro['text']='0'
            self.title('NUEVO PROVEEDOR ACREEDOR')
            pos = 'Introduzca datos nuevo registro'
        else:
            # self.showfield(self.idadm, 'id')
            # Clave PK no modificable (auto-increment)
            self.idpro['text']=str(self.idrec)
            campos=['emppro','nifpro']
            controles=[self.emppro,self.nifpro]
            for i in range(len(campos)):
                if self.registro[campos[i]] != '':
                    controles[i].insert(0, self.registro[campos[i]])
                else:
                    print("Se ha dado un valor nulo no imprimible en " + campos[i])
                    
            pos = 'Actualize datos del Proveedor Acreedor'
            self.title('EDICION DATOS DE PROVEEDOR ACREEDOR')
            
        # Mostramos la posicion en el statusbar
        self.statusbar.showMensaje(pos, True)
        # Enfocamos en campo primero a modificar
        self.emppro.focus_set()
       
    def onsave(self, *args):
        # Componemos la instrucción SQL
        if self.modo == 'INSERT':
            strsql = "INSERT INTO proveedores "
            strsql  += "(emppro,nifpro) " 
            strsql +=" VALUES ('{}','{}')"
            strsql = strsql.format(self.emppro.get(),self.nifpro.get())
        else:
            strsql = "UPDATE proveedores SET emppro='{}',nifpro='{}' WHERE id = {}"
            strsql = strsql.format(self.emppro.get(),self.nifpro.get(), self.idpro['text'])
        
        # Ejecutamos
        db.actualiza(strsql, con=self.cnn)
        self.closer()

