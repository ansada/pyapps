from Forms import *
from tkinter import scrolledtext
import smtplib
import Dialogo
from Dialogo import dialogo

class oilmail(Form):

    def __init__(self, hcaller, name=''):
        """ Constructor: Recibe parámetro del 
            el control cuando cerremos app y e
        """
        super().__init__(hcaller, name)
        self.title("Envio de correo electronico")

        self.prop=cmvar.properties
        # Boton Grabar, Nuevo (limpiar campos) y heredado Salir de la aplicación
        self.imgsend = tk.PhotoImage(file='img/emailBW32.png')
        self.btnsend=tk.Button(self.buttonbar, image=self.imgsend, command=self.enviar)
        self.btnsend.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        self.statusbar.createTip(self.btnsend, "Enviar correo electrónico <F3>")
        self.imgnew = tk.PhotoImage(file='img/document-new.png')
        self.btnnew=tk.Button(self.buttonbar, image=self.imgnew, command=self.clearText)
        self.btnnew.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        self.statusbar.createTip(self.btnnew, "Nuevo correo / Borrar mensaje actual [F10]")
        self.bind("<F3>", self.enviar)
        self.bind("<F10>", self.clearText)

        #
        # Aquí diseñamos los widgets que se verán en forma de ficha
        self.declaraControls()
        #
        # Esto lo hago para que al pulsar TAB desde maiadm entre en el obsadm
        # directamente, sino hay que pulsar dos veces TAB
        self.pulsadaTab=False
        self.asunto.bind('<FocusOut>', lambda event:  self.porfoco(event))
        self.asunto.bind('<Tab>', self.pulsaTab)
        # 
        self.destino.focus()

    def pulsaTab(self, *args):
        # Flag para avanzar desde maiadm a obsadm
        self.pulsadaTab = True

    def porfoco(self, *args):
        # Si se ha perdido el foco desde maiadm pulsando Tab
        if self.pulsadaTab==True:
            # Enfocamos a obsadm (Sino hay que pulsar 2 veces)
            self.mensaje.focus()
            # Retiramos flag para próximavez
            self.pulsadaTab=False

    def declaraControls(self):
        # Area de contenido
        self.contenido=tk.Frame(self, pady=10, highlightbackground="black", highlightthickness=1)
        # Mostramos Etiquetas
        tk.Label(self.contenido, text="Destinatarios:").grid(row=0, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="Copia:").grid(row=1, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="Asunto:").grid(row=2, column=0, sticky=tk.E)
        tk.Label(self.contenido, text="Mensaje:").grid(row=3, column=0, sticky=tk.NE)
        
        self.destino=Textbox(self.contenido, width=100, tipo=Textbox.MINUSCULAS)
        self.destino.grid(row=0, column=1, columnspan=3, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.copia=Textbox(self.contenido, width=100, tipo=Textbox.MINUSCULAS)
        self.copia.grid(row=1, column=1, columnspan=3, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.asunto=Textbox(self.contenido, width=100)
        self.asunto.grid(row=2, column=1, columnspan=3, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.mensaje = scrolledtext.ScrolledText(self.contenido, wrap=tk.WORD, height=5)
        self.mensaje.grid(row=3,column=1, columnspan=self.contenido.grid_size()[0], 
                         sticky=tk.NSEW, ipadx=3, ipady=3, padx=3, pady=3)
        
        self.contenido.rowconfigure(3, weight=1)
        self.contenido.columnconfigure(1, weight=1)

        self.contenido.pack(fill=tk.BOTH, expand=True)

    def setMessage(self, toAddrs, subject, msg):
        # Limpiamos los posibles datos introducidos
        self.clearText()
        # Uno las direcciones mail recibidas en la lista toAddrs
        destinatarios=','.join(toAddrs)
        self.destino.insert(0,destinatarios)
        if self.copia.get()=='':
            self.copia.insert(0, self.prop.getProperty('mail'))

        self.asunto.insert(0,subject)
        self.mensaje.insert('1.0', msg)
        self.asunto.focus()

    def clearText(self, *args):
        self.destino.delete(0, tk.END)
        self.copia.delete(0, tk.END)
        self.copia.insert(0, self.prop.getProperty('mail'))
        self.asunto.delete(0, tk.END)
        self.mensaje.delete('1.0', tk.END)

    def enviar(self, *args):
        # Enviamos Correo actual
        #
        hostsmtp = self.prop.getProperty('hostsmtp')
        pasword = self.prop.getProperty('passmtp')
        usuario = self.prop.getProperty('usersmtp')
        # Campos
        # fecha=date.strftime(date.today(), '%d-%m-%Y')
        destinatarios = self.destino.get()
        if self.copia.get() != '':
            destinatarios += ','+self.copia.get()

        asunto = self.asunto.get()
        mensaje = self.mensaje.get("1.0", tk.END)
        # Procesamos e-mail
        try:
            # Iniciar el server
            server = smtplib.SMTP(host=hostsmtp, port=587)
            server.ehlo()
            server.starttls()
            server.login(user=usuario, password=pasword)

            message = 'Subject: {}\n\n{}'.format(asunto, mensaje)

            # Enviamos
            enviarA = tuple(destinatarios.split(','))
            # server.sendmail(from_addr=usuario,to_addrs=enviarA,msg=message)
            server.sendmail(from_addr=usuario,to_addrs=enviarA, msg=message.encode('utf8'))

            # Cerramos la conexion
            server.quit()

        except Exception as e:
            msg = f"Se ha producido un error {e}, {type(e)}"
            dlgerr = dialogo(self, "ERROR ENVIO MAIL", msg, ['Aceptar'], Dialogo.ERROR )
            dlgerr.showmodal()
            
    