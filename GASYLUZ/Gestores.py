import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

from Propiedades import *
from Controls import *
from Forms import *
from DBsql import *

class gestores(FormData):
    """
        Formulario Gestores de clientes

    """
    
    def __init__(self, hcaller, name):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
        """
        self.prop=cmvar.properties
        
        # Conexión a datos ya realizada en gasyluz
        self.cnn="GYL"
        strsql = "SELECT * FROM gestores"
        
        super().__init__(hcaller, name, strsql, self.cnn, 'nomges')
        self.title("GESTORES DE CLIENTES")
        #
        # Icono que aparece en ventana minimizada (Barra de tareas)
        self.setIcon('img/user32.gif')
        #
        # Aquí diseñamos los widgets que se verán en forma de ficha
        self.contenido=Framegest(self)
        # Añadimos boton ver gestionados
        self.imgGest = tk.PhotoImage(file='img/list32.png')
        self.btngestionados=tk.Button(self.contenido,image=self.imgGest,text='Clientes',compound=tk.LEFT,command=self.ver_gestionados)
        self.btngestionados.grid(row=1, column=4, ipadx=3, ipady=3, padx=3, pady=3)
        self.statusbar.createTip(self.btngestionados, "Ver Clientes gestionados [F6]")
        #
        # Ponernos a la escucha de eventos generados por Buttons de Buttonbar
        # Cada vez que el cursor del result cambie
        self.bind('<<cursordata>>', self.showdata)
        # Cuando se editen - añadan - eliminen datos
        self.bind('<<editdata>>', self.on_btnedit)
        self.bind('<<newdata>>', self.on_btnnew)
        self.bind('<<deldata>>', self.on_btndel)
        self.bind('<F6>', self.ver_gestionados)
        #
        # Es la primera entrada/exposición de datos
        if self.current.get() >= 0:
            self.showdata()
        # Capturar evento buscar (F5)
        self.bind('<<seledata>>', self.seledata)
        #hcaller.hide()
        self.geometry('950x450+540+160')
        self.update()
        #self.center()
        
    # Metodos
    def showdata(self, *args):
        
        self.contenido.dataShow(self.rst[self.current.get()])
        # Actualizo combobox de busqueda
        self.cmbfind.set(self.contenido.nomges.get())
        # Mostramos la posicion en el statusbar
        pos = 'Registro: ' + str(self.current.get()+1) + ' de ' + str(len(self.rst))
        self.statusbar.showMensaje(pos, True)
        # Actualizar estado de barra de botones
        self.updateBar()
        
    # # Respuesta a Eventos escuchados
        
    def on_btnnew(self, *args):
        # Nuevo gestor de clientes
        frmeditges = frmgesedit(self)
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
        
        frmedit = frmgesedit(self, '', registro=registro)
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
        idges = self.rst[self.current.get()]['id']
        consulta = 'SELECT COUNT(*) AS registros FROM clientes WHERE gescli = {}'.format(str(idges))
        rstexist = db.consultar(consulta, con=self.con)
        if int(rstexist[0]['registros']) > 0:
            # Hay algún registro referenciado (cliente asignado a este gestor)
            messagebox.showinfo(
                "ELIMINAR REGISTRO "+str(idges), 
                "Este gestor tiene "+str(rstexist[0]['registros'])+" de cliente asignados\nIMPOSIBLE ELIMINAR",
                parent=self)
            return
        else:
            ok = messagebox.askokcancel(message="¿Está ud. seguro?", title="ELIMINAR", parent=self)
            if ok == True:
                strsql = "DELETE FROM gestores WHERE id = {}"
                strsql = strsql.format(idges)
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
        self.cmbfind.set(self.contenido.nomges.get())
        return

    def seledata(self, *args):

        frmsele = SeleData(self,
                           self.rst,
                           [ {'titulo':'Gestor',
                              'campo': 'nomges',
                              'ancho': 300,
                              'alineacion': tk.W},
                              {'titulo':'Contacto',
                              'campo': 'conges',
                              'ancho': 300,
                              'alineacion': tk.W},
                              {'titulo':'Telef 1',
                              'campo': 'tf1ges',
                              'ancho': 100,
                              'alineacion': tk.E},
                              {'titulo':'Telef 2',
                              'campo': 'tf2ges',
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

    def ver_gestionados(self, *args):
        # Ver clientes gestionados por este administrador/gestor de clientes
        # Id del del administrador
        idges = self.rst[self.current.get()]['id']
        strsqladm = 'SELECT * FROM clientes WHERE gescli={}'.format(idges)
        self.rstcli = db.consultar(strsqladm, con=self.con)
        
        if len(self.rstcli) == 0:
            messagebox.showinfo(parent=self, 
                                message="Ningún cliente está gestionado por este gestor", 
                                title="CLIENTES GESTIONADOS")
        else:
            # Declaro puntero intvar usado por seledata
            posicioncli = tk.IntVar()
            posicioncli.set(0)
            # Cargar formulario para selección de registro
            # con busqueda por contenido en.
            frmsele = SeleData(self,
                        self.rstcli,
                        [ {'titulo':'Cliente',
                            'campo': 'nomcli',
                            'ancho': 350,
                            'alineacion': tk.W},
                            {'titulo':'Contacto',
                            'campo': 'concli',
                            'ancho': 350,
                            'alineacion': tk.W},
                            {'titulo':'Dirección',
                            'campo': 'dircli',
                            'ancho': 350,
                            'alineacion': tk.W},
                            {'titulo':'D.P.',
                            'campo': 'discli',
                            'ancho': 70,
                            'alineacion': tk.E},
                            {'titulo':'Población',
                            'campo': 'pobcli',
                            'ancho': 200,
                            'alineacion': tk.W},
                            {'titulo':'Telefono1',
                            'campo': 'tf1cli',
                            'ancho': 110,
                            'alineacion': tk.E},
                            {'titulo':'Telefono2',
                            'campo': 'tf2cli',
                            'ancho': 110,
                            'alineacion': tk.E}], posicioncli, 0)
                            
        return
    
class Framegest(tk.Frame):
    '''
        Ficha de componentes/controles de visualización de gestores/administradores
    '''    
    def __init__(self, hcaller):
        # Formulario contenedor
        self.hcaller = hcaller
        # Creamos Frame con marco de 1 px en negro y un margen sup. e inf. de 10
        super().__init__(hcaller, pady=10, highlightbackground="black", highlightthickness=1)
        # Area de contenido
        # Mostramos datos titular de las aplicaciones (NO MODIFICABLE EN este formulario)
        tk.Label(self, text="Nombre:").grid(row=0, column=0, sticky=tk.E)
        tk.Label(self, text="ID:").grid(row=0, column=3, sticky=tk.E)
        tk.Label(self, text="Contacto:").grid(row=1, column=0, sticky=tk.E)
        tk.Label(self, text="Teléfonos:").grid(row=2, column=0, sticky=tk.E)
        tk.Label(self, text="Mail:").grid(row=3, column=0, sticky=tk.E)
        tk.Label(self, text="Observaciones").grid(row=4, column=0, sticky=tk.E)

        self.nomges=Textbox(self, width=40, tipo=Textbox.MAYUSCULAS)
        self.nomges.grid(row=0, column=1, columnspan=3, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.idges=Numbox(self, width=5, takefocus=0)
        self.idges.grid(row=0, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.conges=Textbox(self, width=40, tipo=Textbox.TITLE)
        self.conges.grid(row=1, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.tf1ges = Numbox(self, width=9)
        self.tf1ges.grid(row=2, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.tf2ges = Numbox(self, width=9)
        self.tf2ges.grid(row=2, column=2, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.maiges = Textbox(self,  width=40, tipo=Textbox.MINUSCULAS)
        self.maiges.grid(row=3, column=1, columnspan=3, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.obsges = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=5)
        self.obsges.grid(row=5,column=0, columnspan=self.grid_size()[0], 
                         sticky=tk.NSEW, ipadx=3, ipady=3, padx=3, pady=3)
        # self.imgGest = tk.PhotoImage(file='img/list32.png')
        # self.btngestionados=tk.Button(self,image=self.imgGest,text='Clientes',compound=tk.LEFT,command=self.hcaller.ver_gestionados)
        # self.btngestionados.grid(row=1, column=4, ipadx=3, ipady=3, padx=3, pady=3)
        # self.hcaller.statusbar.createTip(self.btngestionados, "Ver Clientes gestionados [F6]")

        self.rowconfigure(5, weight=1)
        self.columnconfigure(2, weight=1)
        self.pack(fill=tk.BOTH, expand=True)
        # Esto lo hago para que al pulsar TAB desde maiges entre en el obsges
        # directamente, sino hay que pulsar dos veces TAB
        self.pulsadaTab=False
        self.maiges.bind('<Tab>', lambda event: self.pulsaTab(event))
        self.maiges.bind('<FocusOut>', lambda event:  self.porfoco(event))

    def pulsaTab(self, evt):
        # Flag para avanzar desde maiges a obsges
        self.pulsadaTab = True
        print("Pulsada Tab en maiges")

    def porfoco(self, evt):
        # Si se ha perdido el foco desde maiges pulsando Tab
        if self.pulsadaTab==True:
            # Enfocamos a obsges (Sino hay que pulsar 2 veces)
            self.obsges.focus()
            # Retiramos flag para próximavez
            self.pulsadaTab=False


    # Metodos del Frame
    def clear(self):
        #  Limpiar value de los entry
        try:
            for w in self.winfo_children():
                if w.winfo_class() == 'Entry':
                    w['state']='normal'
                    w.delete(0, 'end')
                    w['state']='readonly'

            self.obsges['state']='normal'
            self.obsges.delete(1.0, 'end')
            self.obsges['state']='disabled'
        except:
            messagebox.showinfo("ERROR clearFields", "Se ha producido un error")

    def dataShow(self, dicdata):
        # Diccionario de datos con los campos a mostrar y valores
        self.clear()
        # Hacemos editables los textbox/entry
        for w in self.winfo_children():
            if w.winfo_class() == 'Entry':
                w['state']='normal'
        
        self.idges.set_value(dicdata['id'])
        self.nomges.set_texto(dicdata['nomges'])
        self.conges.set_texto(dicdata['conges'])
        self.tf1ges.set_texto(dicdata['tf1ges'])
        self.tf2ges.set_texto(dicdata['tf2ges'])
        self.maiges.set_texto(dicdata['maiges'])
        # Revertimos edición y ponemos readonly textbox
        for w in self.winfo_children():
            if w.winfo_class() == 'Entry':
                w['state']='readonly'

        # Cuadro de observaciones
        self.obsges['state']='normal'
        self.obsges.delete('1.0', tk.END)
        if dicdata['obsges']!= None:
            self.obsges.insert('1.0', dicdata['obsges'])

        self.obsges['state']='disabled'

    def setEditable(self, estado=True):
        # Hacemos editables los textbox/entry (Por si acaso)
        for w in self.winfo_children():
            if w.winfo_class() in ['Entry','Text']:
                w['state']='normal'

        self.obsges['state']= 'normal'
        self.idges['state'] = 'readonly'
            


class frmgesedit(FormEdit):
    """
        Formulario Edición Gestores de clientes

    """
    
    def __init__(self, hcaller, name='', registro={}):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
            El registro es un diccionario con los datos a modificar.
            Si esta vacío es nuevo.
        """
        # La conexión creada en gasyluz
        # Entendemos que se ha establecido (y la referenciamos)
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
        self.contenido=Framegest(self)
        #
        # Icono que aparece en ventana minimizada (Barra de tareas)
        self.setIcon('img/user32.gif')
        
        # Ponernos a la escucha de eventos generados por Buttons de Buttonbar
        # Cuando queramos grabar el registro
        self.bind('<<savedata>>', self.onsave)

        self.showdata()
        self.contenido.nomges.focus_force()
        self.geometry('950x450+540+160')
        self.update()

    def showdata(self, *args):

        if self.idrec == 0:
            self.contenido.idges.set_value(0)
            self.title('NUEVO GESTOR DE CLIENTES')
            pos = 'Introduzca datos del nuevo Gestor'
        else:
            self.contenido.dataShow(self.registro)
            pos = 'Actualize datos del Gestor'
            self.title('EDICION DATOS DEL GESTOR DE CLIENTES')
            
        # Mostramos la posicion en el statusbar
        self.statusbar.showMensaje(pos, True)
        # Hacemos editables los textbox/entry (Por si acaso)
        self.contenido.setEditable()
        # Enfocamos en campo primero a modificar
        self.contenido.nomges.focus_set()

    def onsave(self, *args):
        # Componemos la instrucción SQL
        if self.modo == 'INSERT':
            strsql = "INSERT INTO gestores "
            strsql  += "(nomges,conges,tf1ges,tf2ges,maiges,obsges) " 
            strsql +=" VALUES ('{}'" +  ",'{}'"*5 + ")"
            strsql = strsql.format(self.contenido.nomges.get(),self.contenido.conges.get(),
                                   self.contenido.tf1ges.get(),self.contenido.tf2ges.get(),
                                   self.contenido.maiges.get(),self.contenido.obsges.get("1.0", tk.END))
        else:
            strsql = "UPDATE gestores SET nomges='{}',conges='{}',tf1ges='{}',tf2ges='{}',"
            strsql += "maiges='{}',obsges='{}' WHERE id = {}"
            strsql = strsql.format(self.contenido.nomges.get(),self.contenido.conges.get(),
                                   self.contenido.tf1ges.get(),self.contenido.tf2ges.get(),
                                   self.contenido.maiges.get(),self.contenido.obsges.get("1.0", tk.END),
                                   str(self.idrec))
        
        # Ejecutamos
        db.actualiza(strsql, con=self.cnn)
        self.contenido.nomges.focus_force()
        self.closer()

