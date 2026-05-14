import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Clase que maneja la vista del historial de entregas (usando una estructura LIFO/Pila)
class HistoryView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Referencia visual a la lista del historial
        self.history_listbox = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Título de la vista
        title_label = ttk.Label(self, text="Historial de Entregas", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Contenedor para la lista y su barra de desplazamiento
        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.history_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10)
        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.history_listbox.yview)
        
        # Contenedor de botones de acción
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(buttons_frame, text="Ver Último Pedido", command=self._view_last).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Eliminar Último Pedido", command=self._remove_last).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Limpiar Historial", command=self._clear_history).pack(side="right", padx=5)

    # Actualiza la lista visible en pantalla con los datos más recientes
    def update_history(self, deliveries_stack):
        self.history_listbox.delete(0, tk.END)
        # La pila se muestra al revés (LIFO) para que lo más nuevo quede arriba
        for delivery in reversed(deliveries_stack):
            self.history_listbox.insert(tk.END, delivery)
            
    # Función para visualizar el último elemento en ser insertado (Tope de la pila)
    def _view_last(self):
        last_delivery = self.controller.get_last_delivery_from_history()
        if last_delivery:
            messagebox.showinfo("Último Pedido Entregado", last_delivery)
        else:
            messagebox.showwarning("Historial Vacío", "No hay entregas en el historial.")
            
    # Elimina el elemento tope de la pila (Desapilar)
    def _remove_last(self):
        success = self.controller.remove_last_delivery()
        if success:
            messagebox.showinfo("Éxito", "Último pedido eliminado del historial.")
        else:
            messagebox.showwarning("Historial Vacío", "No hay entregas para eliminar.")

    # Vacía toda la estructura de datos del historial
    def _clear_history(self):
        if messagebox.askyesno("Confirmar", "¿Seguro que desea limpiar todo el historial?"):
            self.controller.clear_delivery_history()
            messagebox.showinfo("Éxito", "Historial limpiado.")
