import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pdfplumber

from ExtraerListado import extraer_datos_con_pdfplumber
from ExtraerCertificados import extraer_datos_certificados

# ---------------- Lógica ----------------
def ejecutar_proceso(archivo_pdf, inicio_listado, fin_listado, inicio_cert, fin_cert, tree):
    try:
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

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema: {e}")

def seleccionar_pdf(entry_pdf, spin_listado_ini, spin_listado_fin, spin_cert_ini, spin_cert_fin):
    archivo_pdf = filedialog.askopenfilename(
        title="Seleccionar archivo PDF con listado y certificados",
        filetypes=[("PDF files", "*.pdf")]
    )
    if archivo_pdf:
        entry_pdf.delete(0, tk.END)
        entry_pdf.insert(0, archivo_pdf)

        with pdfplumber.open(archivo_pdf) as pdf:
            total_paginas = len(pdf.pages)
            for spin in (spin_listado_ini, spin_listado_fin, spin_cert_ini, spin_cert_fin):
                spin.config(to=total_paginas)

# ---------------- Interfaz ----------------
def main():
    root = tk.Tk()
    root.title("Extractor Listado + Certificados")
    root.geometry("1050x600")
    root.configure(bg="#f4f6f7")

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#dfe6e9")
    style.configure("Treeview", font=("Segoe UI", 9), rowheight=25)

    # ----- Sección Archivo -----
    frame_sel = ttk.LabelFrame(root, text=" Selección de archivo ", padding=10)
    frame_sel.pack(pady=10, padx=10, fill="x")

    tk.Label(frame_sel, text="Archivo PDF:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")
    entry_pdf = ttk.Entry(frame_sel, width=80)
    entry_pdf.grid(row=0, column=1, padx=5)
    ttk.Button(frame_sel, text="📂 Buscar",
               command=lambda: seleccionar_pdf(entry_pdf, spin_listado_ini, spin_listado_fin, spin_cert_ini, spin_cert_fin)
    ).grid(row=0, column=2, padx=5)

    # ----- Sección Rango de páginas -----
    frame_rangos = ttk.LabelFrame(root, text=" Rango de páginas ", padding=10)
    frame_rangos.pack(pady=5, padx=10, fill="x")

    tk.Label(frame_rangos, text="Listado:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="e")
    spin_listado_ini = tk.Spinbox(frame_rangos, from_=1, to=1, width=5)
    spin_listado_ini.grid(row=0, column=1, padx=5)
    spin_listado_fin = tk.Spinbox(frame_rangos, from_=1, to=1, width=5)
    spin_listado_fin.grid(row=0, column=2, padx=5)

    tk.Label(frame_rangos, text="Certificados:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="e")
    spin_cert_ini = tk.Spinbox(frame_rangos, from_=1, to=1, width=5)
    spin_cert_ini.grid(row=1, column=1, padx=5)
    spin_cert_fin = tk.Spinbox(frame_rangos, from_=1, to=1, width=5)
    spin_cert_fin.grid(row=1, column=2, padx=5)

    # ----- Botón procesar -----
    ttk.Button(root, text="▶ Procesar",
               command=lambda: ejecutar_proceso(
                   entry_pdf.get(),
                   int(spin_listado_ini.get()), int(spin_listado_fin.get()),
                   int(spin_cert_ini.get()), int(spin_cert_fin.get()),
                   tree
               )).pack(pady=10)

    # ----- Tabla de resultados -----
    frame_tabla = ttk.LabelFrame(root, text=" Resultados ", padding=10)
    frame_tabla.pack(pady=10, padx=10, fill="both", expand=True)

    cols = ("No.", "Tipo L", "Doc L", "Nombre Listado", "Tipo C", "Doc C", "Nombre Certificado")
    tree = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=15)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=120 if col not in ["Nombre Listado", "Nombre Certificado"] else 250)

    tree.pack(fill="both", expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    root.mainloop()

if __name__ == "__main__":
    main()
