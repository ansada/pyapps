import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

from Propiedades import *
from Controls import *
from Forms import *
from DBsql import *

class tarifas(FormData):
    """
        Formulario de Tarifas

    """
    
    def __init__(self, hcaller, name):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
        """
        self.prop=cmvar.properties
        
        # Conexión a datos ya realizada en gasyluz
        self.cnn="GYL"
        strsql = "SELECT * FROM tarifas"
        
        super().__init__(hcaller, name, strsql, self.cnn, 'destfa')
        self.title("TARIFAS DE ACCESO")
        #
        # Icono que aparece en ventana minimizada (Barra de tareas)
        self.setIcon('img/tarifas.png')
        #
        # Aquí diseñamos los widgets que se verán en forma de ficha
        self.contenido=Frametarifa(self)
        #
        # Ponernos a la escucha de eventos generados por Buttons de Buttonbar
        # Cada vez que el cursor del result cambie
        self.bind('<<cursordata>>', self.showdata)
        # Cuando se editen - añadan - eliminen datos
        self.bind('<<editdata>>', self.on_btnedit)
        self.bind('<<newdata>>', self.on_btnnew)
        # self.bind('<<deldata>>', self.on_btndel)
        # self.bind('<F6>', self.ver_gestionados)
        #
        # Es la primera entrada/exposición de datos
        if self.current.get() >= 0:
            self.showdata()
        # Capturar evento buscar (F5)
        self.bind('<<seledata>>', self.seledata)
        #hcaller.hide()
        #self.geometry('950x450+540+160')
        self.update()
        #self.center()
        
    # Metodos
    def showdata(self, *args):
        
        self.contenido.dataShow(self.rst[self.current.get()])
        # Actualizo combobox de busqueda
        self.cmbfind.set(self.contenido.txtdes.get())
        # Mostramos la posicion en el statusbar
        pos = 'Registro: ' + str(self.current.get()+1) + ' de ' + str(len(self.rst))
        self.statusbar.showMensaje(pos, True)
        # Actualizar estado de barra de botones
        self.updateBar()
        
    # # Respuesta a Eventos escuchados
        
    def on_btnnew(self, *args):
        # Nuevo gestor de clientes
        frmedit = frmtfaedit(self)
        self.withdraw()
        self.wait_window(frmedit)
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
        
        frmedit = frmtfaedit(self, '', registro=registro)
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
        
    # def on_btndel(self, *args):
    #     indice = self.current.get()
    #     idges = self.rst[self.current.get()]['id']
    #     consulta = 'SELECT COUNT(*) AS registros FROM clientes WHERE gescli = {}'.format(str(idges))
    #     rstexist = db.consultar(consulta, con=self.con)
    #     if int(rstexist[0]['registros']) > 0:
    #         # Hay algún registro referenciado (cliente asignado a este gestor)
    #         messagebox.showinfo(
    #             "ELIMINAR REGISTRO "+str(idges), 
    #             "Este gestor tiene "+str(rstexist[0]['registros'])+" de cliente asignados\nIMPOSIBLE ELIMINAR",
    #             parent=self)
    #         return
    #     else:
    #         ok = messagebox.askokcancel(message="¿Está ud. seguro?", title="ELIMINAR", parent=self)
    #         if ok == True:
    #             strsql = "DELETE FROM gestores WHERE id = {}"
    #             strsql = strsql.format(idges)
    #             db.actualiza(strsql, con=self.cnn)
    #             # messagebox.showinfo("ELIMINADO", "Registro borrado", parent=self)
    #         else:
    #             return

    #     # Volvemos a cargar el DataFrame
    #     self.loadData()
    #     # Si la posición anterior era la última ahora
    #     # será mayor que el tamaño de la Lista, por tanto
    #     # hacemos que sea el último registro
    #     if indice >= len(self.rst)-1:
    #         self.current.set(len(self.rst)-1)
        
    #     self.showdata()
    #     self.cmbfind.set(self.contenido.nomges.get())
    #     return

    def seledata(self, *args):

        frmsele = SeleData(self,
                           self.rst,
                           [ {'titulo':'Tarifa',
                              'campo': 'destfa',
                              'ancho': 300,
                              'alineacion': tk.W},
                              {'titulo':'ATR',
                              'campo': 'codtfa',
                              'ancho': 50,
                              'alineacion': tk.W},
                              {'titulo':'TIPO',
                              'campo': 'tiptfa',
                              'ancho': 50,
                              'alineacion': tk.E},
                              {'titulo':'Estado',
                              'campo': 'stdtfa',
                              'ancho': 50,
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
    
class Frametarifa(tk.Frame):
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
        tk.Label(self, text="ID:").grid(row=0, column=0, sticky=tk.E)
        tk.Label(self, text="Descripción:").grid(row=1, column=0, sticky=tk.E)
        tk.Label(self, text="Tipo:").grid(row=0, column=2, sticky=tk.E)
        tk.Label(self, text="ATR:").grid(row=1, column=5, sticky=tk.E)

        self.txtid=tk.Entry(self, width=3, takefocus=False)
        self.txtid.grid(row=0, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttip=Textbox(self, width=1, tipo=Textbox.MAYUSCULAS)
        self.txttip.grid(row=0, column=3, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttipo=tk.Entry(self, takefocus=False)
        self.txttipo.grid(row=0, column=4, columnspan=2, sticky=tk.EW, ipadx=3,ipady=3, padx=3, pady=3)
        self.txtstdo=tk.Entry(self, takefocus=False)
        self.txtstdo.grid(row=0, column=6, sticky=tk.EW, ipadx=3,ipady=3, padx=3, pady=3)
        self.txtdes = Textbox(self, width=20, tipo=Textbox.MAYUSCULAS)
        self.txtdes.grid(row=1, column=1, columnspan=4, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtatr = Textbox(self, width=6, tipo=Textbox.MAYUSCULAS)
        self.txtatr.grid(row=1, column =6, sticky=tk.EW)

        self.columnconfigure(4, weight=1)
        # self.rowconfigure(3, weight=1)
        self.pack(fill=tk.BOTH, expand=True)
        self.txttip.bind('<FocusOut>', self.changeTip)
        
    # Metodos del Frame

    def dataShow(self, dicdata):
        # Diccionario de datos con los campos a mostrar y valores
        # self.showContenido(self.txtid, dicdata['id'])
        self.showContenido(self.txtid, str(dicdata['id']))
        self.showContenido(self.txttip, dicdata['tiptfa'])
        tipo = ('GAS' if dicdata['tiptfa']=='G' else 'ELECTRICIDAD')
        self.showContenido(self.txttipo, tipo)
        stdo = ('ACTIVA' if dicdata['stdtfa'] else 'INACTIVA')
        self.showContenido(self.txtstdo, stdo)
        self.showContenido(self.txtdes, dicdata['destfa'])
        self.showContenido(self.txtatr, dicdata['codtfa'])
                    
    def showContenido(self, w, value):
        w['state']='normal'
        w.delete(0,tk.END)
        w.insert(0, value)
        w['state']='readonly'

    def setEditable(self, editar=True):
        # Controles que aceptan modificaciones
        ctrls=[self.txttip, self.txtdes, self.txtatr]
        # Los hacemos editables
        for w in ctrls:
            cambio=('normal' if editar else 'readonly')
            w['state']=cambio

    def changeTip(self, *args):
        # Cuando cambia el contenido de txttip al perder el foco
        if self.txttip.get() in ['L','G']: 
            tipo = ('GAS' if self.txttip.get()=='G' else 'ELECTRICIDAD')
        else:
            messagebox.showerror("TIPO INVALIDO",'Debe introducir\nG = Gas\no L = ELECTRICIDAD', parent=self)
            self.txttip.focus_set()
            return

        self.showContenido(self.txttipo, tipo)


class frmtfaedit(FormEdit):
    """
        Formulario Edición de tarifas de acceso

    """
    
    def __init__(self, hcaller, name='', registro={}):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
            El registro es un diccionario con los datos a modificar.
            Si esta vacío es nuevo.
        """
        # La conexión creada en gasyluz
        # Entendemos que se ha establecido
        self.condb = hcaller.cnn
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
        self.contenido=Frametarifa(self)
        #
        # Icono que aparece en ventana minimizada (Barra de tareas)
        self.setIcon('img/tarifas.png')
        
        # Ponernos a la escucha de eventos generados por Buttons de Buttonbar
        # Cuando queramos grabar el registro
        self.bind('<<savedata>>', self.onsave)

        self.showdata()

        #self.geometry('950x450+540+160')
        self.update()

    def showdata(self, *args):
        
        # Hacemos editables los textbox/entry
        self.contenido.setEditable()
        # Si es actualización no dejamos modificar el tipo
        if self.idrec == 0:
            self.contenido.showContenido(self.contenido.txtid, str(0))
            self.title('NUEVA TARIFA DE ACCESO')
            pos = 'Introduzca datos del nuevo Gestor'
        else:
            self.contenido.dataShow(self.registro)
            pos = 'Actualize datos del Gestor'
            self.title('EDICION TARIFA DE ACCESO')
            self.contenido.txttip['state']='readonly'
            
        # Mostramos la posicion en el statusbar
        self.statusbar.showMensaje(pos, True)
        # Enfocamos en campo primero a modificar
        if self.modo=='INSERT':
            self.contenido.txttip.focus_set()
        else:
            self.contenido.txtdes.focus_set()

    def onsave(self, *args):
        # Componemos la instrucción SQL
        if self.modo == 'INSERT':
            strsql = "INSERT INTO tarifas "
            strsql  += "(tiptfa,codtfa,destfa,stdtfa) " 
            strsql +=" VALUES ('{}'" +  ",'{}'"*3 + ")"
            strsql = strsql.format(self.contenido.txttip.get(),self.contenido.txtatr.get(),
                                   self.contenido.txtdes.get(),True)
        else:
            strsql = "UPDATE tarifas SET tiptfa='{}',codtfa='{}',destfa='{}' WHERE id = {}"
            strsql = strsql.format(self.contenido.txttip.get(),self.contenido.txtatr.get(),
                                   self.contenido.txtdes.get(), str(self.idrec))
        
        # Ejecutamos
        db.actualiza(strsql, con=self.condb)
        self.closer()

