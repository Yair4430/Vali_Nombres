import pdfplumber
import tkinter as tk
from tkinter import filedialog
import re

def extraer_datos_con_pdfplumber():
    """
    Extrae tipos, documentos y nombres usando pdfplumber
    """
    root = tk.Tk()
    root.withdraw()

    archivo_pdf = filedialog.askopenfilename(
        title="Seleccionar archivo PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not archivo_pdf:
        return [], [], [], archivo_pdf

    tipos = []
    documentos = []
    nombres = []

    with pdfplumber.open(archivo_pdf) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            
            # Patrón para capturar: número. TIPO-documento NOMBRE COMPLETO POR CERTIFICAR APROBADO 80
            # Ahora capturamos el tipo de documento (CC, CE, TI, PPT, etc.)
            patron = re.compile(r'(\d+)\.\s+([A-Z]{2,4})[-\s]?(\d+)\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)\s+POR CERTIFICAR\s+APROBADO\s+80')
            
            matches = patron.findall(texto)
            for match in matches:
                tipo = match[1]  # CC, CE, TI, PPT, etc.
                documento = match[2]
                nombre = match[3].strip()
                
                tipos.append(tipo)
                documentos.append(documento)
                nombres.append(nombre)
    
    return tipos, documentos, nombres, archivo_pdf

def main():
    # Extraer datos usando pdfplumber
    tipos, documentos, nombres, archivo_pdf = extraer_datos_con_pdfplumber()
    
    # Unir resultados
    listado_final = []
    min_length = min(len(tipos), len(documentos), len(nombres))
    
    for i in range(min_length):
        listado_final.append((tipos[i], documentos[i], nombres[i]))
    
    # Mostrar la tabla con la nueva columna TIPO
    print(f"{'No.':<4} {'TIPO':<6} {'DOCUMENTO':<15} {'NOMBRES Y APELLIDOS':<50}")
    print("-"*80)
    
    for i, (tipo, doc, nom) in enumerate(listado_final, 1):
        print(f"{i:<4} {tipo:<6} {doc:<15} {nom:<50}")
    
    print(f"\nTotal: {len(listado_final)} aprendices")

if __name__ == "__main__":
    main()