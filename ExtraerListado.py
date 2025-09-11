import pdfplumber
import re

def extraer_datos_con_pdfplumber(archivo_pdf, pagina_inicio, pagina_fin):
    """
    Extrae tipos, documentos y nombres usando pdfplumber,
    en el rango de páginas dado.
    """
    tipos, documentos, nombres = [], [], []

    with pdfplumber.open(archivo_pdf) as pdf:
        for page_num in range(pagina_inicio - 1, pagina_fin):
            texto = pdf.pages[page_num].extract_text()
            if not texto:
                continue

            # Patrón para capturar: número. TIPO-documento NOMBRE COMPLETO POR CERTIFICAR APROBADO 80
            patron = re.compile(
                r'(\d+)\.\s+([A-Z]{2,4})[-\s]?(\d+)\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)\s+POR CERTIFICAR\s+APROBADO\s+80'
            )

            matches = patron.findall(texto)
            for match in matches:
                tipo = match[1]      # CC, CE, TI, PPT, etc.
                documento = match[2]
                nombre = match[3].strip()

                tipos.append(tipo)
                documentos.append(documento)
                nombres.append(nombre)

    return tipos, documentos, nombres
