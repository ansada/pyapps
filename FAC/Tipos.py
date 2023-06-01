import tkinter as tk
from tkinter import messagebox

from Propiedades import *
from Controls import *
from Forms import *
from DBsql import *
import Dialogo as dlg

class frmTipo(FormData):
    """
        Formulario Acreedores (Proveedores)

    """
    
    def __init__(self, hcaller, name, tipo):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
        """
        self.prop=cmvar.properties
        self.tipo = tipo
        # Conexión a datos
        self.cnn="FAC"
        tabla = 'tiposing'
        if tipo == 'G':
            tabla = 'tiposgto'
            
        self.tabla=tabla
        
        strsql = f"SELECT * FROM {self.tabla}"

        super().__init__(hcaller, name, strsql, self.cnn, 'nomtip')
        #
        # Aquí diseñamos los widgets que se verán en forma de ficha
        self.declaraControls()
        #
        # Icono que aparece en ventana minimizada (Barra de tareas)
        if tipo == 'G':
            self.setIcon('img/indent-less.png')
            self.title("TIPOS DE GASTO")
        else:
            self.setIcon('img/indent-more.png')
            self.title("TIPOS DE INGRESO")

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
        tk.Label(self.contenido, text="Denominacion:").grid(row=1, column=0, sticky=tk.E)
        
        self.idtip=tk.Label(self.contenido, width=5, anchor=tk.E)
        self.idtip.grid(row=0, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.nomtip=tk.Label(self.contenido, width=70, anchor=tk.W)
        self.nomtip.grid(row=1, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        
        self.contenido.columnconfigure(1, weight=1)

        self.contenido.pack(fill=tk.BOTH, expand=True)

    
    def showdata(self, *args):
        reg = self.current.get()
        #    
        self.idtip['text']=self.rst[reg]['id']
        self.nomtip['text']=self.rst[reg]['nomtip']
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
        
    # Respuesta a Eventos escuchados
        
    def on_btnnew(self, *args):
        # Nuevo tipo
        frmedittip = frmtipedit(self)
        self.withdraw()
        self.wait_window(frmedittip)
        self.show()
        self.loadData()
        self.current.set(len(self.rst)-1)
        self.showdata()

    def on_btnedit(self, *args):
        indice = self.current.get()
        registro=self.rst[indice]
        
        frmedittip = frmtipedit(self, '', registro=registro)
        self.withdraw()
        self.wait_window(frmedittip)
        self.show()
        self.loadData()
        self.current.set(indice)
        self.showdata()
        self.cmbfind.set(self.nomtip['text'])
        
    def on_btndel(self, *args):
        indice = self.current.get()
        idtip = self.rst[self.current.get()]['id']
        origen='facturas'
        campo='tipfac'
        if self.tipo=='G':
            origen='gastos'
            campo='tipgto'

        consulta = 'SELECT COUNT(*) AS registros FROM {} WHERE {} = {}'.format(origen,campo,str(idtip))
        rstexist = db.consultar(consulta, con=self.cnn)
        if int(rstexist[0]['registros']) > 0:
            strmsg="Este tipo se ha usado en "+str(rstexist[0]['registros'])+" registros de "+origen+"\nIMPOSIBLE ELIMINAR"
            dlg.dialogo(self,"ELIMINAR REGISTRO "+str(idtip),strmsg,img=dlg.ERROR)
            return
        else:
            ok=dlg.dialogo(self,"ELIMINAR REGISTRO "+str(idtip),"¿Está ud. seguro?",['Aceptar','Cancelar'],img=dlg.PREGUNTA).showmodal()
            if ok == 0:
                strsql = "DELETE FROM {} WHERE id = {}"
                strsql = strsql.format(self.tabla,idtip)
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
        self.cmbfind.set(self.nomtip['text'])
        return

    def seledata(self, *args):

        frmsele = SeleData(self,
                           self.rst,
                           [ {'titulo':'ID',
                              'campo': 'id',
                              'ancho': 80,
                              'alineacion': tk.W},
                              {'titulo':'DENOMINACION',
                              'campo': 'nomtip',
                              'ancho': 300,
                              'alineacion': tk.W}], self.current, 0)
        
        frmsele.bind('<<gotodata>>', self.on_selected)
        
        # Esperamos a que devuelva el control
        #self.wait_window(frmsele)
        # Y volvemos a mostrar
        #self.show()

    def on_selected(self, *args):
        # self.center()
        self.showPosicion()

   

class frmtipedit(FormEdit):
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
        self.nomtip.focus_force()


    # Metodos

    def declaraControls(self):
        tk.Label(self.buttonbar, text="ID: ").pack(side=tk.LEFT, padx=20)
        self.idtip=tk.Label(self.buttonbar, bg='white',borderwidth=1,
                           relief="solid", width=5,anchor=tk.E)
        self.idtip.pack(side=tk.LEFT, ipadx=3, ipady=3, padx=3, pady=3)

        # Area de contenido
        self.contenido=tk.Frame(self, pady=10, highlightbackground="black", highlightthickness=1)

        tk.Label(self.contenido, text="Denominacion:").grid(row=1, column=0, sticky=tk.E)
        
        self.nomtip=Textbox(self.contenido, width=40, tipo=Textbox.MAYUSCULAS)
        self.nomtip.grid(row=1, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
            
        self.contenido.columnconfigure(1, weight=1)
        
        self.contenido.pack(fill=tk.BOTH, expand=True)
        
    def showdata(self, *args):
        
        tipo = 'GASTO'
        if self.hcaller.tipo == 'I':
            tipo='INGRESO'

        if self.idrec == 0:
            self.idtip['text']='0'
            self.title('NUEVO TIPO DE '+tipo)
            pos = 'Introduzca datos nuevo registro'
        else:
            # self.showfield(self.idadm, 'id')
            # Clave PK no modificable (auto-increment)
            self.idtip['text']=str(self.idrec)
            self.nomtip.set_texto(self.registro['nomtip'])
            pos = 'Actualize datos tipo de '+tipo
            self.title('EDICION DATOS DE '+tipo)
            
        # Mostramos la posicion en el statusbar
        self.statusbar.showMensaje(pos, True)
        # Enfocamos en campo a modificar
        self.nomtip.focus_set()
       
    def onsave(self, *args):
        # Componemos la instrucción SQL
        if self.modo == 'INSERT':
            strsql = f"INSERT INTO {self.hcaller.tabla} "
            strsql  += "(nomtip) " 
            strsql +=" VALUES ('{}')"
            strsql = strsql.format(self.nomtip.get())
        else:
            strsql = "UPDATE {} SET nomtip='{}' WHERE id = {}"
            strsql = strsql.format(self.hcaller.tabla,self.nomtip.get(),self.idtip['text'])
        
        # Ejecutamos
        db.actualiza(strsql, con=self.cnn)
        self.closer()

class frmtipgto(frmTipo):
    """
        Formulario tipo de gasto

    """

    def __init__(self, hcaller, name=""):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
        """
        self.hcaller = hcaller

        super().__init__(self.hcaller, name, tipo='G')


class frmtiping(frmTipo):
    """
        Formulario tipo de ingreso

    """

    def __init__(self, hcaller, name=""):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
        """
        self.hcaller = hcaller

        super().__init__(self.hcaller, name, tipo='I')