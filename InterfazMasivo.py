import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from CompararDatos import comparar_datos
from Masivo import procesar_masivo

resultados_globales = {}

def ejecutar_masivo(carpeta_principal, combo, tree):
    try:
        if not carpeta_principal:
            messagebox.showerror("Error", "Seleccione una carpeta primero")
            return
        
        # Mostrar mensaje de progreso
        progress_window = tk.Toplevel()
        progress_window.title("Procesando...")
        progress_window.geometry("300x100")
        progress_label = tk.Label(progress_window, text="Procesando archivos PDF, por favor espere...")
        progress_label.pack(pady=20)
        progress_window.update()
        
        # Usar el procesador masivo con detección automática
        global resultados_globales
        resultados_globales = procesar_masivo(carpeta_principal)

        # Cerrar ventana de progreso
        progress_window.destroy()

        if not resultados_globales:
            messagebox.showwarning("Aviso", "No se encontraron PDFs en las subcarpetas")
            return

        # Llenar combobox con nombres de PDFs
        combo["values"] = list(resultados_globales.keys())
        if combo["values"]:
            combo.current(0)
            mostrar_resultados_pdf(combo.get(), tree)

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema en modo masivo: {str(e)}")

def mostrar_resultados_pdf(nombre_pdf, tree):
    """Carga los resultados de un PDF específico en el treeview"""
    for item in tree.get_children():
        tree.delete(item)

    resultados = resultados_globales.get(nombre_pdf, [])

    for fila in resultados:
        i, tipo_l, doc_l, nom_list, tipo_c, doc_c, nom_cert, sim_doc, sim_nom, estado = fila

        if estado == "OK" and sim_doc == "100.0%" and sim_nom == "100.0%":
            tag = "correcto"
        elif estado == "Duplicado":
            tag = "duplicado"
        elif estado in ["Falta Certificado", "No existe en listado"]:
            tag = "error"
        elif float(sim_nom.replace("%", "")) >= 70:
            tag = "parcial"
        else:
            tag = "error"

        tree.insert("", "end", values=fila, tags=(tag,))

def main_masivo():
    root = tk.Tk()
    root.title("Extractor Listado + Certificados - Modo Masivo")
    root.geometry("1200x700")
    root.configure(bg="#f4f6f7")

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#dfe6e9")
    style.configure("Treeview", font=("Segoe UI", 9), rowheight=25)

    # Sección Carpeta principal
    frame_carpeta = ttk.LabelFrame(root, text=" Selección de carpeta principal ", padding=10)
    frame_carpeta.pack(pady=10, padx=10, fill="x")

    tk.Label(frame_carpeta, text="Carpeta con PDFs:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")
    entry_carpeta = ttk.Entry(frame_carpeta, width=80)
    entry_carpeta.grid(row=0, column=1, padx=5)
    
    ttk.Button(frame_carpeta, text="📂 Buscar Carpeta",
               command=lambda: (
                   carpeta := filedialog.askdirectory(title="Seleccionar carpeta principal"),
                   entry_carpeta.delete(0, tk.END) or entry_carpeta.insert(0, carpeta) if carpeta else None
               )).grid(row=0, column=2, padx=5)

    # Botón ejecutar masivo
    ttk.Button(root, text="🚀 Ejecutar Procesamiento Masivo",
               command=lambda: ejecutar_masivo(
                   entry_carpeta.get(),
                   combo_pdf,
                   tree
               )).pack(pady=10)

    # Combobox para seleccionar PDF procesado
    frame_combo = ttk.LabelFrame(root, text=" Selección de PDF procesado ", padding=10)
    frame_combo.pack(pady=5, padx=10, fill="x")

    combo_pdf = ttk.Combobox(frame_combo, state="readonly")
    combo_pdf.pack(fill="x", padx=5, pady=5)
    combo_pdf.bind("<<ComboboxSelected>>", lambda e: mostrar_resultados_pdf(combo_pdf.get(), tree))

    # Información sobre el modo masivo
    frame_info = ttk.LabelFrame(root, text=" Información del Modo Masivo ", padding=10)
    frame_info.pack(pady=5, padx=10, fill="x")
    
    info_text = """
    • El modo masivo procesa automáticamente todos los PDFs en la carpeta seleccionada
    • Detecta automáticamente los rangos de páginas para listados y certificados
    • Busca recursivamente en todas las subcarpetas
    • Los resultados se pueden seleccionar en la lista desplegable
    """
    tk.Label(frame_info, text=info_text, font=("Segoe UI", 9), justify="left").pack(padx=5, pady=5)

    # Tabla de resultados
    frame_tabla = ttk.LabelFrame(root, text=" Resultados ", padding=10)
    frame_tabla.pack(pady=10, padx=10, fill="both", expand=True)

    cols = ("No.", "Tipo L", "Doc L", "Nombre Listado", "Tipo C", "Doc C", "Nombre Certificado", "%Doc", "%Nombre", "Estado")
    tree = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=15)

    col_widths = [50, 80, 120, 220, 80, 120, 220, 80, 80, 150]
    for col, w in zip(cols, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=w)

    # Tags de colores
    tree.tag_configure("correcto", background="#e8f5e8")   # Verde
    tree.tag_configure("parcial", background="#fff7e6")    # Amarillo
    tree.tag_configure("duplicado", background="#ffe066")  # Amarillo fuerte
    tree.tag_configure("error", background="#ffe6e6")      # Rojo

    tree.pack(fill="both", expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    root.mainloop()

if __name__ == "__main__":
    main_masivo()