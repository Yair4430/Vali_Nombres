import React, { useState } from 'react'
import axios from 'axios'

const ModoMasivo = () => {
  const [carpeta, setCarpeta] = useState('')
  const [resultados, setResultados] = useState({})
  const [pdfSeleccionado, setPdfSeleccionado] = useState('')
  const [cargando, setCargando] = useState(false)
  const [mensaje, setMensaje] = useState('')

  const handleProcesarMasivo = async () => {
    if (!carpeta.trim()) {
      alert('Ingrese la ruta de la carpeta primero')
      return
    }

    setCargando(true)
    setMensaje('Procesando...')
    
    try {
      const response = await axios.post('/api/masivo', {
        carpeta: carpeta.trim()
      })
      
      if (response.data.success) {
        setResultados(response.data.resultados)
        if (Object.keys(response.data.resultados).length > 0) {
          setPdfSeleccionado(Object.keys(response.data.resultados)[0])
          setMensaje(`Procesamiento completado. Se encontraron ${Object.keys(response.data.resultados).length} archivos PDF.`)
        } else {
          setMensaje('No se encontraron archivos PDF en la carpeta especificada.')
        }
      } else {
        setMensaje('Error: ' + response.data.error)
        alert('Error: ' + response.data.error)
      }
    } catch (error) {
      console.error('Error al procesar:', error)
      const errorMsg = error.response?.data?.error || error.message || 'Error al procesar la carpeta'
      setMensaje('Error: ' + errorMsg)
      alert('Error: ' + errorMsg)
    } finally {
      setCargando(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleProcesarMasivo()
    }
  }

  return (
    <div className="panel">
      <h2 className="panel-title">Modo Masivo</h2>
      
      <div className="form-group">
        <label>Ruta de la carpeta con PDFs:</label>
        <input
          type="text"
          value={carpeta}
          onChange={(e) => setCarpeta(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ej: C:\Users\Usuario\Documents\PDFs"
          className="form-control"
          disabled={cargando}
        />
        <small style={{color: '#666', marginTop: '5px'}}>
          Ingrese la ruta completa de la carpeta que contiene los archivos PDF
        </small>
      </div>

      <button 
        onClick={handleProcesarMasivo} 
        disabled={cargando || !carpeta.trim()}
        className="btn btn-success"
        style={{marginRight: '10px'}}
      >
        {cargando ? '🔄 Procesando...' : '🚀 Ejecutar Procesamiento Masivo'}
      </button>

      {mensaje && (
        <div style={{
          margin: '15px 0',
          padding: '10px',
          backgroundColor: cargando ? '#e3f2fd' : '#e8f5e8',
          border: '1px solid',
          borderColor: cargando ? '#bbdefb' : '#c8e6c9',
          borderRadius: '4px'
        }}>
          {mensaje}
        </div>
      )}

      {Object.keys(resultados).length > 0 && (
        <>
          <div className="form-group">
            <label>Seleccionar PDF para ver detalles:</label>
            <select
              value={pdfSeleccionado}
              onChange={(e) => setPdfSeleccionado(e.target.value)}
              className="form-control"
            >
              {Object.keys(resultados).map(pdf => (
                <option key={pdf} value={pdf}>{pdf}</option>
              ))}
            </select>
          </div>

          <div className="table-container">
            <h3>Resultados de: {pdfSeleccionado}</h3>
            <div style={{marginBottom: '10px', fontSize: '14px', color: '#666'}}>
              Mostrando {resultados[pdfSeleccionado]?.length || 0} registros
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>No.</th>
                  <th>Tipo L</th>
                  <th>Doc L</th>
                  <th>Nombre Listado</th>
                  <th>Tipo C</th>
                  <th>Doc C</th>
                  <th>Nombre Certificado</th>
                  <th>%Doc</th>
                  <th>%Nombre</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {resultados[pdfSeleccionado]?.map((fila, index) => (
                  <tr key={index} className={fila[9].toLowerCase()}>
                    {fila.map((celda, cellIndex) => (
                      <td key={cellIndex}>{celda}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{marginTop: '20px', textAlign: 'center'}}>
            <button 
              onClick={() => {
                // Función para exportar resultados
                const dataStr = JSON.stringify(resultados, null, 2)
                const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
                const exportFileDefaultName = 'resultados_masivo.json'
                
                const linkElement = document.createElement('a')
                linkElement.setAttribute('href', dataUri)
                linkElement.setAttribute('download', exportFileDefaultName)
                linkElement.click()
              }}
              className="btn btn-primary"
            >
              💾 Exportar Resultados JSON
            </button>
          </div>
        </>
      )}

      <div className="panel" style={{ marginTop: '20px', background: '#f8f9fa' }}>
        <h4>Información del Modo Masivo</h4>
        <ul style={{ textAlign: 'left', paddingLeft: '20px' }}>
          <li><strong>Procesamiento automático:</strong> Analiza todos los PDFs en la carpeta y subcarpetas</li>
          <li><strong>Detección inteligente:</strong> Identifica automáticamente listados y certificados</li>
          <li><strong>Búsqueda recursiva:</strong> Examina todas las subcarpetas de la ruta proporcionada</li>
          <li><strong>Resultados detallados:</strong> Muestra comparaciones individuales por archivo</li>
          <li><strong>Formatos soportados:</strong> PDF con estructura de listado + certificados</li>
        </ul>
        
        <div style={{marginTop: '15px', padding: '10px', backgroundColor: '#fff3cd', border: '1px solid #ffeaa7', borderRadius: '4px'}}>
          <strong>💡 Ejemplos de rutas:</strong><br/>
          Windows: <code>C:\\Users\\Usuario\\Documents\\PDFs</code><br/>
          Linux/Mac: <code>/home/usuario/documentos/pdfs</code>
        </div>
      </div>
    </div>
  )
}

export default ModoMasivo