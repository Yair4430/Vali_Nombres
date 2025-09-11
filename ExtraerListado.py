import pdfplumber
import re

def extraer_datos_con_pdfplumber(archivo_pdf, pagina_inicio, pagina_fin):
    tipos, documentos, nombres = [], [], []

    with pdfplumber.open(archivo_pdf) as pdf:
        for page_num in range(pagina_inicio - 1, pagina_fin):
            texto = pdf.pages[page_num].extract_text()
            if not texto:
                continue

            # Patrón ajustado para capturar el formato correcto
            patron = re.compile(
                r'(\d+)\.\s+([A-Z0-9-]+)\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)\s+POR CERTIFICAR\s+APROBADO\s+40'
            )

            matches = patron.findall(texto)
            for match in matches:
                # El tipo y documento vienen juntos en el formato "CC-38231834" o "11-1033734512"
                tipo_doc_completo = match[1]
                nombre = match[2].strip()
                
                # Separar tipo y documento
                if '-' in tipo_doc_completo:
                    tipo, documento = tipo_doc_completo.split('-', 1)
                else:
                    # Si no hay guion, asumir que es solo documento (para casos como PPT)
                    tipo = tipo_doc_completo[:3]  # Tomar primeras letras como tipo
                    documento = tipo_doc_completo
                
                tipos.append(tipo)
                documentos.append(documento)
                nombres.append(nombre)

    return tipos, documentos, nombres