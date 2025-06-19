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

def comparar(cedulas, certificados):
    resultados = []
    resultados.append(f"{'DOCUMENTO':<20} {'NOMBRE CERTIFICADO':<40} {'RESULTADO':<50}")
    resultados.append("-" * 110)

    cert_dict = {doc: nombre for doc, nombre in certificados}

    for doc in cedulas:
        if doc in cert_dict:
            nombre = cert_dict[doc]
            estado = "✅ OK"
        else:
            nombre = ""
            estado = "❌ SIN CERTIFICADO"
        resultados.append(f"{doc:<20} {nombre:<40} {estado:<50}")

    return resultados

def procesar_pdf(ruta_pdf):
    paginas = extraer_texto_pdf(ruta_pdf)
    cedulas = extraer_listado(paginas[:1])  # está todo en la primera página
    certificados = extraer_certificados(paginas)

    if not cedulas:
        return "⚠️ No se encontró listado válido."
    if not certificados:
        return "⚠️ No se encontraron certificados."

    resultados = comparar(cedulas, certificados)
    return "\n".join(resultados)

