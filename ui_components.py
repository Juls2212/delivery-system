from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class TitleLabel(ttk.Label):
    def __init__(self, master: tk.Misc, text: str, style_name: str = "Title.TLabel", **kwargs: object) -> None:
        # Este componente unifica los encabezados principales de la interfaz.
        super().__init__(master, text=text, style=style_name, **kwargs)


class StandardButton(ttk.Button):
    def __init__(self, master: tk.Misc, text: str, command: object, style_name: str = "Action.TButton", **kwargs: object) -> None:
        # Este botón reutilizable mantiene una apariencia consistente en toda la app.
        super().__init__(master, text=text, command=command, style=style_name, **kwargs)


class ResultTextBox(ttk.Frame):
    def __init__(self, master: tk.Misc, **kwargs: object) -> None:
        # Este contenedor ofrece un área de resultados con barra de desplazamiento integrada.
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.text_widget = tk.Text(
            self,
            wrap="word",
            font=("Segoe UI", 10),
            background="#fbfcfe",
            foreground="#1f2937",
            relief="flat",
            padx=14,
            pady=14,
            state="disabled",
        )
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)

        self.text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def append(self, text: str) -> None:
        # Este método agrega nuevas líneas sin permitir edición manual del usuario.
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", f"{text}\n")
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def clear(self) -> None:
        # Este método limpia el historial visual mostrado en pantalla.
        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.configure(state="disabled")


def show_message(title: str, message: str, kind: str = "info") -> None:
    # Esta función encapsula los cuadros de diálogo para reutilizarlos fácilmente.
    dialog_map = {
        "info": messagebox.showinfo,
        "warning": messagebox.showwarning,
        "error": messagebox.showerror,
    }
    dialog = dialog_map.get(kind, messagebox.showinfo)
    dialog(title, message)
