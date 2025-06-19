import fitz
import re
from thefuzz import fuzz
import unicodedata

def extraer_texto_pdf(ruta_pdf):
    doc = fitz.open(ruta_pdf)
    return [pagina.get_text() for pagina in doc]

def normalizar(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def extraer_nombres_aprobados(paginas):
    nombres = []
    patron_nombre = re.compile(r'^([A-ZÑÁÉÍÓÚÜ ]{10,})$')  # al menos 10 letras mayúsculas seguidas (para evitar palabras sueltas)

    for pagina in paginas:
        lineas = pagina.split('\n')
        for linea in lineas:
            linea_normal = normalizar(linea).upper().strip()

            if patron_nombre.match(linea_normal):
                nombres.append(linea_normal)

    return nombres

def extraer_listado(paginas):
    cedulas = []
    for pagina in paginas:
        lineas = pagina.split('\n')
        for linea in lineas:
            linea_normal = normalizar(linea).upper().strip()
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
            certificados.append((doc_limpio, nombre.strip()))

    return certificados

def comparar(listado, certificados):
    resultados = []
    resultados.append(f"{'DOCUMENTO':<20} {'NOMBRE CERTIFICADO':<40} {'RESULTADO':<50}")
    resultados.append("-" * 110)

    cert_dict = {doc: nombre for doc, nombre in certificados}

    for item in listado:
        doc, nombre_listado = item
        doc = str(doc)  # ← por seguridad
        nombre_listado = str(nombre_listado)

        if doc in cert_dict:
            estado = "✅ OK"
            nombre_final = cert_dict[doc]
        else:
            estado = "❌ SIN CERTIFICADO"
            nombre_final = nombre_listado

        resultados.append(f"{doc:<20} {nombre_final:<40} {estado:<50}")

    return resultados

def procesar_pdf(ruta_pdf):
    paginas = extraer_texto_pdf(ruta_pdf)

    cedulas = extraer_listado(paginas[:1])  # las cédulas sí están en la primera página
    nombres = extraer_nombres_aprobados(paginas)  # nuevos nombres robustos
    certificados = extraer_certificados(paginas)

    if not cedulas or not nombres:
        return "⚠️ No se encontraron todos los datos del listado."
    
    # Emparejar cédula con nombre por índice
    listado = []
    for i in range(min(len(cedulas), len(nombres))):
        listado.append((cedulas[i], nombres[i]))  # ✅ aquí cedulas[i] y nombres[i] deben ser strings

    resultados = comparar(listado, certificados)
    return "\n".join(resultados)

