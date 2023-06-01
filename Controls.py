import tkinter as tk


class Textbox(tk.Entry):
    
    NORMAL = 0
    MAYUSCULAS = 1
    CAPITAL = 2
    MINUSCULAS = 3
    TITLE = 4

    def __init__(self, padre, tipo=0, *args, **kwargs):
        """
        Entry con funciones de >> mayusculas - uppercase = True
                               >> numericas - typenum = decimales admitidos (0=Entero)
                               >> No acepta más caracteres que el width declarado
        """
        super().__init__(padre, *args, **kwargs)

        # Controlamos pulsaciones para limitar width
        self.var = tk.StringVar()
        self['textvariable']=self.var
        self.var.trace("w", lambda name1, name2, op, widget=self.var: self.toTipo(widget,name1,name2,op))

        self.tipo = tipo
    
            
    def toTipo(self, var, name1, name2, op):
        '''
        Convierte texto dependiendo de la opcion elegida
        '''

        texto = var.get()
        if self.tipo ==  Textbox.MAYUSCULAS:
            texto = texto.upper()
            texto.replace('ñ','Ñ')
        
        elif self.tipo == Textbox.MINUSCULAS:
            texto = texto.lower()
            texto.replace('Ñ', 'ñ')
        
        elif self.tipo == Textbox.CAPITAL:
            texto = texto.capitalize()

        elif self.tipo == Textbox.TITLE:
            texto = texto.title()

        # Controlamos que el ancho del texto no sea mayor que 
        # el width declarado    
        if self['width'] > 0:
            texto = texto[:self['width']]
        
        var.set(texto)

    def set_texto(self, texto):
        # Si es de tipo texto (MAYUSCULAS, MINUSCULAS....)
        if self.tipo in range(5) :
            # Guardamos estado inicial del control
            estado=self['state']
            # Lo ponemos a normal para aceptar insert
            self['state']='normal'
        else:
            # Sino no hacemos nada
            return

        self.delete(0, tk.END)
        v = str(texto)
        # Insertamos caracter a caracter
        for c in v:
            self.insert(tk.END, c)
        # Y devolvemos el estado anterior.
        self['state']=estado

        return


class Numbox(Textbox):
    
    def __init__(self, padre, decimales=0, *args, **kwargs):
        """
        Entry con funciones de >> numericas - typenum = decimales admitidos (0=Entero)
                               >> No acepta más caracteres que el width declarado
        """
        super().__init__(padre, tipo=0, *args, **kwargs)

        self.decimales = decimales
        # Enlazamos tecla [Enter] con Tab
        self.bind('<KP_Enter>', lambda x: padre.event_generate('<Tab>'))
        # Registramos validación de las pulsaciones
        self['validate'] = 'key'
        self['validatecommand'] = (self.register(self.onlynum),'%P','%d','%S')

        self.config(justify=tk.RIGHT)

    def onlynum(self, texto, accion, caracter):
        ''' 
        Acepta unicamente digitos numéricos
        '''
        if accion == '1':       # Insertar
            # Es el punto decimal y no hay otro
            if caracter == '.':
                if self.decimales > 0:
                    # Puede haber un punto o ninguno
                    if texto.find('.') == 0:
                        # No puede estar sin un entero anterior
                        return False
                    if self['width'] > 0 and texto.find('.') == self['width']-1:
                        # Tampoco tiene sentido que sea el último caracter
                        return False
                    if texto.count('.') == 1:
                        return True
                else:
                    # No admite decimales
                    return False
            
            if self.decimales > 0 and texto.count('.') == 1:
                # No puede haber más decimales de los declarados 
                # para ser admitidos
                if texto[::-1].find('.') > self.decimales:
                    return False

            # NUMEROS ENTEROS
            return caracter.isdigit()

        # Falta controlar punto decimal y numero de decimales

        return True    
    
    def set_value(self, valor):
        # Guardamos estado inicial del control
        estado=self['state']
        # Lo ponemos a normal para aceptar insert
        self['state']='normal'

        self.delete(0, tk.END)
        # Convertimos el valor a String
        v = str(valor)
        # Y lo introducimos caracter a caracter
        for c in v:
            self.insert(tk.END, c)

        self['state']=estado

        return

    def get_value(self):
        if self.decimales > 0:  # Si decimales (devolvemos float)
            valor = float(self.get())
        else:                   # No decimales (devolvemos entero)
            valor = int(self.get())
        
        return valor