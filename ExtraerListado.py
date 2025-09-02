import pdfplumber
import tkinter as tk
from tkinter import filedialog
import re

def extraer_datos_con_pdfplumber():
    """
    Extrae documentos y nombres usando pdfplumber con enfoque más preciso
    """
    root = tk.Tk()
    root.withdraw()

    archivo_pdf = filedialog.askopenfilename(
        title="Seleccionar archivo PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not archivo_pdf:
        return [], [], archivo_pdf

    documentos = []
    nombres = []

    with pdfplumber.open(archivo_pdf) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            
            # Patrón más preciso para capturar todas las líneas de aprendices
            # Busca: número. CC-documento NOMBRE COMPLETO POR CERTIFICAR APROBADO 80
            patron = re.compile(r'(\d+)\.\s+CC[-\s]?(\d+)\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)\s+POR CERTIFICAR\s+APROBADO\s+80')
            
            matches = patron.findall(texto)
            for match in matches:
                numero_linea = int(match[0])
                documento = match[1]
                nombre = match[2].strip()
                
                documentos.append(documento)
                nombres.append(nombre)
                
                print(f"Línea {numero_linea}: {documento} - {nombre}")
    
    return documentos, nombres, archivo_pdf

def main():
    # Extraer datos usando pdfplumber
    documentos, nombres, archivo_pdf = extraer_datos_con_pdfplumber()
    
    print(f"\nDocumentos encontrados: {len(documentos)}")
    print(f"Nombres encontrados: {len(nombres)}")
    
    # Mostrar lo que se encontró para depuración
    print("Documentos:", documentos)
    print("Nombres:", nombres)
    
    # Verificar si faltan algunos
    if len(documentos) != 34:
        print(f"⚠️  Faltan {34 - len(documentos)} aprendices por extraer")
    
    # Unir resultados
    listado_final = []
    min_length = min(len(documentos), len(nombres))
    
    for i in range(min_length):
        listado_final.append((documentos[i], nombres[i]))
    
    # Mostrar resultados finales
    print("\n" + "="*80)
    print("LISTADO FINAL DE APRENDICES")
    print("="*80)
    print(f"{'No.':<4} {'DOCUMENTO':<15} {'NOMBRES Y APELLIDOS':<50}")
    print("-"*80)
    
    for i, (doc, nom) in enumerate(listado_final, 1):
        print(f"{i:<4} {doc:<15} {nom:<50}")
    
    print(f"\nTotal: {len(listado_final)} aprendices")
    print(f"Archivo procesado: {archivo_pdf}")

if __name__ == "__main__":
    main()