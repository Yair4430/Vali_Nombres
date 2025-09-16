import pdfplumber
import re

def extraer_datos_certificados(archivo_pdf, pagina_inicio, pagina_fin):
    nombres = []
    numeros_documento = []
    tipos_documento = []
    paginas = []  # Nueva lista para almacenar las páginas

    with pdfplumber.open(archivo_pdf) as pdf:
        for page_num in range(pagina_inicio - 1, pagina_fin):
            texto = pdf.pages[page_num].extract_text()
            if not texto:
                continue

            tipo_doc, numero_doc, nombre = "", "", ""

            # --- Detectar CC ---
            if "Cédula de Ciudadanía" in texto:
                tipo_doc = "CC"
                numero_doc_match = re.search(r"Cédula de Ciudadanía:\s*([\d.]+)", texto)
                if numero_doc_match:
                    numero_doc = numero_doc_match.group(1).replace(".", "")
                
                nombre_match = re.search(r"A nombre de:\s+([A-ZÁÉÍÓÚÑ\s]+?)(?=\s+Estado|\n|$)", texto)
                if nombre_match:
                    nombre = nombre_match.group(1).strip()
                    nombre = re.sub(r'\s+', ' ', nombre).strip()

            # --- Detectar PPT ---
            elif "Permiso por Protección Temporal" in texto:
                tipo_doc = "PPT"
                numero_doc_match = re.search(r"Permiso por Protección Temporal N°:\s*([\d]+)", texto)
                if numero_doc_match:
                    numero_doc = numero_doc_match.group(1).strip()

                nombres_match = re.search(r"Nombres:\s*([A-ZÁÉÍÓÚÑ\s]+?)(?=\s+Apellidos|\s+País|\n|$)", texto)
                apellidos_match = re.search(r"Apellidos:\s*([A-ZÁÉÍÓÚÑ\s]+?)(?=\s+País|\s+Nacionalidad|\n|$)", texto)

                if nombres_match and apellidos_match:
                    nombre_completo = f"{nombres_match.group(1).strip()} {apellidos_match.group(1).strip()}"
                    nombre = re.sub(r'\s+[AP]$', '', nombre_completo).strip()

            # --- Detectar TI ---
            elif "Número Único de Identificación Personal" in texto or "CERTIFICADO DE INSCRIPCIÓN" in texto:
                tipo_doc = "TI"
                numero_doc_match = re.search(r"Número Único de Identificación Personal\s*(\d+)", texto)
                if numero_doc_match:
                    numero_doc = numero_doc_match.group(1).strip()

                nombre_match = re.search(r",\s*([A-ZÁÉÍÓÚÑ\s]+)\s+tiene inscrito", texto)
                if not nombre_match:
                    nombre_match = re.search(r"certifica.*?,\s*([A-ZÁÉÍÓÚÑ\s]+)\s*", texto)
                
                if nombre_match:
                    nombre_completo = nombre_match.group(1).strip().upper()
                    
                    partes_nombre = nombre_completo.split()
                    
                    if len(partes_nombre) >= 3:
                        apellidos = partes_nombre[:2]
                        nombres_persona = partes_nombre[2:]
                        nombre = ' '.join(nombres_persona + apellidos)
                    elif len(partes_nombre) == 2:
                        nombre = f"{partes_nombre[1]} {partes_nombre[0]}"
                    else:
                        nombre = nombre_completo

            # --- Guardar resultados ---
            if nombre and numero_doc and tipo_doc:
                nombre = re.sub(r'\s+[A-Z]$', '', nombre.strip())
                nombre = re.sub(r'\s+', ' ', nombre).strip()
                nombres.append(nombre)
                numeros_documento.append(numero_doc)
                tipos_documento.append(tipo_doc)
                paginas.append(page_num + 1)  # Guardar número de página (1-based)

    return nombres, numeros_documento, tipos_documento, paginas  # Devolver también las páginas