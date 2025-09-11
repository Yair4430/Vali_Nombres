import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys

def abrir_modo_normal():
    """Abre la interfaz en modo normal"""
    try:
        subprocess.Popen([sys.executable, "InterfazNormal.py"])
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el modo normal: {e}")

def abrir_modo_masivo():
    """Abre la interfaz en modo masivo"""
    try:
        subprocess.Popen([sys.executable, "InterfazMasivo.py"])
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el modo masivo: {e}")

def main():
    root = tk.Tk()
    root.title("Selector de Modo - Extractor Listado + Certificados")
    root.geometry("500x300")
    root.configure(bg="#f4f6f7")

    # Frame principal
    frame = ttk.Frame(root, padding=20)
    frame.pack(expand=True, fill="both")

    # Título
    titulo = ttk.Label(frame, text="Extractor Listado + Certificados", 
                      font=("Segoe UI", 16, "bold"))
    titulo.pack(pady=20)

    # Descripción
    descripcion = ttk.Label(frame, text="Seleccione el modo de operación:", 
                           font=("Segoe UI", 12))
    descripcion.pack(pady=10)

    # Botones de selección de modo
    frame_botones = ttk.Frame(frame)
    frame_botones.pack(pady=30)

    btn_normal = ttk.Button(frame_botones, text="📄 Modo Normal", 
                          command=abrir_modo_normal, width=20)
    btn_normal.grid(row=0, column=0, padx=20, pady=10)

    btn_masivo = ttk.Button(frame_botones, text="📂 Modo Masivo", 
                           command=abrir_modo_masivo, width=20)
    btn_masivo.grid(row=0, column=1, padx=20, pady=10)

    # Información de modos
    frame_info = ttk.LabelFrame(frame, text="Información de Modos", padding=10)
    frame_info.pack(pady=20, fill="x")

    info_text = """
    📄 Modo Normal: Procesa un solo PDF con selección manual de rangos de páginas
    📂 Modo Masivo: Procesa múltiples PDFs automáticamente con detección de rangos
    """
    
    lbl_info = ttk.Label(frame_info, text=info_text, justify="left")
    lbl_info.pack()

    root.mainloop()

if __name__ == "__main__":
    main()