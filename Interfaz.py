import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pdfplumber
from ExtraerListado import extraer_datos_con_pdfplumber
from ExtraerCertificados import extraer_datos_certificados

def ejecutar_proceso(archivo_pdf, inicio_listado, fin_listado, inicio_cert, fin_cert, tree):
    try:
        if not archivo_pdf:
            messagebox.showerror("Error", "Seleccione un archivo PDF primero")
            return
            
        tipos_listado, docs_listado, nombres_listado = extraer_datos_con_pdfplumber(
            archivo_pdf, inicio_listado, fin_listado
        )
        nombres_cert, docs_cert, tipos_cert = extraer_datos_certificados(
            archivo_pdf, inicio_cert, fin_cert
        )

        certificados_dict = {
            doc: (tipo, nombre) for doc, tipo, nombre in zip(docs_cert, tipos_cert, nombres_cert)
        }

        for item in tree.get_children():
            tree.delete(item)

        for i, (tipo, doc, nombre) in enumerate(zip(tipos_listado, docs_listado, nombres_listado), 1):
            if doc in certificados_dict:
                tipo_cert, nombre_cert = certificados_dict[doc]
                tree.insert("", "end", values=(i, tipo, doc, nombre, tipo_cert, doc, nombre_cert))
            else:
                tree.insert("", "end", values=(i, tipo, doc, nombre, "❌", "❌", "No encontrado"))

        messagebox.showinfo("Completado", f"Procesado: {len(docs_listado)} registros del listado\n{len(docs_cert)} certificados encontrados")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema: {str(e)}")

def seleccionar_pdf(entry_pdf, spin_listado_ini, spin_listado_fin, spin_cert_ini, spin_cert_fin):
    archivo_pdf = filedialog.askopenfilename(
        title="Seleccionar archivo PDF con listado y certificados",
        filetypes=[("PDF files", "*.pdf")]
    )
    if archivo_pdf:
        entry_pdf.delete(0, tk.END)
        entry_pdf.insert(0, archivo_pdf)

        try:
            with pdfplumber.open(archivo_pdf) as pdf:
                total_paginas = len(pdf.pages)
                for spin in [spin_listado_ini, spin_listado_fin, spin_cert_ini, spin_cert_fin]:
                    spin.config(to=total_paginas)
                    spin.delete(0, tk.END)
                    spin.insert(0, "1")
                spin_listado_fin.delete(0, tk.END)
                spin_listado_fin.insert(0, str(total_paginas))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el PDF: {str(e)}")

def main():
    root = tk.Tk()
    root.title("Extractor Listado + Certificados")
    root.geometry("1200x700")
    root.configure(bg="#f4f6f7")

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#dfe6e9")
    style.configure("Treeview", font=("Segoe UI", 9), rowheight=25)

    # Sección Archivo
    frame_sel = ttk.LabelFrame(root, text=" Selección de archivo ", padding=10)
    frame_sel.pack(pady=10, padx=10, fill="x")

    tk.Label(frame_sel, text="Archivo PDF:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")
    entry_pdf = ttk.Entry(frame_sel, width=80)
    entry_pdf.grid(row=0, column=1, padx=5)
    ttk.Button(frame_sel, text="📂 Buscar",
               command=lambda: seleccionar_pdf(entry_pdf, spin_listado_ini, spin_listado_fin, spin_cert_ini, spin_cert_fin)
    ).grid(row=0, column=2, padx=5)

    # Sección Rango de páginas
    frame_rangos = ttk.LabelFrame(root, text=" Rango de páginas ", padding=10)
    frame_rangos.pack(pady=5, padx=10, fill="x")

    tk.Label(frame_rangos, text="Listado - Inicio:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="e", padx=5)
    spin_listado_ini = tk.Spinbox(frame_rangos, from_=1, to=1, width=5)
    spin_listado_ini.grid(row=0, column=1, padx=5)
    tk.Label(frame_rangos, text="Fin:", font=("Segoe UI", 10)).grid(row=0, column=2, sticky="e", padx=5)
    spin_listado_fin = tk.Spinbox(frame_rangos, from_=1, to=1, width=5)
    spin_listado_fin.grid(row=0, column=3, padx=5)

    tk.Label(frame_rangos, text="Certificados - Inicio:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="e", padx=5)
    spin_cert_ini = tk.Spinbox(frame_rangos, from_=1, to=1, width=5)
    spin_cert_ini.grid(row=1, column=1, padx=5)
    tk.Label(frame_rangos, text="Fin:", font=("Segoe UI", 10)).grid(row=1, column=2, sticky="e", padx=5)
    spin_cert_fin = tk.Spinbox(frame_rangos, from_=1, to=1, width=5)
    spin_cert_fin.grid(row=1, column=3, padx=5)

    # Botón procesar
    ttk.Button(root, text="▶ Procesar",
               command=lambda: ejecutar_proceso(
                   entry_pdf.get(),
                   int(spin_listado_ini.get()), int(spin_listado_fin.get()),
                   int(spin_cert_ini.get()), int(spin_cert_fin.get()),
                   tree
               )).pack(pady=10)

    # Tabla de resultados
    frame_tabla = ttk.LabelFrame(root, text=" Resultados ", padding=10)
    frame_tabla.pack(pady=10, padx=10, fill="both", expand=True)

    cols = ("No.", "Tipo L", "Doc L", "Nombre Listado", "Tipo C", "Doc C", "Nombre Certificado")
    tree = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=15)
    
    # Configurar columnas
    tree.column("No.", width=50)
    tree.column("Tipo L", width=80)
    tree.column("Doc L", width=120)
    tree.column("Nombre Listado", width=250)
    tree.column("Tipo C", width=80)
    tree.column("Doc C", width=120)
    tree.column("Nombre Certificado", width=250)
    
    for col in cols:
        tree.heading(col, text=col)

    tree.pack(fill="both", expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    root.mainloop()

if __name__ == "__main__":
    main()