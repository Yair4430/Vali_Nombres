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
    nombres = []
    for pagina in paginas:
        lineas = pagina.split('\n')
        for linea in lineas:
            linea_normal = normalizar(linea).upper().strip()

            # Buscar cédulas
            if linea_normal.startswith("CC") or linea_normal.startswith("TI"):
                match = re.search(r"(CC|TI)\s+(\d{7,})", linea_normal)
                if match:
                    cedulas.append(f"{match.group(1)} {match.group(2)}")

            # Buscar nombres con "APROBADO"
            elif "APROBADO" in linea_normal:
                nombre = linea_normal.replace("APROBADO", "").strip()
                if nombre:  # asegurarse de que no esté vacío
                    nombres.append(nombre)

        print("CÉDULAS:", cedulas)
        print("NOMBRES:", nombres)

    if len(cedulas) != len(nombres):
        print(f"⚠️ Advertencia: {len(cedulas)} cédulas y {len(nombres)} nombres. Puede haber desalineación visual.")

    listado = []
    for i in range(min(len(cedulas), len(nombres))):
        listado.append((cedulas[i], nombres[i]))
    return listado

def extraer_certificados(paginas):
    certificados = []
    patron = r"A nombre de:\s+([A-ZÑÁÉÍÓÚÜ ]+)"
    for pagina in paginas:
        encontrados = re.findall(patron, pagina)
        certificados.extend([nombre.strip() for nombre in encontrados])
    return certificados

def comparar(listado, certificados):
    resultados = []
    resultados.append(f"{'DOCUMENTO':<20} {'NOMBRE LISTADO':<40} {'RESULTADO':<50}")
    resultados.append("-" * 110)

    longitud = min(len(listado), len(certificados))

    for i in range(longitud):
        doc, nombre_listado = listado[i]
        certificado = certificados[i]
        similitud = fuzz.ratio(nombre_listado.upper(), certificado.upper())

        if similitud > 90:
            estado = "✅ OK"
        else:
            estado = f"❌ NO COINCIDE ({similitud}% con '{certificado[:20]}')"

        resultados.append(f"{doc:<20} {nombre_listado:<40} {estado:<50}")

    # En caso de que haya más en el listado que en certificados
    if len(listado) > len(certificados):
        for j in range(len(certificados), len(listado)):
            doc, nombre_listado = listado[j]
            resultados.append(f"{doc:<20} {nombre_listado:<40} {'❌ SIN CERTIFICADO':<50}")

    return resultados

def procesar_pdf(ruta_pdf):
    paginas = extraer_texto_pdf(ruta_pdf)
    listado = extraer_listado(paginas[:3])  # primeras páginas tienen el listado

    if not listado:
        return "⚠️ No se encontró listado válido."

    certificados = extraer_certificados(paginas)

    if not certificados:
        return "⚠️ No se encontraron certificados."

    resultados = comparar(listado, certificados)
    return "\n".join(resultados)
