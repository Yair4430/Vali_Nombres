import fitz
import re
import unicodedata
from thefuzz import fuzz  # Comparación difusa
# from spellchecker import SpellChecker  # <- Comentado, no es útil para nombres propios

def extraer_texto_pdf(ruta_pdf):
    doc = fitz.open(ruta_pdf)
    return [pagina.get_text() for pagina in doc]

def normalizar(texto):
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return re.sub(r'\s+', ' ', texto).strip().upper()

def extraer_nombres_aprobados(paginas):
    nombres = []
    patron_cedula = re.compile(r"(CC|TI)\s+(\d{7,})")
    
    for pagina in paginas:
        lineas = pagina.split('\n')
        for i, linea in enumerate(lineas):
            linea_normal = normalizar(linea)
            if patron_cedula.search(linea_normal):
                # Buscar nombre en la línea siguiente o dos líneas después
                for offset in range(1, 3):
                    if i + offset < len(lineas):
                        posible_nombre = normalizar(lineas[i + offset])
                        if (len(posible_nombre.split()) >= 2 and 
                            all(palabra.isalpha() for palabra in posible_nombre.split()) and 
                            15 <= len(posible_nombre) <= 60):
                            nombres.append(posible_nombre)
                            break
                else:
                    nombres.append("NO ENCONTRADO")
    return nombres

def extraer_listado(paginas):
    cedulas = []
    for pagina in paginas:
        lineas = pagina.split('\n')
        for linea in lineas:
            linea_normal = normalizar(linea)
            match = re.search(r"(CC|TI)\s+(\d{7,})", linea_normal)
            if match:
                cedulas.append(f"{match.group(1)} {match.group(2)}")
    if not cedulas:
        print("⚠️ No se encontraron cédulas en las páginas.")
    return cedulas

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

# Comentado para evitar falsos positivos en nombres
# def verificar_errores_ortograficos(nombre):
#     spell = SpellChecker(language='es')
#     palabras = nombre.split()
#     errores = [palabra for palabra in palabras if palabra not in spell]
#     return errores

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

            if similarity < 100:
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

    # Extraemos cédulas
    cedulas = extraer_listado(paginas_listado)

    # Extraemos nombres del bloque "APROBADO"
    nombres = []
    for pagina in paginas_listado:
        lineas = pagina.split('\n')
        for i in range(len(lineas) - 1):
            nombre = normalizar(lineas[i])
            siguiente = normalizar(lineas[i + 1])
            if siguiente == "APROBADO":
                nombres.append(nombre)

    # Creamos listado uniendo por orden
    listado = []
    for i in range(min(len(cedulas), len(nombres))):
        listado.append((cedulas[i], nombres[i]))

    certificados = extraer_certificados(paginas)

    if not cedulas or not nombres:
        return "⚠️ No se encontraron todos los datos del listado."

    resultados = comparar(listado, certificados)
    return "\n".join(resultados)

