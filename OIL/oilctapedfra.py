from Forms import *
from DBsql import *
import tkinter as tk
from tkinter import messagebox
from tkinter import Scrollbar
from OIL.pedidos import frmfichaped
import time

class CtaPedFra(Form):
    """
        Debería ser instanciado desde un FormData.
        Treeview para mostrar tabla de datos que
        permite seleccionar registro.
        Recibe el pedido seleccionado actualmente:
            
        El result será obtenido de la view sqlite3 vseleped
        
    """

    def __init__(self, hcaller, idfra):
        """ Constructor: Recibe parámetro del caller para devolver
            el control cuando cerremos app
            idfra = Numero de factura  en la que estan incluidos los pedidos
                    a visualizar
        """
        # Conexión a datos
        self.cnn="OIL"
        # Componemos filtro

        strsql = 'SELECT * FROM seleped WHERE {} = {}'.format('factura', idfra)
        # Cargamos datos a mostrar (la consulta esta creada con order by fecped)
        self.rstped = db.consultar(strsql, con=self.cnn)
        # Instanciamos nivel superior para que no falle caso de salir
        # porque no hay registros
        super().__init__(hcaller)
        # Si recibimos una posicion < que 0 hay que situarse en ultimo registro
        # self.posicion = len(self.rstped)-1
        # 
        self.hasdata = True
        if len(self.rstped) <= 0:
            self.hasdata = False
            
        # Siempre y cuando el resultado contenga datos.
        # if self.hasdata:
        #     self.fdesde = datetime.datetime.strptime(self.rstped[0]['fecped'][:10],'%Y-%m-%d').date()
        #     self.fhasta = datetime.datetime.strptime(self.rstped[-1]['fecped'][:10],'%Y-%m-%d').date()

        # Inicializamos entorno de datos
        self.titulos=['ID', 'FECHA','CLIENTE','PROD.','LTS','PVP','IMPORTE','COMISION','IMPORTE']
        self.campos=['pedido','fecha','cliente','producto','cantidad','precio','importe','comision','impcms']
        # Alineación: E -> Right    W -> Left
        self.alinea=[tk.E,tk.W,tk.W,tk.W,tk.E,tk.E,tk.E,tk.E,tk.E]
        self.anchos=[70,90,300,110,100,100,100,100,100,100]
        self.tv = ttk.Treeview(self, columns=self.campos, selectmode=tk.BROWSE)
        self.tv.column('#0', width=0, stretch=tk.NO)
        self.frmTotales = tk.Frame(self, highlightbackground="black", highlightthickness=1)
        tk.Label(self.frmTotales, text= "TOTALES").pack(side=tk.LEFT)
        self.lbltocms = tk.Label(self.frmTotales, width=7, background='white')
        self.lbltocms.pack(side=tk.RIGHT)
        tk.Label(self.frmTotales, text= "COMISION: ").pack(side=tk.RIGHT)
        self.lbltolitros = tk.Label(self.frmTotales, width=7, background='white')
        self.lbltolitros.pack(side=tk.RIGHT)
        tk.Label(self.frmTotales, text= "LITROS: ").pack(side=tk.RIGHT)

        self.frmTotales.pack(side=tk.BOTTOM, fill=tk.X)
        anchototal = 0
        for i in range(len(self.campos)):
            anchototal+=self.anchos[i]
            self.tv.column(self.campos[i], anchor=self.alinea[i], width=self.anchos[i])
            self.tv.heading(self.campos[i], text=self.titulos[i], anchor=self.alinea[i])

        self.statusbar.showMensaje("Pulse [Alt-S] para salir")
        # 
        tk.Label(self.buttonbar, text="Pedidos incluidos en FACTURA: ").pack(side=tk.LEFT, padx=3)
        self.txtfactura=tk.Label(self.buttonbar, background='white', width=6, text=str(idfra),anchor=tk.E)
        self.txtfactura.pack(side=tk.LEFT, padx=3, pady=6, fill=tk.Y)
        # Barra de desplazamiento
        self.vscrlbar = Scrollbar(self, orient="vertical", command=self.tv.yview)
        self.vscrlbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tv.configure(yscrollcommand=self.vscrlbar.set)

        self.tv.pack(fill=tk.BOTH, expand=True, pady=10)
        # 
        self.grab_set()
        #
        # Eventos
        # Anchura mínima para controles de busqueda/orden, etc.
        anchototal += 170
            
        if anchototal > self.winfo_screenwidth():
            anchototal = self.winfo_screenwidth()

        self.title("CONSULTA PEDIDOS INCLUIDOS EN FACTURA "+str(idfra))
        
        alto = int(self.winfo_screenheight()/2)
        self.geometry(str(anchototal)+'x'+str(alto))
        self.center()

        
        self.loadData()
        
        self.tv.focus_set()

        if len(self.rstped) <= 0:
            if idfra == 0:
                messagebox.showerror("ERROR","No hay pedidos pendientes de Facturar")
            else:
                messagebox.showerror("ERROR","No hay pedidos incluidos en esta Factura")
    
        self.statusbar.showMensaje("Visualizar Ficha Registro de Pedido [Doble-Click]")
        # Para ver la ficha del pedido seleccionado.
        self.tv.bind("<Double-Button-1>", self.on_sele)
        # Selección desde Teclado alfabético
        self.tv.bind('<Return>', self.on_sele)
        # Selección desde Teclado numérico
        self.tv.bind('<KP_Enter>', self.on_sele)

    def on_sele(self, *args):
        # Este evento nos permitira mostrar un pantallazo
        # a modo de ficha del pedido seleccionado.
        # Asignamos numero de pedido a variable pedselec
        # pedselec = self.result[int(self.tv.focus())]['pedido']
        # messagebox.showinfo('VER PEDIDO','Veremos el pedido: '+pedselec, parent=self)
        # La devolvemos en la StringVar posicion
        #self.posicion.set(pedselec)
        # Generamos el evento escuchado por el hcaller 
        # que mostrará el registro seleccionado
        # self.event_generate('<<gotodata>>')
        # Y cerramos
        # self.closer()
        itseleccionado=self.tv.selection()[0]
        pedselec=self.tv.item(itseleccionado)['values'][self.tv['columns'].index('pedido')]
        # Cargar formulario para visualizar pedido
        self.update()
        time.sleep(1)
        self.withdraw()
        self.frmver = frmfichaped(self, pedselec)
        self.wait_window(self.frmver)
        self.show()
        self.lift()

    def on_cancel(self, *args):
        
        self.closer()
    
    def loadData(self, *args):
        if self.hasdata == False:
            return
              
        # Limpiamos de resultados anteriores el Treeview
        self.tv.delete(*self.tv.get_children())
        self.update()
        # Inicio contadores
        litros = 0
        cmsion = 0
        # Cargamos los datos en el Treeview
        
        for i in range(len(self.rstped)):
            valores=list(self.rstped[i][k] for k in self.campos)
            # Los 4 ultimos campos los mostramos con decimales formateados
            litros += self.rstped[i]['cantidad']
            cmsion += self.rstped[i]['impcms']
            for j in range(-4,0,2): 
                valores[j]=f'{valores[j]:5.4f}'
                valores[j+1]=f'{valores[j+1]:5.2f}'
                
            self.tv.insert('', tk.END, text='', values=valores, iid=str(i))

        # Mostramos valores totales
        self.lbltocms.config(text='{:.2f}'.format(cmsion))
        self.lbltolitros.config(text='{:.0f}'.format(litros))

        