from tkinter import Frame, StringVar
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as scrolledtext

import serial
import time
import threading
import serial.tools.list_ports

'''
def find_USB_device(USB_DEV_NAME=None):
    # Funcion alternativa para encontrar puertos seriales, No es usada en este app

    myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    print(myports)
    usb_port_list = [p[0] for p in myports]
    usb_device_list = [p[1] for p in myports]
    print(usb_device_list)

    if USB_DEV_NAME is None:
        return myports
    else:
        USB_DEV_NAME = str(USB_DEV_NAME).replace("'", "").replace("b", "")
        for device in usb_device_list:
            print("{} -> {}".format(USB_DEV_NAME, device))
            print(USB_DEV_NAME in device)
            if USB_DEV_NAME in device:
                print(device)
                usb_id = device[device.index("COM"):device.index("COM")+4]
            
                print("{} port is {}".format(USB_DEV_NAME, usb_id))
                return usb_id
'''

class MainFrame(Frame):
    def __init__(self, master = None):
        super().__init__(master, width = 600, height = 600)                
        self.master = master    
        self.master.protocol('WM_DELETE_WINDOW', self.askQuit)
        self.pack()

        self.hilo1 = threading.Thread(target = self.getDataSerial, daemon = True)
        self.dispositivo = None
        #self.portlist=find_USB_device()
        #self.items=[p[0] for p in self.portlist]#["COM1","COM2"]
        self.strComando = StringVar()
        self.my_isOpen = False

        self.valPuerto = StringVar()
        self.valVelocidad = StringVar()
        self.create_widgets()
        self.isRun = False

    def askQuit(self):
        if self.isRun:
            self.isRun = False
            self.hilo1.join(0.1)
        if self.my_isOpen: 
            self.dispositivo.close()
        self.master.quit()
        self.master.destroy()
        print("*** finalizando...")

    def getDataSerial(self):
        while self.isRun:
            if self.my_isOpen:
                if self.dispositivo.in_waiting > 0:
                    cad = self.dispositivo.readline().decode('ascii').strip() + '\n'
                    if cad:
                        self.txtRecepcion.insert(tk.END, cad)  
                        self.txtRecepcion.see('end')       
               
    def sendCommand(self):
        cad = self.strComando.get() + '\n'
        self.txtRecepcion.insert(tk.END, '>>'+cad)
        self.txtRecepcion.see('end')
        print(cad)
        self.dispositivo.write(cad.encode('ascii'))

    def clsRecepcion(self):
        self.txtRecepcion.delete("1.0", "end")
        
    def serial_ports(self):
        if not serial.tools.list_ports.comports():
            return "NO_PUERTOS"
        else:
            #global ports
            ports = serial.tools.list_ports.comports()
            # puertos
            print("ports: ", ports[0][0])
            return ports

    def conect(self):
        if self.btnConectar.cget("text") == 'Conectar':
            print(self.valPuerto.get())
            if self.valPuerto.get() == "NO_PUERTOS":
                print("No se puede conectar")
            else:
                puerto = self.valPuerto.get().split("-")[0].strip()
                print(puerto) # Validar en Linux
                print(self.valVelocidad.get())
                self.dispositivo = serial.Serial(puerto, int(self.valVelocidad.get()))

                while not self.dispositivo.is_open: # espera que el puerto este abierto
                    time.sleep(0.01)

                self.my_isOpen = True
                self.isRun = True

                if not self.hilo1.is_alive():
                    self.hilo1.start()

                self.txtComando.configure(state = 'normal')
                self.btnEnviar.configure(state = 'normal')
                self.btnLimpiar.configure(state = 'normal')
                self.txtRecepcion.configure(state = 'normal')
                self.btnConectar.configure(text = 'Desconectar')

                self.cmbPuerto.configure(state = 'disabled')
                self.cmbVelocidad.configure(state = 'disabled')
        else: # Desconectar
            self.my_isOpen = False
            self.dispositivo.close()

            self.btnConectar.configure(text = 'Conectar')
            self.cmbPuerto.configure(state = 'normal')
            self.cmbVelocidad.configure(state = 'normal')
            self.txtComando.configure(state = 'disabled')
            self.btnEnviar.configure(state = 'disabled')
            self.txtRecepcion.configure(state = 'disabled')
            self.btnLimpiar.configure(state = 'disabled')

    def port_changed(self, event):
        self.cmbVelocidad.configure(state = 'enabled')

    def baud_changed(self, event):
        self.btnConectar.configure(state = 'normal')   

    def create_widgets(self):
        # Conexion Serial ***
        grpSerialInfo = tk.LabelFrame(self, 
                                       text = "Conexion Serial",
                                       height = 75,
                                       width = 590
                                      ).place(x=5, y=0)
        
        tk.Label(grpSerialInfo, text="Puerto:").place(x=10, y=20)
        self.cmbPuerto = ttk.Combobox(grpSerialInfo,
                                 width = 38,
                                 values = self.serial_ports(),
                                 textvariable = self.valPuerto                         
                                )
        self.cmbPuerto.bind('<<ComboboxSelected>>', self.port_changed)
        self.cmbPuerto.place(x=10, y=40)

        tk.Label(grpSerialInfo, text="Velocidad:").place(x=340, y=20)
        optVelocidad = ("2400", "4800", "9600", "14400", "19200", "28800", "38400", "57600", "115200")
        self.cmbVelocidad = ttk.Combobox(grpSerialInfo,
                                    width = 14,   
                                    values = optVelocidad,
                                    textvariable = self.valVelocidad,
                                    state = "disabled"                      
                                    )
        self.cmbVelocidad.bind('<<ComboboxSelected>>', self.baud_changed)
        self.cmbVelocidad .place(x=340, y=40)

        self.btnConectar = tk.Button(grpSerialInfo, text="Conectar", width = 10, command = self.conect, state = "disabled")
        self.btnConectar.place(x=480, y=38)
        # Transmicion de Datos ***
        grpDataSend = tk.LabelFrame(self, 
                                       text = "Transmicion de Datos",
                                       height = 60,
                                       width = 590
                                      ).place(x=5, y=75)
        
        self.txtComando = tk.Entry(grpDataSend,
                                 width = 57,
                                 textvariable = self.strComando,
                                 state = "disabled"                   
                                )
        self.txtComando.place(x=10, y=100)

        self.btnEnviar = tk.Button(grpDataSend, text="Enviar", command = self.sendCommand, width = 10, state = "disabled")
        self.btnEnviar.place(x=480, y=98)
        # Recepcion de Datos ***
        grpDataGet = tk.LabelFrame(self, 
                                       text = "Recepcion de Datos",
                                       height = 400,
                                       width = 590
                                      ).place(x=5, y=135)
        
        self.txtRecepcion = scrolledtext.ScrolledText(grpDataGet, undo = True, width = 70, height = 23, wrap = 'word')
        
        self.txtRecepcion.pack()
        self.txtRecepcion.configure(state = 'disabled')
        self.txtRecepcion.place(x=10, y=155)

        self.btnLimpiar = tk.Button(grpDataGet, text = "Limpiar", command = self.clsRecepcion, width = 10, state = "disabled")
        self.btnLimpiar.place(x=250, y=560)

if __name__=="__main__":
    root = tk.Tk()
    root.wm_title("Terminal Serial")
    root.resizable(False, False)
    app = MainFrame(root)
    app.mainloop()
    
