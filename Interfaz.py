import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pdfplumber
from ExtraerListado import extraer_datos_con_pdfplumber
from ExtraerCertificados import extraer_datos_certificados
from CompararDatos import comparar_datos

def ejecutar_proceso(archivo_pdf, inicio_listado, fin_listado, inicio_cert, fin_cert, tree, label_paginas):
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
                # Insertar con color para certificados encontrados (verde claro)
                item = tree.insert("", "end", values=(i, tipo, doc, nombre, tipo_cert, doc, nombre_cert))
                tree.set(item, "Nombre Certificado", nombre_cert)
                # Aplicar color verde claro a la fila
                tree.tag_configure('encontrado', background='#e8f5e8')  # Verde claro
                tree.item(item, tags=('encontrado',))
            else:
                # Insertar con color para no encontrados (rojo claro)
                item = tree.insert("", "end", values=(i, tipo, doc, nombre, "❌", "❌", "No encontrado"))
                tree.tag_configure('no_encontrado', background='#ffe6e6')  # Rojo claro
                tree.item(item, tags=('no_encontrado',))

        messagebox.showinfo("Completado", f"Procesado: {len(docs_listado)} registros del listado\n{len(docs_cert)} certificados encontrados")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema: {str(e)}")

def seleccionar_pdf(entry_pdf, spin_listado_ini, spin_listado_fin, spin_cert_ini, spin_cert_fin, label_paginas):
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
                # Actualizar label con el total de páginas
                label_paginas.config(text=f"Total páginas: {total_paginas}")
                
                for spin in [spin_listado_ini, spin_listado_fin, spin_cert_ini, spin_cert_fin]:
                    spin.config(to=total_paginas)
                    spin.delete(0, tk.END)
                    spin.insert(0, "1")
                spin_listado_fin.delete(0, tk.END)
                spin_listado_fin.insert(0, str(total_paginas))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el PDF: {str(e)}")

def ejecutar_comparacion(archivo_pdf, inicio_listado, fin_listado, inicio_cert, fin_cert, tree):
    try:
        resultados = comparar_datos(archivo_pdf, inicio_listado, fin_listado, inicio_cert, fin_cert)

        for item in tree.get_children():
            tree.delete(item)

        for fila in resultados:
            i, tipo_l, doc_l, nom_list, tipo_c, doc_c, nom_cert, sim_doc, sim_nom = fila

            # Asignar tag según % de similitud
            if sim_doc == "100.0%" and sim_nom == "100.0%":
                tag = "correcto"
            elif float(sim_nom.replace("%", "")) >= 70:
                tag = "parcial"
            else:
                tag = "error"

            tree.insert("", "end", values=fila, tags=(tag,))

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema en comparación: {str(e)}")

def ejecutar_comparacion(archivo_pdf, inicio_listado, fin_listado, inicio_cert, fin_cert, tree):
    try:
        resultados = comparar_datos(archivo_pdf, inicio_listado, fin_listado, inicio_cert, fin_cert)

        for item in tree.get_children():
            tree.delete(item)

        for fila in resultados:
            i, tipo_l, doc_l, nom_list, tipo_c, doc_c, nom_cert, sim_doc, sim_nom, estado = fila

            # Asignar tag según estado
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

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema en comparación: {str(e)}")

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
               command=lambda: seleccionar_pdf(entry_pdf, spin_listado_ini, spin_listado_fin, spin_cert_ini, spin_cert_fin, label_paginas)
    ).grid(row=0, column=2, padx=5)

    # Label para mostrar total de páginas
    label_paginas = tk.Label(frame_sel, text="Total páginas: 0", font=("Segoe UI", 10, "bold"), fg="blue")
    label_paginas.grid(row=0, column=3, padx=10)

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
                   tree,
                   label_paginas
               )).pack(pady=10)
        # Botón comparar
    ttk.Button(root, text="🔍 Comparar",
               command=lambda: ejecutar_comparacion(
                   entry_pdf.get(),
                   int(spin_listado_ini.get()), int(spin_listado_fin.get()),
                   int(spin_cert_ini.get()), int(spin_cert_fin.get()),
                   tree
               )).pack(pady=5)

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

    # Configurar tags para colores
    tree.tag_configure('encontrado', background='#e8f5e8')  # Verde claro para encontrados
    tree.tag_configure('no_encontrado', background='#ffe6e6')  # Rojo claro para no encontrados

    tree.pack(fill="both", expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    root.mainloop()

if __name__ == "__main__":
    main()