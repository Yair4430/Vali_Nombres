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
                
                # Buscar número de documento - patrón más robusto
                numero_doc_match = re.search(r"Número Único de Identificación Personal\s*(\d+)", texto)
                if not numero_doc_match:
                    # Intentar otro patrón alternativo
                    numero_doc_match = re.search(r"Identificación Personal\s*(\d+)", texto)
                
                if numero_doc_match:
                    numero_doc = numero_doc_match.group(1).strip()

                # PATRÓN MEJORADO para nombres en certificados TI
                # Buscar el patrón: ", NOMBRE COMPLETO tiene inscrito"
                nombre_match = re.search(r",\s*([A-ZÁÉÍÓÚÑ\s]+(?:\s+[A-ZÁÉÍÓÚÑ]+)*)\s+tiene inscrito", texto)
                
                if not nombre_match:
                    # Patrón alternativo: buscar después de "certifica que" 
                    nombre_match = re.search(r"certifica que.*?,\s*([A-ZÁÉÍÓÚÑ\s]+(?:\s+[A-ZÁÉÍÓÚÑ]+)*)\s", texto)
                
                if not nombre_match:
                    # Último intento: buscar cualquier texto en mayúsculas entre "," y "tiene inscrito"
                    nombre_match = re.search(r",\s*([^,]+?)\s+tiene inscrito", texto)
                    if nombre_match:
                        # Filtrar solo letras mayúsculas y espacios
                        nombre_crudo = nombre_match.group(1)
                        nombre_limpio = re.sub(r'[^A-ZÁÉÍÓÚÑ\s]', '', nombre_crudo).strip()
                        if nombre_limpio:
                            nombre_match = type('obj', (object,), {'group': lambda self, x: nombre_limpio})()
                
                if nombre_match:
                    nombre_completo = nombre_match.group(1).strip().upper()
                    
                    # MEJORADO: Limpiar el nombre de caracteres no deseados
                    nombre_completo = re.sub(r'[^A-ZÁÉÍÓÚÑ\s]', '', nombre_completo)
                    nombre_completo = re.sub(r'\s+', ' ', nombre_completo).strip()
                    
                    # MEJORADO: Reorganizar nombre manejando casos con pocas partes
                    partes_nombre = nombre_completo.split()

                    if len(partes_nombre) >= 4:
                        # Caso típico: 4 o más partes (2 apellidos + 2 o más nombres)
                        apellidos = partes_nombre[:2]  # Primeros 2 son apellidos
                        nombres_persona = partes_nombre[2:]  # Resto son nombres
                        nombre = ' '.join(nombres_persona + apellidos)
                        
                    elif len(partes_nombre) == 3:
                        # Caso de 3 partes - decidir si es "Apellido Nombre1 Nombre2" o "Apellido1 Apellido2 Nombre"
                        # Verificar si el último podría ser un segundo nombre (más corto)
                        ultima_parte = partes_nombre[2]
                        primera_parte = partes_nombre[0]
                        
                        # Si la última parte es muy corta (2-3 letras), probablemente es segundo nombre
                        if len(ultima_parte) <= 3:
                            # Formato: Apellido Nombre1 Nombre2 (Nombre2 corto)
                            apellidos = partes_nombre[:1]  # Un apellido
                            nombres_persona = partes_nombre[1:]  # Dos nombres
                            nombre = ' '.join(nombres_persona + apellidos)
                        else:
                            # Formato: Apellido1 Apellido2 Nombre
                            apellidos = partes_nombre[:2]  # Dos apellidos
                            nombres_persona = partes_nombre[2:]  # Un nombre
                            nombre = ' '.join(nombres_persona + apellidos)
                            
                    elif len(partes_nombre) == 2:
                        # Caso de 2 partes - "Apellido Nombre"
                        nombre = f"{partes_nombre[1]} {partes_nombre[0]}"
                        
                    else:
                        # Caso de 1 parte - dejar como está
                        nombre = nombre_completo

            # --- Guardar resultados ---
            if nombre and numero_doc and tipo_doc:
                # Limpieza final del nombre
                nombre = re.sub(r'\s+[A-Z]$', '', nombre.strip())
                nombre = re.sub(r'\s+', ' ', nombre).strip()
                nombres.append(nombre)
                numeros_documento.append(numero_doc)
                tipos_documento.append(tipo_doc)
                paginas.append(page_num + 1)  # Guardar número de página (1-based)

    return nombres, numeros_documento, tipos_documento, paginas