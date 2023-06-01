import tkinter  as tk
from tkinter import ttk
from Forms import *
from Controls import *
from tkinter import messagebox
from Propiedades import *
from tkfontchooser import askfont
#from ttkwidgets.font import askfont
from tkinter import font
from tkinter import filedialog
import subprocess
import platform
import CommonVar as cmvar
import os

class frmpar(Form):
    """
        Clase de inicio de la aplicación con el nombre que lo contiene
    """

    def __init__(self, hcaller, name=''):
        """ Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos app
        """
        super().__init__(hcaller, name)
        
        self.title("PARAMETROS COMUNES APLICACION")
        
        self.setIcon("img/settings32.gif")
               
        # Cargamos propiedades existentes en fichero
        self.prop=cmvar.properties
        # Boton Grabar y Salir de la aplicación
        self.imgsave = tk.PhotoImage(file='img/save32.png')
        self.btnsave=tk.Button(self.buttonbar, image=self.imgsave, command=self.on_save)
        self.btnsave.pack(side=tk.RIGHT, fill=tk.Y, padx=3, pady=3)
        self.statusbar.createTip(self.btnsave, "Guardar parámetros <F3>")
        self.bind("<F3>", self.on_save)
        #
        # Form de captura de datos (Formulario)
        #
        self.formulario = tk.Frame(self)
        tk.Label(self.formulario, text="Titular:").grid(row=0, column=0, sticky=tk.E)
        tk.Label(self.formulario, text="DNI:").grid(row=0, column=3, sticky=tk.E)
        tk.Label(self.formulario, text="Dirección:").grid(row=1, column=0, sticky=tk.E)
        tk.Label(self.formulario, text="Distrito:").grid(row=1, column=3, sticky=tk.E)
        tk.Label(self.formulario, text="Población:").grid(row=2,column=0, sticky=tk.E)
        tk.Label(self.formulario, text="Provincia:").grid(row=2, column=3, sticky=tk.E)
        tk.Label(self.formulario, text="Teléfonos:").grid(row=3, column=0, sticky=tk.E)
        tk.Label(self.formulario, text="Mail:").grid(row=3, column=3, sticky=tk.E)
        tk.Label(self.formulario, text="Fuente:").grid(row=4, column=0, sticky=tk.E)
        tk.Label(self.formulario, text="Host Datos:").grid(row=5, column=0, sticky=tk.E)
        tk.Label(self.formulario, text="Impresora por defecto").grid(row=5, column=4)
        tk.Label(self.formulario, text="Directorio Informes:").grid(row=6, column=0, sticky=tk.E)
        tk.Label(self.formulario, text="Usuario SMTP:").grid(row=7, column=0, sticky=tk.E)
        tk.Label(self.formulario, text="Host SMTP:").grid(row=7, column=3, sticky=tk.E)
        tk.Label(self.formulario, text="Password:").grid(row=8, column=0, sticky=tk.E)
        
        # Entradas de texto - Entry / Textbox
        self.txttitular=Textbox(self.formulario, tipo=Textbox.MAYUSCULAS, width=40)
        self.txttitular.grid(row=0, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtdni=Textbox(self.formulario, tipo=Textbox.MAYUSCULAS, width=9)
        self.txtdni.grid(row=0, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtdireccion=Textbox(self.formulario, width=40)
        self.txtdireccion.grid(row=1, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtdistrito=Numbox(self.formulario, decimales=2, width=5)
        self.txtdistrito.grid(row=1, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtpoblacion=Textbox(self.formulario, width=20)
        self.txtpoblacion.grid(row=2, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtprovincia=Textbox(self.formulario, tipo=Textbox.MAYUSCULAS, width=20)
        self.txtprovincia.grid(row=2, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttlf1 = Numbox(self.formulario, width=9)
        self.txttlf1.grid(row=3, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttlf2 = Numbox(self.formulario, width=9)
        self.txttlf2.grid(row=3, column=2, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtemail = Textbox(self.formulario, tipo=Textbox.MINUSCULAS, width=30)
        self.txtemail.grid(row=3, column=4, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtfont = tk.Entry(self.formulario, takefocus=0)
        self.txtfont.grid(row=4, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.imgfont = tk.PhotoImage(file='img/fontsize24.png')
        self.btnfont = tk.Button(self.formulario, image=self.imgfont, command=self.onbtnfontclick)
        self.btnfont.grid(row=4, column=3, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.statusbar.createTip(self.btnfont, "Fuente por defecto para la aplicación")
        self.txthost = tk.Entry(self.formulario, takefocus=0)
        self.txthost.grid(row=5, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.imghost = tk.PhotoImage(file='img/folder24.png')
        self.btnhost = tk.Button(self.formulario, image=self.imghost, command=self.onbtnhostclick)
        self.btnhost.grid(row=5, column=3, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.statusbar.createTip(self.btnhost, "Seleccione carpeta que actua como host para Sqlite3")
        self.txtinfor = tk.Entry(self.formulario, takefocus=0)
        self.txtinfor.grid(row=6, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.btninfor = tk.Button(self.formulario, image=self.imghost, command=self.onbtninforclick)
        self.btninfor.grid(row=6, column=3, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.statusbar.createTip(self.btninfor, "Seleccione carpeta donde grabar informes")
        plataforma = platform.system()
        impresoras = []
        #impresoras disponibles en el sistema
        if plataforma == 'Linux':
            output = subprocess.run(["lpstat","-e"], stdout=subprocess.PIPE)
            for impre in output.stdout.decode('utf-8').split('\n'):
                if len(impre) > 0:      # Si esta vacía no 
                    impresoras.append(impre) 
                else:
                    impresoras.append("DISPOSITIVO NO DETECTADO")

        elif plataforma == "Windows":
            import win32print
            imprenames = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
            if len(imprenames) == 0:
                impresoras.append("DISPOSITIVO NO DETECTADO")
            else:
                for impre in imprenames:
                    # print(impre[0], impre[1])
                    impresoras.append(impre[1]) 

        else:
            impresoras.append('PLATAFORMA DESCONOCIDA')


        self.cmbprint=ttk.Combobox(self.formulario, state="readonly", values=impresoras)

        self.cmbprint.grid(row=6, column=4, sticky=tk.EW)
        self.cmbprint.current(0)
        # Servidor de correo electronico
        self.txtuser=tk.Entry(self.formulario)
        self.txtuser.grid(row=7, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtsmtp=tk.Entry(self.formulario)
        self.txtsmtp.grid(row=7, column=4, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtpass=tk.Entry(self.formulario)
        self.txtpass.grid(row=8, column=1, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        
        self.formulario.grid_columnconfigure(2, weight=1)
        self.formulario.grid_columnconfigure(4, weight=1)

        # Empaquetamos el frame con los controles 
        self.formulario.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        self.registraFocus()
        # Mostramos los datos que han sido cargados
        self.mostrarDatos()
        self.txttitular.focus_set()
        # Como sale bien en pantalla no lo centramos
        # self.center()
        # Hacemos que sea el form superior hasta que se cierre
        # y no acepte eventos en otros formularios
        self.grab_set()
        # y siempre se muestre encima de todas
        self.attributes('-topmost', 'true')

        
    def registraFocus(self):
        # Al entrar y salir de botones capturamos evento foco
        for w in self.formulario.winfo_children():
            if w.winfo_class() == 'Entry':
                w.bind("<FocusIn>", self.onFocusIn)
                w.bind("<FocusOut>", self.onFocusOut)


    def onFocusIn(self, event):
        # Al recibir el foco cambia color de fondo y letra
        #event.widget["foreground"]="white"
        event.widget["background"]="sky blue"


    def onFocusOut(self, event):
        # Al perder el foco restauramos
        event.widget["background"]="white"
        #event.widget["foreground"]="black"


    def onbtnfontclick(self):
        # 
        # Abrimos el diálogo seleccionar fuente
        #
        self.hide()
        dfont = askfont(parent=self, font=font.nametofont('TkDefaultFont').actual())
        self.show()
        # dfont es "" si se ha pulsado cancel
        if dfont:
            # Cambiamos fuente en los parámetros
            fuente = dfont["family"] + "," + str(dfont["size"]) + "," + dfont["weight"] + "," + dfont["slant"]
            self.changeText(self.txtfont, fuente)


    def onbtnhostclick(self):
        # Impedir carpetas ocultas
        try:
            try:
                self.tk.call('tk_getOpenFile' , '-foobarbaz')
            except TclError:
                pass
        
            self.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
            self.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
        except:
            pass
        # 
        # Abrir la carpeta que hace las funciones de Host de datos Sqlite3
        #
        iniciar = self.txthost.get()
        folder_selected = filedialog.askdirectory(parent=self.btnhost, initialdir = iniciar, title = "SELECCIONE HOST DATOS")
        # Si pulsa cancelar será "" o False.
        if folder_selected:
            # Cambiamos dirección en parámetros
            self.changeText(self.txthost, folder_selected)
    

    def onbtninforclick(self):
        # Evento selector de carpeta de informes - impresión
        # Impedir carpetas ocultas
        try:
            try:
                self.tk.call('tk_getOpenFile' , '-foobarbaz')
            except TclError:
                pass
                # No mostrar directorios ocultos
            self.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
            self.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
        except:
            pass
        # -------------------------------------
        # Abrir carpeta depósito de los informes
        iniciar = self.txtinfor.get()
        folder_selected = filedialog.askdirectory(parent=self, initialdir = iniciar, title = "SELECCIONE DIRECTORIO DE INFORMES")
        # Si no pulsa cancel ("" o False)
        if folder_selected:
            # Cambiamos en los parámetros la carpeta seleccionada
            self.changeText(self.txtinfor, folder_selected)
            

    def changeText(self, widget, texto):
        # Cambia texto de un widget readonly restaurandolo después
        widget['state']= tk.NORMAL
        widget.delete(0, tk.END)
        widget.insert(0, texto)
        widget['state']='readonly'


    def mostrarDatos(self):
        
        for w in [self.txthost, self.txtinfor, self.txtfont]:
            w["state"] = tk.NORMAL

        self.txttitular.insert(0, self.prop.getProperty("titular", "ANTONIO SALAS"))    
        self.txtdireccion.insert(0, self.prop.getProperty("direccion"))
        self.txtdni.insert(0, self.prop.getProperty("dni"))
        self.txtdistrito.insert(0, self.prop.getProperty("distrito"))
        self.txtpoblacion.insert(0, self.prop.getProperty('poblacion', 'Zaragoza'))
        self.txtprovincia.insert(0, self.prop.getProperty('provincia', 'ZARAGOZA'))
        self.txttlf1.insert(0, self.prop.getProperty("telefono1"))
        self.txttlf2.insert(0,self.prop.getProperty('telefono2'))
        self.txtemail.insert(0, self.prop.getProperty("mail"))
        self.txtfont.insert(0, self.prop.getProperty("fuente", "Helvetica,12,normal,roman"))

        self.txthost.insert(0, self.prop.getProperty("host", os.getenv("HOME")))
        self.txtinfor.insert(0,self.prop.getProperty("informes", os.getenv("HOME")))
        self.txtsmtp.insert(0, self.prop.getProperty("hostsmtp", "smtp.gmail.com"))
        self.txtpass.insert(0, self.prop.getProperty("passmtp", " "))
        self.txtuser.insert(0, self.prop.getProperty("usersmtp", " "))
        
        defaultprint=self.prop.getProperty("impresora", " ")

        if defaultprint == " ":
            self.cmbprint.current(0)
        else:
            for n in range(len(self.cmbprint["values"])):
                if self.cmbprint["values"][n] == defaultprint:
                    self.cmbprint.current(n)
                    break
        
        # Devolvemos los estados readonly a txthost, txtinfor, txtfont
        for w in [self.txthost, self.txtinfor, self.txtfont]:
            w["state"] = 'readonly'

            
    def on_save(self, *args):
        # Grabar los datos cambiados o no 
        lastfont = self.prop.getProperty("fuente", "Helvetica,12,normal,roman")
        # 
        self.prop.setProperty('titular', self.txttitular.get())
        self.prop.setProperty('dni', self.txtdni.get())
        self.prop.setProperty('direccion', self.txtdireccion.get())
        self.prop.setProperty('distrito', self.txtdistrito.get())
        self.prop.setProperty('poblacion', self.txtpoblacion.get())
        self.prop.setProperty('provincia', self.txtprovincia.get())
        self.prop.setProperty('telefono1', self.txttlf1.get())
        self.prop.setProperty('telefono2', self.txttlf2.get())
        self.prop.setProperty('mail', self.txtemail.get())
        self.prop.setProperty('fuente', self.txtfont.get())
        self.prop.setProperty('host', self.txthost.get())
        self.prop.setProperty('informes', self.txtinfor.get())
        self.prop.setProperty('impresora', self.cmbprint.get())
        self.prop.setProperty('hostsmtp', self.txtsmtp.get())
        self.prop.setProperty('passmtp', self.txtpass.get())
        self.prop.setProperty('usersmtp', self.txtuser.get())
        
        self.prop.saveProperties()
        messagebox.showinfo("Paràmetros", "Guardados datos modificados", parent=self)
        # Si la fuente ha sido cambiada, volvemos a restaurarlas en
        # todos los esquemas
        if lastfont != self.prop.getProperty("fuente"):
            listfuente=self.prop.getProperty("fuente").split(',')
            for f in font.names():
                dfuente=font.nametofont(f)
                dfuente.config(family=listfuente[0])  
                dfuente.config(size=int(listfuente[1]))
                dfuente.config(weight=listfuente[2])          
                dfuente.config(slant=listfuente[3])
                
        # Si se ha grabado salimos finalizando
        # del cmvar.winopen[self.name]
        self.destroy()
        
    def closer(self, *args):
        # Sobreescribimos este método para que no interfiera con otras instancias
        # de programas que son padres de otros forms
        # Cerrar este formulario
        # Destruimos instancia
        # self.hcaller.show()
        self.destroy()