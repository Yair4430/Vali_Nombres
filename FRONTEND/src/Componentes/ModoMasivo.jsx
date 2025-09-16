import React, { useState } from 'react'
import axios from 'axios'

const ModoMasivo = () => {
  const [carpeta, setCarpeta] = useState('')
  const [resultados, setResultados] = useState({})
  const [pdfSeleccionado, setPdfSeleccionado] = useState('')
  const [cargando, setCargando] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [mostrarResultados, setMostrarResultados] = useState(false)

  const handleProcesarMasivo = async () => {
    if (!carpeta.trim()) {
      alert('Ingrese la ruta de la carpeta primero')
      return
    }

    setCargando(true)
    setMensaje('Procesando...')
    setMostrarResultados(false)
    
    try {
      const response = await axios.post('/api/masivo', {
        carpeta: carpeta.trim()
      })
      
      if (response.data.success) {
        setResultados(response.data.resultados)
        if (Object.keys(response.data.resultados).length > 0) {
          // Seleccionar el primer PDF por defecto
          const primerPdf = Object.keys(response.data.resultados)[0]
          setPdfSeleccionado(primerPdf)
          setMensaje(`Procesamiento completado. Se encontraron ${Object.keys(response.data.resultados).length} archivos PDF.`)
          setMostrarResultados(true)
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

  // Función para determinar la clase CSS según el estado del PDF
  const getClaseEstadoPdf = (estado) => {
    switch (estado) {
      case 'perfecto':
        return 'estado-perfecto'
      case 'con_problemas':
        return 'estado-con-problemas'
      case 'error':
        return 'estado-error'
      default:
        return ''
    }
  }

  return (
    <div className="panel">
      <h2 className="panel-title">
        <span className="icon-multiple"></span>
        Procesamiento Masivo
      </h2>
      
      <div className="form-group">
        <label className="form-label">
          <span className="label-icon">📁</span>
          Ruta de la carpeta con PDFs
        </label>
        <div className="folder-input-container">
          <input
            type="text"
            value={carpeta}
            onChange={(e) => setCarpeta(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ej: C:\Users\Usuario\Documents\PDFs"
            className="form-control folder-input"
            disabled={cargando}
          />
          <button 
            onClick={handleProcesarMasivo} 
            disabled={cargando || !carpeta.trim()}
            className="btn btn-folder"
          >
            <span className="folder-icon">📂</span>
            Examinar
          </button>
        </div>
        <small className="form-hint">
          Ingrese la ruta completa de la carpeta que contiene los archivos PDF o haga clic en examinar
        </small>
      </div>

      <div className="action-buttons">
        <button 
          onClick={handleProcesarMasivo} 
          disabled={cargando || !carpeta.trim()}
          className="btn btn-success process-massive-btn"
        >
          {cargando ? (
            <>
              <span className="spinner"></span> 
              Procesando carpeta...
            </>
          ) : (
            <>
              <span className="btn-process-icon">🚀</span>
              Ejecutar Procesamiento Masivo
            </>
          )}
        </button>
      </div>

      {mensaje && (
        <div className={`alert ${cargando ? 'alert-info' : resultados && Object.keys(resultados).length > 0 ? 'alert-success' : 'alert-info'}`}>
          <span className="alert-icon">{cargando ? '⏳' : '✅'}</span>
          {mensaje}
        </div>
      )}

      {Object.keys(resultados).length > 0 && (
        <>
          <div className={`results-container massive ${mostrarResultados ? 'visible' : ''}`}>
            <div className="results-header">
              <div className="results-selection">
                <label>Seleccionar PDF para ver detalles:</label>
                <select
                  value={pdfSeleccionado}
                  onChange={(e) => setPdfSeleccionado(e.target.value)}
                  className="form-control pdf-selector"
                >
                  {Object.keys(resultados).map(pdf => (
                    <option 
                      key={pdf} 
                      value={pdf}
                      className={getClaseEstadoPdf(resultados[pdf]?.estado_general)}
                    >
                      {pdf} {resultados[pdf]?.estado_general === 'perfecto' ? '✅' : 
                            resultados[pdf]?.estado_general === 'con_problemas' ? '⚠️' : 
                            resultados[pdf]?.estado_general === 'error' ? '❌' : ''}
                    </option>
                  ))}
                </select>
                <span className="results-count">
                  {resultados[pdfSeleccionado]?.total_registros || 0} registros
                  {resultados[pdfSeleccionado]?.problemas > 0 && 
                    ` (${resultados[pdfSeleccionado]?.problemas} problemas)`}
                </span>
              </div>
            </div>

            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>No.</th>
                    <th>Tipo Documento Listado</th>
                    <th>No. Documento Listado</th>
                    <th>Nombres y Apellidos Listado</th>
                    <th>Tipo Documento Certificado</th>
                    <th>No. Documento Certificado</th>
                    <th>Nombres y Apellidos Certificado</th>
                    <th>% Numero de Documento</th>
                    <th>% Nombres y Apellidos</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {resultados[pdfSeleccionado]?.resultados?.map((fila, index) => {
                    const porcentajeDoc = parseFloat(fila[7].replace('%', '')) || 0
                    const porcentajeNombre = parseFloat(fila[8].replace('%', '')) || 0
                    const estado = fila[9].toLowerCase()

                    let claseSubrayado = ''

                    if (estado === 'duplicado') {
                      claseSubrayado = 'subrayado-amarillo'
                    } else if (estado === 'falta certificado' || estado === 'no existe en listado') {
                      claseSubrayado = 'subrayado-naranja'
                    } else if (porcentajeDoc < 100 || porcentajeNombre < 100) {
                      claseSubrayado = 'subrayado-rojo'
                    }

                    const claseFila = `${fila[9].toLowerCase()} ${claseSubrayado}`.trim()

                    return (
                      <tr key={index} className={claseFila}>
                        {fila.map((celda, cellIndex) => (
                          <td key={cellIndex}>{celda}</td>
                        ))}
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default ModoMasivo