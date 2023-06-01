import tkinter as tk
from tkinter import ttk
import datetime, time
from datetime import timedelta
from Propiedades import *
from DBsql import *
from Controls import *
from Forms import *
from tkcalendar import DateEntry
from tkinter import Scrollbar
import Dialogo as dlg
from tkinter import messagebox
import string

class contrato(FormData):
    """
        Formulario Contrato de suministro

    """

    def __init__(self, hcaller, name="", tipo='L'):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
        """
        # Por defecto añadimos propiedad tipo de contrato Luz
        self.tipo = tipo
        # Otro tipo (GAS), modificar en init
        # Carga de contratos segun tipo
        self.strsql = "SELECT * FROM contratos WHERE tipcon = '{}'".format(self.tipo)
        self.cnn="GYL"
        
        super().__init__(hcaller, name, self.strsql, self.cnn, '')
        

        self.title("CONTRATO DE SUMINISTRO")
        #
        # Aquí diseñamos los widgets que se verán en forma de ficha
        # Implementaremos en cada clase que herede de contrato
        # bien sea de luz o de gas
        self.declaraControls()
        #
        # Icono que aparece en ventana minimizada (Barra de tareas)
        self.setIcon('img/editArea32.png')

        # Ponernos a la escucha de eventos generados por Buttons de Buttonbar
        
        self.bind('<<cursordata>>', self.showdata)
        if self.current.get() >= 0:
            self.showdata()

        if len(self.rst) == 0:
            # Como está vacío, ¿Insertar registro?
            ok = dlg.dialogo(self, 'NO EXISTEN DATOS', 'Insertar registro en Base de Datos?',['Aceptar','Cancelar'], dlg.ADVERTENCIA).showmodal()
        
            if ok == 0:
                self.on_btnnew()

        self.bind('<<seledata>>', self.seledata)
        # self.bind('<<editdata>>', self.on_btnedit)
        self.bind('<<newdata>>', self.on_btnnew)
        self.bind('<F6>', self.cabecera.verContratosTit)
        self.bind('<F9>', self.cabecera.verContratosGes)
        self.bind('<<deldata>>', self.on_btndel)
        # Solo para modificar comentarios al contrato
        self.bind('<Alt-E>', self.observa.editaObservaciones)
        self.bind('<Alt-e>', self.observa.editaObservaciones)

    def seledata(self, *args):
        actualcontrato=int(self.cabecera.txtid.get())
        frmsele = SeleCon(self, idcon=actualcontrato, tipo=self.tipo)
        contrato=frmsele.showModal()
        self.show()
        # buscamos y cambiamos el current
        for i in range(len(self.rst)):
            if self.rst[i]['id']==contrato:
                self.current.set(i)
                self.showdata()
                break
       

    def declaraControls(self):
        # Esto por defecto, pero sobreescribimos el método en
        # la clase contratoluz y contratogas
        # Generamos cabecera de contrato
        self.cabecera=frmCab(self)
        # Detalles del punto de suministro
        self.detalle=frmDetalle(self)
        # Observaciones al contrato
        self.observa=frmAnota(self)

    def showdata(self,*args):
        registro = self.rst[self.current.get()]
        self.cabecera.showdatos(registro)
        self.detalle.showdatos(registro)
        self.observa.showdatos(registro)
        self.updateBar()

    def showfield(self, w, valor):
        w['state']='normal'
        w.delete(0,tk.END)
        w.insert(0, valor)
        w['state']='readonly'

    def on_btnnew(self, *args):
        # Antes de solicitar alta había
        numContratos=len(self.rst)
        actualContrato=self.current.get()
        # 
        frmNew = newContrato(self, self.tipo)
        self.withdraw()
        self.wait_window(frmNew)
        self.show()
        self.loadData()
        # Si al volver hay los mismos es que no lo
        # hemos creado. Si hay más el último es el 
        # nuevo contrato
        if len(self.rst) > numContratos:
            # Posicionamos el current en el último
            self.current.set(len(self.rst)-1)
        else:
            # Mantenemos el mismo registro
            self.current.set(actualContrato)

        self.showdata()
        # Levantamos la ventana a primer level
        # por alguna razón nos la deja en minimizado
        self.lift()

    def botonSave(self):
        self.imgsave = tk.PhotoImage(file='img/save32.png')
        self.btnsave = tk.Button(self.buttonbar, image=self.imgsave)
        self.btnsave.pack(side=tk.RIGHT, fill=tk.Y, padx=3)
        self.statusbar.createTip(self.btnsave, "Grabar los cambios [F3]")

    def on_btndel(self, *args):
        # Si es un contrato ya facturado no podemos borrarlo
        # daremos opcion de registrar baja por cambio de comercializador
        contrato=self.rst[self.current.get()]['id']
        if self.rst[self.current.get()]['percon']>0:
            strmsg=f'El contrato {contrato} ya ha sido incluido en registro de facturación\nde comisiones.\n'
            strmsg+="¿Desea registrar baja del contrato?"
            ok=dlg.dialogo(self,'EL CONTRATO TIENE DEPENDENCIAS', strmsg,['REGISTRAR BAJA','CANCELAR ACCION'],dlg.ADVERTENCIA).showmodal()
            if ok == 0:
                messagebox.showinfo("Registro baja", "registraremos baja y modificaremos estado", parent=self)
            else:
                return
        else:  
            strsql = f'DELETE FROM contratos WHERE id={contrato}'
            db.actualiza(strsql, con=self.cnn)
            strsql = f'DELETE FROM modificaciones WHERE conmod={contrato}'
            db.actualiza(strsql, con=self.cnn)
            messagebox.showinfo("ELIMINADO CONTRATO","Eliminado el contrato de la base de datos", parent=self)
            self.loadData()
        
        return
            
        

class contratoluz(contrato):
    """
        Formulario Contrato de suministro electrico

    """

    def __init__(self, hcaller, name=""):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
        """
        self.hcaller = hcaller

        super().__init__(self.hcaller, name, tipo='L')
        
        self.title("CONTRATO DE SUMINISTRO DE ELECTRICIDAD")
        self.bind('<<editdata>>', self.on_btnedit)
        

    def on_btnedit(self, *args):
        # Contrato activo
        numcon = self.rst[self.current.get()]['id']
        modifica = dlg.dialogo(self, "MODIFICACION DE CONTRATO",
                               "Que tipo de modificación realizar?",
                               ['Titular','Tarifa/Precio','Renovación','Potencia','Cancelar'],dlg.PREGUNTA).showmodal()
        
        if modifica == 0:
            frmmod=FrmModifica(self,numcon,modifica)
            self.wait_window(frmmod)
            dlg.dialogo(self, "MODIFICACION SE HABRA REALIZADO",
                               "Cambio de titular",
                               img=dlg.PREGUNTA).showmodal()
        elif modifica == 1:
            print('Tarifa Precio')
        elif modifica == 2:
            print('Renovacion')
            # self.detalle.setEditable()
        else:
            return
    

class contratogas(contrato):
    """
        Formulario Contrato de suministro de GAS

    """

    def __init__(self, hcaller, name=""):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
        """
        self.hcaller = hcaller
        super().__init__(self.hcaller, name, tipo='G')

        self.title("CONTRATO DE SUMINISTRO DE GAS")

    # Sobreescribimos

    # def on_btnnew(self):
    #     # Metodo sobreescrito
    #     msg = dlg.dialogo(self, 'DESDE contrato GAS', 'Seleccionado insertar Contrato de GAS',img=dlg.INFO)
    #     opcion = msg.showmodal()
    #     print(opcion)

class frmCab(tk.Frame):
    '''
        Frame que acoge a 3 frames de cabecera de contratos
    '''

    def __init__(self, contenedor):
        # Referenciamos metodo que muestra los campos
        self.showfield = contenedor.showfield
        self.contenedor = contenedor
        # Iniciamos clase padre
        super().__init__(contenedor)
        # Cabecera con el id - fecha - CUPS de contrato
        frmID = tk.Frame(self)
        tk.Label(frmID, text='Num.Contrato:').grid(row=0, column=0, columnspan=2, sticky=tk.E)
        tk.Label(frmID, text='Fecha:').grid(row=1, column=1, sticky=tk.E)
        tk.Label(frmID, text='CUPS:').grid(row=2, column=0, sticky=tk.E)

        self.txtid=tk.Entry(frmID, width=8)
        self.txtid.grid(row=0, column=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        # Valor inicial (nada) = 0 Por si editamos observacion sin haber un contrato seleccionado
        self.txtid.insert(0,'0')        
        self.txtfec=tk.Entry(frmID, width=8)
        self.txtfec.grid(row=1, column=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtcups=tk.Entry(frmID, width=22)
        self.txtcups.grid(row=2,column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        frmID.pack(side=tk.LEFT)
        # Cabecera con el titular y sus datos
        frmTIT = tk.Frame(self)
        tk.Label(frmTIT, text='Titular:').grid(row=0, column=0, sticky=tk.E)
        self.imgbusca=tk.PhotoImage(file='img/find32.png')
        btnvercontit=tk.Button(frmTIT, image=self.imgbusca, takefocus=0, command=self.verContratosTit)
        contenedor.statusbar.createTip(btnvercontit, "Ver contratos de este titular [F6]")
        btnvercontit.grid(row=0, column=2)
        tk.Label(frmTIT, text='Contacto:').grid(row=1, column=0, sticky=tk.E)
        tk.Label(frmTIT, text='Direccion:').grid(row=2, column=0, sticky=tk.E)
        self.cmbtit = ttk.Combobox(frmTIT, width=30, state='disabled')
        # self.cmbtit=tk.Entry(frmTIT, width=30)
        self.cmbtit.grid(row=0, column=1, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtnif=tk.Entry(frmTIT, width=9)
        self.txtnif.grid(row=0, column=3, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtcontit=tk.Entry(frmTIT, width=30)
        self.txtcontit.grid(row=1, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttf1tit=tk.Entry(frmTIT, width=9)
        self.txttf1tit.grid(row=1, column=3, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtdirtit=tk.Entry(frmTIT, width=9)
        self.txtdirtit.grid(row=2, column=1, columnspan=2,sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttf2tit=tk.Entry(frmTIT, width=9)
        self.txttf2tit.grid(row=2, column=3, ipadx=3, ipady=3, padx=3, pady=3)
        frmTIT.columnconfigure(1, weight=1)
        frmTIT.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Cabecera datos de gestor
        frmGES = tk.Frame(self)
        tk.Label(frmGES, text="GESTOR",bg='seashell4',fg='white').grid(row=0, column=0, columnspan=2, sticky=tk.EW)
        btnverconges=tk.Button(frmGES, image=self.imgbusca, takefocus=0,command=self.verContratosGes)
        contenedor.statusbar.createTip(btnverconges, "Ver contratos asignados a este gestor [F9]")
        btnverconges.grid(row=0, column=2, sticky=tk.E)
        self.txtnomges=tk.Entry(frmGES, width=30)
        self.txtnomges.grid(row=1, column=0, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttf1ges=tk.Entry(frmGES, width=9)
        self.txttf1ges.grid(row=1, column=1,columnspan=2,sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtconges=tk.Entry(frmGES, width=30)
        self.txtconges.grid(row=2, column=0, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttf2ges=tk.Entry(frmGES, width=9)
        self.txttf2ges.grid(row=2, column=1,columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        frmGES.pack(side=tk.RIGHT)
        # Empaquetamos la clase (Frame) en el contenedor que lo ha instanciado
        self.pack(side=tk.TOP, fill=tk.X)
        # Separador por debajo de area de detalle
        tk.Frame(contenedor, background='black', height=1).pack(side=tk.TOP, fill=tk.X)
        self.loadAuxiliares()
        self.cmbtit.bind('<<ComboboxSelected>>', self.changeTit)

    def verContratosTit(self, *args):
        actualcontrato=int(self.txtid.get())
        frmsele = SeleCon(self.contenedor, idcon=actualcontrato, tipo=self.contenedor.tipo, filtro='CLI', numfiltro=self.rsttit['id'])
        contrato=frmsele.showModal()
        self.contenedor.show()
        # buscamos y cambiamos el current
        for i in range(len(self.contenedor.rst)):
            if self.contenedor.rst[i]['id']==contrato:
                self.contenedor.current.set(i)
                self.contenedor.showdata()
                break

    def verContratosGes(self, *args):
        actualcontrato=int(self.txtid.get())
        frmsele = SeleCon(self.contenedor, idcon=actualcontrato, tipo=self.contenedor.tipo, filtro='GES', numfiltro=self.rsttit['gescli'])
        contrato=frmsele.showModal()
        self.contenedor.show()
        # buscamos y cambiamos el current
        for i in range(len(self.contenedor.rst)):
            if self.contenedor.rst[i]['id']==contrato:
                self.contenedor.current.set(i)
                self.contenedor.showdata()
                break

    def showdatos(self, rst):
        # Mostrar los datos del result recibido como parámetro
        self.showfield(self.txtid, str(rst['id']))
        # mostrar()
        # getattr(getattr(self.contenedor,'hcaller'), 'showfield')(self.txtid, str(rst['id']))
        #getattr(self.contenedor, 'hcaller').getattr(showfield(self.txtid, str(rst['id']))
        fecha = datetime.datetime.strptime(rst['feccon'][:10],'%Y-%m-%d').date().strftime('%d-%m-%y')
        self.showfield(self.txtfec, fecha)
        self.showfield(self.txtcups, rst['cupcon'])
        # Datos titular
        self.rsttit = db.consultar('SELECT * FROM clientes WHERE id={}'.format(rst['clicon']))[0]
        # Doy por sentado que existe el cliente
        self.showfield(self.txtnif, self.rsttit['nifcli'])
        self.cmbtit['state']='readonly'
        self.cmbtit.set(self.rsttit['nomcli'])
        self.cmbtit['state']='disable'
        self.showfield(self.txtcontit, self.rsttit['concli'])
        self.showfield(self.txtdirtit, self.rsttit['dircli'])
        self.showfield(self.txttf1tit, self.rsttit['tf1cli'])
        self.showfield(self.txttf2tit, self.rsttit['tf2cli'])
        # Datos gestor
        rstges = db.consultar('SELECT * FROM gestores WHERE id={}'.format(self.rsttit['gescli']))[0]
        # Doy por sentado que existe el cliente
        self.showfield(self.txtnomges, rstges['nomges'])
        self.showfield(self.txtconges, rstges['conges'])
        self.showfield(self.txttf1ges, rstges['tf1ges'])
        self.showfield(self.txttf2ges, rstges['tf2ges'])

    def loadAuxiliares(self):
        auxtit=db.consultar('SELECT * FROM clientes ORDER BY nomcli')
        listitular = [x['nomcli'] for x in auxtit]
        self.cmbtit['values'] = listitular
        self.cmbtit.set(listitular[-1])
    
    def changeTit(self, *args):
        sTitular = self.cmbtit.get()
        # Datos titular
        rsttit = db.consultar("SELECT * FROM clientes WHERE nomcli='{}'".format(sTitular))[0]
        # Doy por sentado que existe el cliente
        self.showfield(self.txtnif, rsttit['nifcli'])
        # self.showfield(self.txttit, rsttit['nomcli'])
        self.showfield(self.txtcontit, rsttit['concli'])
        self.showfield(self.txtdirtit, rsttit['dircli'])
        self.showfield(self.txttf1tit, rsttit['tf1cli'])
        self.showfield(self.txttf2tit, rsttit['tf2cli'])
        # Datos gestor
        rstges = db.consultar('SELECT * FROM gestores WHERE id={}'.format(rsttit['gescli']))[0]
        # Doy por sentado que existe el cliente
        self.showfield(self.txtnomges, rstges['nomges'])
        self.showfield(self.txtconges, rstges['conges'])
        self.showfield(self.txttf1ges, rstges['tf1ges'])
        self.showfield(self.txttf2ges, rstges['tf2ges'])


class frmDetalle(tk.Frame):
    '''
        Frame que acoge a 2 frames: frmsum (punto de suministro)
                                    frmmod (Treeview de las modificaciones) 
    '''

    def __init__(self, contenedor):
        # Referenciamos metodo que muestra los campos
        self.showfield = contenedor.showfield
        self.contenedor= contenedor
        # Iniciamos clase padre
        super().__init__(contenedor)
        # 
        frmsum = tk.Frame(self)
        tk.Label(frmsum, text='PUNTO DE SUMINISTRO ELECTRICO',bg='seashell4',fg='white').grid(row=0, column=0, columnspan=3, sticky=tk.EW)
        tk.Label(frmsum, text='Tarifa:').grid(row=0, column=3, sticky=tk.E)
        self.cmbtfa = ttk.Combobox(frmsum, width=20, state='disabled')
        # self.txttfa=tk.Entry(frmsum, width=20)
        self.cmbtfa.grid(row=0, column=4, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtatr=tk.Entry(frmsum, width=6, takefocus=0)
        self.txtatr.grid(row=0, column=6, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(frmsum, text='Dirección:').grid(row=1, column=0, sticky=tk.E)
        self.txtdirsum=tk.Entry(frmsum, width=30)
        self.txtdirsum.grid(row=1, column=1,columnspan=4, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(frmsum, text='DP:').grid(row=1, column=5, sticky=tk.E)
        self.txtdpsum=tk.Entry(frmsum, width=5)
        self.txtdpsum.grid(row=1, column=6,sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(frmsum, text='Población:').grid(row=2, column=0, sticky=tk.E)
        self.txtpobsum=tk.Entry(frmsum, width=20)
        self.txtpobsum.grid(row=2, column=1,columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(frmsum, text='Provincia:').grid(row=2, column=3, sticky=tk.E)
        self.txtprvsum=tk.Entry(frmsum, width=20)
        self.txtprvsum.grid(row=2, column=4,columnspan=3, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(frmsum, text='Comisión:').grid(row=3, column=0, sticky=tk.E)
        self.txtcms=tk.Entry(frmsum, width=8, justify=tk.RIGHT )
        self.txtcms.grid(row=3, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(frmsum, text='Mes devengo:').grid(row=3, column=2,columnspan=2, sticky=tk.E)
        self.txtmes=tk.Entry(frmsum, width=3, justify=tk.RIGHT)
        self.txtmes.grid(row=3, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(frmsum, text='Ult.Fact.:').grid(row=3, column=5, sticky=tk.E)
        self.txtper=tk.Entry(frmsum, width=4, justify=tk.RIGHT, takefocus=0)
        self.txtper.grid(row=3, column=6, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        if self.contenedor.tipo=='L':
            tk.Label(frmsum, text='Potencia P1').grid(row=4, column=0, sticky=tk.E)
            self.txtp1=tk.Entry(frmsum, width=6, justify=tk.RIGHT)
            self.txtp1.grid(row=4, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(frmsum, text='P2').grid(row=4, column=2, sticky=tk.E)
            self.txtp2=tk.Entry(frmsum, width=6, justify=tk.RIGHT)
            self.txtp2.grid(row=4, column=3, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(frmsum, text='P3').grid(row=4, column=5, sticky=tk.E)
            self.txtp3=tk.Entry(frmsum, width=6, justify=tk.RIGHT)
            self.txtp3.grid(row=4, column=6, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(frmsum, text='P4').grid(row=5, column=0, sticky=tk.E)
            self.txtp4=tk.Entry(frmsum, width=6, justify=tk.RIGHT)
            self.txtp4.grid(row=5, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(frmsum, text='P5').grid(row=5, column=2, sticky=tk.E)
            self.txtp5=tk.Entry(frmsum, width=6, justify=tk.RIGHT)
            self.txtp5.grid(row=5, column=3, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(frmsum, text='P6').grid(row=5, column=5, sticky=tk.E)
            self.txtp6=tk.Entry(frmsum, width=6, justify=tk.RIGHT)
            self.txtp6.grid(row=5, column=6, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        else:
            tk.Label(frmsum, text='Consumo Anual KW:').grid(row=4, column=0, sticky=tk.E)
            self.txtcon=tk.Entry(frmsum, width=8, justify=tk.RIGHT)
            self.txtcon.grid(row=4, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(frmsum, text='Precio pactado fijo:').grid(row=5, column=0, sticky=tk.E)
            self.txtpf1=tk.Entry(frmsum, width=8, justify=tk.RIGHT)
            self.txtpf1.grid(row=5, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)

        frmmod = tk.Frame(self)
        tk.Label(frmmod, text='MODIFICACIONES AL CONTRATO',bg='seashell4',fg='white').pack(side=tk.TOP,fill=tk.X)
        campos=['fecmod','tipmod','codtfa','destfa']
        # titulos=['FECHA','TIPO','ATR','TARIFA']
        self.tvmod=ttk.Treeview(frmmod, selectmode=tk.BROWSE, columns=campos)
        self.tvmod.column('#0', width=0, stretch=tk.NO)
        self.tvmod.column('fecmod', anchor=tk.W, width=60)
        self.tvmod.column('tipmod', anchor=tk.W, width=50)
        self.tvmod.column('codtfa', anchor=tk.W, width=40)
        self.tvmod.column('destfa', anchor=tk.W, width=110)
        self.tvmod.heading('fecmod', text='FECHA', anchor=tk.W)
        self.tvmod.heading('tipmod', text='TIPO', anchor=tk.W)
        self.tvmod.heading('codtfa', text='ATR', anchor=tk.W)
        self.tvmod.heading('destfa', text='TARIFA', anchor=tk.W)
        
        # Barra de desplazamiento por si es necesaria
        self.vscrlbar = Scrollbar(self, orient="vertical", command=self.tvmod.yview)
        self.vscrlbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tvmod.configure(yscrollcommand=self.vscrlbar.set)
        self.tvmod.pack(side=tk.BOTTOM, fill=tk.BOTH,expand=True, pady=10)
        # Empaquetamos dentro de frmdetalle (que es esta clase)
        frmsum.pack(side=tk.LEFT, fill=tk.BOTH)
        frmmod.pack(side=tk.RIGHT,fill=tk.BOTH,expand=True)
        # Empaquetamos la clase (Frame) en el contenedor que lo ha instanciado
        self.pack(side=tk.TOP,fill=tk.X)
        self.loadAuxiliares()
        self.cmbtfa.bind('<<ComboboxSelected>>', self.changeTfa)

    def showdatos(self, rst):
        # Mostrar los datos del result recibido como parámetro
        self.showfield(self.txtdirsum, str(rst['dircon']))
        self.showfield(self.txtdpsum, str(rst['discon']))
        self.showfield(self.txtpobsum, str(rst['pobcon']))
        self.showfield(self.txtprvsum, str(rst['prvcon']))
        comision=rst['cmscon']
        self.showfield(self.txtcms, f'{comision:6.2f}')
        self.showfield(self.txtmes, str(rst['mescon']))
        self.showfield(self.txtper, str(rst['percon']))

        if self.contenedor.tipo=='L':
            self.showfield(self.txtp1, f'{rst["pt1con"]}')
            self.showfield(self.txtp2, f'{rst["pt2con"]}')
            self.showfield(self.txtp3, f'{rst["pt3con"]}')
            self.showfield(self.txtp4, f'{rst["pt4con"]}')
            self.showfield(self.txtp5, f'{rst["pt5con"]}')
            self.showfield(self.txtp6, f'{rst["pt6con"]}')

        if self.contenedor.tipo=='G':
            self.showfield(self.txtpf1, f'{rst["pt1con"]:6.2f}')
            self.showfield(self.txtcon, f'{rst["concon"]}')
        
        # Datos tarifa
        rsttfa = db.consultar('SELECT * FROM tarifas WHERE id={}'.format(rst['tfacon']))[0]
        #
        self.cmbtfa['state']='readonly'
        self.cmbtfa.set(rsttfa['destfa'])
        self.cmbtfa['state']='disable'
        self.showfield(self.txtatr, rsttfa['codtfa'])
        # Modificaciones de contrato si existen
        strmod='SELECT * FROM  vselemod WHERE conmod={}'.format(rst['id'])
        rstmod = db.consultar(strmod, con=self.contenedor.cnn)
        self.tvmod.delete(*self.tvmod.get_children())
        if len(rstmod)==0:
            # No hay modificaciones al contrato
            return
        else:
            for modif in rstmod:
                fechamod=datetime.datetime.strptime(modif['fecmod'], '%Y-%m-%d %H:%M:%S').date().strftime('%d-%m-%y')
                valores=[fechamod,modif['tipmod'],modif['codtfa'],modif['destfa']]
                self.tvmod.insert('', tk.END, text='', values=valores)

    def loadAuxiliares(self):
        auxtfa=db.consultar('SELECT * FROM tarifas WHERE tiptfa="L" ORDER BY destfa')
        listfa = [x['destfa'] for x in auxtfa]
        self.cmbtfa['values'] = listfa
        self.cmbtfa.set(listfa[-1])
    
    def changeTfa(self, *args):
        sTfa = self.cmbtfa.get()
        # Datos titular
        rsttfa = db.consultar("SELECT * FROM tarifas WHERE destfa='{}'".format(sTfa))[0]
        # 
        self.showfield(self.txtatr, rsttfa['codtfa'])
    

class frmAnota(tk.Frame):
    '''
        Frame que acoge a 2 frames: frmsum (punto de suministro)
                                    frmmod (Treeview de las modificaciones) 
    '''

    def __init__(self, contenedor):
        # Iniciamos clase padre
        super().__init__(contenedor)
        
        # Referencia al contrato contenedor que llama
        self.contenedor = contenedor
        # Nº de contrato que estamos tratando. 0 = No hay contratos
        self.contrato = 0
        # Conexión a datos del contenedor (que llama)
        self.con = contenedor.cnn
        # Estado de los comentarios
        self.modified = False
        cabObs = tk.Frame(self)
        self.imgAnota=tk.PhotoImage(file='img/edit32.png')
        btneditobs=tk.Button(cabObs, image=self.imgAnota, takefocus=0, command=lambda: self.editaObservaciones(self.contrato))
        contenedor.statusbar.createTip(btneditobs, "Editar observaciones al contrato [ALT-E]")
        btneditobs.grid(row=0, column=0, sticky=tk.W)
        self.imgsaveanota=tk.PhotoImage(file='img/save32.png')
        btnsaveobs=tk.Button(cabObs, image=self.imgsaveanota, takefocus=0, command=self.saveObservaciones)
        contenedor.statusbar.createTip(btnsaveobs, "Guardar modificaciones [ALT-G]")
        btnsaveobs.grid(row=0, column=1, sticky=tk.W)
        tk.Label(cabObs, text='OBSERVACIONES AL CONTRATO',bg='seashell4',fg='white').grid(row=0, column=2, sticky=tk.EW)
        self.estado = tk.Label(cabObs, text="ACTIVO", width=10)
        self.estado.grid(row=0, column=5, sticky=tk.E)
        cabObs.grid(row=0, column=0, sticky=tk.EW)
        cabObs.columnconfigure(2, weight=1)
        self.obscon = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=5)
        self.obscon.grid(row=2,column=0, columnspan=self.grid_size()[0], 
                         sticky=tk.NSEW, ipadx=3, ipady=3, padx=3, pady=3)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        
        self.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        # Separador del area de detalle
        tk.Frame(contenedor, background='black', height=1).pack(side=tk.BOTTOM, fill=tk.X)
        # Al pulsar INTRO en teclado numerico es como ENTER en teclado alfabetico
        self.obscon.bind('<KP_Enter>', lambda x: self.obscon.event_generate('<Return>'))
        # self.obscon.bind('<Control-2>', self.editaObservaciones)
        # Capturamos evento de editar observaciones desde el form contenedor
        # self.contenedor.bind('<Alt-E>', self.editaObservaciones)
        # self.contenedor.bind('<Alt-e>', self.editaObservaciones)
        self.obscon.bind('<FocusOut>', self.outObservaciones)
        self.obscon.bind('<Alt-G>', self.saveObservaciones)
        self.obscon.bind('<Alt-g>', self.saveObservaciones)
        # Registramos validación de las pulsaciones
        self.obscon.bind('<Key>', self.antPulsado)
        self.obscon.bind('<KeyRelease>', self.postPulsado)

    # Eventos y métodos
    def antPulsado(self, evt):
        # Guarda la longitud del texto antes de mostrar la pulsacion
        self.longitudTexto=len(self.obscon.get('1.0',tk.END))
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
        if self.longitudTexto != len(self.obscon.get('1.0',tk.END)):
            self.modified=True

    def showdatos(self, rst):
        # Mostrar el string recibido en campo observaciones
        self.obscon['state'] = 'normal'
        self.obscon.delete('1.0', tk.END)
        self.obscon.insert('1.0', rst['obscon'])
        self.obscon['state'] = 'disabled'
        # Guardamos el numero de contrato que significará que
        # estamos editando un contrato existente, sino será 0
        self.contrato = rst['id']
        # Longitud del texto actual
        self.longitudTexto=len(self.obscon.get('1.0',tk.END))
        # Mostramos estado del contrato
        if rst['stdcon']==True:
            self.estado.config(bg='white', text='ACTIVO')
            # self.estado['text']="ACTIVO"
        else:
            self.estado.config(bg='red', text='INACTIVO')
            #self.estado['text']="INACTIVO"

    def editaObservaciones(self, *args):
        #self.contrato = int(self.txtcontrato.get())
        self.contrato = int(self.contenedor.cabecera.txtid.get())
        if self.contrato==0:
            return
        
        self.obscon.focus_set()
        self.obscon['state']='normal'
        # Posicionamos el cursor al final
        self.obscon.mark_set('insert',self.obscon.index('%s-1c'%tk.END))
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
            strmodifica='UPDATE contratos SET obscon="{}" WHERE id={}'.format(self.obscon.get('1.0',tk.END),self.contrato)
            db.actualiza(strmodifica, con=self.con)
            self.obscon['state'] = 'disabled'
            self.modified = False
            # Guardamos el cambio en el result del contenedor
            self.contenedor.rst[self.contenedor.current.get()]['obscon'] = self.obscon.get('1.0',tk.END)
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


class newContrato(Form):
    '''
        Nuevo contrato - Solo captura los datos de cabecera:
        NUMERO DE CONTRATO, CUPS Y FECHA
    '''
    def __init__(self, hcaller, tipo):
        # Tipo L - Luz
        # Tipo G - Gas
        self.hcaller = hcaller
        self.tipo = tipo
        self.cnn = self.hcaller.cnn

        super().__init__(self.hcaller, '')

        if self.tipo == 'L':
            self.title("NUEVO CONTRATO DE SUMINISTRO DE ELECTRICIDAD")
        else:
            self.title("NUEVO CONTRATO DE SUMINISTRO DE GAS")

        self.showfield = hcaller.showfield

        # Boton de grabar
        self.imgsave = tk.PhotoImage(file='img/save32.png')
        self.btnsave = tk.Button(
            self.buttonbar, image=self.imgsave, command=self.on_Save)
        self.btnsave.pack(side=tk.LEFT, fill=tk.Y, padx=3)
        # Tips de los botones
        self.statusbar.createTip(self.btnsave, "Grabar datos nuevo contrato [F3]")
        self.statusbar.showMensaje(
            'Introduzca los datos de cabecera del contrato', fixed=True)
        # Evento que se generará al pulsar el button save o F3
        self.bind('<F3>', self.on_Save)
        # Hace de contenedor de Frames en cabecera
        self.frmCAB = tk.Frame(self)
        # Cabecera con el id - fecha - CUPS de contrato
        frmID = tk.Frame(self.frmCAB)
        tk.Label(frmID, text='Num.Contrato:').grid(row=0, column=0, columnspan=2, sticky=tk.E)
        tk.Label(frmID, text='Fecha:').grid(row=1, column=1, sticky=tk.E)
        tk.Label(frmID, text='CUPS:').grid(row=2, column=0, sticky=tk.E)

        self.txtid=Numbox(frmID, width=8)
        self.txtid.grid(row=0, column=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtfec=DateEntry(frmID, date_pattern='dd-MM-yyyy')
        self.txtfec.grid(row=1, column=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtcups=Textbox(frmID, width=22, tipo=Textbox.MAYUSCULAS)
        self.txtcups.grid(row=2,column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        frmID.pack(side=tk.LEFT)
        # Cabecera con el titular y sus datos
        frmTIT = tk.Frame(self.frmCAB)
        tk.Label(frmTIT, text='Titular:').grid(row=0, column=0, sticky=tk.E)
        self.imgbusca=tk.PhotoImage(file='img/find32.png')
        btnsearchtit=tk.Button(frmTIT, image=self.imgbusca, takefocus=0, command=self.seleTit)
        self.statusbar.createTip(btnsearchtit, "Busqueda de Titular [F6]")
        btnsearchtit.grid(row=0, column=2)
        tk.Label(frmTIT, text='Contacto:').grid(row=1, column=0, sticky=tk.E)
        tk.Label(frmTIT, text='Direccion:').grid(row=2, column=0, sticky=tk.E)
        self.cmbtit = ttk.Combobox(frmTIT, width=30, state='readonly')
        self.cmbtit.grid(row=0, column=1, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtnif=tk.Entry(frmTIT, width=9, takefocus=0)
        self.txtnif.grid(row=0, column=3, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtcontit=tk.Entry(frmTIT, width=30, takefocus=0)
        self.txtcontit.grid(row=1, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttf1tit=tk.Entry(frmTIT, width=9, takefocus=0)
        self.txttf1tit.grid(row=1, column=3, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtdirtit=tk.Entry(frmTIT, width=9, takefocus=0)
        self.txtdirtit.grid(row=2, column=1, columnspan=2,sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttf2tit=tk.Entry(frmTIT, width=9, takefocus=0)
        self.txttf2tit.grid(row=2, column=3, ipadx=3, ipady=3, padx=3, pady=3)
        frmTIT.columnconfigure(1, weight=1)
        frmTIT.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Cabecera datos de gestor
        frmGES = tk.Frame(self.frmCAB)
        tk.Label(frmGES, text="GESTOR",bg='seashell4',fg='white').grid(row=0, column=0, columnspan=3, sticky=tk.EW,ipadx=3, ipady=3, padx=3, pady=3)
        self.txtnomges=tk.Entry(frmGES, width=30, takefocus=0)
        self.txtnomges.grid(row=1, column=0, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttf1ges=tk.Entry(frmGES, width=9, takefocus=0)
        self.txttf1ges.grid(row=1, column=1,columnspan=2,sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtconges=tk.Entry(frmGES, width=30, takefocus=0)
        self.txtconges.grid(row=2, column=0, ipadx=3, ipady=3, padx=3, pady=3)
        self.txttf2ges=tk.Entry(frmGES, width=9, takefocus=0)
        self.txttf2ges.grid(row=2, column=1,columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        frmGES.pack(side=tk.RIGHT)
        # Empaquetamos frmCab arriba
        self.frmCAB.pack(side=tk.TOP, fill=tk.X)
        # Empaquetamos la clase (Frame) en el contenedor que lo ha instanciado
        # self.pack(side=tk.TOP, fill=tk.X)
        # Separador por debajo de area de detalle
        tk.Frame(self, background='black', height=1).pack(side=tk.TOP, fill=tk.X)
        # Mostramos area de detalle basada en el tipo de contrato
        self.detalle()
 
        self.loadAuxiliares()
        self.changeTit()
        self.cmbtit.bind('<<ComboboxSelected>>', self.changeTit)
        self.cmbtfa.bind('<<ComboboxSelected>>', self.changeTfa)
        self.bind('<F6>', self.seleTit)
        self.center()
        self.txtid.focus_set()
        
        self.txtid.bind('<FocusOut>', self.validaId)
        self.txtcups.bind('<FocusOut>', self.validaCUPS)

    def detalle(self):
        # Datos del punto de suministro y condiciones economicas
        self.frmsum = tk.Frame(self)
        # Titulamos sección según tipo de alta de suministro LUZ o GAS
        if self.tipo=='L':
            tk.Label(self.frmsum, text='PUNTO DE SUMINISTRO ELECTRICO',bg='seashell4',fg='white').grid(row=0, column=0, columnspan=3, sticky=tk.EW)
        else:
            tk.Label(self.frmsum, text='PUNTO DE SUMINISTRO DE GAS',bg='seashell4',fg='white').grid(row=0, column=0, columnspan=3, sticky=tk.EW)

        # Estos son controles comunes
        tk.Label(self.frmsum, text='Tarifa:').grid(row=0, column=3, sticky=tk.E)
        self.cmbtfa = ttk.Combobox(self.frmsum, width=20, state='readonly')
        self.cmbtfa.grid(row=0, column=4, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtatr=tk.Entry(self.frmsum, width=6, takefocus=0)
        self.txtatr.grid(row=0, column=6, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmsum, text='Dirección:').grid(row=1, column=0, sticky=tk.E)
        self.txtdirsum=Textbox(self.frmsum, width=40, tipo=Textbox.TITLE)
        self.txtdirsum.grid(row=1, column=1,columnspan=4, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmsum, text='DP:').grid(row=1, column=5, sticky=tk.E)
        self.txtdpsum=Numbox(self.frmsum, width=5)
        self.txtdpsum.grid(row=1, column=6,sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmsum, text='Población:').grid(row=2, column=0, sticky=tk.E)
        self.txtpobsum=Textbox(self.frmsum, width=30, tipo=Textbox.TITLE)
        self.txtpobsum.set_texto("Zaragoza")
        self.txtpobsum.grid(row=2, column=1,columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmsum, text='Provincia:').grid(row=2, column=3, sticky=tk.E)
        self.txtprvsum=Textbox(self.frmsum, width=30, tipo=Textbox.MAYUSCULAS)
        self.txtpobsum.set_texto("ZARAGOZA")
        self.txtprvsum.grid(row=2, column=4,columnspan=3, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmsum, text='Comisión:').grid(row=3, column=0, sticky=tk.E)
        self.txtcms=Numbox(self.frmsum, width=8, decimales=2)
        self.txtcms.grid(row=3, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmsum, text='Mes devengo:').grid(row=3, column=2,columnspan=2, sticky=tk.E)
        self.txtmes=ttk.Spinbox(self.frmsum, from_=1, to=12, increment=1, state='readonly', width=2, wrap=True)
        self.txtmes.grid(row=3, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.txtmes.set(datetime.date.today().month)
        # tk.Label(self.frmsum, text='Ult.Fact.:').grid(row=3, column=5, sticky=tk.E)
        # self.txtper=tk.Entry(self.frmsum, width=4, justify=tk.RIGHT, takefocus=0)
        # self.txtper.grid(row=3, column=6, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        # Para la LUZ son potencias:
        if self.tipo=='L':
            tk.Label(self.frmsum, text='Potencia P1').grid(row=4, column=0, sticky=tk.E)
            self.txtp1=Numbox(self.frmsum, width=6, decimales=2)
            self.txtp1.grid(row=4, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(self.frmsum, text='P2').grid(row=4, column=2, sticky=tk.E)
            self.txtp2=Numbox(self.frmsum, width=6, decimales=2)
            self.txtp2.grid(row=4, column=3, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(self.frmsum, text='P3').grid(row=4, column=5, sticky=tk.E)
            self.txtp3=Numbox(self.frmsum, width=6, decimales=2)
            self.txtp3.grid(row=4, column=6, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(self.frmsum, text='P4').grid(row=5, column=0, sticky=tk.E)
            self.txtp4=Numbox(self.frmsum, width=6, decimales=2)
            self.txtp4.grid(row=5, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(self.frmsum, text='P5').grid(row=5, column=2, sticky=tk.E)
            self.txtp5=Numbox(self.frmsum, width=6, decimales=2)
            self.txtp5.grid(row=5, column=3, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(self.frmsum, text='P6').grid(row=5, column=5, sticky=tk.E)
            self.txtp6=Numbox(self.frmsum, width=6, decimales=2)
            self.txtp6.grid(row=5, column=6, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        else:
            tk.Label(self.frmsum, text='Consumo Anual KW:').grid(row=4, column=0, sticky=tk.E)
            self.txtcon=Numbox(self.frmsum, width=8,text='0')
            self.txtcon.grid(row=4, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(self.frmsum, text='Precio pactado fijo:').grid(row=5, column=0, sticky=tk.E)
            self.txtp1=Numbox(self.frmsum, width=8, decimales=6)
            self.txtp1.grid(row=5, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)

        # También es comun
        tk.Label(self.frmsum, text="OBSERVACIONES AL CONTRATO",bg='seashell4',fg='white').grid(row=0, column=7, sticky=tk.EW)
        self.obscon = scrolledtext.ScrolledText(self.frmsum, wrap=tk.WORD,height=10)
        self.obscon.grid(row=1,column=7, rowspan=6, sticky=tk.NSEW, ipadx=3, ipady=3, padx=3, pady=3)
        self.frmsum.rowconfigure(6, weight=1)
        self.frmsum.columnconfigure(7, weight=1)
        self.frmsum.pack(side=tk.TOP,fill=tk.BOTH, expand=True)
        if self.tipo=='L':
            numericos=[self.txtp1,self.txtp2,self.txtp3,self.txtp4,self.txtp5,self.txtp6,self.txtcms]
            for ctrl in numericos:
                    ctrl.set_value(0)
                    ctrl['state']='normal'
        else:
            self.txtp1.set_value(0)
            self.txtp1['state']='normal'

    def loadAuxiliares(self):
        # Titulares
        auxtit=db.consultar('SELECT * FROM clientes ORDER BY nomcli',con=self.cnn)
        listitular = [x['nomcli'] for x in auxtit]
        self.cmbtit['values'] = listitular
        self.cmbtit.set(listitular[-1])
        # Tarifas
        auxtfa=db.consultar("SELECT * FROM tarifas WHERE tiptfa='{}' AND stdtfa={} ORDER BY destfa".format(self.tipo,True),con=self.cnn)
        listarifa = [x['destfa'] for x in auxtfa]
        self.cmbtfa['values']=listarifa
        self.cmbtfa.set(listarifa[0])
        self.changeTfa()

    def changeTit(self, *args):
        # Si la direccion del punto de suministro es igual que la del titular
        # la actualizaremos al cambiar
        # cambiar = True if self.txtdirsum.get()=='' or self.txtdirsum.get()==self.txtdirtit.get() else False
        cambiar = True
        sTitular = self.cmbtit.get()
        # Datos titular
        rsttit = db.consultar("SELECT * FROM clientes WHERE nomcli='{}'".format(sTitular), con=self.cnn)[0]
        # Doy por sentado que existe el cliente
        self.showfield(self.txtnif, rsttit['nifcli'])
        # self.showfield(self.txttit, rsttit['nomcli'])
        self.showfield(self.txtcontit, rsttit['concli'])
        self.showfield(self.txtdirtit, rsttit['dircli'])
        self.showfield(self.txttf1tit, rsttit['tf1cli'])
        self.showfield(self.txttf2tit, rsttit['tf2cli'])
        # Datos gestor
        rstges = db.consultar('SELECT * FROM gestores WHERE id={}'.format(rsttit['gescli']))[0]
        # Doy por sentado que existe el cliente
        self.showfield(self.txtnomges, rstges['nomges'])
        self.showfield(self.txtconges, rstges['conges'])
        self.showfield(self.txttf1ges, rstges['tf1ges'])
        self.showfield(self.txttf2ges, rstges['tf2ges'])
        if cambiar:
            self.showfield(self.txtdirsum,rsttit['dircli'])
            self.showfield(self.txtdpsum, rsttit['discli'])
            self.showfield(self.txtpobsum,rsttit['pobcli'])
            self.showfield(self.txtprvsum,rsttit['prvcli'])
            # restaurar estado editable
            txt=[self.txtdirsum,self.txtdpsum,self.txtpobsum,self.txtprvsum]
            for ctrl in txt:
                ctrl['state']='normal'
            
        self.cmbtfa.focus_set()
    
    def changeTfa(self, *args):
        sTfa = self.cmbtfa.get()
        # Datos titular
        rsttfa = db.consultar("SELECT * FROM tarifas WHERE destfa='{}'".format(sTfa),con=self.cnn)[0]
        # 
        self.showfield(self.txtatr, rsttfa['codtfa'])

    def seleTit(self, *args):
        # Por si acaso compruebo que haya un numero de contrato y sea valido(no exista)
        if self.txtid.get() == '':
            return
        else:
            self.validaId()

        if self.txtcups.get() == '':
            self.txtcups.focus_set()
            strmsg = 'Necesario indicar el CUPS.'
            dlg.dialogo(self,'ERROR', strmsg, ['Aceptar'], dlg.ADVERTENCIA)
            return

        # Cargamos result de los clientes para elegir
        rstcli = db.consultar('SELECT * FROM clientes ORDER BY nomcli', con=self.cnn)
        # Variable que en que nos devuelve la posición en el result
        currentcli=tk.IntVar()
        # Por defecto apunta al último
        currentcli.set(len(rstcli)-1)

        for i in range(len(rstcli)):
            if rstcli[i]['nomcli']==self.cmbtit.get():
                currentcli.set(i)

        frmsele = SeleData(self,
                           rstcli,
                           [ {'titulo':'Cliente',
                              'campo': 'nomcli',
                              'ancho': 300,
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
                              'alineacion': tk.W},
                              {'titulo':'Telef 1',
                              'campo': 'tf1cli',
                              'ancho': 100,
                              'alineacion': tk.E},
                              {'titulo':'Telef 2',
                              'campo': 'tf2cli',
                              'ancho': 100,
                              'alineacion': tk.E}], currentcli, 0)
        
        self.withdraw()
        # Esperamos a que devuelva el control
        self.wait_window(frmsele)
        # Y volvemos a mostrar
        self.show()
        # Actualizamos el cliente devuelto
        self.cmbtit.set(rstcli[currentcli.get()]['nomcli'])
        self.changeTit()

    def on_Save(self, *args):
        if self.txtid.get() == '' or self.txtcups.get()=='':
            strmsg = 'Debe indicar un numero de contrato no existente\ny/o un CUPS válido'
            dlg.dialogo(self,'ERROR', strmsg, ['Aceptar'], dlg.ERROR).showmodal()
            return
        else:
            strsql = "INSERT INTO contratos "
            strsql += "(id,tipcon,feccon,clicon,cupcon,dircon,discon,pobcon,prvcon,tfacon,cmscon,mescon,percon,pt1con"
            if self.tipo =='L': # Para electrcidad - potencias
                strsql += ",pt2con,pt3con,pt4con,pt5con,pt6con"
            else: # Quiere decir que es GAS - precio fijo y consumo unicamente
                strsql += ",concon"

            strsql += ",stdcon,obscon)"
            #fechacon=self.txtfec.get_date()
            fecha = self.txtfec.get_date().strftime('%Y-%m-%d 00:00:00')
            cliente = self.getIdTitular()
            tarifa = self.getIdTarifa()
            listaFields=[int(self.txtid.get()),self.tipo,fecha,cliente, self.txtcups.get(),self.txtdirsum.get(),
                         self.txtdpsum.get(),self.txtpobsum.get(),self.txtprvsum.get(),tarifa,self.txtcms.get_value(),
                         int(self.txtmes.get()),0,self.txtp1.get_value()]
            if self.tipo == 'L':
                listaFields.extend([self.txtp2.get_value(),self.txtp3.get_value(),self.txtp4.get_value(),self.txtp5.get_value(),self.txtp6.get_value()])
            else: 
                listaFields.append(self.txtcon.get())
            
            listaFields.extend([1,self.obscon.get('1.0',tk.END)])
            # Ahora incluimos marcas de formato apropiadas
            strsql +=" VALUES ({},'{}','{}',{},'{}','{}','{}','{}','{}',{},{},{},{},{},"
            if self.tipo == 'L':
                strsql +="{},"*5
            else:
                strsql +="{},"
            
            # Finalizamos con los 2 últimos campos comunes
            strsql += "{},'{}')"

        db.actualiza(strsql=strsql.format(*listaFields), con=self.cnn)
        # Ahora insertar modificacion ALTA en registro de modificaciones de contrato
        strsql = "INSERT INTO modificaciones(fecmod,tipmod,conmod,climod,cupmod,tfamod,cmsmod,mesmod,obsmod)"
        strsql+=" VALUES('{}','ALTA',{},{},'{}',{},{},{},'{}')"
        obs=""
        if self.tipo=='G':
            obs = "Consumo: " + self.txtcon.get() 
            if self.txtp1.get_value() > 0:
                obs +=  " a precio fijo " + self.txtp1.get()

        if self.tipo=='L':
            obs = "Potencias:\n"
            pot=[self.txtp1,self.txtp2,self.txtp3,self.txtp4,self.txtp5,self.txtp6]
            for z in range(len(pot)):
                obs+="P"+str(z)+"\t"+pot[z].get()+"\n"

        listaFields=[fecha,self.txtid.get_value(),cliente,self.txtcups.get(),tarifa,self.txtcms.get_value(),int(self.txtmes.get()),obs]
        # dlg.dialogo(self,'MODIFCACION ALTA','Registro modificacion alta de nuevo contrato').showmodal()
        db.actualiza(strsql=strsql.format(*listaFields), con=self.cnn)
        self.closer()


    def getIdTitular(self):
        idTitular = 1
        # seleccionado en el combobox
        titularSel=self.cmbtit.get()

        auxtit=db.consultar(f"SELECT * FROM clientes WHERE nomcli='{titularSel}'", con=self.cnn)
        if len(auxtit) == 0:
            print("Hay un error en la seleccion de titular!!!")
        else:  # Obtenemos el indice en el result
            idTitular = auxtit[0]['id']

        return idTitular

    def getIdTarifa(self):
        idTarifa = 0
        # Seleccionada en el combobox...
        tarifaSel = self.cmbtfa.get()
        auxtfa=db.consultar(f"SELECT * FROM tarifas WHERE destfa='{tarifaSel}'", con=self.cnn)
        if len(auxtfa) == 0:
            print("Hay un error en la selección de tarifa.")
        else:   # Pasamos el indice del result
            idTarifa = auxtfa[0]['id']        

        return idTarifa

    def validaId(self, *args):
        ''' Comprobamos que no exista el contrato actualmente
            Es nuevo y no puede duplicarse
        '''
        contrato = self.txtid.get()
        if contrato=='' or contrato=='0':
            self.txtid.focus_set()
            return

        rstexist=db.consultar(f'SELECT * FROM contratos WHERE id={int(self.txtid.get())}', con=self.cnn)
        if len(rstexist) > 0:
            dlg.dialogo(self,'CONTRATO EXISTE','Este contrato ya esta actualmente registrado', img=dlg.ADVERTENCIA).showmodal()
            self.txtid.focus_set()
            return
        
    def validaCUPS(self, *args):
        ''' Comprobamos si ya tenemos datos del CUPS y si no está actualmente en activo.
            Si esta de baja, rellenamos campos conocidos y continuamos.
            Si esta actualmente registrado, debera dar de baja el suministro anterior
            para crear nuevo contrato
        '''
        if self.txtcups.get()=='':
            self.txtcups.focus_set()
            return
        
        strsql="SELECT * FROM contratos WHERE cupcon='{}'".format(self.txtcups.get())
        rstcup = db.consultar(strsql, con=self.cnn)
        if len(rstcup) > 0:
            stdactivo=False
            for cups in rstcup:
                if cups['stdcon']:
                    stdactivo=True

            if stdactivo:
                dlg.dialogo(self,
                            'CUPS REGISTRADO','Este punto de suministro ya existe y está activo', 
                            img=dlg.ADVERTENCIA).showmodal()
                self.txtcups.focus_set()
            else:
                # Existe el cups en la base de datos pero no está activo.
                # Relleno los campos con datos conocidos
                contrato=rstcup[-1]
                self.showDatosConocidos(contrato)
                

    def showDatosConocidos(self, contrato):
        # Datos comunes independientemente del tipo de contrato
        self.txtdirsum.set_texto(contrato['dircon'])
        self.txtdpsum.set_texto(contrato['discon'])
        self.txtpobsum.set_texto(contrato['pobcon'])
        self.txtprvsum.set_texto(contrato['prvcon'])
        self.txtcms.set_value(contrato['cmscon'])
        numcli=contrato['clicon']
        auxtit=db.consultar('SELECT * FROM clientes WHERE id={}'.format(numcli), con=self.cnn)
        if len(auxtit)>0:
            # Compruebo por si acaso, pero debería existir si o si
            # porque si hay contrato dependiente no permito borrarlo
            self.cmbtit.set(auxtit[-1]['nomcli'])
            self.changeTit()
        
        auxtfa=db.consultar('SELECT * FROM tarifas WHERE id={}'.format(contrato['tfacon']), con=self.cnn)
        if len(auxtfa)>0:
            # Existe la tarifa. Pero está activa?
            # Si no está activa no la aceptamos....
            if auxtfa[0]['stdtfa']:
                self.cmbtfa.set(auxtfa[0]['destfa'])
                self.changeTfa()
        
        # Solo para suministros de electricidad
        if self.tipo=='L':
            self.txtp1.set_value(contrato['pt1con'])
            self.txtp2.set_value(contrato['pt2con'])
            self.txtp3.set_value(contrato['pt3con'])
            self.txtp4.set_value(contrato['pt4con'])
            self.txtp5.set_value(contrato['pt5con'])
            self.txtp6.set_value(contrato['pt6con'])
        else:  # Solo para suministros de GAS
            self.txtcon.set_value(contrato["concon"])
            self.txtp1.set_value(contrato["pt1con"])
                                           
                
class SeleCon(Form):
    """
        Debería ser instanciado desde un FormData.
        Treeview para mostrar tabla de datos que
        permite seleccionar registro de contrato.
        Recibe el numero de contrato seleccionado actualmente:
            
        El result será obtenido de la view sqlite3 vselecon
        
    """

    def __init__(self, hcaller, idcon=0, tipo='L', filtro='', numfiltro=0):
        """ Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos app
            
            posicion = Numero entero con el id del pedido seleccionado
        """
        # Conexión a datos
        self.hcaller = hcaller
        self.cnn = self.hcaller.cnn
        self.tipo = tipo
        self.filtro = filtro
        self.numfiltro = numfiltro

        super().__init__(hcaller)
        # Mostramos en titulo la seleccion de tipo de contrato
        if self.tipo == 'L':
            self.title('SELECCION DE CONTRATO DE ELECTRICIDAD')
        else:
            self.title('SELECCION DE CONTRATO DE GAS')
        # Inicializamos entorno de datos
        self.titulos=['NUMERO','CUPS','FECHA','CLIENTE','DIRECCION','ATR','MES']
        self.campos=['numero','cups','fecha', 'cliente','direccion','codtfa', 'mes']
        self.alinea=['w','w','w','w','w','w','e']
        # Alineación: E -> Right    W -> Left
        self.anchos=[70,220,110,370,370,60,40]

        self.tv = ttk.Treeview(self, columns=self.campos, selectmode=tk.BROWSE)
        self.tv.column('#0', width=0, stretch=tk.NO)
        for i in range(len(self.campos)):
            self.tv.column(self.campos[i],anchor=self.alinea[i], width=self.anchos[i])
            self.tv.heading(self.campos[i],anchor=self.alinea[i], text=self.titulos[i])

        # Fijamos ancho de todo menos de cliente y dirección
        self.tv.column('numero', width=70, stretch=tk.NO)
        self.tv.column('codtfa', width=80, stretch=tk.NO)
        #self.tv.column('tipo', width=40, stretch=tk.NO)
        self.tv.column('mes', width=40, stretch=tk.NO)
        self.tv.column('fecha', width=110, stretch=tk.NO)
        self.tv.column('cups', width=220, stretch=tk.NO)
        self.statusbar.showMensaje("Seleccione Registro [Doble-Click]")
        # Boton Seleccionar registro actualmente seleccionado
        self.btnok = tk.Button(self.buttonbar, text="Seleccionar", pady=3, command=self.on_sele)
        self.btnok.pack(side=tk.LEFT, padx=3, pady=6, fill=tk.Y)
        # Selector de campo de filtro
        tk.Label(self.buttonbar, text="Campo sobre el que aplicar filtro:").pack(side=tk.LEFT)
        self.cmbfiltro=ttk.Combobox(self.buttonbar, width=12, values=self.titulos, state='readonly')
        self.cmbfiltro.current(0)
        self.cmbfiltro.pack(side='left')
        self.txtfiltro=Textbox(self.buttonbar, width=40, tipo=Textbox.MAYUSCULAS)
        self.txtfiltro.pack(side='left', padx=3,pady=3,fill=tk.X, expand=True)
        self.txtfiltro['validate'] = 'key'
        self.txtfiltro['validatecommand'] = (self.txtfiltro.register(self.on_filtro), '%P', '%d', '%S')       
        # Barra de desplazamiento
        self.vscrlbar = tk.Scrollbar(self, orient="vertical", command=self.tv.yview)
        self.vscrlbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tv.configure(yscrollcommand=self.vscrlbar.set)

        self.tv.pack(fill=tk.BOTH, expand=True, pady=10)
        # Control de color para los contratos no activos
        self.tv.tag_configure('inactivo', foreground='red')
        self.tv.tag_configure('activo', foreground='black')
        # 
        self.grab_set()
        # Podriamos crear metodo loadData
        # Cargar inicialmente los datos obteniendo  self.rstcon
        self.strcon = f'SELECT * FROM vselecon WHERE tipo="{self.tipo}" '
        if self.filtro == 'CLI':
            self.strcon += f'AND clicon={self.numfiltro}'

        if self.filtro == 'GES':
            self.strcon += f'AND gestor={self.numfiltro}'

        self.rstcon = db.consultar(self.strcon, con=self.cnn)

        # Si recibimos una posicion = 0 o menor hay que situarse en ultimo registro
        self.idcon = idcon
        self.posicion = len(self.rstcon)-1

        # Si no actualizamos ncontrato al seleccionar, devolvera el inicial
        # que si era 0 corresponderá al ultimo contrato del result
        if self.idcon > 0:
            self.ncontrato = self.idcon
        else:
            self.ncontrato = self.rstcon[-1]['numero']

        alto = int(self.winfo_screenheight()/2)
        anchototal = sum(self.anchos)+10
        self.geometry(str(anchototal)+'x'+str(alto))

        self.populateData()

        # Eventos
        self.tv.bind('<<TreeviewSelect>>', self.seleccionado)
        self.tv.bind("<Double-Button-1>", self.on_sele)
        # Selección desde Teclado alfabético
        self.tv.bind('<Return>', self.on_sele)
        # Selección desde Teclado numérico
        self.tv.bind('<KP_Enter>', self.on_sele)
        self.txtfiltro.bind('<KeyRelease>', self.populateData)
        # Cuando se pulse Enter desde txtcontiene se selecciona
        # el primero de la lista y se devuelve
        # Selección desde Teclado alfabético
        self.txtfiltro.bind('<Return>', self.on_SeleFirst)
        # Selección desde Teclado numérico
        self.txtfiltro.bind('<KP_Enter>', self.on_SeleFirst)
        # Cada vez que cambie el campo de filtro
        # elimino expresion de filtro
        self.cmbfiltro.bind('<<ComboboxSelected>>', self.changeFiltro)
        self.tv.focus_set()
    
    def changeFiltro(self, *args):
        self.txtfiltro.delete(0,tk.END)
        self.textofiltro = self.txtfiltro.get()
        self.txtfiltro.focus_set()

    def on_SeleFirst(self, *args):
        # Desde expresion de filtro se selecciona el primero que cumple
        # la condición y está en la lista
        self.tv.focus(self.tv.get_children()[0])
        self.on_sele()

    def seleccionado(self, *args):
        # Actualiza el contrato que se encuentra seleccionado
        # self.idcon=self.tv.selection_get()[0]['values'][0]
        self.posicion = self.tv.index(self.tv.focus())
        
    def on_sele(self, *args):
        # Actualiza el indicador (ncontrato) que se devolverá al cerrar
        self.ncontrato=int(self.tv.item(str(self.posicion))['values'][0])
        self.closer()


    def populateData(self, *args):
        # Cadena de expresion de busqueda
        self.textofiltro = self.txtfiltro.get()
        # Limpiamos de resultados anteriores el Treeview
        self.tv.delete(*self.tv.get_children())
        self.update()
        # Si no hay datos no hacemos nada
        if len(self.rstcon) == 0:
            # Solo podemos salir, no seleccionar
            self.btnok['state']=tk.DISABLED
            return
        
        encontrado = False
        # Obtenemos el result filtrado con los datos a mostrar
        rstfilt=list(filter(lambda x: self.textofiltro in str(x[self.campos[self.cmbfiltro.current()]]),self.rstcon))
        # Si el contrato inicial solicitado es 0 posicion será último
        if self.idcon==0:
            self.posicion = len(rstfilt)-1
            # Y el contrato inicial será este último
            self.idcon=rstfilt[self.posicion]['numero']

        # Cargamos los datos en el Treeview
        for i in range(len(rstfilt)):
            valores=list(rstfilt[i][k] for k in self.campos)
            tag_std='inactivo' if self.rstcon[i]['estado']==False else 'activo'
            # Cuando filtramos datos o puede cambiar posicion
            # por tanto comprobamos el contrato actual seleccionado
            # que cuando entra por primera vez corresponde a idcon=ncontrato
            # pero que si no se selecciona por dobleclick, boton o Enter
            # ncontrato no se actualizara
            if self.idcon == valores[0]:
                self.posicion = i
                # El contrato seleccionado inicialmente cumple con la seleccion
                encontrado = True

            self.tv.insert('', tk.END, text='', values=valores, iid=str(i), tags=tag_std)

        # Si se ha encontrato el contrato inicial porque cumple con la seleccion
        
        if encontrado:
            self.tv.focus(str(self.posicion))
            self.tv.see(str(self.posicion))
            self.tv.selection_set(str(self.posicion))
        else:
            # No coincide el contrato que había seleccionado con el criterio de busqueda
            # Por tanto asignamos el primero que cumpla con el criterio
            self.tv.focus('0')
            self.tv.selection_set('0')
            self.tv.see('0')

        
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
        # Sólo aceptamos la cadena que filtra por
        # contenido los registros mostrados
        self.textofiltro = self.txtfiltro.get()+caracter
        # Controlamos que haya algún registro que cumpla la condicion
        aceptado = False
        campofiltro = self.campos[self.cmbfiltro.current()]
        for r in self.rstcon:
            if self.textofiltro.upper() in str(r[campofiltro]).upper():
                aceptado = True
                # Al menos un registro cumple con el filtro
                break

        return aceptado

    def showModal(self):
        self.hcaller.hide()
        self.center()
        self.wait_window()
        # Cuando se ejectua closer de Form (Clase Base) retoma el control
        return self.ncontrato
    
class FrmModifica(Form):
    """
        Debe ser instanciado desde un Contrato.
        
        Recibe el numero de contrato seleccionado actualmente:
        
    """

    def __init__(self, hcaller, idcon, moditip=0):
        """
        Tipos de modificacion.
        0 (Default)     Titular
        1               Precio/Tarifa
        2               Renovación de contrato (ANUAL en principio)
        3               Potencia (Caso especial de Electricidad)
        """
        self.hcaller = hcaller
        self.cnn = self.hcaller.cnn
        self.idcon = idcon
        self.moditip = moditip

        super().__init__(hcaller)
        # Cargamos los datos del contrato
        self.loadContrato()
        # Mostramos en titulo la seleccion de tipo de contrato
        if self.moditip == 0:
            self.title('MODIFICACION DE TITULAR DE CONTRATO')
        elif self.moditip==1:
            self.title('MODIFICACION CONDICIONES ECONOMICAS/TARIFA')
        elif self.moditip==2:
            self.title('RENOVACION DE CONTRATO DE SUMINISTRO')
        else:
            if self.rstcon['tipcon']=='G':
                dlg.dialogo(self, 'ERROR', 'SUMINISTRO DE GAS no puede modificaar potencia',img=dlg.ERROR).showmodal()
                self.closer()
            else:
                self.title('MODIFICACION DE POTENCIA')
        
        self.detalle()
        self.center()

    def loadContrato(self):
        strsql = f"SELECT * FROM contratos WHERE id={self.idcon}"
        self.rstcon = db.consultar(strsql, con=self.hcaller.cnn)[0]
        # Entendemos que siempre habrá un contrato válido desde donde se llama 
        # para hacer la modificación y que sólo habrá uno
        
    def detalle(self):
        # Contenedor del detalle dependiendo de la solicitud de modificacion
        self.contenido=tk.Frame(self)

        if self.moditip == 0:   # Cambio de Titular
            self.detalleTit()

        self.contenido.pack(fill=tk.X)
        
        # Area de anotaciones a la modificacion
        frmAnota=tk.Frame(self)
        tk.Label(frmAnota, text='OBSERVACIONES AL CONTRATO',bg='seashell4',fg='white').pack(side=tk.TOP, fill=tk.X)
        obsAnota=tk.Frame(frmAnota)
        self.obscon = scrolledtext.ScrolledText(obsAnota, wrap=tk.WORD, height=5)
        self.obscon.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        obsAnota.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        # Separador del area de detalle
        tk.Frame(frmAnota, background='black', height=1).pack(side=tk.BOTTOM, fill=tk.X)
        frmAnota.pack(fill=tk.BOTH, expand=True)

    def detalleTit(self):
        # La modificación solicitada es cambio de titular
        # Mostramos un frame con el titular actual y otro con la
        # posibilidad de cambiar de titular.
        antcli = self.rstcon['clicon']
        rstcli = db.consultar(f"SELECT * FROM clientes WHERE id={antcli}",con=self.hcaller.cnn)[0]
        self.titularActual=rstcli['nomcli']
        self.anterior = tk.Frame(self.contenido)
        tk.Label(self.anterior, text="CONTRATO:").grid(row=0,column=0,sticky=tk.E, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.anterior, 
                 text=str(self.idcon),
                 bg='white',borderwidth=1, relief="solid",
                 width=8,anchor=tk.E).grid(row=0, column=1,sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.anterior, text="DE FECHA:").grid(row=0,column=2,sticky=tk.E, ipadx=3, ipady=3, padx=3, pady=3)
        fecha = datetime.datetime.strptime(self.rstcon['feccon'][:10],'%Y-%m-%d').date().strftime('%d-%m-%y')
        tk.Label(self.anterior, text=fecha, bg='white',borderwidth=1, relief="solid",
                 width=10).grid(row=0, column=3,sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.anterior, text="ACTUAL TITULAR:").grid(row=1,column=0,sticky=tk.E, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.anterior, 
                 text=rstcli['nomcli'],
                 bg='white',borderwidth=1, relief="solid",
                 width=30, anchor=tk.W).grid(row=1, column=1,columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.anterior, 
                 text=rstcli['nifcli'],
                 bg='white',borderwidth=1, relief="solid",
                 width=10, anchor=tk.W).grid(row=1, column=3,sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.anterior, 
                 text=rstcli['dircli'],
                 bg='white',borderwidth=1, relief="solid",
                 width=30, anchor=tk.W).grid(row=2, column=1,columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.anterior, 
                 text=rstcli['discli'],
                 bg='white',borderwidth=1, relief="solid",
                 width=6, anchor=tk.W).grid(row=2, column=3,sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.anterior, 
                 text=rstcli['pobcli'],
                 bg='white',borderwidth=1, relief="solid",
                 width=20, anchor=tk.W).grid(row=3, column=1,columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.anterior, 
                 text=rstcli['prvcli'],
                 bg='white',borderwidth=1, relief="solid",
                 width=10, anchor=tk.W).grid(row=3, column=3,sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        
        self.posterior = tk.Frame(self.contenido)
        tk.Label(self.posterior, text='NUEVO TITULAR DEL CONTRATO DE SUMINISTRO',bg='seashell4').grid(row=0,column=0, columnspan=4, sticky=tk.EW,ipadx=3, ipady=3, padx=3, pady=3)
        strsqltit=f"SELECT * FROM clientes WHERE id !={antcli} ORDER BY nomcli"
        rstit = db.consultar(strsqltit, con=self.hcaller.cnn)
        valtit= [x['nomcli'] for x in rstit]
        self.cmbcli = ttk.Combobox(self.posterior, state='readonly', values=valtit)
        self.cmbcli.grid(row=1, column=0,columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.cmbcli.set(rstit[-1]['nomcli'])
        self.imgbusca=tk.PhotoImage(file='img/find32.png')
        btnseletit=tk.Button(self.posterior, image=self.imgbusca,takefocus=0, command=self.seleNewTit)
        self.statusbar.createTip(btnseletit, "Busqueda de Nuevo Titular [F6]")
        btnseletit.grid(row=1, column=3,sticky=tk.W)

        self.lbldir=tk.Label(self.posterior, 
                text=rstit[-1]['dircli'],
                 bg='white',borderwidth=1, relief="solid",
                 width=30, anchor=tk.W)
        self.lbldir.grid(row=2, column=0,columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        
        self.lbldis=tk.Label(self.posterior, 
                 text=rstit[-1]['discli'],
                 bg='white',borderwidth=1, relief="solid",
                 width=6, anchor=tk.W)
        self.lbldis.grid(row=2, column=3,sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        
        self.lblpob=tk.Label(self.posterior, 
                 text=rstit[-1]['pobcli'],
                 bg='white',borderwidth=1, relief="solid",
                 width=20, anchor=tk.W)
        self.lblpob.grid(row=3, column=0,columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        
        self.lblprv=tk.Label(self.posterior,text=rstit[-1]['prvcli'],bg='white',borderwidth=1,relief='solid',width=10,anchor=tk.W)
        self.lblprv.grid(row=3,column=3,sticky=tk.W,ipadx=3,ipady=3,padx=3,pady=3)
        
        self.posterior.columnconfigure(0,weight=1)
        self.anterior.columnconfigure(1, weight=1)

        self.anterior.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.posterior.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.statusbar.showMensaje("Seleccione Nuevo Titular", True)
        self.contenido.pack(fill=tk.X)
        self.cmbcli.bind('<<ComboboxSelected>>', self.changeNewTit)
        self.cmbcli.focus_set()


    def seleNewTit(self, *args):
        # Cargamos result de los clientes para elegir
        # Pero quitamos el titular actual...
        rstcli = db.consultar(f"SELECT * FROM clientes WHERE nomcli!='{self.titularActual}' ORDER BY nomcli", con=self.cnn)
        # Variable que en que nos devuelve la posición en el result
        currentcli=tk.IntVar()
        # Por defecto apunta al último
        for i in range(len(rstcli)):
            if rstcli[i]['nomcli']==self.cmbcli.get():
                currentcli.set(i)
                break

        frmsele = SeleData(self,
                           rstcli,
                           [ {'titulo':'Cliente',
                              'campo': 'nomcli',
                              'ancho': 300,
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
                              'alineacion': tk.W},
                              {'titulo':'Telef 1',
                              'campo': 'tf1cli',
                              'ancho': 100,
                              'alineacion': tk.E},
                              {'titulo':'Telef 2',
                              'campo': 'tf2cli',
                              'ancho': 100,
                              'alineacion': tk.E}], currentcli, 0)
        
        self.withdraw()
        # Esperamos a que devuelva el control
        self.wait_window(frmsele)
        # Y volvemos a mostrar
        self.show()
        # Actualizamos el cliente devuelto
        self.cmbcli.set(rstcli[currentcli.get()]['nomcli'])
        self.changeNewTit()

    def changeNewTit(self, *args):
        self.titularActual = self.cmbcli.get()
        # Datos titular
        rsttit = db.consultar("SELECT * FROM clientes WHERE nomcli='{}'".format(self.titularActual), con=self.cnn)[0]
        # Doy por sentado que existe el cliente
        self.lbldir.config(text=rsttit['dircli'])
        self.lbldis.config(text=rsttit['discli'])
        self.lblpob.config(text=rsttit['pobcli'])
        self.lblprv.config(text=rsttit['prvcli'])
        

class Vercontrato(Form):
    """
        Recibe el numero de contrato a visualizar
    """
    def __init__(self, hcaller, idcon):
        """
            hcaller (Form que lo llama)
            idcon -> Contrato a visualizar
        """
        self.hcaller = hcaller
        self.cnn = self.hcaller.cnn
        self.idcon = idcon

        super().__init__(hcaller)
    
        # Hace de contenedor de Frames en cabecera
        self.frmCAB = tk.Frame(self)
        # Cabecera con el id - fecha - CUPS de contrato
        frmID = tk.Frame(self.frmCAB)
        tk.Label(frmID, text='Num.Contrato:').grid(row=0, column=0, columnspan=2, sticky=tk.E)
        tk.Label(frmID, text='Fecha:').grid(row=1, column=1, sticky=tk.E)
        tk.Label(frmID, text='CUPS:').grid(row=2, column=0, sticky=tk.E)

        self.lblid=tk.Label(frmID, width=7,bg='white',borderwidth=1,relief='solid', anchor=tk.E)
        self.lblid.grid(row=0, column=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.lblfec=tk.Label(frmID, width=8,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lblfec.grid(row=1, column=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.lblcups=tk.Label(frmID, width=20, bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lblcups.grid(row=2,column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        frmID.pack(side=tk.LEFT)
        # Cabecera con el titular y sus datos
        frmTIT = tk.Frame(self.frmCAB)
        tk.Label(frmTIT, text='Titular:').grid(row=0, column=0, sticky=tk.E)
        tk.Label(frmTIT, text='Contacto:').grid(row=1, column=0, sticky=tk.E)
        tk.Label(frmTIT, text='Direccion:').grid(row=2, column=0, sticky=tk.E)
        self.lbltit = tk.Label(frmTIT, width=30,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lbltit.grid(row=0, column=1, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.lblnif=tk.Label(frmTIT, width=9,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lblnif.grid(row=0, column=3, ipadx=3, ipady=3, padx=3, pady=3)
        self.lblcontit=tk.Label(frmTIT, width=30,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lblcontit.grid(row=1, column=1, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.lbltf1tit=tk.Label(frmTIT, width=9,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lbltf1tit.grid(row=1, column=3, ipadx=3, ipady=3, padx=3, pady=3)
        self.lbldirtit=tk.Label(frmTIT, width=30,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lbldirtit.grid(row=2, column=1, columnspan=2,sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.lbltf2tit=tk.Label(frmTIT, width=9,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lbltf2tit.grid(row=2, column=3, ipadx=3, ipady=3, padx=3, pady=3)
        frmTIT.columnconfigure(1, weight=1)
        frmTIT.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Cabecera datos de gestor
        frmGES = tk.Frame(self.frmCAB)
        tk.Label(frmGES, text="GESTOR",bg='seashell4',fg='white').grid(row=0, column=0, columnspan=3, sticky=tk.EW,ipadx=3, ipady=3, padx=3, pady=3)
        self.lblnomges=tk.Label(frmGES, width=30,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lblnomges.grid(row=1, column=0, ipadx=3, ipady=3, padx=3, pady=3)
        self.lbltf1ges=tk.Label(frmGES, width=9,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lbltf1ges.grid(row=1, column=1,columnspan=2,sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        self.lblconges=tk.Label(frmGES, width=30,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lblconges.grid(row=2, column=0, ipadx=3, ipady=3, padx=3, pady=3)
        self.lbltf2ges=tk.Label(frmGES, width=9,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lbltf2ges.grid(row=2, column=1,columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        frmGES.pack(side=tk.RIGHT)
        # Empaquetamos frmCab arriba
        self.frmCAB.pack(side=tk.TOP, fill=tk.X)
        # Separador por debajo de area de detalle
        tk.Frame(self, background='black', height=1).pack(side=tk.TOP, fill=tk.X)
        # Cargamos los datos del contrato
        self.loadContrato()
        # Mostramos area de detalle basada en el tipo de contrato
        self.detalle()
        self.geometry("1304x450+156+157")
        self.center()
        self.showdatos()
        self.grab_set()

    def detalle(self):
        # Datos del punto de suministro y condiciones economicas
        self.frmsum = tk.Frame(self)
        # Titulamos sección según tipo de alta de suministro LUZ o GAS
        if self.tipo=='L':
            tk.Label(self.frmsum, text='PUNTO DE SUMINISTRO ELECTRICO',bg='seashell4',fg='white').grid(row=0, column=0, columnspan=3, sticky=tk.EW)
        else:
            tk.Label(self.frmsum, text='PUNTO DE SUMINISTRO DE GAS',bg='seashell4',fg='white').grid(row=0, column=0, columnspan=3, sticky=tk.EW)

        # Estos son controles comunes
        tk.Label(self.frmsum, text='Tarifa:').grid(row=0, column=3, sticky=tk.E)
        self.lbltfa = tk.Label(self.frmsum, width=20,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lbltfa.grid(row=0, column=4, columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        # self.nfac=tk.Label(self.cabecera, bg='white',borderwidth=1,
        #                    relief="solid", width=8,anchor=tk.E)
        self.lblatr=tk.Label(self.frmsum, width=6,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lblatr.grid(row=0, column=6, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmsum, text='Dirección:').grid(row=1, column=0, sticky=tk.E)
        self.lbldirsum=tk.Label(self.frmsum, width=25,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lbldirsum.grid(row=1, column=1,columnspan=4, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmsum, text='DP:').grid(row=1, column=5, sticky=tk.E)
        self.lbldpsum=tk.Label(self.frmsum, width=5,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lbldpsum.grid(row=1, column=6,sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmsum, text='Población:').grid(row=2, column=0, sticky=tk.E)
        self.lblpobsum=tk.Label(self.frmsum, width=25,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lblpobsum.grid(row=2, column=1,columnspan=2, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmsum, text='Provincia:').grid(row=2, column=3, sticky=tk.E)
        self.lblprvsum=tk.Label(self.frmsum, width=25,bg='white',borderwidth=1,relief='solid',anchor=tk.W)
        self.lblprvsum.grid(row=2, column=4,columnspan=3, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmsum, text='Comisión:').grid(row=3, column=0, sticky=tk.E)
        self.lblcms=tk.Label(self.frmsum, width=8,bg='white',borderwidth=1,relief='solid',anchor=tk.E)
        self.lblcms.grid(row=3, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmsum, text='Mes devengo:').grid(row=3, column=2,columnspan=2, sticky=tk.E)
        self.lblmes=tk.Label(self.frmsum, width=3,bg='white',borderwidth=1,relief='solid',anchor=tk.E)
        self.lblmes.grid(row=3, column=4, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        # Para la LUZ son potencias:
        if self.tipo=='L':
            tk.Label(self.frmsum, text='Potencia P1').grid(row=4, column=0, sticky=tk.E)
            self.lblp1=tk.Label(self.frmsum, width=6,bg='white',borderwidth=1,relief='solid',anchor=tk.E)
            self.lblp1.grid(row=4, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(self.frmsum, text='P2').grid(row=4, column=2, sticky=tk.E)
            self.lblp2=tk.Label(self.frmsum, width=6,bg='white',borderwidth=1,relief='solid',anchor=tk.E)
            self.lblp2.grid(row=4, column=3, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(self.frmsum, text='P3').grid(row=4, column=5, sticky=tk.E)
            self.lblp3=tk.Label(self.frmsum, width=6,bg='white',borderwidth=1,relief='solid',anchor=tk.E)
            self.lblp3.grid(row=4, column=6, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(self.frmsum, text='P4').grid(row=5, column=0, sticky=tk.E)
            self.lblp4=tk.Label(self.frmsum, width=6,bg='white',borderwidth=1,relief='solid',anchor=tk.E)
            self.lblp4.grid(row=5, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(self.frmsum, text='P5').grid(row=5, column=2, sticky=tk.E)
            self.lblp5=tk.Label(self.frmsum, width=6,bg='white',borderwidth=1,relief='solid',anchor=tk.E)
            self.lblp5.grid(row=5, column=3, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(self.frmsum, text='P6').grid(row=5, column=5, sticky=tk.E)
            self.lblp6=tk.Label(self.frmsum, width=6,bg='white',borderwidth=1,relief='solid',anchor=tk.E)
            self.lblp6.grid(row=5, column=6, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        else:
            tk.Label(self.frmsum, text='Consumo Anual KW:').grid(row=4, column=0, sticky=tk.E)
            self.lblcon=tk.Label(self.frmsum, width=8,text='0',bg='white',borderwidth=1,relief='solid',anchor=tk.E)
            self.lblcon.grid(row=4, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
            tk.Label(self.frmsum, text='Precio pactado fijo:').grid(row=5, column=0, sticky=tk.E)
            self.lblp1=tk.Label(self.frmsum, width=6,bg='white',borderwidth=1,relief='solid',anchor=tk.E)
            self.lblp1.grid(row=5, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)

        # También es comun
        tk.Label(self.frmsum, text="OBSERVACIONES AL CONTRATO",bg='seashell4',fg='white').grid(row=0, column=7, sticky=tk.EW)
        self.obscon = scrolledtext.ScrolledText(self.frmsum, wrap=tk.WORD,height=10)
        self.obscon.grid(row=1,column=7, rowspan=6, sticky=tk.NSEW, ipadx=3, ipady=3, padx=3, pady=3)
        self.frmsum.rowconfigure(6, weight=1)
        self.frmsum.columnconfigure(7, weight=1)
        self.frmsum.pack(side=tk.TOP,fill=tk.BOTH, expand=True)

    def loadContrato(self):
        strsql = f"SELECT * FROM contratos WHERE id={self.idcon}"
        self.rstcon = db.consultar(strsql, con=self.hcaller.cnn)[0]
        self.tipo=self.rstcon['tipcon']
        # Entendemos que siempre habrá un contrato válido desde donde se llama
        # Titular
        self.rsttit=db.consultar(f'SELECT * FROM clientes WHERE id={self.rstcon["clicon"]}',con=self.cnn)[0]
        # Gestor del titular
        self.rstges=db.consultar(f'SELECT * FROM gestores WHERE id={self.rsttit["gescli"]}',con=self.cnn)[0]
        # Tarifa
        self.rsttfa=db.consultar(f"SELECT * FROM tarifas WHERE id={self.rstcon['tfacon']}",con=self.cnn)[0]

    def showdatos(self):
        self.lblid['text']=str(self.idcon)
        self.lblfec['text']=datetime.datetime.strptime(self.rstcon['feccon'][:10],'%Y-%m-%d').date().strftime('%d-%m-%y')
        self.lblcups['text']=self.rstcon['cupcon']
        self.lbltit['text']=self.rsttit['nomcli']
        self.lblnif['text']=self.rsttit['nifcli']
        self.lblcontit['text']=self.rsttit['concli']
        self.lbldirtit['text']=self.rsttit['dircli']
        self.lbltf1tit['text']=self.rsttit['tf1cli']
        self.lbltf2tit['text']=self.rsttit['tf2cli']
        self.lblnomges['text']=self.rstges['nomges']
        self.lbltf1ges['text']=self.rstges['tf1ges']
        self.lblconges['text']=self.rstges['conges']
        self.lbltf2ges['text']=self.rstges['tf2ges']

        self.lbltfa['text']=self.rsttfa['destfa']
        self.lblatr['text']=self.rsttfa['codtfa']
        self.lbldirsum['text']=self.rstcon['dircon']
        self.lbldpsum['text']=self.rstcon['discon']
        self.lblpobsum['text']=self.rstcon['pobcon']
        self.lblprvsum['text']=self.rstcon['prvcon']
        self.lblcms['text']="{:6.2f}".format(self.rstcon['cmscon'])
        self.lblmes['text']="{:2}".format(self.rstcon['mescon'])
        self.lblp1['text']="{:6.2f}".format(self.rstcon['pt1con'])
        if self.tipo=='L':
            self.lblp2['text']="{:6.2f}".format(self.rstcon['pt2con'])
            self.lblp3['text']="{:6.2f}".format(self.rstcon['pt3con'])
            self.lblp4['text']="{:6.2f}".format(self.rstcon['pt4con'])
            self.lblp5['text']="{:6.2f}".format(self.rstcon['pt5con'])
            self.lblp6['text']="{:6.2f}".format(self.rstcon['pt6con'])
        else:
            self.lblcon['text']=self.rstcon['concon']
            
        self.obscon.insert('1.0', self.rstcon['obscon'])
        self.obscon['state']="disabled"
        
