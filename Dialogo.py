import tkinter as tk

# Constantes imagen tipo de cuadro
NO = ''
ADVERTENCIA='img/advertencia48.png'
ERROR='img/error48.png'
PREGUNTA='img/pregunta48.png'
INFO='img/info48.png'

class dialogo(tk.Toplevel):


    def __init__(self, parent, titulo, msg, botones=['Aceptar'], img=NO):
                 
        super().__init__(parent)
        self.title(titulo)
        frameMsg=tk.Frame(self)
        tk.Label(frameMsg, text=msg, font=['Helvetica', 10, 'bold'],justify=tk.LEFT).pack(side=tk.RIGHT,
                padx=10, pady=10, fill=tk.X, expand=True)
        
        if img != '':
            self.imgdlg = tk.PhotoImage(file=img)
            tk.Label(frameMsg, image=self.imgdlg).pack(side=tk.LEFT)

        frameMsg.pack(side=tk.TOP, fill=tk.BOTH)
        # Mostramos los botones requeridos
        self.frameBtn = tk.Frame(self)
        self.frameBtn.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        # Por defecto opcion es el último boton
        self.seleccion = len(botones)-1
        btn=[]
        for i in range(len(botones)):
            btn.append(tk.Button(self.frameBtn, text=botones[i], command=lambda op=i: self.on_button(op)))
            btn[i].grid(row=5, column=i, padx=5, pady=10)
            self.frameBtn.columnconfigure(i, weight=1)

        # Hacemos esta ventana Modal
        self.attributes('-topmost', 'true')
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.resizable(height = False, width = False)
        #self.grab_set()
        self.transient(parent)
        # self.overrideredirect(True)
        self.center()
        btn[-1].focus_set()

    def on_button(self, op):
        self.seleccion=op
        self.destroy()
        
    def showmodal(self):
        self.wait_window()
        return self.seleccion
    
    def center(self):
        # Centra la ventana en la pantalla
        self.update()
        #self.update_idletasks()
        # Alto de la ventana
        altoScreen = int(self.winfo_screenheight())
        # Anco de la ventana
        anchoScreen = int(self.winfo_screenwidth())
        # Alto del formulario (self)
        altoWin = int(self.winfo_height())
        # Ancho del formulario (self)
        anchoWin = int(self.winfo_width())
        # Posicionamos al 50% del ancho y al 25% de alto
        posx = int((anchoScreen - anchoWin) / 2)
        posy = int((altoScreen - altoWin) / 2)

        posicion = str(anchoWin) + "x" + str(altoWin) + \
            "+" + str(posx) + "+" + str(posy)
        self.geometry(posicion)
