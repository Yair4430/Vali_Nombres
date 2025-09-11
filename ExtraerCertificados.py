import pdfplumber
import tkinter as tk
from tkinter import filedialog
import re

def extraer_datos_certificados():
    """
    Extrae nombres, números de documento y tipo de documento de los certificados
    en el orden en que aparecen en el PDF.
    """
    root = tk.Tk()
    root.withdraw()

    archivo_pdf = filedialog.askopenfilename(
        title="Seleccionar archivo PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not archivo_pdf:
        return [], [], [], archivo_pdf

    nombres = []
    numeros_documento = []
    tipos_documento = []

    with pdfplumber.open(archivo_pdf) as pdf:
        total_paginas = len(pdf.pages)
        print(f"\nEl PDF tiene {total_paginas} páginas.")

        # Pedir al usuario el rango de páginas
        pagina_inicio = int(input(f"Ingrese la página inicial (1 - {total_paginas}): "))
        pagina_fin = int(input(f"Ingrese la página final ({pagina_inicio} - {total_paginas}): "))

        if pagina_inicio < 1 or pagina_fin > total_paginas or pagina_inicio > pagina_fin:
            print("⚠️ Rango de páginas inválido. Se procesará todo el documento.")
            pagina_inicio, pagina_fin = 1, total_paginas

        for page_num in range(pagina_inicio - 1, pagina_fin):
            texto = pdf.pages[page_num].extract_text()
            if not texto:
                continue

            # Buscar tipo de documento (siempre es CC en este caso)
            tipo_doc_match = re.search(r"Cédula de Ciudadanía:", texto)
            tipo_doc = "CC" if tipo_doc_match else ""

            # Buscar número de documento (sin puntos)
            numero_doc_match = re.search(r"Cédula de Ciudadanía:\s*([\d.]+)", texto)
            if numero_doc_match:
                numero_doc = numero_doc_match.group(1).replace(".", "")
            else:
                numero_doc = ""

            # Buscar patrón: "A nombre de:  NOMBRE COMPLETO"
            patron_nombre = re.compile(r"A nombre de:\s+([A-ZÁÉÍÓÚÑ\s]+?)(?=\n|$)")
            matches_nombre = patron_nombre.findall(texto)

            for match in matches_nombre:
                nombre = match.strip()

                # Filtrar mejor los resultados no deseados
                # Eliminar líneas que contengan solo "E" o letras sueltas
                palabras = nombre.split()
                # Mantener solo palabras con más de 1 carácter
                nombre_filtrado = ' '.join([palabra for palabra in palabras if len(palabra) > 1])
                
                if nombre_filtrado and len(nombre_filtrado) > 3:
                    nombres.append(nombre_filtrado)
                    numeros_documento.append(numero_doc)
                    tipos_documento.append(tipo_doc)

    return nombres, numeros_documento, tipos_documento, archivo_pdf


def main():
    # CORRECCIÓN: El orden de retorno estaba incorrecto
    nombres, numeros_documento, tipos_documento, archivo_pdf = extraer_datos_certificados()

    # Mostrar listado de datos
    print(f"\n{'No.':<4} {'TIPO':<6} {'DOCUMENTO':<15} {'NOMBRES Y APELLIDOS':<50}")
    print("-" * 80)

    for i, (nombre, numero_doc, tipo_doc) in enumerate(zip(nombres, numeros_documento, tipos_documento), 1):
        print(f"{i:<4} {tipo_doc:<6} {numero_doc:<15} {nombre:<50}")

    print(f"\nTotal: {len(nombres)} certificados encontrados")
    print(f"Archivo procesado: {archivo_pdf}")


if __name__ == "__main__":
    main()