import os
import pdfplumber
import re
from CompararDatos import comparar_datos
from LimpiarCertificados import limpiar_certificados_pdf, obtener_documentos_validos

def detectar_listado_y_certificados(ruta_pdf):
    """
    Detecta automáticamente dónde termina el listado y comienzan los certificados
    analizando el contenido de las páginas.
    """
    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            total_paginas = len(pdf.pages)
            
            # Patrones para identificar listado vs certificados
            patrones_listado = [
                r'\d+\.\s+[A-Z0-9-]+\s+[A-ZÁÉÍÓÚÑ\s]+?POR CERTIFICAR',
                r'listado de',
                r'número\s+documento\s+nombre',
                r'no\.\s*tipo\s*doc\s*nombre'
            ]
            
            patrones_certificados = [
                r'cédula de ciudadanía',
                r'permiso por protección temporal',
                r'certificado de',
                r'número único de identificación personal',
                r'a nombre de:',
                r'república de colombia'
            ]
            
            # Analizar cada página para determinar su tipo
            ultima_pagina_listado = 0
            primera_pagina_certificados = total_paginas + 1
            
            for i, page in enumerate(pdf.pages, 1):
                texto = page.extract_text() or ""
                texto = texto.lower()
                
                # Contar coincidencias con patrones de listado
                coincidencias_listado = sum(1 for patron in patrones_listado if re.search(patron, texto, re.IGNORECASE))
                
                # Contar coincidencias con patrones de certificados
                coincidencias_certificados = sum(1 for patron in patrones_certificados if re.search(patron, texto, re.IGNORECASE))
                
                if coincidencias_listado > coincidencias_certificados:
                    ultima_pagina_listado = i
                elif coincidencias_certificados > coincidencias_listado:
                    if primera_pagina_certificados > i:
                        primera_pagina_certificados = i
            
            # Si encontramos una transición clara
            if ultima_pagina_listado > 0 and primera_pagina_certificados <= total_paginas:
                return 1, ultima_pagina_listado, primera_pagina_certificados, total_paginas
            
            # Si no encontramos transición clara, usar heurística
            # Asumir que los certificados son las últimas páginas
            punto_division = max(1, total_paginas - 5)  # Últimas 5 páginas para certificados
            
            return 1, punto_division, punto_division + 1, total_paginas
            
    except Exception as e:
        print(f"Error en detección automática para {ruta_pdf}: {e}")
        # Valores por defecto conservadores
        return 1, 1, 1, 1

def procesar_masivo(carpeta_principal):
    """
    Procesa en modo masivo con detección automática de rangos
    """
    resultados_masivos = {}

    if not os.path.isdir(carpeta_principal):
        raise ValueError("La ruta seleccionada no es una carpeta válida")

    # Recorremos subcarpetas
    for root, dirs, files in os.walk(carpeta_principal):
        for file in files:
            if file.lower().endswith(".pdf"):
                ruta_pdf = os.path.join(root, file)
                try:
                    # Detectar rangos automáticamente para este PDF
                    inicio_listado, fin_listado, inicio_cert, fin_cert = detectar_listado_y_certificados(ruta_pdf)
                    
                    print(f"Procesando {file}: Listado({inicio_listado}-{fin_listado}), Certificados({inicio_cert}-{fin_cert})")
                    
                    resultados = comparar_datos(ruta_pdf, inicio_listado, fin_listado, inicio_cert, fin_cert)
                    # Guardar tanto los resultados como la ruta completa
                    resultados_masivos[file] = {
                        'resultados': resultados,
                        'ruta_completa': ruta_pdf
                    }
                    
                except Exception as e:
                    print(f"Error procesando {file}: {e}")
                    resultados_masivos[file] = {
                        'resultados': [("Error", "-", "-", "-", "-", "-", "-", "-", "-", f"Error: {str(e)}")],
                        'ruta_completa': ruta_pdf
                    }

    return resultados_masivos

def limpiar_certificados_masivo(carpeta_principal, resultados_previos):
    """
    Limpia certificados innecesarios en todos los PDFs procesados
    """
    resultados_limpieza = {}
    
    if not os.path.isdir(carpeta_principal):
        raise ValueError("La ruta seleccionada no es una carpeta válida")
    
    for archivo, datos in resultados_previos.items():
        # Usar la ruta completa guardada durante el procesamiento
        if 'ruta_completa' in datos:
            ruta_pdf = datos['ruta_completa']
        else:
            # Fallback: construir la ruta desde la carpeta principal
            ruta_pdf = os.path.join(carpeta_principal, archivo)
        
        try:
            # Verificar que el archivo existe antes de procesarlo
            if not os.path.exists(ruta_pdf):
                resultados_limpieza[archivo] = {
                    'success': False,
                    'error': f"Archivo no encontrado: {ruta_pdf}",
                    'ruta_buscada': ruta_pdf
                }
                continue
            
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