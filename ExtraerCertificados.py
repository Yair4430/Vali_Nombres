import pdfplumber
import re

def extraer_datos_certificados(archivo_pdf, pagina_inicio, pagina_fin):
    nombres = []
    numeros_documento = []
    tipos_documento = []

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
                
                # Ajustar la expresión regular para evitar capturar la "E" de "Estado"
                nombre_match = re.search(r"A nombre de:\s+([A-ZÁÉÍÓÚÑ\s]+?)(?=\s+Estado|\n|$)", texto)
                if nombre_match:
                    nombre = nombre_match.group(1).strip()
                    # Limpiar espacios extras y posibles caracteres no deseados
                    nombre = re.sub(r'\s+', ' ', nombre).strip()

            # --- Detectar PPT ---
            elif "Permiso por Protección Temporal" in texto:
                tipo_doc = "PPT"
                numero_doc_match = re.search(r"Permiso por Protección Temporal N°:\s*([\d]+)", texto)
                if numero_doc_match:
                    numero_doc = numero_doc_match.group(1).strip()

                # Buscar nombres y apellidos con lookahead para evitar capturar "País" y "Nacionalidad"
                nombres_match = re.search(r"Nombres:\s*([A-ZÁÉÍÓÚÑ\s]+?)(?=\s+Apellidos|\s+País|\n|$)", texto)
                apellidos_match = re.search(r"Apellidos:\s*([A-ZÁÉÍÓÚÑ\s]+?)(?=\s+País|\s+Nacionalidad|\n|$)", texto)

                if nombres_match and apellidos_match:
                    nombre_completo = f"{nombres_match.group(1).strip()} {apellidos_match.group(1).strip()}"
                    # Limpiar posibles letras sueltas al final
                    nombre = re.sub(r'\s+[AP]$', '', nombre_completo).strip()

            # --- Detectar TI ---
            elif "Número Único de Identificación Personal" in texto or "CERTIFICADO DE INSCRIPCIÓN" in texto:
                tipo_doc = "TI"
                numero_doc_match = re.search(r"Número Único de Identificación Personal\s*(\d+)", texto)
                if numero_doc_match:
                    numero_doc = numero_doc_match.group(1).strip()

                # Extraer el nombre completo (apellidos + nombres)
                nombre_match = re.search(r",\s*([A-ZÁÉÍÓÚÑ\s]+)\s+tiene inscrito", texto)
                if not nombre_match:
                    nombre_match = re.search(r"certifica.*?,\s*([A-ZÁÉÍÓÚÑ\s]+)\s*", texto)
                
                if nombre_match:
                    nombre_completo = nombre_match.group(1).strip().upper()
                    
                    # Dividir en palabras y reorganizar: convertir APELLIDOS NOMBRES a NOMBRES APELLIDOS
                    partes_nombre = nombre_completo.split()
                    
                    # Asumimos que los primeros 1-2 elementos son apellidos y el resto nombres
                    # Esto es común en formatos colombianos: APELLIDO1 APELLIDO2 NOMBRE1 NOMBRE2
                    if len(partes_nombre) >= 3:
                        # Si hay 3 o más partes, asumimos 2 apellidos y el resto nombres
                        apellidos = partes_nombre[:2]
                        nombres_persona = partes_nombre[2:]
                        nombre = ' '.join(nombres_persona + apellidos)
                    elif len(partes_nombre) == 2:
                        # Si hay 2 partes, asumimos 1 apellido y 1 nombre
                        nombre = f"{partes_nombre[1]} {partes_nombre[0]}"
                    else:
                        # Si solo hay 1 parte, dejarlo igual
                        nombre = nombre_completo

            # --- Guardar resultados ---
            if nombre and numero_doc and tipo_doc:
                # Limpieza final del nombre - eliminar letras sueltas al final
                nombre = re.sub(r'\s+[A-Z]$', '', nombre.strip())
                nombre = re.sub(r'\s+', ' ', nombre).strip()
                nombres.append(nombre)
                numeros_documento.append(numero_doc)
                tipos_documento.append(tipo_doc)

    return nombres, numeros_documento, tipos_documento