import React, { useState } from 'react'
import axios from 'axios'

const ModoMasivo = () => {
  const [carpeta, setCarpeta] = useState('')
  const [resultados, setResultados] = useState({})
  const [pdfSeleccionado, setPdfSeleccionado] = useState('')
  const [cargando, setCargando] = useState(false)
  const [limpiando, setLimpiando] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [mostrarResultados, setMostrarResultados] = useState(false)
  const [resultadosLimpieza, setResultadosLimpieza] = useState(null)

  const handleProcesarMasivo = async () => {
    if (!carpeta.trim()) {
      alert('Ingrese la ruta de la carpeta primero')
      return
    }

    setCargando(true)
    setMensaje('Procesando...')
    setMostrarResultados(false)
    setResultadosLimpieza(null)
    
    try {
      const response = await axios.post('/api/masivo', {
        carpeta: carpeta.trim()
      })
      
      if (response.data.success) {
        setResultados(response.data.resultados)
        if (Object.keys(response.data.resultados).length > 0) {
          const primerPdf = Object.keys(response.data.resultados)[0]
          setPdfSeleccionado(primerPdf)
          setMensaje(`✅ Procesamiento completado. Se encontraron ${Object.keys(response.data.resultados).length} archivos PDF.`)
          setMostrarResultados(true)
        } else {
          setMensaje('ℹ️ No se encontraron archivos PDF en la carpeta especificada.')
        }
      } else {
        setMensaje('❌ Error: ' + response.data.error)
        alert('Error: ' + response.data.error)
      }
    } catch (error) {
      console.error('Error al procesar:', error)
      const errorMsg = error.response?.data?.error || error.message || 'Error al procesar la carpeta'
      setMensaje('❌ Error: ' + errorMsg)
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

  const handleLimpiarCertificados = async () => {
    if (!carpeta.trim() || Object.keys(resultados).length === 0) {
      alert('Primero debe procesar la carpeta para identificar certificados innecesarios')
      return
    }

    if (!confirm('¿Está seguro de que desea eliminar los certificados innecesarios?\n\nEsta acción:' +
                 '\n• Eliminará certificados que no están en el listado' +
                 '\n• Eliminará certificados duplicados (conservando solo el primero)' +
                 '\n• Sobrescribirá los archivos PDF originales' +
                 '\n• NO se puede deshacer')) {
      return
    }

    setLimpiando(true)
    setMensaje('🧹 Eliminando certificados innecesarios...')
    
    try {
      const response = await axios.post('/api/limpiar-certificados', {
        carpeta: carpeta.trim(),
        resultados_previos: resultados
      })
      
      if (response.data.success) {
        setResultadosLimpieza(response.data)
        const { total_paginas_eliminadas, archivos_exitosos } = response.data.estadisticas
        setMensaje(`✅ Limpieza completada. Se eliminaron ${total_paginas_eliminadas} páginas innecesarias de ${archivos_exitosos} archivos.`)
        
        // Reprocesar automáticamente para mostrar resultados actualizados
        handleReprocesarCarpeta()
      } else {
        setMensaje('❌ Error en la limpieza: ' + response.data.error)
      }
    } catch (error) {
      console.error('Error al limpiar certificados:', error)
      const errorMsg = error.response?.data?.error || error.message || 'Error al limpiar certificados'
      setMensaje('❌ Error: ' + errorMsg)
    } finally {
      setLimpiando(false)
    }
  }

  const handleReprocesarCarpeta = async () => {
    setCargando(true)
    setMensaje('🔄 Reprocesando carpeta después de la limpieza...')
    
    try {
      const response = await axios.post('/api/masivo', {
        carpeta: carpeta.trim()
      })
      
      if (response.data.success) {
        setResultados(response.data.resultados)
        if (Object.keys(response.data.resultados).length > 0) {
          const primerPdf = Object.keys(response.data.resultados)[0]
          setPdfSeleccionado(primerPdf)
        }
        
        // Calcular estadísticas después del reprocesamiento
        const totalArchivos = Object.keys(response.data.resultados).length
        const archivosPerfectos = Object.values(response.data.resultados).filter(
          pdf => pdf.estado_general === 'perfecto'
        ).length
        
        setMensaje(`✅ Reprocesamiento completado. ${archivosPerfectos} de ${totalArchivos} archivos están ahora perfectos.`)
      } else {
        setMensaje('❌ Error al reprocesar: ' + response.data.error)
      }
    } catch (error) {
      console.error('Error al reprocesar:', error)
      setMensaje('❌ Error al reprocesar: ' + (error.response?.data?.error || error.message))
    } finally {
      setCargando(false)
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

  // Calcular estadísticas generales
  const calcularEstadisticas = () => {
    const totalArchivos = Object.keys(resultados).length
    const archivosPerfectos = Object.values(resultados).filter(
      pdf => pdf.estado_general === 'perfecto'
    ).length
    const archivosConProblemas = Object.values(resultados).filter(
      pdf => pdf.estado_general === 'con_problemas'
    ).length
    const archivosConError = Object.values(resultados).filter(
      pdf => pdf.estado_general === 'error'
    ).length

    return { totalArchivos, archivosPerfectos, archivosConProblemas, archivosConError }
  }

  const estadisticas = calcularEstadisticas()

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
            disabled={cargando || limpiando}
          />
          <button 
            onClick={handleProcesarMasivo} 
            disabled={cargando || limpiando || !carpeta.trim()}
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

      {/* Estadísticas rápidas */}
      {estadisticas.totalArchivos > 0 && (
        <div className="estadisticas-rapidas">
          <div className="estadistica-item">
            <span className="estadistica-numero">{estadisticas.totalArchivos}</span>
            <span className="estadistica-label">Total PDFs</span>
          </div>
          <div className="estadistica-item perfecto">
            <span className="estadistica-numero">{estadisticas.archivosPerfectos}</span>
            <span className="estadistica-label">Perfectos</span>
          </div>
          <div className="estadistica-item problemas">
            <span className="estadistica-numero">{estadisticas.archivosConProblemas}</span>
            <span className="estadistica-label">Con problemas</span>
          </div>
          <div className="estadistica-item error">
            <span className="estadistica-numero">{estadisticas.archivosConError}</span>
            <span className="estadistica-label">Con error</span>
          </div>
        </div>
      )}

      <div className="action-buttons">
        <button 
          onClick={handleProcesarMasivo} 
          disabled={cargando || limpiando || !carpeta.trim()}
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

        <button 
          onClick={handleLimpiarCertificados} 
          disabled={limpiando || cargando || Object.keys(resultados).length === 0}
          className="btn btn-warning clean-certificates-btn"
          style={{ marginLeft: '10px' }}
          title="Eliminar certificados que no están en el listado o están duplicados"
        >
          {limpiando ? (
            <>
              <span className="spinner"></span> 
              Limpiando certificados...
            </>
          ) : (
            <>
              <span className="btn-clean-icon">🧹</span>
              Borrar Certificados Innecesarios
            </>
          )}
        </button>
      </div>

      {mensaje && (
        <div className={`alert ${cargando ? 'alert-info' : limpiando ? 'alert-warning' : resultados && Object.keys(resultados).length > 0 ? 'alert-success' : 'alert-info'}`}>
          <span className="alert-icon">
            {cargando ? '⏳' : limpiando ? '🧹' : '✅'}
          </span>
          {mensaje}
        </div>
      )}

      {/* Mostrar resultados de limpieza */}
      {resultadosLimpieza && (
        <div className="alert alert-info">
          <h4>📊 Resultados de la Limpieza:</h4>
          <ul>
            <li><strong>Archivos procesados:</strong> {resultadosLimpieza.estadisticas.total_archivos}</li>
            <li><strong>Archivos exitosos:</strong> {resultadosLimpieza.estadisticas.archivos_exitosos}</li>
            <li><strong>Páginas eliminadas:</strong> {resultadosLimpieza.estadisticas.total_paginas_eliminadas}</li>
          </ul>
          <details>
            <summary>📋 Ver detalles por archivo</summary>
            <div className="limpieza-detalles">
              {Object.entries(resultadosLimpieza.resultados_limpieza).map(([archivo, resultado]) => (
                <div key={archivo} className={`archivo-limpieza ${resultado.success ? 'exitoso' : 'error'}`}>
                  <strong>{archivo}:</strong> {resultado.success ? 
                    `✅ ${resultado.paginas_eliminadas} páginas eliminadas (${resultado.paginas_originales} → ${resultado.paginas_finales})` : 
                    `❌ Error: ${resultado.error}`}
                </div>
              ))}
            </div>
          </details>
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
                  disabled={cargando || limpiando}
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
                    <th>Página</th>
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