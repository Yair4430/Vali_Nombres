import re
import os
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter

def encontrar_ruta_archivo(carpeta_principal, nombre_archivo):
    """
    Busca recursivamente un archivo en la carpeta principal y sus subcarpetas
    """
    for root, dirs, files in os.walk(carpeta_principal):
        if nombre_archivo in files:
            return os.path.join(root, nombre_archivo)
    return None

def obtener_documentos_validos(resultados_comparacion):
    """
    Extrae los documentos válidos de los resultados de comparación.
    Un documento es válido si está en el listado y no está duplicado.
    """
    documentos_validos = set()
    documentos_vistos = set()
    
    for fila in resultados_comparacion:
        if len(fila) > 5:
            doc_listado = fila[2]  # Documento del listado
            doc_certificado = fila[5]  # Documento del certificado
            estado = fila[9].lower() if len(fila) > 9 else ""
            
            # Solo considerar documentos que están en el listado y no son duplicados
            if (doc_listado and doc_listado != "❌" and doc_listado != "-" and
                estado != "duplicado" and estado != "no existe en listado"):
                
                if doc_listado not in documentos_vistos:
                    documentos_validos.add(doc_listado)
                    documentos_vistos.add(doc_listado)
    
    return documentos_validos

def limpiar_certificados_pdf(ruta_pdf, documentos_validos):
    """
    Elimina páginas de certificados que no están en la lista de documentos válidos
    o que están duplicados, manteniendo solo la primera ocurrencia.
    """
    try:
        # Leer el PDF original
        reader = PdfReader(ruta_pdf)
        total_paginas_original = len(reader.pages)
        
        # Extraer información de certificados para identificar páginas
        paginas_a_conservar = set()
        documentos_encontrados = set()
        paginas_por_documento = {}
        
        # Identificar páginas que contienen certificados
        with pdfplumber.open(ruta_pdf) as pdf:
            for pagina_num in range(len(pdf.pages)):
                texto = pdf.pages[pagina_num].extract_text() or ""
                
                # Buscar documentos en esta página
                documento_en_pagina = None
                
                # Patrón para CC
                cc_match = re.search(r"Cédula de Ciudadanía:\s*([\d.]+)", texto)
                if cc_match:
                    documento_en_pagina = cc_match.group(1).replace(".", "")
                
                # Patrón para PPT
                if not documento_en_pagina:
                    ppt_match = re.search(r"Permiso por Protección Temporal N°:\s*([\d]+)", texto)
                    if ppt_match:
                        documento_en_pagina = ppt_match.group(1).strip()
                
                # Patrón para TI
                if not documento_en_pagina:
                    ti_match = re.search(r"Número Único de Identificación Personal\s*(\d+)", texto)
                    if ti_match:
                        documento_en_pagina = ti_match.group(1).strip()
                
                if documento_en_pagina:
                    # Si es un documento válido y no duplicado, conservar la página
                    if (documento_en_pagina in documentos_validos and 
                        documento_en_pagina not in documentos_encontrados):
                        paginas_a_conservar.add(pagina_num)
                        documentos_encontrados.add(documento_en_pagina)
                        paginas_por_documento[documento_en_pagina] = pagina_num + 1
                    else:
                        # Documento no válido o duplicado, no conservar
                        continue
                else:
                    # Página que no es certificado (probablemente listado), conservar
                    paginas_a_conservar.add(pagina_num)
        
        # Si no hay páginas para eliminar, retornar sin cambios
        if len(paginas_a_conservar) == total_paginas_original:
            return {
                'success': True,
                'paginas_originales': total_paginas_original,
                'paginas_finales': total_paginas_original,
                'paginas_eliminadas': 0,
                'documentos_conservados': len(documentos_encontrados),
                'paginas_por_documento': paginas_por_documento,
                'mensaje': 'No se encontraron certificados innecesarios para eliminar'
            }
        
        # Crear nuevo PDF solo con páginas a conservar
        writer = PdfWriter()
        
        for pagina_num in range(total_paginas_original):
            if pagina_num in paginas_a_conservar:
                writer.add_page(reader.pages[pagina_num])
        
        # Guardar el PDF limpio (sobrescribir el original)
        with open(ruta_pdf, 'wb') as output_pdf:
            writer.write(output_pdf)
        
        return {
            'success': True,
            'paginas_originales': total_paginas_original,
            'paginas_finales': len(paginas_a_conservar),
            'paginas_eliminadas': total_paginas_original - len(paginas_a_conservar),
            'documentos_conservados': len(documentos_encontrados),
            'paginas_por_documento': paginas_por_documento
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def limpiar_certificados_masivo(carpeta_principal, resultados_previos):
    """
    Limpia certificados innecesarios en todos los PDFs procesados
    """
    resultados_limpieza = {}
    
    if not os.path.isdir(carpeta_principal):
        raise ValueError("La ruta seleccionada no es una carpeta válida")
    
    for archivo, datos in resultados_previos.items():
        # Primero intentar con la ruta completa guardada
        ruta_pdf = datos.get('ruta_completa', '')
        
        # Si no hay ruta completa o el archivo no existe, buscar recursivamente
        if not ruta_pdf or not os.path.exists(ruta_pdf):
            ruta_pdf = encontrar_ruta_archivo(carpeta_principal, archivo)
        
        # Si aún no encontramos el archivo, reportar error
        if not ruta_pdf or not os.path.exists(ruta_pdf):
            resultados_limpieza[archivo] = {
                'success': False,
                'error': f"Archivo no encontrado: {archivo}",
                'carpeta_buscada': carpeta_principal,
                'sugerencia': "El archivo podría haber sido movido o eliminado"
            }
            continue
        
        try:
            # Obtener documentos válidos para este PDF
            documentos_validos = obtener_documentos_validos(datos.get('resultados', []))
            
            # Limpiar certificados
            resultado_limpieza = limpiar_certificados_pdf(ruta_pdf, documentos_validos)
            resultado_limpieza['ruta_procesada'] = ruta_pdf
            resultados_limpieza[archivo] = resultado_limpieza
            
        except Exception as e:
            resultados_limpieza[archivo] = {
                'success': False,
                'error': f"Error limpiando certificados: {str(e)}",
                'ruta_intentada': ruta_pdf
            }
    
    return resultados_limpieza