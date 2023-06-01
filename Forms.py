import tkinter as tk
from tkinter import ttk
import CommonVar as cmvar
from DBsql import *
from Controls import *
from tkinter import scrolledtext
import pandas as pd
#
# Formularios de aplicación
# y componentes comunes - StatusBar y ButtonBar
#

class StatusBar(tk.Frame):
    """
        Barra de estado de un Form
        Devuelve un Frame que empaquetará el caller tk.BOTTOM 
        Metodos : showMensaje(Texto_A_Mostrar)
                  createTip(widget, mensaje)
    """

    def __init__(self, contenedor):
        """ Constructor: Recibe parámetro del Form que
            es el contenedor del StatusBar
        """

        super().__init__(contenedor, highlightbackground="black", highlightthickness=1)

        # Variable para texto de status
        self.msg = tk.StringVar()
        self.msg.set("Seleccione opción de trabajo")
        self.msgAnterior = self.msg.get()

        # Barra de estado. Borde esterior plano de 1 pixel
        tk.Label(self, text="Autor: A.Salas", padx=5, font=(
            "Courier", 10, "bold")).pack(side=tk.RIGHT)
        self.mensaje = tk.Label(
            self, textvariable=self.msg, anchor=tk.W, padx=10)
        self.mensaje.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.pack(side=tk.BOTTOM, fill=tk.X)

    def showMensaje(self, mensaje, fixed=False):
        # Si fixed es True, este mensaje quedará como
        # mensaje fijado cuando no haya otro que mostrar
        self.msg.set(mensaje)
        if fixed == True:
            self.msgAnterior = mensaje

    def createTip(self, widget, mensaje):
        # Enlazamos evento que al pasar el cursor del mouse por el widget
        # muestre el mensaje parámetro
        widget.bind("<Enter>", lambda event: self.onEnter(
            event, mensaje), add='+')
        widget.bind("<Leave>", self.onLeave, add='+')

    def onEnter(self, event="",  mensaje=" "):
        self.showMensaje(mensaje)
        #self.msgAnterior = self.msg.get()

    def onLeave(self, event=""):
        self.showMensaje(self.msgAnterior)


class ButtonBar(tk.Frame):
    """
        Barra Contenedora de botones de acción salir a la derecha
        Devuelve un Frame que empaquetará el caller TOP
    """

    def __init__(self, padre):
        """ Constructor: Recibe parámetro del hcaller que
            es el contenedor del ButtonBar y es 
            el Form que contiene metodo close
            y la barra de mensaje statusbar
        """
        self.padre = padre
        # Tiene un marco negro de 1 px.
        super().__init__(padre, highlightbackground="black", highlightthickness=1)
        # Boton Cerrar / salir
        if self.padre.winfo_class() == 'Tk':
            # Si el que lo llama (contiene) es Tk() imagen = Salir
            self.imgexit = tk.PhotoImage(file='img/exit32.png')
        else:
            # De otro modo la imagen es Cerrar
            self.imgexit = tk.PhotoImage(file='img/power-button32.png')

        self.btnexit = tk.Button(
            self, image=self.imgexit, command=self.toClose)
        # Declararemos un método closer que lanza evento indicando que cierra
        # el Form que lo contiene
        if self.padre.winfo_class() == 'Tk':
            # Si es Tk en la barra de estado muestra SALIR
            self.padre.statusbar.createTip(
                self.btnexit, "Cerrar Aplicaciones y Salir [ESC]")
            # El bind a ESC se entiende vendrá hecho en Tk()
        else:
            # Si no es Tk mostrará CERRAR
            # Alt-s siempre será cerrar el formulario (Excepto Tk() que es ESC)
            self.padre.statusbar.createTip(
                self.btnexit, "Cerrar Formulario [Alt-S]")
            self.padre.bind('<Alt-s>', self.toClose, add='+')
            self.padre.bind('<Alt-S>', self.toClose, add='+')

        self.btnexit.pack(side=tk.RIGHT, fill=tk.Y, padx=3, pady=3)

        # Empaquetamos el Frame buttonbar (Arriba y se extiende a lo ancho)
        self.pack(side=tk.TOP, fill=tk.X)
        # btnexit generará un evento que solicita salir llamando a el método closer
        # que será capturado por el formulario contenedor. Excepto en Tk() que lo implementamos
        # en FormBase se captura y si queremos suplantamos añadiendo el método self.closer a la
        # instancia del mismo
        self.event_add("<<closer>>", "None")

    def toClose(self, *args):
        # print("Clase del caller: " + self.hcaller.winfo_class())
        # El padre (contenedor que llama) debe implementar el metodo closer()
        self.event_generate("<<closer>>")


class Form(tk.Toplevel):
    """
        Formulario contenedor.
        Metodos:
               show: Mostrar form
               hide: Ocultar (sin destruir)
           minimize: Ocultar (mostrando en barra de ventanas abiertas)
             closer: Cerrar - Evento capturado <<closer>>
             center: Centrar en pantalla
            setIcon: Muestra icono pasado como parámetro en barra de tareas

        Componentes: statusbar
                Metodos: createTip (Muestra mensaje en barra cuando entra cursor en widget que lo declare)
                     buttonbar : Barra superior contenedora de botones. Por defecto btnExit


    """

    def __init__(self, hcaller, name=''):
        """ Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos Form
            name = Clave del diccionario con el que se ha registrado en
                   lanzador de aplicaciones
            Si es '' (modal) estará por encima de todos y esperará a cerrar
        """
        self.name = name
        self.hcaller = hcaller

        super().__init__(hcaller)
        # Todo Form base tiene una barra de status
        self.statusbar = StatusBar(self)
        # y una barra de herramientas con el boton salir.
        self.buttonbar = ButtonBar(self)

        self.protocol("WM_DELETE_WINDOW", self.closer)
        # Registro ventana abierta
        # cmvar.winopen[name] = self

        if name == '':
            # No tiene name - es modal - no registrada
            # Por encima de todas las ventanas
            self.attributes('-topmost', 'true')
            self.lift()
            # self.grab_set()
            # self.hcaller.hide()

        # Forzamos el foco a este formulario
        self.focus_force()
        self.bind("<<closer>>", self.closer)

    def center(self):
        # Centra la ventana en la pantalla
        # self.update()
        self.update_idletasks()
        # Alto de la ventana
        altoScreen = self.winfo_screenheight()
        # Anco de la ventana
        anchoScreen = self.winfo_screenwidth()
        # Alto del formulario (self)
        altoWin = int(self.winfo_height())
        # Ancho del formulario (self)
        anchoWin = int(self.winfo_width())
        # Posicionamos al 50% del ancho y al 25% de alto
        posx = int((anchoScreen - anchoWin) / 2)
        posy = int((altoScreen - altoWin) / 4)

        posicion = str(anchoWin) + "x" + str(altoWin) + \
            "+" + str(posx) + "+" + str(posy)
        self.geometry(posicion)

    def show(self):
        # Muestra el Form - Si estaba minimizado cambia a withdraw y restaura
        self.update()
        self.withdraw()
        # Lo levantamos y mostramos en pantalla (Podríamos usar lift?)
        self.deiconify()
        self.focus()

    def closer(self, *args):
        # Este método sólo esta para ser sobrecargado por la instancia de la clase
        # Si name no es '' y existe en winopen mostramos el hcaller y quitamos
        # la ventana de winopen. Si name es '' es modal y no registrada.
        if self.name != '' and self.name in cmvar.winopen:
            cmvar.winopen[self.name].hcaller.show()
            cmvar.winopen[self.name].hcaller.lift()
            del cmvar.winopen[self.name]

        self.destroy()

    def hide(self):
        # Ocultar el Form a la vista
        # no mostrándolo en la barra de tareas
        # self.withdraw() no lo mostraría en la barra (ocultaria)
        self.withdraw()

    def minimize(self):
        # Ocultar el Form a la vista
        # mostrándolo en la barra de tareas
        # self.withdraw() no lo mostraría en la barra (ocultaria)
        self.iconify()

    # Metodos
    def setIcon(self, img):
        # Pone img como icono de la ventana.
        self.iconphoto(True, tk.PhotoImage(file=img))

    def openForm(self, frmapp, name=''):
        # lambda e: self.openForm(claseForm, nombre)
        if name == '':
            # Si no tiene nombre no se registra y será modal
            # en cualquier caso
            winForm = frmapp(self)
            # y esperamos a que devuelva el control
            self.withdraw()
            self.wait_window(winForm)
            # Y volvemos a mostrar
            self.show()
            return
        else:
            # No es modal y tiene name
            # La registramos si no existe y continuamos
            if name in cmvar.winopen:
                # Si existe la ponemos en primer plano
                cmvar.winopen[name].show()
                self.iconify()
                return
            else:
                # Sino generamos la instacia y la registramos
                cmvar.winopen[name] = frmapp(self, name)
                self.iconify()


class FormView(Form):
    """
        Formulario contenedor de barra de botones para navegación
        por registros. 
        Es un Form con barra de navegación (y por tanto con statusbar)
        y buttonbar heredados de Form con botones de navegación que situan
        puntero de registro y llaman al método showdata que generara un
        evento <<cursordata>> y actualizará la barra de navegación
        desactivando o activando botones según la posición del cursor.
        Y un boton de seleccionar que genera un evento buscar.
    """

    def __init__(self, hcaller, name, strsql, con='', fieldfind=''):
        """ Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos app
            name = Clave del diccionario con el que se registra en
                   lanzador de aplicaciones
        """
        super().__init__(hcaller, name)
        #
        self.strsql = strsql
        self.con = con
        self.fieldfind = fieldfind    # Campo de busqueda en el combobox
        #
        # Variable IntVar que indica la posición indice del registro
        self.current = tk.IntVar()

        # Imagenes de los botones
        self.imgfirst = tk.PhotoImage(file='img/goFirst.png')
        self.imgprev = tk.PhotoImage(file='img/goPrevious.png')
        self.imgnext = tk.PhotoImage(file='img/goNext.png')
        self.imglast = tk.PhotoImage(file='img/goLast.png')
        self.imgfind = tk.PhotoImage(file='img/find32.png')
        # Buttons
        self.btnfirst = tk.Button(
            self.buttonbar, image=self.imgfirst, command=self.onFirst)
        self.btnprevious = tk.Button(
            self.buttonbar, image=self.imgprev, command=self.onPrevious)
        self.btnnext = tk.Button(
            self.buttonbar, image=self.imgnext, command=self.onNext)
        self.btnlast = tk.Button(
            self.buttonbar, image=self.imglast, command=self.onLast)
        self.btnfirst.pack(side=tk.LEFT, fill=tk.Y, padx=3)
        self.btnprevious.pack(side=tk.LEFT, fill=tk.Y, padx=3)
        self.btnnext.pack(side=tk.LEFT, fill=tk.Y, padx=3)
        self.btnlast.pack(side=tk.LEFT, fill=tk.Y, padx=3)
        self.btnfind = tk.Button(
            self.buttonbar, image=self.imgfind, command=self.findrecord)
        self.btnfind.pack(side=tk.LEFT, fill=tk.Y, padx=3)

        # Tips de los botones
        self.statusbar.createTip(self.btnfirst, "Primer Registro [Ini]")
        self.statusbar.createTip(
            self.btnprevious, "Registro Anterior [Pg Down]")
        self.statusbar.createTip(self.btnnext, "Siguiente Registro [Pg Up]")
        self.statusbar.createTip(self.btnlast, "Ultimo Registro [End]")
        self.statusbar.createTip(self.btnfind, "Seleccionar Registro [F5]")

        # Combo de busqueda
        self.cmbfind = ttk.Combobox(self.buttonbar, state='readonly')
        self.cmbfind.pack(side=tk.LEFT, fill=tk.BOTH,
                          padx=3, pady=6, expand=True)
        # Si no queremos combobox de busqueda lo ocultamos
        if self.fieldfind == '':
            self.cmbfind.forget()
        else:
            # Si está activado el combobox añadimos evento para situar
            self.cmbfind.bind('<<ComboboxSelected>>', self.onSeleFind)

        # Enlazamos teclado a botones (Shortcuts)
        self.bind('<Home>', self.onFirst, add='+')
        self.bind('<End>', self.onLast, add='+')
        self.bind('<Prior>', self.onPrevious, add='+')
        self.bind('<Next>', self.onNext, add='+')
        self.bind('<F5>', self.findrecord, add='+')

        # Eventos que genera y que captura (o no) la instancia
        # para movimiento del cursor
        self.event_add('<<cursordata>>', 'None')
        # o para llamar a selección de datos
        self.event_add('<<seledata>>', 'None')
        # Y finalmente cargamos los datos
        self.loadData()
        # Cargados los datos llenamos el combobox de busqueda
        if self.fieldfind != '':
            # self.cmbfind['values'] = [x for x in self.rst[self.fieldfind].sort_values()]
            listadmin = [x[self.fieldfind] for x in self.rst]
            listadmin.sort()
            self.cmbfind['values'] = listadmin

    # Metodos

    def loadData(self):
        # Carga datos
        # Consultamos DataFrame
        # self.rst = db.dfquery(self.strsql, con=self.con)
        # Consultamos Lista de Diccionarios
        self.rst = db.consultar(self.strsql, con=self.con)
        # Al cargar datos nos posicionamos en último registro
        # self.current.set(self.rst.shape[0]-1)
        self.current.set(len(self.rst)-1)
        self.showPosicion()

    def showPosicion(self):
        pos = 'Registro: ' + str(self.current.get()+1) + \
            ' de ' + str(len(self.rst))
        self.statusbar.showMensaje(pos, True)
        # Si está activo el combobox de busqueda de registro
        # mostramos el registro seleccionado
        if self.fieldfind != '':
            self.cmbfind.set(self.rst[self.current.get()][self.fieldfind])

        # Lanzamos evento
        self.event_generate('<<cursordata>>')
        self.updateBar()

    def updateBar(self):
        if self.current.get() == 0 or len(self.rst) == 0:
            self.btnfirst["state"] = 'disabled'
            self.btnprevious["state"] = 'disabled'
        else:
            self.btnfirst["state"] = 'normal'
            self.btnprevious["state"] = 'normal'

        if self.current.get() == len(self.rst)-1:
            self.btnlast["state"] = 'disabled'
            self.btnnext["state"] = 'disabled'
        else:
            self.btnlast["state"] = 'normal'
            self.btnnext["state"] = 'normal'

    # Eventos

    def findrecord(self, *args):
        self.event_generate('<<seledata>>')

    def onFirst(self, *args):
        if self.btnfirst['state'] in [tk.NORMAL, tk.ACTIVE]:
            self.current.set(0)
            self.showPosicion()
        # self.event_generate('<<cursordata>>')

    def onNext(self, *args):
        if self.btnnext['state'] in [tk.NORMAL, tk.ACTIVE]:
            if self.current.get() < (len(self.rst)-1):
                self.current.set(self.current.get()+1)
            self.showPosicion()

    def onPrevious(self, *args):
        if self.btnprevious['state'] in [tk.NORMAL, tk.ACTIVE]:
            if self.current.get() > 0:
                self.current.set(self.current.get()-1)
            self.showPosicion()

    def onLast(self, *args):
        if self.btnlast['state'] in [tk.NORMAL, tk.ACTIVE]:
            self.current.set(len(self.rst)-1)
            self.showPosicion()

    def onSeleFind(self, *args):
        idSele = self.current.get()
        # Busca el registro seleccionado en combobox
        busco = self.cmbfind.get()
        for i in range(len(self.rst)):
            if self.rst[i][self.fieldfind] == busco:
                idSele = i
                break

        self.current.set(idSele)
        # Mostrar los datos
        self.showPosicion()


class SeleData(Form):
    """
        Debería ser instanciado desde un FormData.
        Treeview para mostrar tabla de datos que
        permite seleccionar registro.
        Recibe una lista de diccionarios:
            {'titulo':'Nombre columna',
             'campo': 'Nombre del campo en el result',
             'ancho': pixeles,
             'alineacion: [RIGHT, CENTER, LEFT]
             }
        Un result (lista de diccionarios) con los datos
        Un entero - orden - que es la columna por la que se ordena

    """

    def __init__(self, hcaller, result, columnas, posicion, orden=0):
        """ Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos app
            name = Clave del diccionario con el que se ha registrado en
                   lanzador de aplicaciones
            result = Conjunto de datos (lista de diccionarios)
            columnas = lista de diccionarios con cada columna a mostrar
                {'titulo':'Movil',
                 'campo': 'movadm',
                 'ancho': 90,
                 'alineacion': E}
            posicion = Registro actualmente seleccionado (Index en result)
        """
        self.cols = columnas
        self.result = result
        self.posicion = posicion
        self.orden = orden

        super().__init__(hcaller, '')
        self.title("SELECCION DE REGISTRO")
        # Inicializamos entorno de datos
        self.titulos = []
        self.campos = []
        self.alinea = []
        self.anchos = []
        self.textofiltro = ""

        for c in self.cols:
            self.titulos.append(c['titulo'])
            self.campos.append(c['campo'])
            self.alinea.append(c['alineacion'])
            self.anchos.append(c['ancho'])

        self.tv = ttk.Treeview(self, columns=self.campos, selectmode=tk.BROWSE)
        self.tv.column('#0', width=0, stretch=tk.NO)
        anchototal = 0
        for i in range(len(self.campos)):
            anchototal += self.anchos[i]
            self.tv.column(
                self.campos[i], anchor=self.alinea[i], width=self.anchos[i])
            self.tv.heading(
                self.campos[i], text=self.titulos[i], anchor=self.alinea[i])

        self.statusbar.showMensaje("Seleccione Registro [Doble-Click]")
        # Boton Seleccionar registro actualmente seleccionado
        self.btnok = tk.Button(self.buttonbar, text="Seleccionar", pady=3, command=self.on_sele)
        self.btnok.pack(side=tk.LEFT, fill=tk.Y)
        # Combobox que muestra el orden de seleccion
        tk.Label(self.buttonbar, text='Orden: ').pack(side=tk.LEFT, fill=tk.Y)
        self.cmborden = ttk.Combobox(
            self.buttonbar, values=self.titulos, width=20, state='readonly')
        self.cmborden.pack(side=tk.LEFT, fill=tk.Y, pady=6)
        self.cmborden.current(self.orden)
        # Texto de busqueda (contenido en)
        tk.Label(self.buttonbar, text='Filtrar contenido: ').pack(
            side=tk.LEFT, fill=tk.Y)
        self.txtcontiene = Textbox(self.buttonbar, Textbox.MAYUSCULAS)
        self.txtcontiene.pack(side=tk.LEFT, fill=tk.BOTH,
                              pady=6, padx=3, expand=True)
        # Controlaremos las pulsaciones en el cuadro de texto
        # Registramos validación de las pulsaciones
        self.txtcontiene['validate'] = 'key'
        self.txtcontiene['validatecommand'] = (
            self.txtcontiene.register(self.on_filtro), '%P', '%d', '%S')

        # Barra de desplazamiento
        self.vscrlbar = tk.Scrollbar(
            self, orient="vertical", command=self.tv.yview)
        self.vscrlbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tv.configure(yscrollcommand=self.vscrlbar.set)

        self.tv.pack(fill=tk.BOTH, expand=True, pady=10)

        # self.transient(hcaller)
        self.grab_set()

        # self.tv.bind('<<TreeviewSelect>>', self.cambiaSeleccion)
        self.tv.bind("<Double-Button-1>", self.on_sele)
        # Selección desde Teclado alfabético
        self.tv.bind('<Return>', self.on_sele)
        # Selección desde Teclado numérico
        self.tv.bind('<KP_Enter>', self.on_sele)

        # self.update_idletasks
        # anchototal+=50
        # Anchura mínima para controles de busqueda/orden, etc.
        if anchototal < 850:
            anchototal = 850
        else:
            anchototal += 50

        if anchototal > self.winfo_screenwidth():
            anchototal = self.winfo_screenwidth()

        alto = int(self.winfo_screenheight()/2)
        self.geometry(str(anchototal)+'x'+str(alto))
        self.center()

        self.event_add('<<gotodata>>', 'None')

        self.cmborden.bind('<<ComboboxSelected>>', self.onSeleOrden)

        self.txtcontiene.bind('<KeyRelease>', self.loadData)
        # Cuando se pulse Enter desde txtcontiene se selecciona
        # el primero de la lista y se devuelve
        # Selección desde Teclado alfabético
        self.txtcontiene.bind('<Return>', self.on_SeleFirst)
        # Selección desde Teclado numérico
        self.txtcontiene.bind('<KP_Enter>', self.on_SeleFirst)

        self.loadData()
        # Enfocamos directamente el campo de filtrar
        self.txtcontiene.focus_set()

    #
    # Eventos y métodos
    #
    def on_SeleFirst(self, *args):
        self.tv.focus(self.tv.get_children()[0])
        self.on_sele()

    def on_sele(self, *args):
        # Fijamos la posición en la variable controladora del hcaller
        # que corresponde con el iid (focus()) cuando lo cargamos
        # self.posicion.set(int(self.tv.focus()))
        # Avisamos disparando evento gotodata (por si se ha capturado)
        # self.event_generate('<<gotodata>>')
        # self.closer()
        camposelec = self.rstorden[int(self.tv.focus())][self.campos[self.orden]]

        devolver = -1
        for i in range(len(self.result)):

            if self.result[i][self.campos[self.orden]] == camposelec:
                # Encontrado indice en el result original
                devolver = i
                break

        # Si es -1 es que no hay coincidencia
        if devolver == -1:
            print("No encontrado")
        else:
            self.posicion.set(devolver)
            # self.cmbfind.set(self.rst[reg]['empadm'])
            # if self.hcaller.fieldfind != '':
            #     self.hcaller.cmbfind.set(self.result[self.posicion.get()][self.hcaller.fieldfind])
            # Anulamos evento para que no propage en cascada si hay formularios anidados que llamen
            # a seledata 
            self.event_generate('<<gotodata>>')

        self.destroy()
        self.closer()

    def on_cancel(self, *args):

        self.closer()

    def loadData(self, *args):
        # Cadena de expresion de busqueda
        self.textofiltro = self.txtcontiene.get()
        # Limpiamos de resultados anteriores el Treeview
        self.tv.delete(*self.tv.get_children())
        self.update()
        # Cargamos los datos en el Treeview
        # Hay expresión de filtro?
        rstfiltro = list(filter(lambda x: self.textofiltro.upper() in x[self.campos[self.orden]].upper(), self.result))
        # Primero creo indice de ordenación
        self.rstorden = sorted(rstfiltro, key=lambda admin: admin[self.campos[self.orden]])
        seleccionado = self.result[self.posicion.get()][self.campos[self.orden]]

        for i in range(len(self.rstorden)):
            valores = []
            for x in self.campos:
                # Eliminamos espacios en blanco
                # Convertimos a cadena aunque no lo sea por
                # si lo que tenemos es un numero. Si era cadena devuelve la misma cadena
                valores.append(str(self.rstorden[i][x]).strip())

            self.tv.insert('', tk.END, text='', values=valores, iid=str(i))

        if self.textofiltro in seleccionado:
            for i in range(len(self.rstorden)):
                if self.rstorden[i][self.campos[self.orden]] == seleccionado:
                    self.tv.selection_add(str(i))
                    self.tv.focus(str(i))
                    self.tv.see(str(i))
                    # self.tv.focus_set()
                    break
        else:
            if len(self.tv.get_children()) > 0:
                self.tv.selection_add('0')
                self.tv.focus('0')
                self.tv.see('0')

    def onSeleOrden(self, *args):
        self.orden = self.cmborden.current()
        self.tv.delete(*self.tv.get_children())
        self.update()
        self.loadData()

    def on_filtro(self, texto, accion, caracter):
        '''
        Recarga los datos filtrando contenido
        '''
        # Aquí podemos Aceptar o no el contenido según
        # queramos aceptar caracteres...
        if accion != '1':
            # Si no es insertar lo que hacemos, aceptamos
            return True
            # Será retroceso, delete o tecla dirección
        # Actualmente sólo aceptamos la cadena que filtra por
        # contenido los registros mostrados
        self.textofiltro = self.txtcontiene.get()+caracter
        # Controlamos que haya algún registro que cumpla la condicion
        aceptado = False
        for r in self.rstorden:
            if self.textofiltro.upper() in r[self.campos[self.orden]].upper():
                aceptado = True
                # self.loadData()
                break

        return aceptado


class FormData(FormView):
    """
        Formulario contenedor de barra de botones para navegación
        por registros. (FormView)
        Añadidos botones de edición, creación nuevo registro y eliminación
    """

    def __init__(self, hcaller, name, strsql, con='', fieldfind=''):
        """ Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos app
            name = Clave del diccionario con el que se ha registrado en
                   lanzador de aplicaciones
        """
        super().__init__(hcaller, name, strsql, con, fieldfind)
        #
        # Imagenes
        self.imgnew = tk.PhotoImage(file='img/list-add32.png')
        self.imgdel = tk.PhotoImage(file='img/list-remove32.png')
        self.imgedit = tk.PhotoImage(file='img/edit32.png')
        #
        # Buttons
        self.btnnew = tk.Button(
            self.buttonbar, image=self.imgnew, command=self.addrecord)
        self.btnedit = tk.Button(
            self.buttonbar, image=self.imgedit, command=self.modifyrecord)
        self.btndel = tk.Button(
            self.buttonbar, image=self.imgdel, command=self.deleterecord)
        self.btnnew.pack(side=tk.LEFT, fill=tk.Y, padx=3)
        self.btnedit.pack(side=tk.LEFT, fill=tk.Y, padx=3)
        self.btndel.pack(side=tk.LEFT, fill=tk.Y, padx=3)
        self.statusbar.createTip(self.btnnew, "Añadir Registro [F10]")
        self.statusbar.createTip(self.btnedit, "Editar Registro [F2]")
        self.statusbar.createTip(self.btndel, "Eliminar Registro [F4]")
        # Enlazamos teclado a botones
        self.bind('<F10>', self.addrecord, add='+')
        self.bind('<F2>', self.modifyrecord, add='+')
        self.bind('<F4>', self.deleterecord, add='+')
        # Eventos de añadir, editar y eliminar registro
        self.event_add('<<newdata>>', 'None')
        self.event_add('<<editdata>>', 'None')
        self.event_add('<<deldata>>', 'None')

    # Eventos
    def addrecord(self, *args):
        # Si Comprobamos estado del Button en un futuro
        # poder controlar si activo o no al teclado.
        # Así si desactivamos Button, queda desativado atajo teclado
        # if self.btnnew['state'] == NORMAL:
        if self.btnnew['state'] in [tk.NORMAL, tk.ACTIVE]:
            self.event_generate('<<newdata>>')

    def modifyrecord(self, *args):
        if self.btnedit['state'] in [tk.NORMAL, tk.ACTIVE]:
            self.event_generate('<<editdata>>')

    def deleterecord(self, *args):
        if self.btndel['state'] in [tk.NORMAL, tk.ACTIVE]:
            self.event_generate('<<deldata>>')


class FormEdit(Form):
    '''
    Formulario para edición de registros y modificación o adición
    Inicialmente sólo aporta un control de modificación del registro
    para que no salga si se ha modificado algo sin grabar.
    Y un button que genera un evento para salvar el registro modificado
    o insertar el registro introducido.
    '''

    def __init__(self, hcaller, name=''):
        """ Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos app
            name = Clave del diccionario con el que se registra en
                   lanzador de aplicaciones
        """
        super().__init__(hcaller, name)
        #
        self.title('EDICION DE REGISTRO')

        # Imagenes de los botones
        self.imgsave = tk.PhotoImage(file='img/save32.png')
        #
        # Button
        self.btnsave = tk.Button(
            self.buttonbar, image=self.imgsave, command=self.on_Save)
        self.btnsave.pack(side=tk.LEFT, fill=tk.Y, padx=3)
        # Tips de los botones
        self.statusbar.createTip(self.btnsave, "Guardar cambios [F3]")
        self.statusbar.showMensaje(
            'Introduzca los datos del registro', fixed=True)
        # Evento que se generará al pulsar el button save o F3
        self.event_add('<<savedata>>', 'None')
        #
        self.bind('<F3>', self.on_Save)

    def on_Save(self, *args):
        # El padre (contenedor que llama) debe capturar el evento <<savedata>>
        self.event_generate("<<savedata>>")


class FrameMail(tk.Frame):
    '''
    Contenedor para adjuntar a un Form con el diseño
    para el envío de mensajes mail en texto plano.
    '''

    def __init__(self, contenedor: Form):
        """ Constructor: Recibe parámetro del Form que
            es el contenedor del Frame para enviar mails
            El contenedor será un Form con una ButtonBar y un StatusBar
        """

        super().__init__(contenedor, highlightbackground="black", highlightthickness=1)

        # Boton envíar (Cancelar será salir sin envíar)
        self.imgmail = tk.PhotoImage(file='img/emailBW32.png')
        self.btnmail = tk.Button(contenedor.buttonbar, text='Enviar', compound=tk.LEFT, 
                    image=self.imgmail, command=self.on_Send)
        self.btnmail.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        contenedor.statusbar.createTip(self.btnmail, "Enviar Correo [F3]")
        # Limpiar caja de texto del mensaje.
        self.imgclear = tk.PhotoImage(file='img/delete32.png')
        self.btnclear = tk.Button(contenedor.buttonbar, image=self.imgclear,compound=tk.LEFT,text='Borrar Texto')
        self.btnclear.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        # Mostramos controles 
        tk.Label(self, text="Destinatarios:").grid(row=0, column=0, sticky=tk.E)
        tk.Label(self, text="Asunto:").grid(row=1, column=0, sticky=tk.E)
        tk.Label(self, text="Texto del mensaje:").grid(row=2, column=0, sticky=tk.E)
        self.destino = Textbox(self,width=100,tipo=Textbox.MINUSCULAS)
        self.destino.grid(row=0, column=1, columnspan=2,sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.asunto = Textbox(self, width=100,tipo=Textbox.MAYUSCULAS)
        self.asunto.grid(row=1, column=1, sticky=tk.EW,ipadx=3, ipady=3, padx=3, pady=3)
        self.textomsg = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=10)
        self.textomsg.grid(row=3, column=0, columnspan=self.grid_size()[0],
                         sticky=tk.NSEW, ipadx=3, ipady=3, padx=3, pady=3)

        self.rowconfigure(3, weight=1)
        self.columnconfigure(1, weight=1)

        self.pack(fill=tk.BOTH, expand=True)
        self.btnclear.config(command=lambda: self.textomsg.delete('1.0',tk.END))
        # Evento que capturaremos desde el form que llama
        self.event_add('<<sendMail>>', 'None')
        # Cuando pulse F3 se enviará y lanzara evento 
        contenedor.bind('<F3>', self.on_Send)

    def on_Send(self, *args):
        # El padre (contenedor que llama) debe capturar el evento <<sendMail>>
        # si quiere hacer algo tras el envío.
        self.event_generate("<<sendMail>>")


class SeleDfData(Form):
    """
        Debería ser instanciado desde un FormView.
        Treeview para mostrar tabla de datos que
        permite seleccionar registro.
        Recibe parámetros:
        result (DataFrame) con los datos
        columnas (Lista de diccionarios) para configuración
            con el siguiente formato:
            {'titulo':'Nombre columna',
             'campo': 'Nombre del campo en el result',
             'ancho': en pixeles,
             'alineacion: [W, E]
             }
        Un entero(Intvar) - posicion que es el registro inicial al que apuntará.
            Si es < 0 no seleccionará ninguno
        Un entero - orden - que es la columna por la que se ordena inicialmente
            Por defecto será la primera columna (0)

    """

    def __init__(self, hcaller, result, columnas, posicion, orden=0, *args, **kwargs):
        """ Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos app
            name = Clave del diccionario con el que se ha registrado en
                   lanzador de aplicaciones
            result = Conjunto de datos (Dataframe)
            columnas = lista de diccionarios con cada columna a mostrar
                {'titulo':'Movil',
                 'campo': 'movadm',
                 'ancho': 90,
                 'alineacion': E}
            posicion = Registro actualmente seleccionado
        """
        self.cols = columnas
        self.result = result
        self.posicion = posicion
        self.orden = orden

        super().__init__(hcaller, '')
        # Inicializamos entorno de datos
        self.title("SELECCION DE REGISTRO")
        self.titulos = []
        self.campos = []
        self.alinea = []
        self.anchos = []
        self.textofiltro = ""

        for c in self.cols:
            self.titulos.append(c['titulo'])
            self.campos.append(c['campo'])
            self.alinea.append(c['alineacion'])
            self.anchos.append(c['ancho'])

        self.tv = ttk.Treeview(self, columns=self.campos, selectmode=tk.BROWSE)
        self.tv.column('#0', width=0, stretch=tk.NO)
        anchototal = 0
        for i in range(len(self.campos)):
            anchototal += self.anchos[i]
            # Definimos columna según el orden que hemos pasado
            # incluida alineación y ancho
            self.tv.column(
                self.campos[i], anchor=self.alinea[i], width=self.anchos[i])
            # Mostramos cabecera/Titulo de la columna
            # incluida alineación (El ancho lo hemos definido en column)
            self.tv.heading(
                self.campos[i], text=self.titulos[i], anchor=self.alinea[i])

        # Muestro mensaje - Seleccionar con doble click en el registro
        self.statusbar.showMensaje("Seleccione Registro [Doble-Click]")
        # Boton Seleccionar registro actualmente seleccionado
        self.imgok = tk.PhotoImage(file='img/accept32.png')
        self.btnok = tk.Button(
            self.buttonbar, image=self.imgok, command=self.on_sele)
        self.btnok.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        self.statusbar.createTip(
            self.btnok, "Selecciona registro activo [INTRO]")

        # Combobox que muestra el orden de seleccion
        # y que permite cambiarlo para el filtrado contenido en.
        tk.Label(self.buttonbar, text='Orden: ').pack(side=tk.LEFT, fill=tk.Y)
        # Uso como leyenda (values) los títulos de cabecera
        self.cmborden = ttk.Combobox(
            self.buttonbar, values=self.titulos, width=20, state='readonly')
        self.cmborden.pack(side=tk.LEFT, fill=tk.Y, pady=6)
        self.cmborden.current(self.orden)
        # Texto de busqueda (contenido en)
        tk.Label(self.buttonbar, text='Filtrar contenido: ').pack(
            side=tk.LEFT, fill=tk.Y)
        self.txtcontiene = Textbox(self.buttonbar, Textbox.MAYUSCULAS)
        self.txtcontiene.pack(side=tk.LEFT, fill=tk.BOTH,
                              pady=6, padx=3, expand=True)
        # Controlaremos las pulsaciones en el cuadro de texto
        # Registramos validación de las pulsaciones
        self.txtcontiene['validate'] = 'key'
        self.txtcontiene['validatecommand'] = (
            self.txtcontiene.register(self.on_filtro), '%P', '%d', '%S', '%s')

        # Barra de desplazamiento vertical
        self.vscrlbar = tk.Scrollbar(
            self, orient="vertical", command=self.tv.yview)
        self.vscrlbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tv.configure(yscrollcommand=self.vscrlbar.set)

        self.tv.pack(fill=tk.BOTH, expand=True, pady=10)

        # self.tv.bind('<<TreeviewSelect>>', self.cambiaSeleccion)
        self.tv.bind("<Double-Button-1>", self.on_sele)
        # Selección desde Teclado alfabético
        self.tv.bind('<Return>', self.on_sele)
        # Selección desde Teclado numérico
        self.tv.bind('<KP_Enter>', self.on_sele)

        # Anchura mínima para controles de busqueda/orden, etc.
        if anchototal < 850:
            anchototal = 850
        else:
            anchototal += 50

        # Si el ancho supera al de la pantalla lo limitamos
        if anchototal > self.winfo_screenwidth():
            anchototal = self.winfo_screenwidth()

        alto = int(self.winfo_screenheight()/2)
        self.geometry(str(anchototal)+'x'+str(alto))
        # self.center()

        # Evento que capturaremos desde el form que llama
        self.event_add('<<gotodata>>', 'None')
        # Cuando queremos cambiar el orden en que se muestran
        self.cmborden.bind('<<ComboboxSelected>>', self.onSeleOrden)
        # Evento cada vez que se pulsa una tecla en el texto que contiene
        self.txtcontiene.bind('<KeyRelease>', self.loadData)
        # Cargamos los datos
        self.loadData()
        # Solo prueba
        self.tv.bind('<ButtonRelease-1>', self.selectItem)

        # Hacemos que sea modal
        # Por encima de todas las ventanas
        self.grab_set()
        self.attributes('-topmost', 'true')

        # Seleccionado directamente el campo de filtrar por contenido
        self.txtcontiene.focus_set()
        # Cuando se pulse Enter desde txtcontiene se selecciona
        # el primero de la lista y se devuelve
        # Selección desde Teclado alfabético
        self.txtcontiene.bind('<Return>', self.on_SeleFirst)
        # Selección desde Teclado numérico
        self.txtcontiene.bind('<KP_Enter>', self.on_SeleFirst)

    # Sólo para prueba

    def selectItem(self, *args):
        curItem = self.tv.focus()

    def on_SeleFirst(self, *args):
        self.tv.focus(self.tv.get_children()[0])
        self.on_sele()

    def on_sele(self, *args):
        # Fijamos la posición en la variable controladora del hcaller
        # que corresponde con el iid (focus()) cuando lo cargamos
        self.posicion.set(int(self.tv.focus()))
        # Avisamos disparando evento gotodata (por si se ha capturado)
        self.event_generate('<<gotodata>>')

        self.closer()

    def on_cancel(self, *args):

        self.closer()

    def loadData(self, *args):
        # Cadena de expresion de busqueda
        self.textofiltro = self.txtcontiene.get()
        self.orden = self.cmborden.current()
        campoOrden = self.campos[self.orden]
        busco = self.txtcontiene.get()
        # Limpiamos de resultados anteriores el Treeview
        self.tv.delete(*self.tv.get_children())
        self.update()
        # Cargamos los datos en el Treeview
        # Hay expresión de filtro?
        seleccionado = self.result[self.campos[self.orden]
                                   ][self.posicion.get()]
        # DataFrame a mostrar ordenado y filtrado por contenido
        filtrado = self.result[self.result[campoOrden].str.contains(
            busco, case=False)].sort_values(by=campoOrden)
        filtrado.fillna(" ", inplace=True)
        for i in filtrado.index.tolist():
            valores = []

            for campo in self.campos:
                # Eliminamos espacios en blanco (Por si acaso)
                # Pero esto da errores porque no coincide exactamente
                # el contenido de result y el de la columna en el treeview
                # Convertimos a cadena aunque no lo sea por
                # si lo que tenemos es un numero. Si era cadena devuelve la misma cadena
                valores.append(str(filtrado.loc[i, campo]).strip())

            self.tv.insert('', tk.END, text='', values=valores, iid=i)

        # Si el texto a filtrar está contenido en el seleccionado
        # lo fijamos como actual selección
        if self.textofiltro in seleccionado:
            for i in filtrado.index.to_list():
                if filtrado[self.campos[self.orden]][i] == seleccionado:
                    self.tv.selection_add(str(i))
                    self.tv.focus(str(i))
                    self.tv.see(str(i))
                    # self.tv.focus_set()
                    break
        else:
            if len(self.tv.get_children()) > 0:
                primero = str(filtrado.index.to_list()[0])
                self.tv.selection_add(primero)
                self.tv.focus(primero)
                self.tv.see(primero)

    def onSeleOrden(self, *args):
        # Cambiamos el orden en que se muestran
        self.orden = self.cmborden.current()
        self.loadData()

    def on_filtro(self, texto, accion, caracter, txtAnterior):
        '''
        Aseguramos que hay algún registro que cumple filtro contenido
        '''
        # Aquí podemos Aceptar o no el contenido según
        # queramos aceptar caracteres...
        if accion != '1':
            # Si no es insertar lo que hacemos, aceptamos
            return True
            # Será retroceso, delete o tecla dirección
        # Actualmente sólo aceptamos la cadena que filtra por
        # contenido los registros mostrados
        # print("Texto: ", texto)
        # print("Valor asdii del caracter pulsado: ", ord(caracter))
        busco = self.txtcontiene.get() + caracter
        # print("Texto tras pulsarlo: ", busco)
        # Si el texto es igual añadido el caracter pulsado
        # el caracter pulsado no tiene representación (un acento por ejemplo)
        if texto == busco:
            return True
        #     print("Texto anterior y posterior son iguales")
        #     print("Texto ahora:", texto)
        #     print("Anterior", txtAnterior)

        self.result[self.campos[self.orden]].str.contains(busco, case=False)
        idSele = len(self.result.index[self.result[self.campos[self.orden]].str.contains(
            busco, case=False)].tolist())
        return idSele > 0
