import React, { useState } from 'react'
import axios from 'axios'

const ModoMasivo = () => {
  const [carpeta, setCarpeta] = useState('')
  const [resultados, setResultados] = useState({})
  const [pdfSeleccionado, setPdfSeleccionado] = useState('')
  const [cargando, setCargando] = useState(false)
  const [limpiando, setLimpiando] = useState(false)
  const [organizando, setOrganizando] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [mostrarResultados, setMostrarResultados] = useState(false)
  const [resultadosLimpieza, setResultadosLimpieza] = useState(null)
  const [resultadosOrganizacion, setResultadosOrganizacion] = useState(null)

  // Función para eliminar un PDF de la lista
  const handleEliminarPDF = (nombrePdf, event) => {
    // Prevenir que el evento se propague y afecte la selección del dropdown
    event.stopPropagation()
    event.preventDefault()

    if (!confirm(`¿Está seguro de que desea eliminar "${nombrePdf}" de la lista?\n\nEsta acción solo lo quitará de la vista, no eliminará el archivo físico.`)) {
      return
    }

    // Crear una copia de los resultados sin el PDF eliminado
    const nuevosResultados = { ...resultados }
    delete nuevosResultados[nombrePdf]

    // Actualizar el estado
    setResultados(nuevosResultados)

    // Si el PDF eliminado era el seleccionado, seleccionar el primero disponible
    if (pdfSeleccionado === nombrePdf) {
      const pdfsRestantes = Object.keys(nuevosResultados)
      if (pdfsRestantes.length > 0) {
        setPdfSeleccionado(pdfsRestantes[0])
      } else {
        setPdfSeleccionado('')
        setMostrarResultados(false)
      }
    }

    setMensaje(`✅ "${nombrePdf}" ha sido eliminado de la lista.`)
  }

  const handleProcesarMasivo = async () => {
    if (!carpeta.trim()) {
      alert('Ingrese la ruta de la carpeta primero')
      return
    }

    setCargando(true)
    setMensaje('Procesando...')
    setMostrarResultados(false)
    setResultadosLimpieza(null)
    setResultadosOrganizacion(null)
    
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

  const handleOrganizarPDFsPerfectos = async () => {
    if (!carpeta.trim() || Object.keys(resultados).length === 0) {
      alert('Primero debe procesar la carpeta para identificar las subcarpetas perfectas')
      return
    }

    // Contar archivos perfectos para mostrar en la confirmación
    const archivosPerfectos = Object.values(resultados).filter(
      pdf => pdf.estado_general === 'perfecto'
    ).length

    if (archivosPerfectos === 0) {
      alert('No hay archivos PDF en estado "perfecto" para organizar.')
      return
    }

    if (!confirm(`¿Está seguro de que desea organizar las subcarpetas perfectas?\n\nEsta acción:` +
                `\n• Creará una subcarpeta "PDFS EN OK" en la carpeta principal` +
                `\n• Moverá las subcarpetas que contienen solo PDFs perfectos` +
                `\n• Renombrará las subcarpetas agregando "_OK" al final` +
                `\n• Los resultados mostrarán solo los archivos con problemas` +
                `\n• NO se puede deshacer`)) {
      return
    }

    setOrganizando(true)
    setMensaje('📁 Organizando subcarpetas perfectas...')
    
    try {
      const response = await axios.post('/api/organizar-pdfs-perfectos', {
        carpeta: carpeta.trim(),
        resultados_previos: resultados
      })
      
      if (response.data.success) {
        setResultadosOrganizacion(response.data)
        const { total_subcarpetas_movidas } = response.data.resultados_organizacion
        
        // Actualizar resultados para mostrar solo los que tienen problemas
        setResultados(response.data.resultados_filtrados)
        
        if (Object.keys(response.data.resultados_filtrados).length > 0) {
          const primerPdf = Object.keys(response.data.resultados_filtrados)[0]
          setPdfSeleccionado(primerPdf)
        }
        
        setMensaje(`✅ Organización completada. Se movieron ${total_subcarpetas_movidas} subcarpetas perfectas a "PDFS EN OK".`)
      } else {
        setMensaje('❌ Error en la organización: ' + response.data.error)
      }
    } catch (error) {
      console.error('Error al organizar subcarpetas:', error)
      const errorMsg = error.response?.data?.error || error.message || 'Error al organizar subcarpetas'
      setMensaje('❌ Error: ' + errorMsg)
    } finally {
      setOrganizando(false)
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
      case 'error_formato':
        return 'estado-error-formato'
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
            disabled={cargando || limpiando || organizando}
          />
          <button 
            onClick={handleProcesarMasivo} 
            disabled={cargando || limpiando || organizando || !carpeta.trim()}
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
          disabled={cargando || limpiando || organizando || !carpeta.trim()}
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
          disabled={limpiando || cargando || organizando || Object.keys(resultados).length === 0}
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

        {/* BOTÓN PARA ORGANIZAR PDFS PERFECTOS */}
        <button 
          onClick={handleOrganizarPDFsPerfectos} 
          disabled={organizando || cargando || limpiando || Object.keys(resultados).length === 0}
          className="btn btn-info organize-pdfs-btn"
          style={{ marginLeft: '10px' }}
          title="Mover PDFs perfectos a subcarpeta y renombrarlos"
        >
          {organizando ? (
            <>
              <span className="spinner"></span> 
              Organizando PDFs...
            </>
          ) : (
            <>
              <span className="btn-organize-icon">📂</span>
              Reunir los que están bien
            </>
          )}
        </button>
      </div>

      {mensaje && (
        <div className={`alert ${cargando ? 'alert-info' : limpiando ? 'alert-warning' : organizando ? 'alert-primary' : resultados && Object.keys(resultados).length > 0 ? 'alert-success' : 'alert-info'}`}>
          <span className="alert-icon">
            {cargando ? '⏳' : limpiando ? '🧹' : organizando ? '📁' : '✅'}
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

      {/* Mostrar resultados de organización */}
      {resultadosOrganizacion && (
        <div className="alert alert-primary">
          <h4>📁 Resultados de la Organización:</h4>
          <ul>
            <li><strong>Carpeta creada:</strong> {resultadosOrganizacion.resultados_organizacion.carpeta_ok_creada}</li>
            <li><strong>Subcarpetas perfectas encontradas:</strong> {resultadosOrganizacion.resultados_organizacion.total_subcarpetas_perfectas}</li>
            <li><strong>Subcarpetas movidas exitosamente:</strong> {resultadosOrganizacion.resultados_organizacion.total_subcarpetas_movidas}</li>
            <li><strong>Archivos mostrados ahora:</strong> {resultadosOrganizacion.total_archivos_filtrados} (solo con problemas)</li>
          </ul>
          <details>
            <summary>📋 Ver detalles de subcarpetas movidas</summary>
            <div className="organizacion-detalles">
              {resultadosOrganizacion.resultados_organizacion.subcarpetas_movidas.map((subcarpeta, index) => (
                <div key={index} className="subcarpeta-organizada exitosa">
                  <strong>{subcarpeta.subcarpeta_original}</strong> → <strong>{subcarpeta.subcarpeta_renombrada}</strong>
                  <div className="subcarpeta-info">
                    <small>Contiene {subcarpeta.archivos_perfectos} archivos perfectos</small>
                  </div>
                  <div className="ruta-detalle">
                    <small>De: {subcarpeta.ruta_original}</small>
                    <br />
                    <small>A: {subcarpeta.ruta_nueva}</small>
                  </div>
                </div>
              ))}
              {resultadosOrganizacion.resultados_organizacion.subcarpetas_con_error.length > 0 && (
                <>
                  <h5>Subcarpetas con error:</h5>
                  {resultadosOrganizacion.resultados_organizacion.subcarpetas_con_error.map((subcarpeta, index) => (
                    <div key={index} className="subcarpeta-organizada error">
                      <strong>{subcarpeta.subcarpeta}</strong> - Error: {subcarpeta.error}
                    </div>
                  ))}
                </>
              )}
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
                <div className="pdf-selector-container">
                  <select
                    value={pdfSeleccionado}
                    onChange={(e) => setPdfSeleccionado(e.target.value)}
                    className="form-control pdf-selector"
                    disabled={cargando || limpiando || organizando}
                  >
                    {Object.keys(resultados).map(pdf => (
                      // En el selector de PDFs, actualiza para mostrar el nuevo estado:
                      <option 
                        key={pdf} 
                        value={pdf}
                        className={getClaseEstadoPdf(resultados[pdf]?.estado_general)}
                      >
                        {pdf} {resultados[pdf]?.estado_general === 'perfecto' ? '✅' : 
                              resultados[pdf]?.estado_general === 'con_problemas' ? '⚠️' : 
                              resultados[pdf]?.estado_general === 'error_formato' ? '❌ FORMATO' : 
                              resultados[pdf]?.estado_general === 'error' ? '❌' : ''}
                      </option>
                    ))}
                  </select>
                  <button
                    className="btn-eliminar-pdf"
                    onClick={(e) => handleEliminarPDF(pdfSeleccionado, e)}
                    disabled={cargando || limpiando || organizando || !pdfSeleccionado}
                    title={`Eliminar "${pdfSeleccionado}" de la lista`}
                  >
                    🗑️
                  </button>
                </div>
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