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
        <small className="form-hint">
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
        <div className={`alert ${cargando ? 'alert-info' : 'alert-success'}`}>
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
            <h3 className="panel-subtitle">Resultados de: {pdfSeleccionado}</h3>
            <div className="form-hint">
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
                  {resultados[pdfSeleccionado]?.map((fila, index) => {
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
        </>
      )}
    </div>
  )
}

export default ModoMasivo