import pdfplumber
import re

def extraer_datos_certificados(archivo_pdf, pagina_inicio, pagina_fin):
    """
    Extrae nombres, números de documento y tipo de documento de los certificados
    en el rango de páginas dado.
    """
    nombres = []
    numeros_documento = []
    tipos_documento = []

    with pdfplumber.open(archivo_pdf) as pdf:
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
                palabras = nombre.split()
                nombre_filtrado = ' '.join([p for p in palabras if len(p) > 1])
                if nombre_filtrado and len(nombre_filtrado) > 3:
                    nombres.append(nombre_filtrado)
                    numeros_documento.append(numero_doc)
                    tipos_documento.append(tipo_doc)

    return nombres, numeros_documento, tipos_documento
