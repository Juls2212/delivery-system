from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class TitleLabel(ttk.Label):
    def __init__(self, master: tk.Misc, text: str, style_name: str = "Title.TLabel", **kwargs: object) -> None:
        super().__init__(master, text=text, style=style_name, **kwargs)


class StandardButton(ttk.Button):
    def __init__(self, master: tk.Misc, text: str, command: object, style_name: str = "Action.TButton", **kwargs: object) -> None:
        super().__init__(master, text=text, command=command, style=style_name, **kwargs)


class FormField(ttk.Frame):
    """Campo de formulario reutilizable: etiqueta + entrada de texto."""

    def __init__(self, master: tk.Misc, label: str, variable: tk.StringVar, **kwargs: object) -> None:
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text=label, style="Status.TLabel", background="#ffffff").grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        self.entry = ttk.Entry(self, textvariable=variable, font=("Segoe UI", 10))
        self.entry.grid(row=1, column=0, sticky="ew")

    def focus(self) -> None:
        self.entry.focus_set()

    def get_value(self) -> str:
        return self.entry.get().strip()

    def clear(self) -> None:
        self.entry.delete(0, "end")


class ResultTextBox(ttk.Frame):
    def __init__(self, master: tk.Misc, **kwargs: object) -> None:
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
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", f"{text}\n")
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def clear(self) -> None:
        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.configure(state="disabled")

    def is_empty(self) -> bool:
        return self.text_widget.get("1.0", "end").strip() == ""


def show_message(title: str, message: str, kind: str = "info") -> None:
    dialog_map = {
        "info": messagebox.showinfo,
        "warning": messagebox.showwarning,
        "error": messagebox.showerror,
    }
    dialog = dialog_map.get(kind, messagebox.showinfo)
    dialog(title, message)


def ask_confirmation(title: str, message: str) -> bool:
    """Muestra un diálogo de confirmación y retorna True si el usuario acepta."""
    return messagebox.askyesno(title, message)


def validate_numeric_id(value: str) -> tuple[bool, str]:
    """Valida que el valor sea un ID numérico positivo.

    Retorna (es_valido, mensaje_de_error).
    """
    stripped = value.strip()
    if not stripped:
        return False, "El campo ID no puede estar vacío."
    if not stripped.isdigit():
        return False, "El ID debe ser un número entero positivo."
    if int(stripped) <= 0:
        return False, "El ID debe ser mayor que cero."
    return True, ""
