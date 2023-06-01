#!/usr/bin/env python3

import tkinter as tk
import sys
from tkinter import ttk
from tkinter import font
from DBsql import db
from Forms import *
from enDesarrollo import temporal
from Frmpar import frmpar
from OIL import oil
from FAC import fac
from GASYLUZ import gasyluz

# Ventana principal de acceso
# Program: inicio.py
#   Class: frmMain
# Date: 2022/05/10

class frmMain(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        # Titulo de ventana
        self.title("INICIO APLICACIONES")

        # Posicionamos ventana en pantalla (4/3 del ancho de pantalla)
        ancho = int((self.winfo_screenwidth() / 4 ) * 3)
        # Posicionamos en el punto al 20% del alto y 20% de ancho
        posx = int(self.winfo_screenwidth() / 8)
        posy = int(self.winfo_screenheight() / 8)
        # Composición del parámetro geometry (Altura 80 pixeles)
        self.str_posicion = str(ancho)+"x80+"+str(posx)+"+"+str(posy)
        # Ajustamos geometría de ventana en pantalla
        # guardada en str_posicion para restaurar siempre
        # que devuelve el control una aplicación
        self.geometry(self.str_posicion)
        # Fuente por defecto para widgets Tkinter
        # fuentedef = "Helvetica,12,normal,roman"
        # fuente = "Helvetica,12,normal,roman"
        # listfuente=fuente.split(',')
        fuente = cmvar.properties.getProperty("fuente","Helvetica,12,normal,roman")
        listfuente=fuente.split(',')
        #
        # Normalizamos la fuente para todos los esquemas
        # TkDefaultFont, TkTextFont, TkFixedFont, etc
        for f in font.names():
            dfuente=font.nametofont(f)
            dfuente.config(family=listfuente[0])  
            dfuente.config(size=int(listfuente[1]))
            #dfuente.config(weight=int(listfuente[2]))
            #dfuente.config(slant=listfuente[3])  
        #
        # Combobox colores estado readonly
        # Lo inicio aquí para que se aplique a partir de ahora
        self.style = ttk.Style()
        self.style.map('TCombobox', fieldbackground=[('readonly', 'white')])
        self.style.map('TCombobox', selectbackground=[('readonly', 'white')])
        self.style.map('TCombobox', selectforeground=[('readonly', 'black')])
        self.style.map('TCombobox', fieldbackground=[('focus','lightsteelblue')])
        self.style.map('TCombobox', selectbackground=[('focus', 'blue')])
        self.style.map('TCombobox', selectforeground=[('focus', 'white')])
        self.style.map('TCombobox', foreground=[('disabled', 'black')])
        self.style.map('TSpinbox', fieldbackground=[('readonly', 'white')])
        self.style.map('TSpinbox', selectbackground=[('focus', 'blue')])
        self.style.map('TSpinbox', selectforegroundd=[('readonly', 'black')])
        self.style.map('TSpinbox', selectforegroundd=[('focus', 'white')])
        # # #
        # Interceptamos evento al salir de la aplicación con la X
        # self.protocol("WM_DELETE_WINDOW", self.closer)
        # Icono que se mostrará en la barra de tareas y en barra título
        # self.call('wm', 'iconphoto', self._w, tk.PhotoImage(file='img/linked.gif'))
        icono = tk.PhotoImage(file='img/linked32.png')
        self.iconphoto(False, icono)
        # Barra de estado y mensajes / tooltip
        self.statusbar=StatusBar(self)
        # # Barra de botones de menu / opciones
        # contenedor de los enlaces
        self.buttonbar=ButtonBar(self)
        # Cargar los botones de enlace a las aplicaciones
        self.loadButtons()
        # No redimensionar el alto de la ventana
        # self.resizable(True,False)
        self.resizable(height = False, width = True)
        # master.maxsize(height, width)
        # maxh = int(self.winfo_height())
        minwidth = 0
        # Sumamos los anchos de los button
        for wdg in self.buttonbar.winfo_children():
            minwidth += int(wdg.winfo_width() + 6)
        # Añadimos 10 como margen para el mínimo ancho de ventana
        minwidth += 10
        # Si es menor que la mitad del ancho de la pantalla
        # ponemos como ancho minimo la mitad de la pantalla
        if minwidth < int(self.winfo_screenwidth() / 6 * 4):
            minwidth = int(self.winfo_screenwidth()/6*4)
        # maxw = int(self.winfo_screenwidth()/10*9)
        # Igualamos max y min para que no se pueda redimensionar
        self.maxsize(minwidth,80)
        self.minsize(minwidth,80)
        self.update()
        
        # Esc - Como pulsar Salir (Aunque lo controlamos desde Form)
        self.bind('<Escape>', self.closer)
        self.bind("<<closer>>", self.closer)

        # Mensaje por defecto en Barra de estado
        self.statusbar.showMensaje("Seleccione Aplicación u Opción", True)
        # Registro esta ventana como abierta (Será la 0)
        cmvar.winopen['Tk'] = self

    # Eventos y metodos

    def show(self):
        # Mostrar este formulario
        # 
        # Cambiamos estado porque en Linux
        # si es iconify, no lo muestra de nuevo
        # tiene que estar oculto con withdraw
        self.withdraw()
        # Lo levantamos y mostramos en pantalla
        self.deiconify()
        self.geometry(self.str_posicion)
    
    def closer(self, evt):
        # Cerrar aplicación 
        # Por seguridad cerramos todas las conexiones a datos
        db.closeall()
        # Capturamos el evento cierre que produce
        # el boton btnexit del buttonbar
        self.destroy()
        sys.exit()

    # def enConstruccion(self, *args):
    #     messagebox.showinfo("INICIO APLICACIONES", "Opción en construcción")

    def openForm(self,  frmapp, name=''):
        # lambda e: self.openForm(claseForm, nombre)
        if name == '':
            # Si no tiene nombre no se registra y será modal
            # en cualquier caso
            # Abrimos en primer plano
            winForm = frmapp(self)
            # Ocultamos esta ventana
            self.minimize()
            # y esperamos a que devuelva el control
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
                self.minimize()
                return
            else:
                # Sino generamos la instacia y la registramos
                cmvar.winopen[name] = frmapp(self, name)
                # Minimizamos porque este es punto de entrada
                self.minimize()
        
        # Ocultamos este
        # Pero esto lo hacemos aquí porque es el punto de entrada
        # En el form que llamamos, será la instancia la que oculte o no
        # el form que llama.
        self.minimize()

    def hide(self):
        # Ocultar el Form a la vista
        # mostrándolo en la barra de tareas
        # self.withdraw()
        self.withdraw()

    def minimize(self):
        # Ocultar el Form a la vista
        # mostrándolo en la barra de tareas
        # self.withdraw()
        self.iconify()

    def loadButtons(self):
        # Botones de acción para añadir a ButtonBar
        self.botones = [{'imagen':'img/settings32.png',
                        'accion':frmpar,
                        'name':'',
                        'leyenda':'Parámetros comunes a todas las aplicaciones [Alt-P]',
                        'texto':'PAR',
                        'shortCut':0,
                        'alineacion':tk.RIGHT},
                        {'imagen':'img/oilstation32.png',
                        'accion': oil.app,
                        'name':'oilapp',
                        'leyenda':'Control de pedidos y facturacion de comisiones Gasoil [Alt-O]',
                        'texto':'OIL',
                        'shortCut':0,
                        'alineacion':tk.LEFT},
                        {'imagen':'img/gasYluzICON.png',
                        'accion': gasyluz.app,
                        'name':'GASYLUZ',
                        'leyenda':'Gestión de Contratos y Comisiones de LUZ y GAS [Alt-Y]',
                        'texto':'GASYLUZ',
                        'shortCut':3,
                        'alineacion':tk.LEFT},
                        {'imagen':'img/conta32.png',
                        'accion': fac.app,
                        'name':'FAC',
                        'leyenda':'Facturación y declaracion de Ingresos y Gastos [Alt-F]',
                        'texto':'FAC',
                        'shortCut':0,
                        'alineacion':tk.LEFT},
                        {'imagen':'img/agenda32.png',
                        'accion': temporal,
                        'name':'',
                        'leyenda':'Agenda de contactos y Citas',
                        'texto':'DIA',
                        'shortCut':0,
                        'alineacion':tk.LEFT}
                        ]

        # Opciones retiradas
        # {'imagen':'img/plug32.png',
        #                 'accion': luz.app,
        #                 'name':'',
        #                 'leyenda':'Gestión de Contratos y Comisiones de Electricidad [Alt-L]',
        #                 'texto':'LUZ',
        #                 'shortCut':0,
        #                 'alineacion':tk.LEFT},
        #                 {'imagen':'img/gas32.png',
        #                 'accion': temporal,
        #                 'name':'',
        #                 'leyenda':'Gestión de Contratos y Comisiones de Electricidad [Alt-G]',
        #                 'texto':'GAS',
        #                 'shortCut':0,
        #                 'alineacion':tk.LEFT},
        # Imagenes se han de mantener para que funcione como
        # variable de clase y exista referencia en memoria
        self.imgBtns = []
        self.btns = []

        for btn in self.botones:
            self.imgBtns.append(tk.PhotoImage(file=btn['imagen']))
            self.btns.append(tk.Button(self.buttonbar, image=self.imgBtns[-1],
                            text=btn['texto'], compound=tk.LEFT, underline=btn['shortCut']))
            
            self.btns[-1].configure(command=lambda a=btn['accion'], n=btn['name']: self.openForm(a,n))
            # Letra aceleradora (atajo de teclado)
            letra=btn['texto'][btn['shortCut']]
            # Mayúscula
            atajo = '<Alt-'+letra.upper()+'>'
            self.bind(atajo, lambda e, a=btn['accion'], n=btn['name']: self.openForm(a,n))
            # Minúscula
            atajo = '<Alt-'+letra.lower()+'>'
            self.bind(atajo, lambda e, a=btn['accion'], n=btn['name']: self.openForm(a,n))
            # Empaquetamos
            self.btns[-1].pack(side=btn['alineacion'],fill=tk.Y,padx=3,pady=3)
            self.statusbar.createTip(self.btns[-1], btn['leyenda'])
    

if __name__ == '__main__':
    fmain = frmMain()
    fmain.mainloop()
