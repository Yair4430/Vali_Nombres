import difflib
from collections import Counter
from ExtraerListado import extraer_datos_con_pdfplumber
from ExtraerCertificados import extraer_datos_certificados

def calcular_similitud(texto1, texto2):
    """Devuelve porcentaje de similitud entre dos textos."""
    if not texto1 or not texto2:
        return 0
    return round(difflib.SequenceMatcher(None, str(texto1).strip(), str(texto2).strip()).ratio() * 100, 2)

def comparar_datos(archivo_pdf, inicio_listado, fin_listado, inicio_cert, fin_cert):
    """
    Devuelve lista con comparación de datos:
    (No, Tipo_L, Doc_L, Nombre_Listado, Tipo_C, Doc_C, Nombre_Certificado, %Doc, %Nombre, Estado, Pagina)
    """
    try:
        tipos_listado, docs_listado, nombres_listado = extraer_datos_con_pdfplumber(
            archivo_pdf, inicio_listado, fin_listado
        )
    except Exception as e:
        error_msg = str(e)
        if "No se pudo extraer el listado" in error_msg:
            return [("Error", "-", "-", "❌ NO SE PUEDE PROCESAR - Listado mal elaborado", "-", "-", "-", "-", "-", "Error Formato", "-")]
        else:
            return [("Error", "-", "-", f"Error listado: {error_msg}", "-", "-", "-", "-", "-", "Error", "-")]
    
    try:
        nombres_cert, docs_cert, tipos_cert, paginas_cert = extraer_datos_certificados(
            archivo_pdf, inicio_cert, fin_cert
        )
    except Exception as e:
        # Si hay error extrayendo certificados, marcar todos como no encontrados
        nombres_cert, docs_cert, tipos_cert, paginas_cert = [], [], [], []

    # Contar ocurrencias de certificados para detectar duplicados
    contador_certificados = Counter(docs_cert)

    # Crear diccionario con documento como clave y (tipo, nombre, página) como valor
    certificados_dict = {}
    for doc, tipo, nombre, pagina in zip(docs_cert, tipos_cert, nombres_cert, paginas_cert):
        certificados_dict[doc] = (tipo, nombre, pagina)

    resultados = []
    for i, (tipo_l, doc_l, nom_list) in enumerate(zip(tipos_listado, docs_listado, nombres_listado), 1):
        if doc_l in certificados_dict:
            tipo_c, nom_cert, pagina_cert = certificados_dict[doc_l]

            sim_doc = calcular_similitud(doc_l, doc_l)  # siempre 100 porque doc_l es la clave
            sim_nom = calcular_similitud(nom_list, nom_cert)

            estado = "OK"
            if contador_certificados[doc_l] > 1:
                estado = "Duplicado"
            elif sim_nom < 100:
                estado = "Nombre no coincide"

            resultados.append((i, tipo_l, doc_l, nom_list, tipo_c, doc_l, nom_cert, f"{sim_doc}%", f"{sim_nom}%", estado, pagina_cert))
        else:
            resultados.append((i, tipo_l, doc_l, nom_list, "❌", "❌", "No encontrado", "0%", "0%", "Falta Certificado", "-"))

    # Verificar certificados que no están en el listado
    docs_listado_set = set(docs_listado)
    for doc_c, tipo_c, nom_c, pagina_c in zip(docs_cert, tipos_cert, nombres_cert, paginas_cert):
        if doc_c not in docs_listado_set:
            resultados.append((
                "-", "-", "-", "-", tipo_c, doc_c, nom_c, "0%", "0%", "No existe en listado", pagina_c
            ))

    return resultados