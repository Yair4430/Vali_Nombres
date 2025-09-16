import pdfplumber
import re

def extraer_datos_con_pdfplumber(archivo_pdf, pagina_inicio, pagina_fin):
    tipos, documentos, nombres = [], [], []

    with pdfplumber.open(archivo_pdf) as pdf:
        for page_num in range(pagina_inicio - 1, pagina_fin):
            # Extraer texto con configuración mejorada
            texto = pdf.pages[page_num].extract_text()
            if not texto:
                continue

            # Patrón más flexible que no depende de caracteres especiales
            # Buscar el patrón numérico + tipo-doc + nombre hasta "POR CERTIFICAR"
            patron = re.compile(
                r'(\d+)\.\s+([A-Z0-9-]+)\s+([^\n]+?)\s+POR\s+CERTIFICAR\s+APROBADO'
            )

            matches = patron.findall(texto)
            for match in matches:
                tipo_doc_completo = match[1]
                nombre = match[2].strip()
                
                # Limpiar el nombre - puede contener caracteres especiales mal interpretados
                nombre = re.sub(r'[^A-ZÁÉÍÓÚÜÑ\s]', '', nombre.upper())
                nombre = re.sub(r'\s+', ' ', nombre).strip()
                
                # Separar tipo y documento
                if '-' in tipo_doc_completo:
                    tipo, documento = tipo_doc_completo.split('-', 1)
                else:
                    tipo = ""
                    documento = tipo_doc_completo
                
                tipos.append(tipo)
                documentos.append(documento)
                nombres.append(nombre)

    return tipos, documentos, nombres