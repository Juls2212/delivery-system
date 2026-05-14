import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import os

class ReportGenerator(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.report_text = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        title_label = ttk.Label(self, text="Generador de Reportes", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(buttons_frame, text="Generar Resumen General", command=self._generate_summary).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Generar Estado de Pedidos", command=self._generate_orders_report).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Guardar Reporte", command=self._save_report).pack(side="right", padx=5)
        
        text_frame = ttk.Frame(self)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.report_text = tk.Text(text_frame, yscrollcommand=scrollbar.set, wrap="word")
        self.report_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.report_text.yview)

    def _generate_summary(self):
        report_content = self.controller.get_general_summary_report()
        self._display_report(report_content)
        
    def _generate_orders_report(self):
        report_content = self.controller.get_orders_status_report()
        self._display_report(report_content)

    def _display_report(self, content):
        self.report_text.config(state="normal")
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, content)
    
    def _save_report(self):
        content = self.report_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Advertencia", "No hay contenido para guardar.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Guardar Reporte Como"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                messagebox.showinfo("Éxito", "Reporte guardado exitosamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")
