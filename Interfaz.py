import tkinter as tk
from tkinter import filedialog, messagebox
import Validacion  # Asegúrate de que el archivo se llame exactamente Validacion.py

def seleccionar_pdf():
    ruta = filedialog.askopenfilename(
        title="Selecciona el archivo PDF de listado y certificados",
        filetypes=[("Archivos PDF", "*.pdf")]
    )
    if ruta:
        try:
            resultado = Validacion.procesar_pdf(ruta)

            # Crear nueva ventana para mostrar resultados largos
            resultado_ventana = tk.Toplevel()
            resultado_ventana.title("Resultados de Validación")
            resultado_ventana.geometry("700x500")

            texto = tk.Text(resultado_ventana, wrap=tk.WORD, font=("Consolas", 11))
            texto.insert(tk.END, resultado)
            texto.pack(fill=tk.BOTH, expand=True)

            scrollbar = tk.Scrollbar(texto)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            texto.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=texto.yview)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

# Crear ventana
ventana = tk.Tk()
ventana.title("Validador de Certificados")
ventana.geometry("400x200")

label = tk.Label(ventana, text="Selecciona el PDF para validar", font=("Arial", 14))
label.pack(pady=20)

boton = tk.Button(ventana, text="Seleccionar PDF", command=seleccionar_pdf, font=("Arial", 12))
boton.pack()

ventana.mainloop()
