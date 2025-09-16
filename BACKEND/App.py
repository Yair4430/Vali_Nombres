from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import platform
from werkzeug.utils import secure_filename
from CompararDatos import comparar_datos
from Masivo import procesar_masivo
from ExtraerListado import extraer_datos_con_pdfplumber
from ExtraerCertificados import extraer_datos_certificados

app = Flask(__name__)
CORS(app)

# Configuración
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def normalizar_ruta(ruta):
    """Normaliza la ruta según el sistema operativo"""
    if platform.system() == 'Windows':
        # Para Windows, reemplazar / por \ y normalizar
        ruta = ruta.replace('/', '\\')
        # Asegurarse de que no termine con \
        if ruta.endswith('\\'):
            ruta = ruta[:-1]
    else:
        # Para Unix/Linux/Mac, reemplazar \ por /
        ruta = ruta.replace('\\', '/')
        # Asegurarse de que no termine con /
        if ruta.endswith('/'):
            ruta = ruta[:-1]
    return ruta

@app.route('/api/procesar', methods=['POST'])
def procesar_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se encontró el archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        
        if file and allowed_file(file.filename):
            # Guardar archivo temporal
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Obtener parámetros
            data = request.form
            inicio_listado = int(data.get('inicio_listado', 1))
            fin_listado = int(data.get('fin_listado', 1))
            inicio_cert = int(data.get('inicio_cert', 1))
            fin_cert = int(data.get('fin_cert', 1))
            
            # Procesar
            resultados = comparar_datos(filepath, inicio_listado, fin_listado, inicio_cert, fin_cert)
            
            # Limpiar archivo temporal
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'resultados': resultados,
                'total': len(resultados)
            })
            
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# En la función procesar_masivo_endpoint, modificar para incluir el estado general
@app.route('/api/masivo', methods=['POST'])
def procesar_masivo_endpoint():
    try:
        data = request.json
        carpeta_principal = data.get('carpeta')
        
        if not carpeta_principal:
            return jsonify({'error': 'Debe proporcionar una ruta de carpeta'}), 400
        
        # Normalizar la ruta
        carpeta_principal = normalizar_ruta(carpeta_principal)
        
        if not os.path.isdir(carpeta_principal):
            return jsonify({'error': f'La ruta no existe o no es una carpeta válida: {carpeta_principal}'}), 400
        
        # Verificar permisos de lectura
        if not os.access(carpeta_principal, os.R_OK):
            return jsonify({'error': 'No tiene permisos de lectura para la carpeta especificada'}), 400
        
        resultados = procesar_masivo(carpeta_principal)
        
        # Calcular estado general para cada PDF
        resultados_con_estado = {}
        for archivo, datos in resultados.items():
            # Verificar si hay errores en la extracción
            if datos and len(datos) > 0 and datos[0][0] == "Error":
                resultados_con_estado[archivo] = {
                    "resultados": datos,
                    "estado_general": "error"
                }
                continue
            
            # Contar problemas
            problemas = 0
            for fila in datos:
                estado = fila[9].lower() if len(fila) > 9 else ""
                porcentaje_doc = float(fila[7].replace('%', '')) if len(fila) > 7 else 0
                porcentaje_nombre = float(fila[8].replace('%', '')) if len(fila) > 8 else 0
                
                if (estado in ['duplicado', 'falta certificado', 'no existe en listado', 'error'] or 
                    porcentaje_doc < 100 or porcentaje_nombre < 100):
                    problemas += 1
            
            # Determinar estado general
            if problemas == 0:
                estado_general = "perfecto"
            else:
                estado_general = "con_problemas"
                
            resultados_con_estado[archivo] = {
                "resultados": datos,
                "estado_general": estado_general,
                "problemas": problemas,
                "total_registros": len(datos)
            }
        
        return jsonify({
            'success': True,
            'resultados': resultados_con_estado,
            'total_archivos': len(resultados_con_estado),
            'ruta_procesada': carpeta_principal
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/info-pdf', methods=['POST'])
def obtener_info_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se encontró el archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        
        if file and allowed_file(file.filename):
            # Guardar archivo temporal
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Obtener número de páginas
            import pdfplumber
            with pdfplumber.open(filepath) as pdf:
                total_paginas = len(pdf.pages)
            
            # Limpiar archivo temporal
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'total_paginas': total_paginas
            })
            
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ejemplos-rutas', methods=['GET'])
def obtener_ejemplos_rutas():
    """Devuelve ejemplos de rutas según el sistema operativo"""
    if platform.system() == 'Windows':
        ejemplos = [
            "C:\\Users\\TuUsuario\\Documents\\PDFs",
            "D:\\Proyectos\\Documentos",
            "\\\\servidor\\carpeta_compartida\\archivos"
        ]
    else:
        ejemplos = [
            "/home/usuario/documentos/pdfs",
            "/Users/tuusuario/Downloads",
            "/mnt/external/pdfs"
        ]
    
    return jsonify({
        'sistema_operativo': platform.system(),
        'ejemplos': ejemplos
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)