import tkinter  as tk
from tkinter import ttk
from Forms import *
from Controls import *
from tkinter import messagebox
from Propiedades import *
import Dialogo as dlg
import os
from tkfontchooser import askfont
#from ttkwidgets.font import askfont
from tkinter import font
from tkinter import filedialog
import subprocess
import platform
import CommonVar as cmvar
from tkinter import scrolledtext
from tkinter import filedialog as fd
import string

class frmEditor(Form):
    """
        Clase de inicio de la aplicación con el nombre que lo contiene
    """

    def __init__(self, hcaller, name='', archivo=''):
        """ Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos app
        """
        super().__init__(hcaller, name)

        self.texto = ''
        self.archivo = archivo
        # Cargamos propiedades existentes en fichero de parametros
        self.prop=cmvar.properties

        if self.archivo=='':
            self.title("EDITOR DE TEXTO")
            self.iniciarEn = self.prop.getProperty("informes")
        else:
            self.title(self.archivo)
            self.iniciarEn = os.path.split(self.archivo)[0]
            with open(self.archivo, 'r') as fic:
                self.texto = fic.read()
        
        self.setIcon("img/edit32.gif")
               
        # Cargamos propiedades existentes en fichero
        self.prop=cmvar.properties
        # Boton Grabar Nuevo y Grabar como de la aplicación
        self.imgindentmore = tk.PhotoImage(file='img/indent-more.png')
        self.imgindentless = tk.PhotoImage(file='img/indent-less.png')
        self.imgsaveas = tk.PhotoImage(file='img/document-saved.png')
        self.imgnew = tk.PhotoImage(file='img/document-new.png')
        self.imgopen= tk.PhotoImage(file='img/document-open.png')
        self.imgsave = tk.PhotoImage(file='img/save32.png')
        self.btnnew=tk.Button(self.buttonbar, image=self.imgnew, command=self.on_new)
        self.btnnew.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        self.statusbar.createTip(self.btnnew, "Nuevo documento <F10>")
        self.bind("<F10>", self.on_new)
        self.btnopen=tk.Button(self.buttonbar, image=self.imgopen, command=self.on_open)
        self.btnopen.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        self.statusbar.createTip(self.btnopen, "Abrir documento <F2>")
        self.bind("<F2>", self.on_open)
        self.btnsave=tk.Button(self.buttonbar, image=self.imgsave, command=self.on_save)
        self.btnsave.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        self.statusbar.createTip(self.btnsave, "Guardar Cambios <F3>")
        self.bind("<F3>", self.on_save)
        self.btnsaveas=tk.Button(self.buttonbar, image=self.imgsaveas, command=self.on_saveas)
        self.btnsaveas.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        self.statusbar.createTip(self.btnsaveas, "Guardar Como <Mayúsculas-F3>")
        self.bind("<Shift-F3>", self.on_saveas)
        self.btnindent=tk.Button(self.buttonbar, image=self.imgindentmore, command=self.on_indent)
        self.btnindent.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        self.statusbar.createTip(self.btnindent, "Insertar margen de 1 espacio")
        self.btnunindent=tk.Button(self.buttonbar, image=self.imgindentless, command=self.on_unindent)
        self.btnunindent.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        self.statusbar.createTip(self.btnunindent, "Eliminar 1 espacio de margen")
        self.txtfont = tk.Entry(self.buttonbar, state='readonly')
        self.txtfont.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3, pady=3)
        self.imgfont = tk.PhotoImage(file='img/fontsize24.png')
        self.btnfont = tk.Button(self.buttonbar, image=self.imgfont, command=self.onbtnfontclick)
        self.btnfont.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        self.statusbar.createTip(self.btnfont, "Fuente para el texto mostrado")
        # self.listfuente=list(self.prop.getProperty("fuente").split(','))
        self.listfuente = ['Courier', '12', 'normal']

        self.changeText(self.txtfont, ','.join(self.listfuente), )
        
        #
        # Area de texto
        #
        self.areaTexto = tk.Frame(self)
        self.sctext = scrolledtext.ScrolledText(self.areaTexto, wrap=tk.WORD, height=30, font=self.listfuente)
        # self.lbltxt=tk.Label(self.areaTexto, text='Posición: ', anchor=tk.E)
        # Empaquetamos el frame con los controles 
        self.sctext.pack(side=tk.TOP, fill=tk.BOTH, expand=True, ipadx=3, ipady=3, padx=3, pady=3)
        # self.lbltxt.pack(side=tk.BOTTOM, fill=tk.X)
        self.areaTexto.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=3, pady=3)

        if self.texto != '':
            self.sctext.insert('1.0', self.texto)

        self.sctext.focus_set()

        self.sctext.bind('<Key>', lambda x: self.showPosicion(x))
        self.sctext.bind('<KP_Enter>', lambda x: self.sctext.event_generate('<Return>'))
        self.statusbar.showMensaje('Linea :{:>4} Columna: {:>3}'.format(1, 1), fixed=True)
        anchoPantalla=int(self.winfo_screenwidth()/3*2)
        altoPantalla =int(self.winfo_screenheight()/3*2)
        self.geometry(f"{anchoPantalla}x{altoPantalla}")
        self.center()
        self.modified=False
        #self.sctext.bind('<<Modified>>', self._beenModified)
        self.bind("<<closer>>", self.finEdicion)
        # Registramos validación de las pulsaciones
        self.sctext.bind('<Key>', self.antPulsado)
        self.sctext.bind('<KeyRelease>', self.postPulsado)

    # Eventos y métodos
    def antPulsado(self, evt):
        # Guarda la longitud del texto antes de mostrar la pulsacion
        self.longitudTexto=len(self.sctext.get('1.0',tk.END))
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
        if self.longitudTexto != len(self.sctext.get('1.0',tk.END)):
            self.modified=True
        
    def showPosicion(self, evt):
        lin = int(self.sctext.index(tk.INSERT).split('.')[0])
        col = int(self.sctext.index(tk.INSERT).split('.')[1])
        self.statusbar.showMensaje('Linea :{:>4} Columna: {:>3}'.format(lin, col+1), fixed=True)

    
    def on_save(self, *args):
        # Grabar los datos cambiados o no 
        if self.archivo == '':
            self.on_saveas()
        else:
            with open(self.archivo, 'w') as fic:
                fic.write(self.sctext.get('1.0',tk.END))
                dlg.dialogo(self,'GUARDADO ARCHIVO','El fichero se ha grabado',img=dlg.INFO)
                #messagebox.showinfo("GUARDAR ARCHIVO", "El fichero se ha grabado", parent=self)
                self.modified=False

        return
        
    def on_saveas(self, *args):
        # Grabar los datos cambiados o no 
        if self.archivo == '':
            # self.iniciarEn = self.prop.getProperty("informes")
            filename = 'untitled.txt'
        else:
            filename = os.path.split(self.archivo)[1]
            # self.iniciarEn = os.path.split(self.archivo)[0]

        f = fd.asksaveasfilename(initialfile = filename,
                                initialdir = self.iniciarEn,
                                defaultextension=".txt",filetypes=[("All Files","*.*"),("Text Documents","*.txt")],
                                parent=self)

        # Si no selecciona fichero, estará vacío
        if f == '':
            return
        
        self.title(f)
        with open(f, 'w') as fic:
            fic.write(self.sctext.get('1.0',tk.END))
            self.archivo = f
            self.modified=False
        return

        #messagebox.showinfo("GUARDAR COMO", "Tenemos que pedir el fichero", parent=self)
        
        # with open(self.archivo, 'w') as fic:
        #     fic.write(self.sctext.get('1.0',tk.END))
        #     messagebox.showinfo("GUARDAR COMO", "El fichero se ha grabado", parent=self)
    
    def on_open(self, *args):
        # Grabar los datos cambiados o no 
        filetypes = (('text files', '*.txt'), ('All files', '*.*'))
        
        filename = fd.askopenfilename(
                    title='Open a file',
                    filetypes=filetypes,
                    initialdir=self.iniciarEn,
                    parent=self)

        seguro = True
        #messagebox.showinfo("ABRIR", "Abriremos el fichero "+filename, parent=self)
        #if self.sctext.get('1.0', tk.END) != '':
        if self.modified:
            seguro = messagebox.askokcancel("ABRIR FICHERO", 
                                            'Esta ud. seguro, los cambios se perderan',
                                            icon=messagebox.WARNING, parent=self)
        if seguro:
            self.title(filename)
            self.sctext.delete('1.0', tk.END)
            self.archivo = filename
            self.iniciarEn = os.path.split(self.archivo)[0]
            with open(filename, 'r') as fic:
                self.sctext.insert('1.0', fic.read())
        else:
            return


    def on_new(self, *args):
        # 1º comprobar que el fichero actual está salvado
        # y avisar que se pueden perder los datos
        if self.modified == True:
            # ok = messagebox.askokcancel("NUEVO DOCUMENTO", "Esta úd. seguro?\nSe perderán los cambios en el documento actual", parent=self)
            aviso = dlg.dialogo(self, "ADVERTENCIA",
                            "Esta úd. seguro?\nSe perderán los cambios en el documento actual",
                             ['Aceptar','Cancelar'], dlg.ADVERTENCIA)
            op = aviso.showmodal()
            if op == 1:
                #if ok == tk.NO:
                return
        
        self.archivo = ''
        self.sctext.delete('1.0', tk.END)
        self.title("EDITOR DE TEXTO")
        self.modified = False

    def onbtnfontclick(self):
        # 
        # Abrimos el diálogo seleccionar fuente
        #
        self.hide()
        dfont = askfont(parent=self, font=self.listfuente)
        self.show()
        print(self.sctext['font'])
        # dfont es "" si se ha pulsado cancel
        if dfont == '':
            return

        #
        # print(dfont[0],dfont[1])
        # Cambiamos fuente en el area de texto
        self.listfuente[0] = dfont['family']
        self.listfuente[1] = dfont['size']
        self.listfuente[2] = dfont['weight']
        self.listfuente[3] = dfont['slant']
        # print(self.listfuente)
        fuente=self.listfuente[0]+','+str(self.listfuente[1]) + ',' + self.listfuente[2] + ',' + self.listfuente[3]
        print("String fuente: " + fuente)
        self.changeText(self.txtfont, fuente)
        self.sctext.configure(font=self.listfuente)
    

    def changeText(self, widget, texto):
        # Cambia texto de un widget readonly restaurandolo después
        widget['state']= tk.NORMAL
        widget.delete(0, tk.END)
        widget.insert(0, texto)
        widget['state']='readonly'

    def on_unindent(self):
        lineas = int(self.sctext.index(tk.END).split('.')[0])-1
        for i in range(lineas):
            desde = str(i+1)+'.0'
            hasta = str(i+1)+'.1'
            self.sctext.delete(desde, hasta)

    def on_indent(self):
        lineas = int(self.sctext.index(tk.END).split('.')[0])-1
        for i in range(lineas):
            desde = str(i+1)+'.0'
            self.sctext.insert(desde, ' ')
   
    def finEdicion(self, evt=None):
        if self.modified==True:
            op = dlg.dialogo(self, "ADVERTENCIA",
                            "Guardar cambios?\nSe perderán las modificaciones realizadas",
                             ['Salvar los cambios','Salir sin guardar'], dlg.ADVERTENCIA).showmodal()
            if op == 0:
                self.on_save()

        # Si name no es '' y existe en winopen mostramos el hcaller y quitamos
        # la ventana de winopen. Si name es '' es modal y no registrada.
        if self.name != '' and self.name in cmvar.winopen:
            cmvar.winopen[self.name].hcaller.show()
            cmvar.winopen[self.name].hcaller.lift()
            del cmvar.winopen[self.name]

        self.destroy()

    # def closer(self, *args):
    #     # Sobreescribimos este método para que no interfiera con otras instancias
    #     # de programas que son padres de otros forms
    #     # Cerrar este formulario
    #     # Destruimos instancia
    #     # self.hcaller.show()
    #     self.destroy()
