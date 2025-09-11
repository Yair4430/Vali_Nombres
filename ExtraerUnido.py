import tkinter as tk
from tkinter import filedialog
import pdfplumber

from ExtraerListado import extraer_datos_con_pdfplumber
from ExtraerCertificados import extraer_datos_certificados

def main():
    root = tk.Tk()
    root.withdraw()

    archivo_pdf = filedialog.askopenfilename(
        title="Seleccionar archivo PDF con listado y certificados",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not archivo_pdf:
        return

    with pdfplumber.open(archivo_pdf) as pdf:
        total_paginas = len(pdf.pages)
        print(f"\nEl PDF tiene {total_paginas} páginas.")

        # Rango de páginas para el listado
        inicio_listado = int(input(f"Ingrese la página inicial del LISTADO (1 - {total_paginas}): "))
        fin_listado = int(input(f"Ingrese la página final del LISTADO ({inicio_listado} - {total_paginas}): "))

        # Rango de páginas para los certificados
        inicio_cert = int(input(f"Ingrese la página inicial de los CERTIFICADOS (1 - {total_paginas}): "))
        fin_cert = int(input(f"Ingrese la página final de los CERTIFICADOS ({inicio_cert} - {total_paginas}): "))

    # Usar funciones ajustadas
    tipos_listado, docs_listado, nombres_listado = extraer_datos_con_pdfplumber(
        archivo_pdf, inicio_listado, fin_listado
    )
    nombres_cert, docs_cert, tipos_cert = extraer_datos_certificados(
        archivo_pdf, inicio_cert, fin_cert
    )

# Por esta:
    certificados_dict = {
        doc: (tipo, nombre) for doc, tipo, nombre in zip(docs_cert, tipos_cert, nombres_cert)
    }

    # Reorganizar certificados en el orden del listado
    resultados_finales = []
    for tipo_l, doc_l, nom_list in zip(tipos_listado, docs_listado, nombres_listado):
        if doc_l in certificados_dict:
            tipo_c, nom_cert = certificados_dict[doc_l]
            resultados_finales.append((tipo_l, doc_l, nom_list, tipo_c, doc_l, nom_cert))
        else:
            resultados_finales.append((tipo_l, doc_l, nom_list, "❌", "❌", "No encontrado"))

    # Mostrar resultados
    print(f"\n{'No.':<4} {'TIPO_L':<8} {'DOC_L':<15} {'NOMBRE LISTADO':<35} {'TIPO_C':<8} {'DOC_C':<15} {'NOMBRE CERTIFICADO':<35}")
    print("-" * 135)
    for i, (tipo_l, doc_l, nom_list, tipo_c, doc_c, nom_cert) in enumerate(resultados_finales, 1):
        print(f"{i:<4} {tipo_l:<8} {doc_l:<15} {nom_list:<35} {tipo_c:<8} {doc_c:<15} {nom_cert:<35}")

    print(f"\nTotal en listado: {len(docs_listado)}")
    print(f"Total en certificados: {len(docs_cert)}")

if __name__ == "__main__":
    main()
