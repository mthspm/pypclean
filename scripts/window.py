from typing import Optional, Tuple, Union
from tkinter import filedialog
import customtkinter as ctk
from CTkTable import CTkTable
from PIL import Image
from utils import *
from scan import *
from settings import *
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from generator import LogGenerator
from cleaner import Cleaner

class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, geometry="400x400",title="Window", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry = geometry
        self.title = title
        self.resizable(0,0)

    def load_textbox(self):
        self.log = ctk.CTkTextbox(self)
        self.log.pack(expand=True, fill='both', padx=5, pady=5)

    def load_scrollable_frame(self):
        self.frame = ctk.CTkScrollableFrame(self)
        self.frame.pack(expand=True, fill='both', padx=5, pady=5)

    def load_checkboxes(self, frame, list):
        self.checkboxes = []
        for element in list:
            self.checkboxes.append(ctk.CTkCheckBox(master=frame, text=element))
        for index, checkbox in enumerate(self.checkboxes):
            checkbox.grid(row=index, column=0, padx=5, pady=5, sticky="w")

        self.confirm_button = ctk.CTkButton(master=frame, text="Confirmar", fg_color="transparent", font=("Arial Bold", 14), hover_color="#207244", command=self.confirm)
        self.confirm_button.grid(row=len(self.checkboxes), column=0, padx=5, pady=5, sticky="w")

    def confirm(self):
        self.selected_params = []
        for checkbox in self.checkboxes:
            if checkbox.get():
                self.selected_params.append(checkbox.cget("text"))
        self.destroy()
        if self.selected_params:
            debug(f"Optimization process started with params: {self.selected_params}")
            time_now = time.time()
            cleaner = Cleaner()
            for key, value in Settings.optimze_list.items():
                if value in self.selected_params:
                    debug(f"Optimizing {key}...")
                    cleaner.run(key)
                    debug(f"Finished {key} - OK")
            time_now = time.time() - time_now
            debug(f"Optimization process finished in {round(time_now, 2)}s")
        else:
            debug("Optimization process aborted! No params selected")

    def send_log(self, log):
        self.log.insert("end", f"{timenow()} {log}\n")

class Window(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.scan = Scan()
        self.scan.run()
        self.actual = 'default'
        self.generator = LogGenerator()
        self.setup()

    def send_log(self, log, box):
        box.insert("end", f"{timenow()} {log}\n")

    def navigation(self, frame):
        if self.actual != 'main':
            self.nav[self.actual].pack_forget()
        else:
            self.main_frame.pack_forget()
            self.second_frame.pack_forget()
        if frame == 'main':
            self.main_frame.pack(side='left', fill='y')
            self.second_frame.pack(side='right', fill='y')
        else:
            self.nav[frame].pack(expand=True, fill='both')

        self.actual = frame

    def draw_default(self):
        ctk.CTkLabel(self.default_frame, text="Bem-vindo[a] ao PC SCAN 0.1", font=("Arial Black", 25), text_color="#2A8C55").pack(anchor="nw", pady=(10,0), padx=(29,0))
        ctk.CTkLabel(self.default_frame, text="Logs de Atualização e mais!", font=("Arial Black", 20), text_color="#2A8C55").pack(anchor="nw", pady=(20,0), padx=(29,0))

    def draw_main(self):
        ctk.CTkLabel(self.main_frame, text="Informações do Sistema", font=("Arial Black", 25), text_color="#2A8C55").pack(anchor="nw", pady=(10,0), padx=(29,0))
        
        self.labels1 = {'system': 'Sistema', 'cpu': 'Unidade Central de Processamento (CPU)', 'gpu': 'Unidade de Processamento Gráfico (GPU)'}
        self.labels2 = {'memory': 'Memória RAM', 'disk': 'Disco Rígido Principal', 'network': 'Rede', 'motherboard': 'Placa Mãe'}
        for key, value in self.labels1.items():
            ctk.CTkLabel(self.main_frame, text=value, font=("Arial Black", 20), text_color="#2A8C55").pack(anchor="nw", pady=(29,0), padx=27)
            for key, value in self.scan.data[key].items():
                ctk.CTkLabel(self.main_frame, text=f"{key} : {value}", font=("Arial Black", 17), text_color="#2A8C55").pack(anchor="nw", pady=(0,0), padx=27)

        for key, value in self.labels2.items():
            ctk.CTkLabel(self.second_frame, text=value, font=("Arial Black", 20), text_color="#2A8C55").pack(anchor="nw", pady=(29,0), padx=27)
            for key, value in self.scan.data[key].items():
                ctk.CTkLabel(self.second_frame, text=f"{key} : {value}", font=("Arial Black", 17), text_color="#2A8C55").pack(anchor="nw", pady=(0,0), padx=27)

    def draw_drivers(self):
        ctk.CTkLabel(self.driver_frame, text="Drivers Instalados no Sistema", font=("Arial Black", 25), text_color="#2A8C55").pack(anchor="nw", pady=(10,0), padx=(29,0))

        self.drivers_frame = ctk.CTkScrollableFrame(self.driver_frame, fg_color="transparent")
        self.drivers_frame.pack(expand=True, fill='both', padx=27, pady=21)
        self.driver_table = CTkTable(master=self.drivers_frame, values=self.scan.data['drivers'], colors=["black", "gray"], header_color="#2A8C55", hover_color="#B4B4B4")
        self.driver_table.edit_row(0, text_color="black")
        self.driver_table.pack(expand=True, side='left', anchor='nw')

    def draw_extra(self):
        self.extra_title = ctk.CTkLabel(self.extra_frame, text="Funções Extras", font=("Arial Black", 25), text_color="#2A8C55")
        self.extra_title.grid(row=0, column=0, padx=27, pady=10, sticky="w")

        self.save_button = ctk.CTkButton(master=self.extra_frame, text="Salvar Informações", fg_color="transparent", font=("Arial Bold", 14), hover_color="#207244", command=self.save_log)
        self.save_button.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.save_options = ctk.CTkOptionMenu(master=self.extra_frame, values=["PDF", "EXCEL", "XML", "JSON", "TXT"], command=self.optionmenu_save_callback)
        self.save_options.grid(row=1, column=1, pady=5)
        self.save_choice = "PDF"

        self.scan_button = ctk.CTkButton(master=self.extra_frame, text="Recarregar Informações", fg_color="transparent", font=("Arial Bold", 14), hover_color="#207244", command=self.update)
        self.scan_button.grid(row=2, column=0, padx=20, pady=5, sticky="w")

        self.otimize_button = ctk.CTkButton(master=self.extra_frame, text="Menu de Otimização", fg_color="transparent", font=("Arial Bold", 14), hover_color="#207244", command=self.optimize)
        self.otimize_button.grid(row=3, column=0, padx=20, pady=5, sticky="w")


    def draw_options(self):
        pass

    def optionmenu_save_callback(self, choice):
        self.save_choice = choice

    def open_directory(self):
        destination = filedialog.askdirectory(title="Selecione o local para salvar as informações")
        if not destination:
            return
        return destination

    def save_log(self):
        destination = self.open_directory()
        if destination is not None:
            self.generator.run(self.scan.data, self.save_choice, destination)
            debug(f"Log saved at {destination} as .{self.save_choice.lower()}")
        else:
            debug("Log save process aborted! No directory selected")

    def update(self):
        if self.toplevel_window_log is None or not self.toplevel_window_log.winfo_exists():
            self.toplevel_window_log = ToplevelWindow(self, title="Atualizando Informações")
            self.toplevel_window_log.load_textbox()
            self.toplevel_window_log.focus()
        else:
            self.toplevel_window_log.focus()

        self.toplevel_window_log.send_log("-----------------------------------------------------")
        self.toplevel_window_log.send_log("Atualizando Informações...")
        time_now = time.time()
        self.scan.run()
        for label in self.main_frame.winfo_children() + self.second_frame.winfo_children():
            label.destroy()
        self.draw_main()
        time_now = time.time() - time_now
        self.toplevel_window_log.send_log(f"Tempo de Atualização: {round(time_now, 2)}s")
        self.toplevel_window_log.send_log("Informações Atualizadas!")
        self.toplevel_window_log.send_log("-----------------------------------------------------")

    def optimize(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self, title="Otimizando Sistema")
            self.toplevel_window.load_scrollable_frame()
            self.toplevel_window.load_checkboxes(self.toplevel_window.frame, Settings.optimze_list.values())
        else:
            self.toplevel_window.focus()

                

    def setup(self):
        self.geometry(Settings.SIZE)
        self.title(Settings.TITLE)
        self.toplevel_window = None
        self.toplevel_window_log = None
        
        self.sidebar_frame = ctk.CTkFrame(self, fg_color=Settings.SIDEBAR_COLOR, width=200, height=700, corner_radius=0)
        self.sidebar_frame.pack_propagate(0)
        self.sidebar_frame.pack(side='left', fill='y')

        self.logo_img_data = Image.open(find_path('imgs', 'logo.png')).resize((78, 85))
        self.logo_img = ctk.CTkImage(dark_image=self.logo_img_data, light_image=self.logo_img_data, size=(77.68, 85.42))

        self.default_frame = ctk.CTkFrame(self, corner_radius=0)
        self.default_frame.pack_propagate(0)
        self.default_frame.pack(side='left', fill='both', expand=True)

        self.main_frame = ctk.CTkFrame(self, width=650, height=700, corner_radius=0)
        self.main_frame.pack_propagate(0)

        self.second_frame = ctk.CTkFrame(self, width=1070, height=700, corner_radius=0)
        self.second_frame.pack_propagate(0)

        self.driver_frame = ctk.CTkFrame(self, corner_radius=0)
        self.driver_frame.pack_propagate(0)

        self.extra_frame = ctk.CTkFrame(self, corner_radius=0)
        self.extra_frame.pack_propagate(0)

        self.options_frame = ctk.CTkFrame(self, corner_radius=0)
        self.options_frame.pack_propagate(0)

        ctk.CTkLabel(self.sidebar_frame, text="PC SCANER", image=self.logo_img).pack(pady=(38, 0), anchor="center")
        ctk.CTkButton(master=self.sidebar_frame, text="Sistema", fg_color="transparent", font=("Arial Bold", 14), hover_color="#207244", anchor="w", command=lambda: self.navigation('main')).pack(anchor="center", ipady=5, pady=(16, 0))
        ctk.CTkButton(master=self.sidebar_frame, text="Drivers", fg_color="transparent", font=("Arial Bold", 14), hover_color="#207244", anchor="w", command=lambda: self.navigation('drivers')).pack(anchor="center", ipady=5, pady=(16, 0))
        ctk.CTkButton(master=self.sidebar_frame, text="Extra", fg_color="transparent", font=("Arial Bold", 14), hover_color="#207244", anchor="w", command=lambda: self.navigation('extra')).pack(anchor="center", ipady=5, pady=(16, 0))
        ctk.CTkButton(master=self.sidebar_frame, text="Options", fg_color="transparent", font=("Arial Bold", 14), hover_color="#207244", anchor="w", command=lambda: self.navigation('options')).pack(anchor="center", ipady=5, pady=(16, 0))

        self.draw_default()
        self.draw_main()
        self.draw_drivers()
        self.draw_extra()
        self.draw_options()

        self.main_frame.pack_forget()
        self.second_frame.pack_forget()
        self.driver_frame.pack_forget()
        self.extra_frame.pack_forget()
        self.options_frame.pack_forget()

        self.nav = {'default': self.default_frame,
                    'main': self.main_frame,
                    'drivers': self.driver_frame,
                    'extra': self.extra_frame,
                    'options': self.options_frame}

    def run(self):
        self.mainloop()

if __name__ == '__main__':
    window = Window()
    window.run()