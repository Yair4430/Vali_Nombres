import os
import shutil

def organizar_pdfs_perfectos(carpeta_principal, resultados_previos):
    """
    Crea una subcarpeta 'PDFS EN OK' y mueve allí las subcarpetas que contienen PDFs perfectos,
    renombrándolas con '_OK' al final.
    
    Args:
        carpeta_principal (str): Ruta de la carpeta principal
        resultados_previos (dict): Resultados del procesamiento masivo
    
    Returns:
        dict: Resultados de la operación
    """
    try:
        # Crear la subcarpeta 'PDFS EN OK'
        carpeta_ok = os.path.join(carpeta_principal, "PDFS EN OK")
        if not os.path.exists(carpeta_ok):
            os.makedirs(carpeta_ok)
        
        resultados_organizacion = {
            'success': True,
            'carpeta_ok_creada': carpeta_ok,
            'subcarpetas_movidas': [],
            'subcarpetas_con_error': [],
            'total_subcarpetas_perfectas': 0,
            'total_subcarpetas_movidas': 0
        }
        
        # Identificar subcarpetas que contienen solo PDFs perfectos
        subcarpetas_perfectas = identificar_subcarpetas_perfectas(carpeta_principal, resultados_previos)
        
        resultados_organizacion['total_subcarpetas_perfectas'] = len(subcarpetas_perfectas)
        
        # Mover y renombrar subcarpetas perfectas
        for subcarpeta_info in subcarpetas_perfectas:
            try:
                ruta_original = subcarpeta_info['ruta_original']
                nombre_original = subcarpeta_info['nombre_original']
                
                # Crear nuevo nombre para la subcarpeta con _OK
                nuevo_nombre = f"{nombre_original}_OK"
                nueva_ruta = os.path.join(carpeta_ok, nuevo_nombre)
                
                # Mover y renombrar la subcarpeta completa
                shutil.move(ruta_original, nueva_ruta)
                
                resultados_organizacion['subcarpetas_movidas'].append({
                    'subcarpeta_original': nombre_original,
                    'subcarpeta_renombrada': nuevo_nombre,
                    'ruta_original': ruta_original,
                    'ruta_nueva': nueva_ruta,
                    'archivos_perfectos': subcarpeta_info['archivos_perfectos']
                })
                resultados_organizacion['total_subcarpetas_movidas'] += 1
                
            except Exception as e:
                resultados_organizacion['subcarpetas_con_error'].append({
                    'subcarpeta': subcarpeta_info['nombre_original'],
                    'error': str(e)
                })
        
        return resultados_organizacion
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def identificar_subcarpetas_perfectas(carpeta_principal, resultados_previos):
    """
    Identifica las subcarpetas que contienen solo PDFs perfectos.
    
    Returns:
        list: Lista de diccionarios con información de subcarpetas perfectas
    """
    subcarpetas_info = {}
    
    # Primero, agrupar archivos por su subcarpeta
    for archivo, datos in resultados_previos.items():
        ruta_completa = datos.get('ruta_completa', '')
        if not ruta_completa:
            continue
            
        # Obtener la ruta de la subcarpeta relativa a la carpeta principal
        ruta_relativa = os.path.relpath(os.path.dirname(ruta_completa), carpeta_principal)
        
        # Si está en la raíz, considerar como "sin subcarpeta"
        if ruta_relativa == '.':
            ruta_relativa = ''
        
        if ruta_relativa not in subcarpetas_info:
            subcarpetas_info[ruta_relativa] = {
                'ruta_original': os.path.dirname(ruta_completa),
                'nombre_original': os.path.basename(os.path.dirname(ruta_completa)) if ruta_relativa else 'Archivos Raíz',
                'archivos': [],
                'es_perfecta': True  # Asumir que es perfecta hasta que se demuestre lo contrario
            }
        
        subcarpetas_info[ruta_relativa]['archivos'].append({
            'archivo': archivo,
            'estado': datos.get('estado_general'),
            'ruta': ruta_completa
        })
        
        # Si algún archivo no es perfecto, marcar la subcarpeta como no perfecta
        if datos.get('estado_general') != 'perfecto':
            subcarpetas_info[ruta_relativa]['es_perfecta'] = False
    
    # Filtrar solo las subcarpetas perfectas (que tienen al menos un archivo y todos son perfectos)
    subcarpetas_perfectas = []
    for info in subcarpetas_info.values():
        if info['es_perfecta'] and info['archivos']:
            # Solo incluir si no es la carpeta raíz (para evitar mover la carpeta principal completa)
            if info['nombre_original'] != os.path.basename(carpeta_principal):
                info['archivos_perfectos'] = len(info['archivos'])
                subcarpetas_perfectas.append(info)
    
    return subcarpetas_perfectas

def obtener_resultados_solo_con_problemas(resultados_previos, subcarpetas_movidas):
    """
    Filtra los resultados para mantener solo los archivos que NO están en subcarpetas movidas
    """
    resultados_filtrados = {}
    
    # Crear lista de rutas de subcarpetas que fueron movidas
    rutas_movidas = [item['ruta_original'] for item in subcarpetas_movidas]
    
    for archivo, datos in resultados_previos.items():
        ruta_completa = datos.get('ruta_completa', '')
        if ruta_completa:
            # Verificar si este archivo está en una subcarpeta que fue movida
            carpeta_archivo = os.path.dirname(ruta_completa)
            if carpeta_archivo not in rutas_movidas:
                resultados_filtrados[archivo] = datos
    
    return resultados_filtrados