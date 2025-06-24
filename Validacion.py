import fitz
import re
import unicodedata
from thefuzz import fuzz

def extraer_texto_pdf(ruta_pdf):
    doc = fitz.open(ruta_pdf)
    return [pagina.get_text() for pagina in doc]

def normalizar(texto):
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return re.sub(r'\s+', ' ', texto).strip().upper()

def extraer_listado(paginas):
    documentos = []
    nombres = []
    listado = []

    patron_documento = re.compile(r"(?:\d+\.\s*)?CC[-\s]?(\d{5,})")

    # 1. Extraer documentos válidos
    for pagina in paginas:
        for linea in pagina.split('\n'):
            linea_norm = normalizar(linea)
            match = patron_documento.search(linea_norm)
            if match:
                documentos.append(f"CC {match.group(1).strip()}")

    # 2. Extraer nombres: buscar bloque con nombres (después de "JUICIO DE EVALUACION")
    recolectar = False
    for linea in paginas[0].split('\n'):
        linea_norm = normalizar(linea.strip())

        if "JUICIO DE EVALUACION" in linea_norm:
            recolectar = True
            continue

        if recolectar:
            if (
                len(linea_norm.split()) >= 2 and
                linea_norm.isupper() and
                not re.search(r"\d", linea_norm) and
                not any(palabra in linea_norm for palabra in [
                    "APROBADO", "FIRMA", "COORDINADOR", "SENA", "INSTRUCTOR", "JUICIO DE", 
                    "TOTAL", "NOTA", "OBSERVACIONES", "CERTIFICADOS", "RESPONSABLE", "NO. HORAS",
                    "PROGRAMA", "EVALUACION", "CENTRO", "PRODUCCION", "TOLIMA", "IBAGUE", "EN EJECUCION", 
                    "CURSOS ESPECIALES", "MARIAANGELICA", "OAPROBADO"
                ])
            ):
                nombres.append(linea_norm)

    # 3. Emparejar documentos y nombres por orden
    for i in range(len(documentos)):
        nombre = nombres[i] if i < len(nombres) else "NO ENCONTRADO"
        listado.append((documentos[i], nombre))

    return listado

def extraer_por_bloques(paginas):
    listado = []
    patron_cedula = re.compile(r"^\s*\d+\.\s+(CC|TI)[-\s]?(\d{7,})")
    
    for pagina in paginas:
        lineas = pagina.split('\n')
        i = 0
        while i < len(lineas):
            linea = lineas[i]
            match_cedula = patron_cedula.search(normalizar(linea))
            if match_cedula:
                doc = f"{match_cedula.group(1)} {match_cedula.group(2)}"
                # Buscar nombre en las siguientes líneas
                nombre = "NO ENCONTRADO"
                for j in range(i+1, min(i+3, len(lineas))):  # Busca en las 2 líneas siguientes
                    posible_nombre = normalizar(lineas[j])
                    if (len(posible_nombre.split()) >= 2 and 
                        all(p.isalpha() or p in ['Ñ', 'Á', 'É', 'Í', 'Ó', 'Ú', 'Ü'] 
                            for p in posible_nombre.replace(' ', ''))):
                        nombre = posible_nombre
                        i = j  # Saltar las líneas ya procesadas
                        break
                listado.append((doc, nombre))
            i += 1
    return listado

def extraer_certificados(paginas):
    certificados = []
    patron_doc = re.compile(r"C[eé]dula de Ciudadan[ií]a:\s+([\d.]+)", re.IGNORECASE)
    patron_nombre = re.compile(r"A nombre de:\s+([A-ZÑÁÉÍÓÚÜ ]+)", re.IGNORECASE)

    for pagina in paginas:
        docs = patron_doc.findall(pagina)
        nombres = patron_nombre.findall(pagina)

        for doc, nombre in zip(docs, nombres):
            doc_limpio = f"CC {doc.replace('.', '').strip()}"
            nombre_limpio = normalizar(nombre.strip())
            certificados.append((doc_limpio, nombre_limpio))

    return certificados

def comparar(listado, certificados):
    resultados = []
    resultados.append(f"{'#':<4} {'DOCUMENTO':<20} {'NOMBRE CERTIFICADO':<40} {'RESULTADO':<50} {'ERRORES / DETALLE':<30}")
    resultados.append("-" * 150)

    cert_dict = {doc: nombre for doc, nombre in certificados}

    for idx, item in enumerate(listado, start=1):
        doc, nombre_listado = item
        nombre_listado_norm = normalizar(nombre_listado)
        doc = str(doc)

        if doc in cert_dict:
            nombre_final = cert_dict[doc]
            nombre_final_norm = normalizar(nombre_final)

            similarity = fuzz.ratio(nombre_final_norm, nombre_listado_norm)

            if nombre_listado_norm == "NO ENCONTRADO":
                estado = "❌ NOMBRE NO ENCONTRADO"
                errores_str = f"Nombre no extraído del listado"
            elif similarity < 100:
                estado = f"⚠️ SIMILITUD {similarity}%"
                diferencias = f"Esperado: {nombre_final_norm}, Encontrado: {nombre_listado_norm}"
                errores_str = diferencias
            else:
                estado = "✅ OK"
                errores_str = "Ninguno"
        else:
            estado = "❌ SIN CERTIFICADO"
            nombre_final = nombre_listado
            errores_str = "N/A"

        resultados.append(f"{idx:<4} {doc:<20} {nombre_final:<40} {estado:<50} {errores_str:<30}")
    return resultados

def procesar_pdf(ruta_pdf, pagina_inicio, pagina_fin):
    paginas = extraer_texto_pdf(ruta_pdf)
    paginas_listado = paginas[pagina_inicio:pagina_fin]

    listado = extraer_listado(paginas_listado)
    certificados = extraer_certificados(paginas)

    if not listado:
        return "⚠️ No se encontraron datos del listado."
    if not certificados:
        return "⚠️ No se encontraron certificados en el PDF."

    resultados = comparar(listado, certificados)
    return "\n".join(resultados)