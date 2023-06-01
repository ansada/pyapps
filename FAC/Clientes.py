import tkinter as tk
from tkinter import messagebox

from Propiedades import *
from Controls import *
from Forms import *
from DBsql import *
import Dialogo as dlg
import string

class frmCliente(FormData):
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
        strsql = "SELECT * FROM clientes"
        
        super().__init__(hcaller, name, strsql, self.cnn, 'empcli')
        self.title("CLIENTES")
        #
        # Aquí diseñamos los widgets que se verán en forma de ficha
        # Area de contenido
        self.contenido=tk.Frame(self, pady=10, highlightbackground="black", highlightthickness=1)
        tk.Label(self.contenido, text="ID:").grid(row=0, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="Empresa:").grid(row=1, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="NIF:").grid(row=1, column=6, sticky=tk.E)
        tk.Label(self.contenido, text="Contacto:").grid(row=2, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="Dirección:").grid(row=3, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="DP:").grid(row=3, column=6, sticky=tk.E)
        tk.Label(self.contenido, text="Población:").grid(row=4, column=4, sticky=tk.E)
        tk.Label(self.contenido, text="Provincia:").grid(row=4, column=6, sticky=tk.E)
        tk.Label(self.contenido, text="Teléfono:").grid(row=5, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="Móvil:").grid(row=5, column=2, sticky=tk.E)
        tk.Label(self.contenido, text="Mail:").grid(row=5, column=4, sticky=tk.E)
        tk.Label(self.contenido, text="F.Pago:").grid(row=6, column=0, sticky=tk.E)
        self.txtid =tk.Label(self.contenido, width=3, anchor=tk.E, bg='white',borderwidth=1,relief='solid')
        self.txtnif=tk.Label(self.contenido, width=10,anchor=tk.W, bg='white',borderwidth=1,relief='solid')
        self.txtemp=tk.Label(self.contenido, width=35,anchor=tk.W, bg='white',borderwidth=1,relief='solid')
        self.txtcon=tk.Label(self.contenido, width=35,anchor=tk.W, bg='white',borderwidth=1,relief='solid')
        self.txtdir=tk.Label(self.contenido, width=35,anchor=tk.W, bg='white',borderwidth=1,relief='solid')
        self.txtdis=tk.Label(self.contenido, width=5, anchor=tk.W, bg='white',borderwidth=1,relief='solid')
        self.txtpob=tk.Label(self.contenido, width=20,anchor=tk.W, bg='white',borderwidth=1,relief='solid')
        self.txtprv=tk.Label(self.contenido, width=20,anchor=tk.W, bg='white',borderwidth=1,relief='solid')
        self.txttlf=tk.Label(self.contenido, width=9, anchor=tk.W, bg='white',borderwidth=1,relief='solid')
        self.txtmov=tk.Label(self.contenido, width=9, anchor=tk.W, bg='white',borderwidth=1,relief='solid')
        self.txtmai=tk.Label(self.contenido, width=30,anchor=tk.W, bg='white',borderwidth=1,relief='solid')
        self.txtfpa=tk.Label(self.contenido, width=40,anchor=tk.W, bg='white',borderwidth=1,relief='solid')
        self.txtid .grid(row=0,column=1, padx=3,ipadx=3,pady=3,ipady=3,sticky=tk.E)
        self.txtemp.grid(row=1,column=1,columnspan=5, padx=3,ipadx=3,pady=3,ipady=3, sticky=tk.EW)
        self.txtnif.grid(row=1,column=7, padx=3,ipadx=3,pady=3,ipady=3, sticky=tk.E)
        self.txtcon.grid(row=2,column=1,columnspan=7, padx=3,ipadx=3,pady=3,ipady=3, sticky=tk.EW)
        self.txtdir.grid(row=3,column=1,columnspan=5, padx=3,ipadx=3,pady=3,ipady=3, sticky=tk.EW)
        self.txtdis.grid(row=3,column=7, padx=3,ipadx=3,pady=3,ipady=3)
        self.txtpob.grid(row=4,column=1,columnspan=3, padx=3,ipadx=3,pady=3,ipady=3, sticky=tk.E)
        self.txtprv.grid(row=4,column=5,columnspan=3, padx=3,ipadx=3,pady=3,ipady=3, sticky=tk.EW)
        self.txttlf.grid(row=5,column=1, padx=3,ipadx=3,pady=3,ipady=3)
        self.txtmov.grid(row=5,column=3, padx=3,ipadx=3,pady=3,ipady=3)
        self.txtmai.grid(row=5,column=5,columnspan=3, padx=3,ipadx=3,pady=3,ipady=3,sticky=tk.EW)
        self.txtfpa.grid(row=6,column=1,columnspan=7, padx=3,ipadx=3,pady=3,ipady=3,sticky=tk.EW)
        
        self.contenido.columnconfigure(2, weight=1)
        self.contenido.columnconfigure(5, weight=1)

        self.contenido.pack(fill=tk.BOTH, expand=True)
        # Observaciones al contrato
        self.observa=frmAnota(self)
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
        self.bind('<Alt-E>', self.observa.editaObservaciones)
        self.bind('<Alt-e>', self.observa.editaObservaciones)
        #
        # Es la primera entrada/exposición de datos
        if self.current.get() >= 0:
            self.showdata()
        # Capturar evento buscar (F5)
        self.bind('<<seledata>>', self.seledata)
        # self.center()
        
    # Metodos
    

    # def clearFields(self):
    #     #  Limpiar value
    #     for wdg in ctrls:
    #         wdg['text']=''

    def showdata(self, *args):
        # Controles (widgets - Etiquetas Label)
        ctrls=[self.txtid,self.txtnif,self.txtemp,self.txtcon,self.txtdir,self.txtdis,self.txtpob,self.txtprv,self.txttlf,self.txtmov,self.txtmai,self.txtfpa]
        # Campos en tabla
        field=['id','nifcli','empcli','concli','dircli','discli','pobcli','prvcli','tlfcli','movcli','maicli','fpacli']
        # self.clearFields() - Probablemente no haga falta
        # 
        for i in range(len(ctrls)):
            self.showcampo(ctrls[i],field[i])    
        #
        # Mostramos el campo observaciones
        registro = self.rst[self.current.get()]
        self.observa.showdatos(registro)
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

    def showcampo(self, widget, campo):
        # Entiendo que todos son etiquetas (Label)
        widget['text'] = self.rst[self.current.get()][campo]

    # Respuesta a Eventos escuchados
        
    def on_btnnew(self, *args):
        # Nuevo administrador
        frmeditcli = frmcliedit(self)
        self.withdraw()
        self.wait_window(frmeditcli)
        self.show()
        self.loadData()
        self.current.set(len(self.rst)-1)
        self.showdata()

    def on_btnedit(self, *args):
        indice = self.current.get()
        registro=self.rst[indice]
        
        frmeditcli = frmcliedit(self, '', registro=registro)
        self.withdraw()
        self.wait_window(frmeditcli)
        self.show()
        self.loadData()
        self.current.set(indice)
        self.showdata()
        self.cmbfind.set(self.txtemp['text'])
        
    def on_btndel(self, *args):
        indice = self.current.get()
        idCli = self.rst[self.current.get()]['id']
        consulta = 'SELECT COUNT(*) AS registros FROM facturas WHERE clifac = {}'.format(str(idCli), con=self.cnn)
        rstexist = db.consultar(consulta, con=self.cnn)
        if int(rstexist[0]['registros']) > 0:
            #rstclis=db.consultar('SELECT * FROM clientes WHERE admcli =?',(idAdmin,),con=self.cnn)
            strmsg="Este cliente tiene "+str(rstexist[0]['registros'])+" de facturas registradas\nIMPOSIBLE ELIMINAR"
            dlg.dialogo(self,"ELIMINAR REGISTRO "+str(idCli),strmsg,img=dlg.ERROR)
            return
        else:
            ok=dlg.dialogo(self,"ELIMINAR REGISTRO "+str(idCli),"¿Está ud. seguro?",['Aceptar','Cancelar'],img=dlg.PREGUNTA).showmodal()
            if ok == 0:
                strsql = f"DELETE FROM clientes WHERE id = {idCli}"
                db.actualiza(strsql, con=self.cnn)
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
        self.cmbfind.set(self.txtemp['text'])
        return

    def seledata(self, *args):

        frmsele = SeleData(self,
                           self.rst,
                           [ {'titulo':'Empresa',
                              'campo': 'empcli',
                              'ancho': 300,
                              'alineacion': tk.W},
                              {'titulo':'NIF',
                              'campo': 'nifcli',
                              'ancho': 100,
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
                              'alineacion': tk.W}], self.current, 0)
        
        frmsele.bind('<<gotodata>>', self.on_selected)
        
        # Esperamos a que devuelva el control
        #self.wait_window(frmsele)
        # Y volvemos a mostrar
        #self.show()

    def on_selected(self, *args):
        # self.center()
        self.showPosicion()
    

class frmcliedit(FormEdit):
    """
        Formulario Edición Clientes

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
        # Area de contenido
        self.contenido=tk.Frame(self, pady=10, highlightbackground="black", highlightthickness=1)
        tk.Label(self.contenido, text="ID:").grid(row=0, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="Empresa:").grid(row=1, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="NIF:").grid(row=1, column=6, sticky=tk.E)
        tk.Label(self.contenido, text="Contacto:").grid(row=2, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="Dirección:").grid(row=3, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="DP:").grid(row=3, column=6, sticky=tk.E)
        tk.Label(self.contenido, text="Población:").grid(row=4, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="Provincia:").grid(row=4, column=6, sticky=tk.E)
        tk.Label(self.contenido, text="Teléfono:").grid(row=5, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="Móvil:").grid(row=5, column=2, sticky=tk.E)
        tk.Label(self.contenido, text="Mail:").grid(row=5, column=4, sticky=tk.E)
        tk.Label(self.contenido, text="F.Pago:").grid(row=6, column=0, sticky=tk.E)
        self.txtid =tk.Label(self.contenido, width=3, anchor=tk.E, bg='white',borderwidth=1,relief='solid')
        self.txtemp=Textbox(self.contenido, width=40,justify=tk.LEFT,tipo=Textbox.MAYUSCULAS)
        self.txtnif=Textbox(self.contenido, width=9,justify=tk.LEFT,tipo=Textbox.MAYUSCULAS)
        self.txtcon=Textbox(self.contenido, width=40,justify=tk.LEFT, tipo=Textbox.TITLE)
        self.txtdir=Textbox(self.contenido, width=40,justify=tk.LEFT, tipo=Textbox.TITLE)
        self.txtdis=Numbox(self.contenido, width=5, justify=tk.LEFT)
        self.txtpob=Textbox(self.contenido, width=20,justify=tk.LEFT, tipo=Textbox.TITLE)
        self.txtprv=Textbox(self.contenido, width=20,justify=tk.LEFT, tipo=Textbox.MAYUSCULAS)
        self.txttlf=Numbox(self.contenido, width=9)
        self.txtmov=Numbox(self.contenido, width=9)
        self.txtmai=Textbox(self.contenido, width=30,justify=tk.LEFT,tipo=Textbox.MINUSCULAS)
        self.txtfpa=Textbox(self.contenido, width=40,justify=tk.LEFT,tipo=Textbox.MAYUSCULAS)
        self.txtid .grid(row=0,column=1, padx=3,ipadx=3,pady=3,ipady=3,sticky=tk.E)
        self.txtemp.grid(row=1,column=1,columnspan=5, padx=3,ipadx=3,pady=3,ipady=3, sticky=tk.EW)
        self.txtnif.grid(row=1,column=7, padx=3,ipadx=3,pady=3,ipady=3, sticky=tk.E)
        self.txtcon.grid(row=2,column=1,columnspan=7, padx=3,ipadx=3,pady=3,ipady=3, sticky=tk.EW)
        self.txtdir.grid(row=3,column=1,columnspan=5, padx=3,ipadx=3,pady=3,ipady=3, sticky=tk.EW)
        self.txtdis.grid(row=3,column=7, padx=3,ipadx=3,pady=3,ipady=3)
        self.txtpob.grid(row=4,column=1,columnspan=3, padx=3,ipadx=3,pady=3,ipady=3, sticky=tk.EW)
        self.txtprv.grid(row=4,column=5,columnspan=3, padx=3,ipadx=3,pady=3,ipady=3, sticky=tk.EW)
        self.txttlf.grid(row=5,column=1, padx=3,ipadx=3,pady=3,ipady=3)
        self.txtmov.grid(row=5,column=3, padx=3,ipadx=3,pady=3,ipady=3)
        self.txtmai.grid(row=5,column=5,columnspan=3, padx=3,ipadx=3,pady=3,ipady=3,sticky=tk.EW)
        self.txtfpa.grid(row=6,column=1,columnspan=7, padx=3,ipadx=3,pady=3,ipady=3,sticky=tk.EW)
        
        self.contenido.columnconfigure(2, weight=1)
        self.contenido.columnconfigure(5, weight=1)

        self.contenido.pack(fill=tk.BOTH, expand=True)
        # Por defecto la poblacion y provincia del titular de la aplicacion
        if self.modo=='INSERT':
            poblacion=cmvar.properties.getProperty('poblacion')
            provincia=cmvar.properties.getProperty('provincia')
            self.txtpob['text']=poblacion
            self.txtprv['text']=provincia

        #
        # Icono que aparece en ventana minimizada (Barra de tareas)
        self.setIcon('img/user32.gif')
        # Ponernos a la escucha de eventos generados por Buttons de Buttonbar
        # Cuando queramos grabar el registro
        self.bind('<<savedata>>', self.onsave)

        self.showdata()
        self.txtemp.focus_force()

    # Metodos
    def showdata(self, *args):
        # # Hacemos editables los textbox/entry (Por si acaso)
        # for w in self.contenido.winfo_children():
        #     if w.winfo_class() == 'Entry':
        #         w['state']='normal'
        #
        # Controles (widgets - Etiquetas Label)
        ctrls=[self.txtid,self.txtnif,self.txtemp,self.txtcon,self.txtdir,self.txtdis,self.txtpob,self.txtprv,self.txttlf,self.txtmov,self.txtmai,self.txtfpa]
        # Campos en tabla
        field=['id','nifcli','empcli','concli','dircli','discli','pobcli','prvcli','tlfcli','movcli','maicli','fpacli']
        #
        if self.idrec == 0:
            self.txtid['text']='0'
            self.title('NUEVO CLIENTE')
            pos = 'Introduzca datos nuevo registro'
        else:
            # self.showfield(self.idadm, 'id')
            # Clave PK no modificable (auto-increment)
            self.txtid['text']=str(self.idrec)
            for i in range(len(ctrls)):
                if i==0:
                    continue

                if self.registro[field[i]] != '':
                    ctrls[i].insert(0, self.registro[field[i]])
                else:
                    print("Se ha dado un valor nulo no imprimible en " + field[i])
                    
            pos = 'Actualize datos del Cliente'
            self.title('EDICION DATOS DE CLIENTE')
            
        # Mostramos la posicion en el statusbar
        self.statusbar.showMensaje(pos, True)
        # Enfocamos en campo primero a modificar
        self.txtemp.focus_set()
       
    def onsave(self, *args):
        # Componemos la instrucción SQL
        # Controles (widgets - Etiquetas Label)
        ctrls=[self.txtnif,self.txtemp,self.txtcon,self.txtdir,self.txtdis,self.txtpob,self.txtprv,self.txttlf,self.txtmov,self.txtmai,self.txtfpa]
        valores=[]
        for i in range(len(ctrls)):
            valores.append(ctrls[i].get())
        
        if self.modo == 'INSERT':
            strsql = "INSERT INTO clientes "
            strsql += "(nifcli,empcli,concli,dircli,discli,pobcli,prvcli,tlfcli,movcli,maicli,fpacli) " 
            strsql +=" VALUES (" + "'{}',"*10 + "'{}')"
            strsql = strsql.format(*valores)
        else:
            field=['nifcli','empcli','concli','dircli','discli','pobcli','prvcli','tlfcli','movcli','maicli','fpacli']
            strsql = "UPDATE clientes SET "
            for i in range(len(field)):
                strsql += (field[i]+"='{}',")
                
            strsql = strsql[:-1]
            strsql += " WHERE id = {}"
            valores.append(self.txtid['text'])
            strsql = strsql.format(*valores)

        # Ejecutamos
        db.actualiza(strsql, con=self.cnn)
        self.closer()

class frmAnota(tk.Frame):
    '''
        Frame que se integra en el contendor que lo llama 
    '''

    def __init__(self, contenedor):
        # Iniciamos clase padre
        super().__init__(contenedor)
        
        # Referencia al contrato contenedor que llama
        self.contenedor = contenedor
        # Nº de cliente que estamos tratando. 0 = No hay CLIENTE
        self.idcliente = 0
        # Conexión a datos del contenedor (que llama)
        self.con = contenedor.cnn
        # Estado de los comentarios
        self.modified = False
        cabObs = tk.Frame(self)
        self.imgAnota=tk.PhotoImage(file='img/edit32.png')
        btneditobs=tk.Button(cabObs, image=self.imgAnota, takefocus=0, command=lambda: self.editaObservaciones(self.contrato))
        contenedor.statusbar.createTip(btneditobs, "Editar observaciones al cliente [ALT-E]")
        btneditobs.grid(row=0, column=0, sticky=tk.W)
        self.imgsaveanota=tk.PhotoImage(file='img/save32.png')
        btnsaveobs=tk.Button(cabObs, image=self.imgsaveanota, takefocus=0, command=self.saveObservaciones)
        contenedor.statusbar.createTip(btnsaveobs, "Guardar modificaciones [ALT-G]")
        btnsaveobs.grid(row=0, column=1, sticky=tk.W)
        tk.Label(cabObs, text='OBSERVACIONES AL CLIENTE',bg='seashell4',fg='white').grid(row=0, column=2, sticky=tk.EW)
        cabObs.grid(row=0, column=0, sticky=tk.EW)
        cabObs.columnconfigure(2, weight=1)
        self.obscli = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=5)
        self.obscli.grid(row=2,column=0, columnspan=self.grid_size()[0], 
                         sticky=tk.NSEW, ipadx=3, ipady=3, padx=3, pady=3)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        
        self.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        # Separador del area de detalle
        tk.Frame(contenedor, background='black', height=1).pack(side=tk.BOTTOM, fill=tk.X)
        # Al pulsar INTRO en teclado numerico es como ENTER en teclado alfabetico
        self.obscli.bind('<KP_Enter>', lambda x: self.obscli.event_generate('<Return>'))
        self.obscli.bind('<FocusOut>', self.outObservaciones)
        self.obscli.bind('<Alt-G>', self.saveObservaciones)
        self.obscli.bind('<Alt-g>', self.saveObservaciones)
        # Registramos validación de las pulsaciones
        self.obscli.bind('<Key>', self.antPulsado)
        self.obscli.bind('<KeyRelease>', self.postPulsado)

    # Eventos y métodos
    def antPulsado(self, evt):
        # Guarda la longitud del texto antes de mostrar la pulsacion
        self.longitudTexto=len(self.obscli.get('1.0',tk.END))
        # Teclas que no contemplamos interceptar (flechas direccion,Home,End,etc )
        charNo=[79,80,81,83,85,88,89,87,37,64,50,90,110,111,113,114,115,116,118]

        if evt.keycode in charNo:
            return

        # Y por si pulsamos una tecla que no modifica la longitud del texto.
        if evt.char in string.printable:
            self.modified=True

    def postPulsado(self, evt):
        ''' 
        Registra que se ha modificado si se inserta o borra un caracter
        '''
        if self.longitudTexto != len(self.obscli.get('1.0',tk.END)):
            self.modified=True

    def showdatos(self, rst):
        # Mostrar el string recibido en campo observaciones
        self.obscli['state'] = 'normal'
        self.obscli.delete('1.0', tk.END)
        self.obscli.insert('1.0', rst['obscli'])
        self.obscli['state'] = 'disabled'
        # Guardamos el numero de cliente que significará que
        self.idcliente = rst['id']
        # Longitud del texto que actualmente contiene
        self.longitudTexto=len(self.obscli.get('1.0',tk.END))
        # # Mostramos estado del contrato
        # if rst['stdcon']==True:
        #     self.estado.config(bg='white', text='ACTIVO')
        #     # self.estado['text']="ACTIVO"
        # else:
        #     self.estado.config(bg='red', text='INACTIVO')
        #     #self.estado['text']="INACTIVO"

    def editaObservaciones(self, *args):
        if self.idcliente==0:
            return
        
        self.obscli.focus_set()
        self.obscli['state']='normal'
        # Posicionamos el cursor al final
        self.obscli.mark_set('insert',self.obscli.index('%s-1c'%tk.END))
        # Desactivo botones movimiento del cursor para que no interfieran
        # con la edición del cuadro de texto
        # for w in [self.contenedor.btnprevious, self.contenedor.btnfirst, self.contenedor.btnlast, self.contenedor.btnnext]:
        #      w['state'] = 'disable'
        for wdg in self.contenedor.buttonbar.winfo_children():
            wdg['state']='disable'
        
        self.contenedor.buttonbar.btnexit['state']='normal'

    def saveObservaciones(self, *args):
        if self.modified:
            # Guardamos cambios
            strmodifica='UPDATE clientes SET obscli="{}" WHERE id={}'.format(self.obscli.get('1.0',tk.END),self.idcliente)
            db.actualiza(strmodifica, con=self.con)
            self.obscli['state'] = 'disabled'
            self.modified = False
            # Guardamos el cambio en el result del contenedor
            self.contenedor.rst[self.contenedor.current.get()]['obscli'] = self.obscli.get('1.0',tk.END)
            # Resposicionamos el cursor en el registro
            # y lo mostramos de nuevo
            # registro = self.contenedor.current.get()
            # self.contenedor.loadData()
            # self.contenedor.current.set(registro)
            # Restauramos estado de los botones de contenedor buttonbar
            for wdg in self.contenedor.buttonbar.winfo_children():
                wdg['state']='normal'

            # self.contenedor.updateBar()
            self.contenedor.showdata()

    def outObservaciones(self, *args):
        ok = 1
        if self.modified:
            opciones=['Grabar','Descartar']
            mensaje ='El texto ha sido modificado y se pederán los cambios'
            ok = dlg.dialogo(self.contenedor, 'TEXTO MODIFICADO', msg=mensaje,botones=opciones, img=dlg.ADVERTENCIA).showmodal()
            if ok == 0:
                self.saveObservaciones()
            else:
                for wdg in self.contenedor.buttonbar.winfo_children():
                    wdg['state']='normal'

                self.contenedor.showdata()