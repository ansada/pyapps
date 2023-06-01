import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

from Propiedades import *
from Controls import *
from Forms import *
from DBsql import *
import Dialogo as dlg

class clientes(FormData):
    """
        Formulario Clientes

    """
    
    def __init__(self, hcaller, name):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
        """
        self.prop=cmvar.properties
        
        # Conexión a datos
        self.cnn="GYL"
        strsql = "SELECT * FROM clientes"
        
        super().__init__(hcaller, name, strsql, self.cnn, 'nomcli')
        self.title("CLIENTES")
        #
        # Icono que aparece en ventana minimizada (Barra de tareas)
        self.setIcon('img/user32.gif')
        #
        # Aquí diseñamos los widgets que se verán en forma de ficha
        self.contenido=Framecli(self)
        self.imgvercon = tk.PhotoImage(file='img/list32.png')
        self.btnvercon=tk.Button(self.contenido, image=self.imgvercon)#,command=self.verPedidos)
        self.btnvercon.grid(row=0, column=5, ipadx=3, ipady=3, padx=3, pady=3)
        self.hcaller.statusbar.createTip(self.btnvercon, "Ver contratos asociados a este cliente [F9]")
        #
        # Ponernos a la escucha de eventos generados por Buttons de Buttonbar
        # Cada vez que el cursor del result cambie
        self.bind('<<cursordata>>', self.showdata)
        # Cuando se editen - añadan - eliminen datos
        self.bind('<<editdata>>', self.on_btnedit)
        self.bind('<<newdata>>', self.on_btnnew)
        self.bind('<<deldata>>', self.on_btndel)
        # self.bind('<F6>', self.ver_gestionados)
        #
        # Es la primera entrada/exposición de datos
        if self.current.get() >= 0:
            self.showdata()
        # Capturar evento buscar (F5)
        self.bind('<<seledata>>', self.seledata)
        #hcaller.hide()
        #self.geometry('950x450+540+160')
        #self.update()
        self.center()
        
    # Metodos
    def showdata(self, *args):
        
        self.contenido.dataShow(self.rst[self.current.get()])
        # Actualizo combobox de busqueda
        self.cmbfind.set(self.contenido.nomcli.get())
        # Mostramos la posicion en el statusbar
        pos = 'Registro: ' + str(self.current.get()+1) + ' de ' + str(len(self.rst))
        self.statusbar.showMensaje(pos, True)
        # Actualizar estado de barra de botones
        self.updateBar()
        
    # # Respuesta a Eventos escuchados

    def on_btnnew(self, *args):
        # Nuevo gestor de clientes
        frmeditges = frmcliedit(self)
        self.withdraw()
        self.wait_window(frmeditges)
        self.show()
        self.loadData()
        self.current.set(len(self.rst)-1)
        self.showdata()
        # Levantamos la ventana a primer level
        # por alguna razón nos la deja en minimizado
        self.lift()
        

    def on_btnedit(self, *args):
        indice = self.current.get()
        registro=self.rst[indice]
        
        frmedit = frmcliedit(self, '', registro=registro)
        self.withdraw()
        self.wait_window(frmedit)
        self.show()
        self.loadData()
        self.current.set(indice)
        self.showdata()
        # Levantamos la ventana a primer level
        # por alguna razón nos la deja en minimizado
        self.lift()
        #self.cmbfind.set(self.contenido.nomges.get())
        
    def on_btndel(self, *args):
        indice = self.current.get()
        idcli = self.rst[self.current.get()]['id']
        consulta = 'SELECT COUNT(*) AS registros FROM contratos WHERE clicon = {}'.format(str(idcli))
        rstexist = db.consultar(consulta, con=self.con)
        if int(rstexist[0]['registros']) > 0:
            # Hay algún registro referenciado (cliente asignado a este gestor)
            dlg.dialogo(self,'ELIMINAR REGISTRO '+str(idcli),
                        "Este cliente es titular de "+str(rstexist[0]['registros'])+" contrato/s\nIMPOSIBLE ELIMINAR",
                        img=dlg.ERROR)
            return
        else:
            ok=dlg.dialogo(self,'ELIMINAR REGISTRO '+str(idcli),
                           '¿Está ud. seguro de eliminar el registro\nEsta operación no se puede deshacer.',
                           ['Continuar','Cancelar'], dlg.ADVERTENCIA) 
            if ok == 1:
                strsql = f"DELETE FROM clientes WHERE id = {idcli}"
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
        self.cmbfind.set(self.contenido.nomcli.get())
        return

    def seledata(self, *args):

        frmsele = SeleData(self,
                           self.rst,
                           [ {'titulo':'Cliente',
                              'campo': 'nomcli',
                              'ancho': 300,
                              'alineacion': tk.W},
                              {'titulo':'Contacto',
                              'campo': 'concli',
                              'ancho': 300,
                              'alineacion': tk.W},
                              {'titulo':'Direccion',
                              'campo': 'dircli',
                              'ancho': 300,
                              'alineacion': tk.W},
                              {'titulo':'Población',
                              'campo': 'pobcli',
                              'ancho': 200,
                              'alineacion': tk.W},
                              {'titulo':'Distrito',
                              'campo': 'discli',
                              'ancho': 70,
                              'alineacion': tk.W},
                              {'titulo':'Telef 1',
                              'campo': 'tf1cli',
                              'ancho': 100,
                              'alineacion': tk.E},
                              {'titulo':'Telef 2',
                              'campo': 'tf2cli',
                              'ancho': 100,
                              'alineacion': tk.E}], self.current, 0)
        
        frmsele.bind('<<gotodata>>', self.on_selected)
        
        # Esperamos a que devuelva el control
        self.wait_window(frmsele)
        # Y volvemos a mostrar
        self.show()


    # Eventos
    def on_selected(self, *args):
        # self.center()
        self.showPosicion()

    # def ver_gestionados(self, *args):
    #     # Ver clientes gestionados por este administrador/gestor de clientes
    #     # Id del del administrador
    #     idges = self.rst[self.current.get()]['id']
    #     strsqladm = 'SELECT * FROM clientes WHERE gescli={}'.format(idges)
    #     self.rstcli = db.consultar(strsqladm, con=self.con)
        
    #     if len(self.rstcli) == 0:
    #         messagebox.showinfo(parent=self, 
    #                             message="Ningún cliente está gestionado por este gestor", 
    #                             title="CLIENTES GESTIONADOS")
    #     else:
    #         # Declaro puntero intvar usado por seledata
    #         posicioncli = tk.IntVar()
    #         posicioncli.set(0)
    #         # Cargar formulario para selección de registro
    #         # con busqueda por contenido en.
    #         frmsele = SeleData(self,
    #                     self.rstcli,
    #                     [ {'titulo':'Cliente',
    #                         'campo': 'nomcli',
    #                         'ancho': 300,
    #                         'alineacion': tk.W},
    #                         {'titulo':'Contacto',
    #                         'campo': 'concli',
    #                         'ancho': 300,
    #                         'alineacion': tk.W},
    #                         {'titulo':'Dirección',
    #                         'campo': 'dircli',
    #                         'ancho': 300,
    #                         'alineacion': tk.W},
    #                         {'titulo':'D.P.',
    #                         'campo': 'discli',
    #                         'ancho': 60,
    #                         'alineacion': tk.E},
    #                         {'titulo':'Población',
    #                         'campo': 'pobcli',
    #                         'ancho': 200,
    #                         'alineacion': tk.W},
    #                         {'titulo':'Telefono1',
    #                         'campo': 'tf1cli',
    #                         'ancho': 100,
    #                         'alineacion': tk.E},
    #                         {'titulo':'Telefono2',
    #                         'campo': 'tf2cli',
    #                         'ancho': 100,
    #                         'alineacion': tk.E}], posicioncli, 0)
                            
    #     return
    
class Framecli(tk.Frame):
    '''
        Ficha de componentes/controles de visualización de Clientes
    '''    
    def __init__(self, hcaller):
        # Formulario contenedor
        self.hcaller = hcaller
        # Creamos Frame con marco de 1 px en negro y un margen sup. e inf. de 10
        super().__init__(hcaller, pady=10, highlightbackground="black", highlightthickness=1)
        # Cargamos datos auxiliares de gestores de clientes
        self.rstaux = db.consultar("SELECT * FROM gestores ORDER BY nomges", con=self.hcaller.cnn)
        self.gestores = [x['nomges'] for x in self.rstaux]
        # Area de contenido
        # Mostramos datos titular de las aplicaciones (NO MODIFICABLE EN este formulario)
        tk.Label(self, text="DNI/NIF:").grid(row=0, column=3, sticky=tk.E)
        tk.Label(self, text="ID:").grid(row=0, column=5, sticky=tk.E)
        tk.Label(self, text="Nombre:").grid(row=0, column=0, sticky=tk.E)
        tk.Label(self, text="Contacto:").grid(row=1, column=0, sticky=tk.E)
        tk.Label(self, text="Dirección:").grid(row=2, column=0, sticky=tk.E)
        tk.Label(self, text="Distrito:").grid(row=2, column=3, sticky=tk.E)
        tk.Label(self, text="Población:").grid(row=3, column=0, sticky=tk.E)
        tk.Label(self, text="Provincia:").grid(row=3, column=3, sticky=tk.E)
        tk.Label(self, text="Teléfonos:").grid(row=4, column=0, sticky=tk.E)
        tk.Label(self, text="Mail:").grid(row=4, column=3, sticky=tk.E)
        tk.Label(self, text="Gestor Asignado:").grid(row=5, column=0, sticky=tk.E)
        # tk.Label(self, text="Forma de Pago:").grid(row=6, column=0, sticky=tk.E)
        tk.Label(self, text="Observaciones").grid(row=7, column=0, sticky=tk.E)

        self.nomcli=Textbox(self, width=40, tipo=Textbox.MAYUSCULAS)
        self.nomcli.grid(row=0, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.nifcli=Textbox(self, width=9, tipo=Textbox.MAYUSCULAS)
        self.nifcli.grid(row=0, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        # self.imgvercon = tk.PhotoImage(file='img/list32.png')
        # self.btnverped=tk.Button(self, image=self.imgvercon)#,command=self.verPedidos)
        # self.btnverped.grid(row=0, column=5, ipadx=3, ipady=3, padx=3, pady=3)
        # self.hcaller.statusbar.createTip(self.btnverped, "Ver contratos asociados a este cliente [F9]")
        self.idcli=Numbox(self, width=5, takefocus=0)
        self.idcli.grid(row=0, column=6, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.concli=Textbox(self, width=40, tipo=Textbox.TITLE)
        self.concli.grid(row=1, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.dircli=Textbox(self, width=40)
        self.dircli.grid(row=2, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.discli=Numbox(self, width=5)
        self.discli.grid(row=2, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.pobcli=Textbox(self, width=30, tipo=Textbox.CAPITAL)
        self.pobcli.grid(row=3, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.prvcli=Textbox(self, width=20, tipo=Textbox.MAYUSCULAS)
        self.prvcli.grid(row=3, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.tf1cli = Numbox(self, width=9)
        self.tf1cli.grid(row=4, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.tf2cli = Numbox(self, width=9)
        self.tf2cli.grid(row=4, column=2, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.maicli = Textbox(self,  width=40, tipo=Textbox.MINUSCULAS)
        self.maicli.grid(row=4, column=4, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.imgmail = tk.PhotoImage(file='img/emailBW32.png')
        self.cmbges = ttk.Combobox(self, state='readonly', values=self.gestores)
        self.cmbges.grid(row=5, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.conges = Textbox(self, width=40, takefocus=0)
        self.conges.grid(row=5, column=4, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.tf1ges = Numbox(self, width=9, takefocus=0)
        self.tf1ges.grid(row=6, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.tf2ges = Numbox(self, width=9, takefocus=0)
        self.tf2ges.grid(row=6, column=5, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        # self.fpacli=Textbox(self, width=50, tipo=Textbox.MAYUSCULAS)
        # self.fpacli.grid(row=6, column=1, columnspan=3, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.obscli = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=5)
        self.obscli.grid(row=8,column=0, columnspan=self.grid_size()[0], 
                         sticky=tk.NSEW, ipadx=3, ipady=3, padx=3, pady=3)

        self.rowconfigure(8, weight=1)
        self.columnconfigure(2, weight=1)

        self.pack(fill=tk.BOTH, expand=True)
        
        # Esto lo hago para que al pulsar TAB desde maiges entre en el obsges
        # directamente, sino hay que pulsar dos veces TAB
        self.pulsadaTab=False
        self.maicli.bind('<Tab>', lambda event: self.pulsaTab(event))
        self.maicli.bind('<FocusOut>', lambda event:  self.porfoco(event))

    def pulsaTab(self, evt):
        # Flag para avanzar desde maiges a obsges
        self.pulsadaTab = True
        print("Pulsada Tab en maiges")

    def porfoco(self, evt):
        # Si se ha perdido el foco desde maiges pulsando Tab
        if self.pulsadaTab==True:
            # Enfocamos a obsges (Sino hay que pulsar 2 veces)
            self.obscli.focus()
            # Retiramos flag para próximavez
            self.pulsadaTab=False


    # Metodos del Frame
    def clear(self):
        #  Limpiar value de los entry
        try:
            for w in self.winfo_children():
                if w.winfo_class() == 'Entry':
                    w['state']='normal'
                    w.delete(0, 'end') # type: ignore
                    w['state']='readonly'

            self.obscli['state']='normal'
            self.obscli.delete(1.0, 'end')
            self.obscli['state']='disabled'
        except:
            messagebox.showinfo("ERROR clearFields", "Se ha producido un error")

    def dataShow(self, dicdata):
        # Diccionario de datos con los campos a mostrar y valores
        self.clear()
        # Hacemos editables los textbox/entry
        for w in self.winfo_children():
            if w.winfo_class() == 'Entry':
                w['state']='normal'
        
        self.idcli.set_value(dicdata['id'])
        self.nomcli.set_texto(dicdata['nomcli'])
        self.nifcli.set_texto(dicdata['nifcli'])
        self.concli.set_texto(dicdata['concli'])
        self.dircli.set_texto(dicdata['dircli'])
        self.discli.set_texto(dicdata['discli'])
        self.pobcli.set_texto(dicdata['pobcli'])
        self.prvcli.set_texto(dicdata['prvcli'])
        self.tf1cli.set_texto(dicdata['tf1cli'])
        self.tf2cli.set_texto(dicdata['tf2cli'])
        self.maicli.set_texto(dicdata['maicli'])
        # Datos gestor del cliente
        for i in self.rstaux:
            if i['id']==dicdata['gescli']:
                self.cmbges.set(i['nomges'])
                self.tf1ges.set_texto(i['tf1ges'])
                self.tf2ges.set_texto(i['tf2ges'])
                self.conges.set_texto(i['conges'])
                break

        # Revertimos edición y ponemos readonly textbox
        for w in self.winfo_children():
            if w.winfo_class() == 'Entry':
                w['state']='readonly'

        # Cuadro de observaciones
        self.obscli['state']='normal'
        self.obscli.delete('1.0', tk.END)
        if dicdata['obscli']!= None:
            self.obscli.insert('1.0', dicdata['obscli'])

        self.obscli['state']='disabled'

    def setEditable(self, estado=True):
        # Hacemos editables los textbox/entry (Por si acaso)
        for w in self.winfo_children():
            if w.winfo_class() in ['Entry','Text']:
                w['state']='normal'

        self.obscli['state']= 'normal'
        self.idcli['state'] = 'readonly'
            

class frmcliedit(FormEdit):
    """
        Formulario Edición de clientes

    """
    
    def __init__(self, hcaller, name='', registro={}):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
            El registro es un diccionario con los datos a modificar.
            Si esta vacío es nuevo.
        """
        # La conexión creada en gasyluz
        # Entendemos que se ha establecido
        self.cnn= hcaller.cnn
        self.registro=registro
        # Result auxiliar de gestores de clientes
        self.rstges = db.consultar("SELECT * FROM gestores", con=self.cnn)
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
        self.contenido=Framecli(self)
        #
        # Icono que aparece en ventana minimizada (Barra de tareas)
        self.setIcon('img/user32.gif')
        
        # Ponernos a la escucha de eventos generados por Buttons de Buttonbar
        # Cuando queramos grabar el registro
        self.bind('<<savedata>>', self.onsave)

        self.showdata()
        self.contenido.nomcli.focus_force()
        self.geometry('950x450+540+160')
        self.update()

    def showdata(self, *args):
        # El boton lo declaramos fuera (tras la llamada a framegest)
        # self.contenido.btnverped.grid_forget()
        if self.idrec == 0:
            self.contenido.idcli.set_value(0)
            self.title('ALTA DE NUEVO CLIENTE')
            pos = 'Introduzca datos del nuevo Cliente'
        else:
            self.contenido.dataShow(self.registro)
            pos = 'Actualize datos del Cliente'
            self.title('EDICION DATOS DEL CLIENTE')
            
        # Mostramos la posicion en el statusbar
        self.statusbar.showMensaje(pos, True)
        # Hacemos editables los textbox/entry (Por si acaso)
        self.contenido.setEditable()
        # Enfocamos en campo primero a modificar
        self.contenido.nomcli.focus_set()

    def getidGestor(self):
        idGestor = -1
        # empadm seleccionado en el combobox
        gestorSel=self.contenido.cmbges.get()
        if gestorSel != "":
            # Obtenemos el indice en el result
            indice = db.getIndice(self.rstges, 'nomges', gestorSel)
            # Devolveremos el id del administrador
            idGestor = self.rstges[indice]['id']
        else:
            idGestor=1

        return idGestor

    def onsave(self, *args):
        # Componemos la instrucción SQL
        idGestor=self.getidGestor()
        if self.modo == 'INSERT':
            strsql = "INSERT INTO clientes "
            strsql  += "(nomcli,concli,tf1cli,tf2cli,maicli,obscli,nifcli,dircli,discli,pobcli,prvcli,gescli) " 
            strsql +=" VALUES ('{}'" +  ",'{}'"*10 + ",{})"
            strsql = strsql.format(self.contenido.nomcli.get(),self.contenido.concli.get(),
                                   self.contenido.tf1cli.get(),self.contenido.tf2cli.get(),
                                   self.contenido.maicli.get(),self.contenido.obscli.get("1.0", tk.END),
                                   self.contenido.nifcli.get(),self.contenido.dircli.get(),
                                   self.contenido.discli.get(),self.contenido.pobcli.get(),
                                   self.contenido.prvcli.get(),str(idGestor))
        else:
            strsql = "UPDATE clientes SET nomcli='{}',concli='{}',tf1cli='{}',tf2cli='{}',"
            strsql += "maicli='{}',obscli='{}',nifcli='{}',dircli='{}',discli='{}',pobcli='{}',prvcli='{}',"
            strsql += "gescli={} WHERE id = {}"
            strsql = strsql.format(self.contenido.nomcli.get(),self.contenido.concli.get(),
                                   self.contenido.tf1cli.get(),self.contenido.tf2cli.get(),
                                   self.contenido.maicli.get(),self.contenido.obscli.get("1.0", tk.END),
                                   self.contenido.nifcli.get(),self.contenido.dircli.get(),
                                   self.contenido.discli.get(),self.contenido.pobcli.get(),
                                   self.contenido.prvcli.get(),str(idGestor), str(self.idrec))
        
        # Ejecutamos
        db.actualiza(strsql, con=self.cnn)
        self.contenido.nomcli.focus_force()
        self.closer()