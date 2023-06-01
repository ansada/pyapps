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
from tkcalendar import DateEntry
import tkinter.font as tkfont
from GASYLUZ.Contratos import Vercontrato
from Editor import frmEditor
from datetime import date

class facturacion(FormData):
    """
        Historico de facturacion (Facturas emitidas)

    """

    def __init__(self, hcaller, name=""):
        """ Constructor: Recibe parámetro del hcaller para devolver
            el control cuando cerremos Formulario
        """
        # Conexión a datos
        self.strsql='SELECT * FROM facturas ORDER BY id'
        self.cnn=hcaller.cnn
        
        super().__init__(hcaller, name, self.strsql, self.cnn, '')
        
        self.title("HISTORICO DE FACTURACION")
        #
        self.declaraControls()
        # Icono que aparece en ventana minimizada (Barra de tareas)
        self.setIcon('img/editArea32.png')
        # Boton para imprimir detalle de pedidos de esta factura
        self.imgprint=tk.PhotoImage(file='img/printBW32.png')
        self.btnimprimir=tk.Button(self.buttonbar, image=self.imgprint, compound=tk.LEFT, text='IMPRIMIR', underline=0,command=self.imprimeDetalle)
        self.btnimprimir.pack(side=tk.RIGHT, padx=3, fill=tk.Y)
        self.statusbar.createTip(self.btnimprimir, "Generar listado detalle de pedidos [Alt-I]")
        # Como no se va a permitir modificación de factura emitida
        # ni eliminarla del histórico... QUITAMOS LOS BOTONES
        
        self.btndel.pack_forget()
        self.btnedit.pack_forget()
        
        self.update()
        self.geometry('1200x640')

        self.center()

        if self.current.get() >= 0:
            self.showdata()

        self.tv.focus_set()

        self.bind('<<cursordata>>', self.showdata)
        self.tv.bind("<Double-Button-1>", self.on_vercon)
        # Selección desde Teclado alfabético
        self.tv.bind('<Return>', self.on_vercon)
        # Selección desde Teclado numérico
        self.tv.bind('<KP_Enter>', self.on_vercon)
        self.bind('<Alt-I>', self.imprimeDetalle)
        self.bind('<Alt-i>', self.imprimeDetalle)
        self.bind('<<seledata>>', self.seledata)
    

    def declaraControls(self):
        # Cabecera de factura mostrada
        self.cabecera=tk.Frame(self,highlightbackground="black", highlightthickness=1)
        tk.Label(self.cabecera, text="FACTURA:").pack(side=tk.LEFT,padx=3, pady=3)
        self.nfac=tk.Label(self.cabecera, bg='white',borderwidth=1,
                           relief="solid", width=8,anchor=tk.E)
        self.nfac.pack(side=tk.LEFT,padx=3, pady=3)
        tk.Label(self.cabecera, text="Fecha:").pack(side=tk.LEFT,padx=3, pady=3)
        self.fechafac=tk.Label(self.cabecera, bg='white',borderwidth=1,
                           relief="solid", width=10, anchor=tk.W)
        self.fechafac.pack(side=tk.LEFT,padx=3, pady=3)
        tk.Label(self.cabecera, text="Concepto:").pack(side=tk.LEFT,padx=3, pady=3)
        self.concepto=tk.Label(self.cabecera, bg='white', borderwidth=1,
                               relief='solid',width=40, anchor=tk.W)
        self.concepto.pack(side=tk.LEFT, fill=tk.X, expand=True,padx=3, pady=3)
        tk.Label(self.cabecera, text="Mes/Periodo:").pack(side=tk.LEFT,padx=3, pady=3)
        self.mesper=tk.Label(self.cabecera, bg='white', borderwidth=1,
                               relief='solid', width=8,anchor=tk.W)
        self.mesper.pack(side=tk.RIGHT,padx=3, pady=3)
        self.cabecera.pack(side="top", fill=tk.X)
        # Aqui treeview con detalle de composicon de la parte variable.
        self.detalle=tk.Frame(self)
        self.titulos=['CONTRATO','TIPO','CUPS','CLIENTE','DIRECCION','COMISION']
        self.campos=['conlin','tipcon','cupcon','nomcli','dircon','cmslin']
        self.alinea=['e','center','w','w','w','e']
        self.tv = ttk.Treeview(self.detalle, columns=self.campos, selectmode=tk.BROWSE)
        for i in range(len(self.campos)):
            self.tv.column(self.campos[i],anchor=self.alinea[i])
            self.tv.heading(self.campos[i],anchor=self.alinea[i], text=self.titulos[i])

        self.tv.column('#0', width=0, stretch=tk.NO)
        self.tv.column('conlin',width=95,stretch=tk.NO)
        self.tv.column('tipcon',width=50,stretch=tk.NO)
        self.tv.column('cupcon',width=220,stretch=tk.NO)
        self.tv.column('nomcli',width=250)
        self.tv.column('dircon',width=250)
        self.tv.column('cmslin',width=90,stretch=tk.NO)
        # Barra de desplazamiento por si es necesaria
        self.vscrlbar = Scrollbar(self.detalle, orient="vertical", command=self.tv.yview)
        self.vscrlbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tv.configure(yscrollcommand=self.vscrlbar.set)
        self.tv.pack(fill=tk.BOTH,expand=True, pady=10)
        self.detalle.pack(fill=tk.BOTH, expand=True)
        # Pie de Factura (Resumen)
        self.pie=tk.Frame(self,highlightbackground="black", highlightthickness=1)
        tk.Label(self.pie, text='Importe Fijo:').grid(row=0,column=0,padx=3,pady=3,sticky=tk.E)
        
        self.txtfijo=tk.Label(self.pie, bg='white', borderwidth=1,
                               relief='solid', width=8,anchor=tk.E)
        self.txtfijo.grid(row=0,column=1,padx=3,pady=3,sticky=tk.W)
        tk.Label(self.pie, text='Variable:').grid(row=0,column=2,padx=3,pady=3,sticky=tk.E)
        self.txtvariable=tk.Label(self.pie, bg='white', borderwidth=1,
                               relief='solid', width=8,anchor=tk.E)
        self.txtvariable.grid(row=0,column=3,padx=3,pady=3,sticky=tk.W)
        tk.Label(self.pie, text='Comision:').grid(row=0,column=4,padx=3,pady=3,sticky=tk.E)
        self.txtcomision=tk.Label(self.pie, bg='white', borderwidth=1,
                               relief='solid', width=8,anchor=tk.E)
        self.txtcomision.grid(row=0,column=5,padx=3,pady=3,sticky=tk.W)
        tk.Label(self.pie, text='Neto:').grid(row=0,column=6,padx=3,pady=3,sticky=tk.E)
        self.txtneto=tk.Label(self.pie, bg='white', borderwidth=1,
                               relief='solid', width=8,anchor=tk.E)
        self.txtneto.grid(row=0,column=7,padx=3,pady=3,sticky=tk.W)
        tk.Label(self.pie, text='IVA:').grid(row=1,column=0,padx=3,pady=3,sticky=tk.E)
        self.txtiva=tk.Label(self.pie, bg='white', borderwidth=1,
                               relief='solid', width=6,anchor=tk.E)
        self.txtiva.grid(row=1,column=1,padx=3,pady=3,sticky=tk.W)
        self.txtimpiva=tk.Label(self.pie, bg='white', borderwidth=1,
                               relief='solid', width=8,anchor=tk.E)
        self.txtimpiva.grid(row=1,column=2,padx=3,pady=3,sticky=tk.W)
        tk.Label(self.pie, text='IRPF:').grid(row=1,column=3,padx=3,pady=3,sticky=tk.E)
        self.txtirpf=tk.Label(self.pie, bg='white', borderwidth=1,
                               relief='solid', width=6,anchor=tk.E)
        self.txtirpf.grid(row=1,column=4,padx=3,pady=3,sticky=tk.W)
        self.txtimpirpf=tk.Label(self.pie, bg='white', borderwidth=1,
                               relief='solid', width=8,anchor=tk.E)
        self.txtimpirpf.grid(row=1,column=5,padx=3,pady=3,sticky=tk.W)
        tk.Label(self.pie, text='TOTAL:').grid(row=1,column=6,padx=3,pady=3,sticky=tk.E)
        self.txttotal=tk.Label(self.pie, bg='white', borderwidth=1,
                               relief='solid', width=8,anchor=tk.E)
        self.txttotal.grid(row=1,column=7,padx=3,pady=3,sticky=tk.W)

        self.pie.grid_columnconfigure(6,weight=1)
        self.pie.pack(side=tk.BOTTOM, fill=tk.X)

        # Cambio el numero de factura a negrita
        fteWidget=self.nfac.cget('font')
        fuente = tkfont.Font(family=fteWidget)
        #familia=fuente.actual()['family']
        tamano = fuente.actual()["size"]
        # peso = fuente.actual()['weight']
        self.nfac['font']=[fuente,tamano,'bold']

    
    def showdata(self,*args):
        self.registro = self.rst[self.current.get()]
        self.factura=self.registro['id']
        self.nfac['text']=self.factura
        self.fechafac['text']=datetime.datetime.strptime(self.registro['fecfac'][:10],'%Y-%m-%d').date().strftime('%d-%m-%y')
        self.concepto['text']=self.registro['cnpfac']
        self.mesper['text']=f"{self.registro['mesfac']}/{self.registro['perfac']}"
        fijo=self.registro['fixfac']
        variable=self.registro['varfac']
        comision=self.registro['cmsfac']
        neto=fijo+variable+comision
        self.txtfijo['text']="{:6.2f}".format(self.registro['fixfac'])
        self.txtvariable['text']="{:6.2f}".format(self.registro['varfac'])
        self.txtcomision['text']="{:6.2f}".format(self.registro['cmsfac'])
        self.txtneto['text']="{:6.2f}".format(neto)
        ivafac=cmvar.properties.getProperty('defiva')
        irpfac=cmvar.properties.getProperty('defirpf')
        self.txtiva['text']="{:4.2f}".format(ivafac)
        self.txtirpf['text']="{:4.2f}".format(irpfac)
        impiva=(neto/100)*ivafac
        impirpf=(neto/100)*irpfac
        print(impirpf)
        self.txtimpiva['text']="{:6.2f}".format(impiva)
        self.txtimpirpf['text']="{:6.2f}".format(impirpf)
        total=neto+impiva-impirpf
        self.txttotal['text']="{:6.2f}".format(total)

        self.populatetv()
        self.updateBar()

    def populatetv(self):
        # Cargamos contratos asociados a esta factura
        strsqlcon=f'SELECT * FROM vLineasCms WHERE fac={self.factura} ORDER BY conlin'
        self.rstcon=db.consultar(strsqlcon, con=self.cnn)
        self.tv.delete(*self.tv.get_children())
        self.update()
        # Si no hay datos no hacemos nada
        if len(self.rstcon) == 0:
            return

        # Cargamos los datos en el Treeview
        for i in range(len(self.rstcon)):
            valores=list(self.rstcon[i][k] for k in self.campos)
            self.tv.insert('', tk.END, text='', values=valores, iid=str(i))

        self.tv.focus('0')
        self.tv.selection_set('0')
        self.tv.see('0')

    def on_vercon(self, *args):
        idxcon=self.tv.focus()
        idcontrato=self.tv.item(idxcon)['values'][0]
        frmvercon=Vercontrato(self, idcon=idcontrato)
        self.withdraw()
        self.wait_window(frmvercon)
        self.show()
        
        return
    
    def imprimeDetalle(self, *args):
        self.prop=cmvar.properties

        titulo=f"DETALLE CONTRATOS EN FACTURA {self.factura} DE FECHA {self.fechafac['text']}"
        #
        fichero=self.prop.getProperty('informes')+os.sep+"dtfFra"+str(self.factura)+'.txt'
        # print("Se imprimira: " + fichero)
        # print("Con titulo: " + titulo)

        if os.path.isfile(fichero):
            strmsg=f"El fichero {fichero} ya existe\nReimpresion hará que se pierdan los datos anteriores."
            opciones=['Reimprimir', 'Editar existente', 'Cancelar']
            ok = dlg.dialogo(self, "IMPRESION DETALLE DE FACTURA", strmsg, opciones, dlg.ADVERTENCIA).showmodal()
            if ok == 2:
                return
            
            if ok == 1:
                frmedt = frmEditor(self, name='',archivo=fichero)
                self.wait_window(frmedt)
                return
            

        ok = dlg.dialogo(self, "IMPRESION DETALLE", 
                         "Se imprimirán los contratos asociados a esta factura",
                         ['Valorado','Sin valor'],dlg.PREGUNTA).showmodal()
        
        # Cargamos los contratos que componen esta factura
        rstctr=db.consultar(f'SELECT * FROM vLineasCms WHERE fac={self.factura}', con=self.cnn)
        # Creamos fichero (vacio) para impresion texto
        ficlist=open(fichero,'w')
        # Totalizadores  contadores
        lineasPorPagina=80
        lineas=0
        pagina=1
        
        if ok == 1:
            for i in range(len(rstctr)):
                if lineas==0:
                    # Cabecera
                    ficlist.write('\n')
                    lineacab='{:<69} {:%d-%m-%Y}'.format(titulo, date.today())
                    ficlist.write(lineacab)
                    ficlist.write('\n')
                    ficlist.write(('-'*80)+'\n')
                    #          12345679012345679801234567890
                    lineacab ='{:<8} {:<8} {:<20} {:<6} {:<32}\n'.format('CONTRATO','FECHA','CUPS','ATR','P.SUMINISTRO')
                    ficlist.write(lineacab)
                    ficlist.write(('-'*80)+'\n')
                    lineas += 6
                # datetime.datetime.strptime(self.registro['fecfac'][:10],'%Y-%m-%d').date().strftime('%d-%m-%y')
                contrato=rstctr[i]['conlin']
                fecctr = datetime.datetime.strptime(rstctr[i]['feccon'][:10],'%Y-%m-%d').date().strftime('%d-%m-%y')
                #cliente=rstctr[i]['nomcli'][:35]
                cups=rstctr[i]['cupcon']
                atr =rstctr[i]['codtfa']
                psum=rstctr[i]['dircon'][:32]
                linea='{:>8d} {:<8} {:<20} {:<6} {:<32}\n'.format(contrato,fecctr,cups,atr,psum)
                ficlist.write(linea)
                # Acumuladores
                lineas +=1

                if lineas > lineasPorPagina:
                    ficlist.write(('-'*80)+'\n')
                    ficlist.write(f'Pag: {pagina:>3}\n')
                    ficlist.write(('-'*80)+'\n\n')
                    lineas = 0


            # Salimos del bucle porque ya no hay mas lineas para imprimir
            for i in range(lineas, lineasPorPagina-4):
                # Rellenamos con lineas vacías hasta el pie de pagina
                ficlist.write('\n')

            ficlist.write(('-'*80)+'\n')
            # Imprimimos pie de pagina
            lineaPie = f'Pag: {pagina:>3}\n'
            ficlist.write(lineaPie)
            ficlist.write(('-'*80)+'\n\n')
        else:
            totalComision=0
            for i in range(len(rstctr)):
                if lineas==0:
                    # Cabecera
                    ficlist.write('\n')
                    lineacab='{:<69} {:%d-%m-%Y}'.format(titulo, date.today())
                    ficlist.write(lineacab)
                    ficlist.write('\n')
                    ficlist.write(('-'*80)+'\n')
                    #          12345679012345679801234567890
                    lineacab ='{:<8} {:<8} {:<20} {:<6} {:<26} {:>7}\n'.format('CONTRATO','FECHA','CUPS','ATR','P.SUMINISTRO','CMSION')
                    ficlist.write(lineacab)
                    ficlist.write(('-'*80)+'\n')
                    lineas += 6
                # datetime.datetime.strptime(self.registro['fecfac'][:10],'%Y-%m-%d').date().strftime('%d-%m-%y')
                contrato=rstctr[i]['conlin']
                fecctr = datetime.datetime.strptime(rstctr[i]['feccon'][:10],'%Y-%m-%d').date().strftime('%d-%m-%y')
                #cliente=rstctr[i]['nomcli'][:35]
                cups=rstctr[i]['cupcon']
                atr =rstctr[i]['codtfa']
                psum=rstctr[i]['dircon'][:26]
                comision=rstctr[i]['cmslin']
                totalComision += comision
                linea='{:>8d} {:<8} {:<20} {:<6} {:<27} {:>6.2f}\n'.format(contrato,fecctr,cups,atr,psum,comision)
                ficlist.write(linea)
                # Acumuladores
                lineas +=1

                if lineas > lineasPorPagina:
                    ficlist.write(('-'*80)+'\n')
                    ficlist.write(f'Pag: {pagina:>3}\n')
                    ficlist.write(('-'*80)+'\n\n')
                    lineas = 0


            # Salimos del bucle porque ya no hay mas lineas para imprimir
            for x in range(lineas, lineasPorPagina-4):
                # Rellenamos con lineas vacías hasta el pie de pagina
                ficlist.write('\n')

            ficlist.write(('-'*80)+'\n')
            # Imprimimos pie de pagina
            lineaPie = f'Pag: {pagina:>3} Contratos:{len(rstctr):3d}'+(' '*44)+f'Total:{totalComision:>8.2f}\n'
            ficlist.write(lineaPie)
            ficlist.write(('-'*80)+'\n\n')

            
        ficlist.close()
        strmsg="Visualizar el listado en el Editor?"
        ok = dlg.dialogo(self, "IMPRESION REALIZADA", strmsg, ['Aceptar','Cancelar'], dlg.PREGUNTA).showmodal()
        if ok == 0:
            frmedt = frmEditor(self, name='',archivo=fichero)
            self.wait_window(frmedt)
        
        return
        # if ok == tk.YES:
        #     subprocess.run(["xed", fichero])

    def seledata(self, evt=None):
        frmsele = SeleFac(self, idfac=self.factura)
        factura=frmsele.showModal()
        self.show()
        # buscamos y cambiamos el current
        for i in range(len(self.rst)):
            if self.rst[i]['id']==factura:
                self.current.set(i)
                self.showdata()
                break

class SeleFac(Form):
    """
        Debería ser instanciado desde un FormData.
        Treeview para mostrar tabla de datos que
        permite seleccionar registro de Factura.
        Recibe el numero de Factura seleccionado actualmente:
            
        El result será obtenido de la view sqlite3 vselecon
        
    """

    def __init__(self, hcaller, idfac=0):
        """ Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos app
            
            posicion = Numero entero con el id del pedido seleccionado
        """
        # Conexión a datos
        self.hcaller = hcaller
        self.cnn = self.hcaller.cnn
        self.idfac=idfac

        super().__init__(hcaller)
        # Mostramos en titulo la seleccion de tipo de contrato
        self.title('SELECCION DE FACTURA EMITIDA')
        # Inicializamos entorno de datos
        self.titulos=['FACTURA','FECHA','CONCEPTO','MES','PERIODO','IMP.NETO']
        self.campos=['factura','fecha', 'concepto','mesfac','perfac', 'importe']
        self.alinea=['e','center','w','e','center','e']
        # Alineación: E -> Right    W -> Left
        self.anchos=[90,120,450,60,90,100]

        self.tv = ttk.Treeview(self, columns=self.campos, selectmode=tk.BROWSE)
        for i in range(len(self.campos)):
            self.tv.column(self.campos[i],anchor=self.alinea[i], width=self.anchos[i])
            self.tv.heading(self.campos[i],anchor=self.alinea[i], text=self.titulos[i])

        # Fijamos ancho de todo menos de cliente y dirección
        self.tv.column('#0', width=0, stretch=tk.NO)
        self.tv.column('factura', stretch=tk.NO)
        self.tv.column('fecha', stretch=tk.NO)
        self.tv.column('mesfac', stretch=tk.NO)
        self.tv.column('perfac', stretch=tk.NO)
        # self.tv.column('importe' stretch=tk.NO)
        self.statusbar.showMensaje("Seleccione Registro [Doble-Click]")
        # Boton Seleccionar registro actualmente seleccionado
        self.btnok = tk.Button(self.buttonbar, text="Seleccionar", pady=3, command=self.on_sele)
        self.btnok.pack(side=tk.LEFT, padx=3, pady=6, fill=tk.Y)
        # Barra de desplazamiento
        self.vscrlbar = tk.Scrollbar(self, orient="vertical", command=self.tv.yview)
        self.vscrlbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tv.configure(yscrollcommand=self.vscrlbar.set)

        self.tv.pack(fill=tk.BOTH, expand=True, pady=10)
        # 
        self.grab_set()
        # Podriamos crear metodo loadData
        # Cargar inicialmente los datos obteniendo  self.rstcon
        self.strfac = 'SELECT * FROM vselefac'

        self.rstfac = db.consultar(self.strfac, con=self.cnn)
        self.posicion=len(self.rstfac)-1
        for i in range(len(self.rstfac)):
            if self.rstfac[i]['factura']==self.idfac:
                self.posicion = i

        # Si no actualizamos ncontrato al seleccionar, devolvera el inicial
        # que si era 0 corresponderá al ultimo contrato del result
        if self.idfac > 0:
            self.nfac = self.idfac
        else:
            self.nfac = self.rstfac[-1]['numero']

        alto = int(self.winfo_screenheight()/2)
        anchototal = sum(self.anchos)+20
        self.geometry(str(anchototal)+'x'+str(alto))

        self.populateData()

        # Eventos
        self.tv.bind('<<TreeviewSelect>>', self.seleccionado)
        self.tv.bind("<Double-Button-1>", self.on_sele)
        # Selección desde Teclado alfabético
        self.tv.bind('<Return>', self.on_sele)
        # Selección desde Teclado numérico
        self.tv.bind('<KP_Enter>', self.on_sele)
        self.tv.focus_set()

    def seleccionado(self, *args):
        # Actualiza el contrato que se encuentra seleccionado
        # self.idcon=self.tv.selection_get()[0]['values'][0]
        self.posicion = self.tv.index(self.tv.focus())
        
    def on_sele(self, *args):
        # Actualiza el indicador (ncontrato) que se devolverá al cerrar
        self.nfac=int(self.tv.item(str(self.posicion))['values'][0])
        self.closer()

    def populateData(self, *args):
        # Limpiamos de resultados anteriores el Treeview
        self.tv.delete(*self.tv.get_children())
        self.update()
        # Si no hay datos no hacemos nada
        if len(self.rstfac) == 0:
            # Solo podemos salir, no seleccionar
            self.btnok['state']=tk.DISABLED
            return
        
        encontrado = False
        # Cargamos los datos en el Treeview
        for i in range(len(self.rstfac)):
            valores=list(self.rstfac[i][k] for k in self.campos)
            # importe=
            valores[-1]="{:7.2f}".format(valores[-1])
            if self.idfac == valores[0]:
                self.posicion = i
                # El contrato seleccionado inicialmente cumple con la seleccion
                encontrado = True

            self.tv.insert('', tk.END, text='', values=valores, iid=str(i))

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

    def showModal(self):
        self.hcaller.hide()
        self.center()
        self.wait_window()
        # Cuando se ejectua closer de Form (Clase Base) retoma el control
        return self.nfac
    
class OrdenFacturacion(Form):

    def __init__(self, hcaller, name=''):
        """
        Formulario Orden de Facturación
        Captura el último numero de factura generado
        y lo incrementa en 1.
        Si la fecha de factura es me de enero y la serie de 
        la factura empieza por el año anterior, ofrece la posibilidad
        de inicializar el numero de factura al per(periodo) del año 
        de la fecha factura y la factura la primera.
        
        Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos app
            name = Clave del diccionario con el que se registra en
                   lanzador de aplicaciones
        """
        super().__init__(hcaller, name)
        #
        self.cnn='GYL'
        # Creamos conexión a base de datos fac.db
        ficfac = os.path.join(cmvar.properties.getProperty('host'),'fac.db')
        self.confac='FAC'
        db.conecta(self.confac, ficfac)
        # Entiendo que existe y continuo
        rsfac = db.consultar('SELECT * FROM facturas ORDER BY id',con=self.confac)
        clifac=cmvar.properties.getProperty("clifacluz")
        strsql = 'SELECT empcli,nifcli,fpacli FROM clientes WHERE id=?'
        rstcli = db.consultar(strsql, par=(clifac,), con="FAC")
        cliente, nif, fpago = ('','','')
        if len(rstcli) > 0:    # Quiere decir que ha devuelto un registro
            cliente = rstcli[0]["empcli"]
            nif = rstcli[0]['nifcli']
            fpago=rstcli[0]['fpacli']
        else:
            print("Se ha producido un error de lectura de cliente de facturación")

        # ademas no esta vacio (Por si acaso lo compruebo, pero no va a ocurrir)
        if len(rsfac)==0:
            self.ultfac = ((datetime.date.today().year) * 1000)
        else:
            self.ultfac = rsfac[-1]['id']

        self.title("ORDEN DE FACTURACION")
        self.declaraFrames()
        # Boton confirmar factura e imprimir detalle pendiente de aprobación
        self.btnconfirma=tk.Button(self.buttonbar, text='Confirmar Factura', underline=0,command=self.confirmar)
        self.btnconfirma.pack(side=tk.LEFT, padx=3, fill=tk.Y)
        self.statusbar.createTip(self.btnconfirma, "Grabar factura y actualizar contratos")
        # Boton para imprimir detalle de pedidos de esta factura
        self.imgprint=tk.PhotoImage(file='img/printBW32.png')
        self.btnimprimir=tk.Button(self.buttonbar, image=self.imgprint, compound=tk.LEFT, text='IMPRIMIR', underline=0,command=self.imprimeDetalle)
        self.btnimprimir.pack(side=tk.RIGHT, padx=3, fill=tk.Y)
        self.statusbar.createTip(self.btnimprimir, "Generar listado detalle de pedidos [Alt-I]")
        # Datos del cliente al que facturaremos
        self.lblcli['text']=cliente
        self.lblnif['text']=nif
        self.lblfpa['text']=fpago
        # Only debug
        # print('Ultima factura: ' + str(self.ultfac))
        # print('Se facturará si no lo cambio el numero: ' + str(self.ultfac+1) )
        # Cargamos la última factura de luzYgas emitida
        self.rstfra = db.consultar('SELECT * FROM facturas ORDER BY id',con=self.cnn)[-1]
        # Y tomamos arrastrado el import fijo facturado
        self.fijo = self.rstfra['fixfac']
        #
        # Comprobar la validez del numero de factura
        #
        mesAfac=(datetime.date.today().month)
        if mesAfac == 1:
            mesAfac = 12

        self.txtmes.set(mesAfac)
        self.txtper.set_value(int(self.ultfac/1000))
        self.txtfac.set_value(self.ultfac+1)
        newfecfac=self.fechaFacturaReal()
        self.txtfec.set_date(newfecfac)
        # self.lbliva

        self.rellenaConcepto()
        self.txtfijo.set_texto(f"{self.fijo:5.2f}")
        self.txtvar.set_texto("0.00")
        self.lbliva['text']=f"{cmvar.properties.getProperty('defiva'):5.2f}"
        self.lblirpf['text']=f"{cmvar.properties.getProperty('defirpf'):5.2f}"
        self.populatetv()

        self.tv.bind("<Double-Button-1>", self.on_vercon)
        # Selección desde Teclado alfabético
        self.tv.bind('<Return>', self.on_vercon)
        # Selección desde Teclado numérico
        self.tv.bind('<KP_Enter>', self.on_vercon)

        self.txtmes.bind('<<Increment>>', self.populatetv)
        self.txtmes.bind('<<Decrement>>', self.populatetv)
        self.bind('<Alt-I>', self.imprimeDetalle)
        self.bind('<Alt-i>', self.imprimeDetalle)        

    def declaraFrames(self):
        # Principal
        self.frmDetalle=tk.Frame(self)
        # Cabecera
        self.frmCab=tk.Frame(self.frmDetalle)
        # Detalle de composición de comisiones
        self.frmCom=tk.Frame(self.frmDetalle)
        # Pie - Resumen de totales
        self.frmPie=tk.Frame(self.frmDetalle, highlightbackground="black", highlightthickness=1)
        #
        self.controlsCab()
        self.controlsCom()
        self.controlsPie()
        self.frmDetalle.pack(fill=tk.BOTH, expand=True)    
        
        self.center()

    def controlsCab(self):
        # Widgets del Frame frmCab que está dentro de frmDetalle
        tk.Label(self.frmCab, text='Periodo:').grid(row=0, column=0,sticky=tk.E)
        self.txtper=Numbox(self.frmCab, width=4)
        self.txtper.grid(row=0, column=1, ipadx=3, ipady=3, padx=3, pady=3, sticky=tk.W)
        tk.Label(self.frmCab, text='Mes:').grid(row=0,column=2)
        self.txtmes=ttk.Spinbox(self.frmCab, from_=1, to=12, increment=1, width=2, wrap=True)
        self.txtmes.grid(row=0, column=3, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmCab, text='Cliente:').grid(row=0,column=4, sticky=tk.E)
        self.lblcli=tk.Label(self.frmCab, bg='white',borderwidth=1,relief="solid", width=8,anchor=tk.W)
        self.lblcli.grid(row=0, column=5, columnspan=2,sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmCab, text='NIF:').grid(row=0, column=7)
        self.lblnif=tk.Label(self.frmCab, bg='white',borderwidth=1,relief="solid", width=10,anchor=tk.W)
        self.lblnif.grid(row=0, column=8, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmCab, text='Factura:').grid(row=1, column=0)
        self.txtfac=Numbox(self.frmCab, width=7)
        self.txtfac.grid(row=1, column=1, columnspan=2, ipadx=3, ipady=3, padx=3, pady=3,sticky=tk.W)
        tk.Label(self.frmCab, text='Fecha:').grid(row=1, column=3)
        self.txtfec=DateEntry(self.frmCab, date_pattern='dd-MM-yyyy')
        self.txtfec.grid(row=1, column=4, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmCab, text='Concepto:').grid(row=1, column=5)
        self.txtcnp=Textbox(self.frmCab, width=50, tipo=Textbox.MAYUSCULAS)
        self.txtcnp.grid(row=1, column=6,columnspan=3,sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        # Expand columnas
        self.frmCab.columnconfigure(6,weight=1)
        # Empaquetamos frmCab
        self.frmCab.pack(side=tk.TOP, fill=tk.X)

    def controlsPie(self):
        # Widgets dentrol de frmPie que está dentro de frmDetalle
        tk.Label(self.frmPie, text='Contratos:').grid(row=0, column=0,sticky=tk.E)
        self.lblcon=tk.Label(self.frmPie, bg='white',borderwidth=1,relief="solid", width=3,anchor=tk.E)
        self.lblcon.grid(row=0, column=1, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmPie, text='Fijo:').grid(row=0, column=2,sticky=tk.E)
        self.txtfijo=Numbox(self.frmPie, width=8,decimales=2)
        self.txtfijo.grid(row=0, column=3, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmPie, text='Variable:').grid(row=0, column=4,sticky=tk.E)
        self.txtvar=Numbox(self.frmPie, width=8,decimales=2)
        self.txtvar.grid(row=0, column=5, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmPie, text='Comisión:').grid(row=0, column=7,sticky=tk.E)
        self.lblcms=tk.Label(self.frmPie, bg='white',borderwidth=1,relief="solid", width=8,anchor=tk.E)
        self.lblcms.grid(row=0, column=8, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmPie, text='Importe:').grid(row=0, column=10,sticky=tk.E)
        self.lblimp=tk.Label(self.frmPie, bg='white',borderwidth=1,relief="solid", width=8,anchor=tk.E)
        self.lblimp.grid(row=0, column=11, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        # Segunda Linea
        tk.Label(self.frmPie, text='Forma de pago:').grid(row=1, column=0,sticky=tk.E)
        self.lblfpa=tk.Label(self.frmPie, width=45, bg='white',borderwidth=1,relief="solid",anchor=tk.E)
        self.lblfpa.grid(row=1, column=1, columnspan=3, sticky=tk.EW, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmPie, text='IRPF:').grid(row=1, column=4,sticky=tk.E)
        self.lblirpf=tk.Label(self.frmPie, bg='white',borderwidth=1,relief="solid", width=5,anchor=tk.E)
        self.lblirpf.grid(row=1, column=5,sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.lblimpirpf=tk.Label(self.frmPie, bg='white',borderwidth=1,relief="solid", width=7,anchor=tk.E)
        self.lblimpirpf.grid(row=1, column=6,sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmPie, text='IVA:').grid(row=1, column=7,sticky=tk.E)
        self.lbliva=tk.Label(self.frmPie, bg='white',borderwidth=1,relief="solid", width=5,anchor=tk.E)
        self.lbliva.grid(row=1, column=8, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        self.lblimpiva=tk.Label(self.frmPie, bg='white',borderwidth=1,relief="solid", width=8,anchor=tk.E)
        self.lblimpiva.grid(row=1, column=9,sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        tk.Label(self.frmPie, text='Total:').grid(row=1, column=10,sticky=tk.E)
        self.lbltot=tk.Label(self.frmPie, bg='white',borderwidth=1,relief="solid", width=8,anchor=tk.E)
        self.lbltot.grid(row=1, column=11, sticky=tk.W, ipadx=3, ipady=3, padx=3, pady=3)
        # Expand column (importe)
        self.frmPie.columnconfigure(10, weight=1)
        # Empaquetamos frmPie
        self.frmPie.pack(side=tk.TOP, fill=tk.X)

    def controlsCom(self):
        # Aqui treeview con detalle de composicon de la parte variable.
        self.titulos=['CONTRATO','TIPO','CUPS','CLIENTE','DIRECCION','COMISION']
        self.campos=['numero','tipo','cups','cliente','direccion','comision']
        self.alinea=['e','center','w','w','w','e']
        self.tv = ttk.Treeview(self.frmCom, columns=self.campos, selectmode=tk.BROWSE)
        for i in range(len(self.campos)):
            self.tv.column(self.campos[i],anchor=self.alinea[i])
            self.tv.heading(self.campos[i],anchor=self.alinea[i], text=self.titulos[i])

        self.tv.column('#0', width=0, stretch=tk.NO)
        self.tv.column('numero',width=95,stretch=tk.NO)
        self.tv.column('tipo',width=50,stretch=tk.NO)
        self.tv.column('cups',width=220,stretch=tk.NO)
        self.tv.column('cliente',width=280)
        self.tv.column('direccion',width=280)
        self.tv.column('comision',width=90,stretch=tk.NO)
        # Barra de desplazamiento por si es necesaria
        self.vscrlbar = Scrollbar(self.frmCom, orient="vertical", command=self.tv.yview)
        self.vscrlbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tv.configure(yscrollcommand=self.vscrlbar.set)
        self.tv.pack(fill=tk.BOTH,expand=True, pady=10)
        self.frmCom.pack(fill=tk.BOTH, expand=True)

    def populatetv(self, evt=None):
        # Cargamos contratos asociados a esta factura
        mes=int(self.txtmes.get())
        strsqlcon=f"select * from vselecon where estado=True and mes={mes}"
        # f'SELECT * FROM vLineasCms WHERE fac={self.factura} ORDER BY conlin'
        self.rstcon=db.consultar(strsqlcon, con=self.cnn)
        self.tv.delete(*self.tv.get_children())
        self.update()
        # Si no hay datos no hacemos nada
        if len(self.rstcon) == 0:
            return

        comisiones = 0
        # Cargamos los datos en el Treeview
        for i in range(len(self.rstcon)):
            valores=list(self.rstcon[i][k] for k in self.campos)
            comisiones += valores[-1]
            self.tv.insert('', tk.END, text='', values=valores, iid=str(i))

        self.tv.focus('0')
        self.tv.selection_set('0')
        self.tv.see('0')

        self.lblcon['text']=str(len(self.rstcon))
        self.lblcms['text']=f"{comisiones:7.2f}"
        self.recalcula()


    def on_vercon(self, evt=None):
        idxcon=self.tv.focus()
        idcontrato=self.tv.item(idxcon)['values'][0]
        frmvercon=Vercontrato(self, idcon=idcontrato)
        self.withdraw()
        self.wait_window(frmvercon)
        self.show()
        
        return
        
    def fechaFacturaReal(self):
        per = int(self.txtper.get_value())
        mes = int(self.txtmes.get())
        if mes==12:
            mes = 0
            per+=1

        return date(per, mes+1,1)+datetime.timedelta(days=-1)

    def rellenaConcepto(self):

        meses=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCUTUBRE','NOVIEMBRE','DICIEMBRE']
        mes=self.txtfec.get_date().month
        periodo=self.txtfec.get_date().year
        concepto="COMISIONES DEVENGADAS EN {} DE {}".format(meses[mes], periodo)
        self.txtcnp.set_texto(concepto)

    def recalcula(self):
        fijo = self.txtfijo.get_value()
        variable = self.txtvar.get_value()
        comision = float(self.lblcms['text'])
        importe = fijo+variable+comision
        self.lblimp['text']=f"{importe:7.2f}"
        iva = float(self.lbliva['text'])
        irpf = float(self.lblirpf['text'])
        impiva= round((importe/100)*iva,2)
        impirpf=round((importe/100)*irpf,2)
        self.lblimpiva['text']=f'{impiva:.2f}'
        self.lblimpirpf['text']=f'{impirpf:.2f}'
        total=importe+impiva-impirpf
        self.lbltot['text']=f'{total:.2f}'
        self.rellenaConcepto()

    def imprimeDetalle(self, *args):
        self.prop=cmvar.properties
        #defecha=datetime.date.strftime(self.txtfec.get(), "%d-%m%Y")
        defecha=self.txtfec.get()
        titulo=f"CONTRATOS INCLUIDOS EN PROXIMA FACTURA ({self.ultfac+1}) DE FECHA {defecha}"
        #
        fichero=self.prop.getProperty('informes')+os.sep+"preFra"+str(self.ultfac+1)+'.txt'
        # print("Se imprimira: " + fichero)
        # print("Con titulo: " + titulo)

        if os.path.isfile(fichero):
            strmsg=f"El fichero {fichero} ya existe\nReimpresion hará que se pierdan los datos anteriores."
            opciones=['Reimprimir', 'Editar existente', 'Cancelar']
            ok = dlg.dialogo(self, "IMPRESION DETALLE DE FACTURA", strmsg, opciones, dlg.ADVERTENCIA).showmodal()
            if ok == 2:
                return
            
            if ok == 1:
                frmedt = frmEditor(self, name='',archivo=fichero)
                self.wait_window(frmedt)
                return
            
        ok = dlg.dialogo(self, "IMPRESION DETALLE", 
                         "Se imprimirán los contratos asociados a proxima factura",
                         ['Valorado','Sin valor'],dlg.PREGUNTA).showmodal()

        # Creamos fichero (vacio) para impresion texto
        ficlist=open(fichero,'w')
        # Totalizadores  contadores
        lineasPorPagina=80
        lineas=0
        pagina=1
        
        if ok == 1:
            for i in range(len(self.rstcon)):
                if lineas==0:
                    # Cabecera
                    ficlist.write('\n')
                    lineacab='{:<69} {:%d-%m-%Y}'.format(titulo, date.today())
                    ficlist.write(lineacab)
                    ficlist.write('\n')
                    ficlist.write(('-'*80)+'\n')
                    #          12345679012345679801234567890
                    lineacab ='{:<7} {:<20} {:<25} {:<25}\n'.format('CONTRATO','CUPS','CLIENTE','P.SUMINISTRO')
                    ficlist.write(lineacab)
                    ficlist.write(('-'*80)+'\n')
                    lineas += 6
                # datetime.datetime.strptime(self.registro['fecfac'][:10],'%Y-%m-%d').date().strftime('%d-%m-%y')
                contrato=self.rstcon[i]['numero']
                cups=self.rstcon[i]['cups']
                cliente=self.rstcon[i]['cliente'][:25]
                psum=self.rstcon[i]['direccion'][:25]
                linea='{:>7d} {:<20} {:<25} {:<25}\n'.format(contrato,cups,cliente,psum)
                ficlist.write(linea)
                # Acumuladores
                lineas +=1

                if lineas > lineasPorPagina:
                    ficlist.write(('-'*80)+'\n')
                    ficlist.write(f'Pag: {pagina:>3}\n')
                    ficlist.write(('-'*80)+'\n\n')
                    lineas = 0


            # Salimos del bucle porque ya no hay mas lineas para imprimir
            for x in range(lineas, lineasPorPagina-4):
                # Rellenamos con lineas vacías hasta el pie de pagina
                ficlist.write('\n')

            ficlist.write(('-'*80)+'\n')
            # Imprimimos pie de pagina
            lineaPie = f'Pag: {pagina:>3}\n'
            ficlist.write(lineaPie)
            ficlist.write(('-'*80)+'\n\n')
        else:
            # ficlist.close()
            # return
            totalComision=0
            for i in range(len(self.rstcon)):
                if lineas==0:
                    # Cabecera
                    ficlist.write('\n')
                    lineacab='{:<69} {:%d-%m-%Y}'.format(titulo, date.today())
                    ficlist.write(lineacab)
                    ficlist.write('\n')
                    ficlist.write(('-'*80)+'\n')
                    #  
                    lineacab ='{:<7} {:<20} {:<37} {:<6} {:>6}\n'.format('NUMERO','CUPS','CLIENTE','ATR','CMSION')
                    ficlist.write(lineacab)
                    ficlist.write(('-'*80)+'\n')
                    lineas += 6

                contrato=self.rstcon[i]['numero']
                cups=self.rstcon[i]['cups']
                cliente=self.rstcon[i]['cliente'][:37]
                comision=self.rstcon[i]['comision']
                atr = self.rstcon[i]['codtfa']
                totalComision += comision
                linea='{:>7d} {:<20} {:<37} {:<6} {:>6.2f}\n'.format(contrato,cups,cliente,atr,comision)
                ficlist.write(linea)
                # Acumuladores
                lineas +=1

                if lineas > lineasPorPagina:
                    ficlist.write(('-'*80)+'\n')
                    ficlist.write(f'Pag: {pagina:>3}\n')
                    ficlist.write(('-'*80)+'\n\n')
                    lineas = 0


            # Salimos del bucle porque ya no hay mas lineas para imprimir
            for x in range(lineas, lineasPorPagina-4):
                # Rellenamos con lineas vacías hasta el pie de pagina
                ficlist.write('\n')

            ficlist.write(('-'*80)+'\n')
            # Imprimimos pie de pagina
            lineaPie = f'Pag: {pagina:>3} Contratos:{len(self.rstcon):3d}'+(' '*43)+f'Total:{totalComision:>9.2f}\n'
            ficlist.write(lineaPie)
            ficlist.write(('-'*80)+'\n\n')

            
        ficlist.close()
        strmsg="Visualizar el listado en el Editor?"
        ok = dlg.dialogo(self, "IMPRESION REALIZADA", strmsg, ['Aceptar','Cancelar'], dlg.PREGUNTA).showmodal()
        if ok == 0:
            frmedt = frmEditor(self, name='',archivo=fichero)
            self.wait_window(frmedt)
        
        return
        # if ok == tk.YES:
        #     subprocess.run(["xed", fichero])

    def confirmar(self, *args):
        # Facturar
        # 1º Registramos la factura REAL en fac
        # La conexión ya existe porque se ha tenido que obtener
        # información de la base de datos FAC y no se ha cerrado
        factura = self.txtfac.get_value()
        fechafac= self.txtfec.get_date().strftime('%Y-%m-%d 00:00:00')
        cliente = cmvar.properties.getProperty('clifacluz')
        concepto= self.txtcnp.get()
        importe = float(self.lblimp['text'])
        iva     = cmvar.properties.getProperty('defiva')
        irpf    = cmvar.properties.getProperty('defirpf')
        fpago   = self.lblfpa['text']
        strsql="INSERT INTO facturas VALUES({},'{}',{},'{}',{},{},{},'{}',1)"
        registro=[factura,fechafac,cliente,concepto,importe,iva,irpf,fpago]
        strsql = strsql.format(*registro)
        # Grabamos registro de factura en fac.db
        try:
            db.actualiza(strsql, con=self.confac)
        except:
            print("Error en la grabación de la factura en fac.db")
            dlg.dialogo(self,"ERROR GRABACION FACTURA","No se ha guardado la informacion de factura "+str(factura)).showmodal()
            return
        
        # Guardamos registro de factura en gasyluz.db
        mes = int(self.txtmes.get())
        per = self.txtper.get_value()
        fjo = self.txtfijo.get_value()
        var = self.txtvar.get_value()
        cms = float(self.lblcms['text'])
        registro=[factura,fechafac,mes,per,concepto,iva,irpf,fjo,var,cms]
        strsql="INSERT INTO facturas VALUES({},'{}',{},{},'{}',{},{},{},{},{})"
        strsql = strsql.format(*registro)
        # Grabamos registro de factura
        try:
            db.actualiza(strsql, con=self.cnn)
        except:
            print("Error en la grabación de la factura en gasyluz.db")
            dlg.dialogo(self,"ERROR GRABACION FACTURA","Se ha facturado pero no guardado informacion de factura "+str(factura)).showmodal()
            return
        
        # Actualizamos lineas de contratos facturados
        # que están en self.rstcon
        for reg in self.rstcon:
            contrato=reg['numero']
            comision=reg['comision']
            strsql=f"INSERT INTO lineas VALUES({factura},{contrato},{comision})"
            try:
                db.actualiza(strsql,con=self.cnn)
            except:
                print("Error grabando lineas de contratos facturados")
                dlg.dialogo(self,"ERROR EN LINEAS",f"Se ha fallado al grabar contrato{contrato}").showmodal()
                return
            
            strsql =f"UPDATE contratos SET mescon={mes}, percon={per} WHERE id={contrato}"
            try:
                db.actualiza(strsql, con=self.cnn)
            except:
                print(f"Error actualizando datos de contrato {contrato} al facturar")
                dlg.dialogo(self,"ERROR UPDATE CONTRATO",f"Se ha fallado al actualizar el contrato{contrato}").showmodal()
                return

        # Llegados aquí, se ha guardado toda la informaciónb            
        dlg.dialogo(self,"GRABACION DE FACTURA",f"Se ha grabado la factura {factura} con éxito").showmodal()
