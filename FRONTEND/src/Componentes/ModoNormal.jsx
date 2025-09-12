import React, { useState } from 'react'
import axios from 'axios'

const ModoNormal = () => {
  const [archivo, setArchivo] = useState(null)
  const [nombreArchivo, setNombreArchivo] = useState('')
  const [totalPaginas, setTotalPaginas] = useState(0)
  const [rangos, setRangos] = useState({
    inicio_listado: '',
    fin_listado: '',
    inicio_cert: '',
    fin_cert: ''
  })
  const [resultados, setResultados] = useState([])
  const [cargando, setCargando] = useState(false)
  const [cargandoInfo, setCargandoInfo] = useState(false)
  const [mostrarResultados, setMostrarResultados] = useState(false)

  const handleFileChange = async (e) => {
    const file = e.target.files[0]
    if (file) {
      setArchivo(file)
      setNombreArchivo(file.name)
      setCargandoInfo(true)
      setMostrarResultados(false)
      setResultados([])
      
      // Obtener información del PDF
      const formData = new FormData()
      formData.append('file', file)
      
      try {
        const response = await axios.post('/api/info-pdf', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        if (response.data.success) {
          setTotalPaginas(response.data.total_paginas)
          // Dejamos los campos vacíos en lugar de establecer valores por defecto
          setRangos({
            inicio_listado: '',
            fin_listado: '',
            inicio_cert: '',
            fin_cert: ''
          })
        }
      } catch (error) {
        console.error('Error al obtener información del PDF:', error)
        alert('Error al obtener información del PDF: ' + error.message)
      } finally {
        setCargandoInfo(false)
      }
    }
  }

  const handleProcesar = async () => {
    if (!archivo) {
      alert('Seleccione un archivo PDF primero')
      return
    }

    // Validar que todos los campos estén completos
    if (!rangos.inicio_listado || !rangos.fin_listado || !rangos.inicio_cert || !rangos.fin_cert) {
      alert('Por favor, complete todos los campos de rango de páginas')
      return
    }

    // Validar que los valores estén dentro del rango permitido
    const inicioListado = parseInt(rangos.inicio_listado)
    const finListado = parseInt(rangos.fin_listado)
    const inicioCert = parseInt(rangos.inicio_cert)
    const finCert = parseInt(rangos.fin_cert)

    if (inicioListado < 1 || finListado > totalPaginas || 
        inicioCert < 1 || finCert > totalPaginas ||
        inicioListado > finListado || 
        inicioCert > finCert) {
      alert(`Por favor, ingrese valores válidos entre 1 y ${totalPaginas}`)
      return
    }

    setCargando(true)
    setMostrarResultados(false)
    
    const formData = new FormData()
    formData.append('file', archivo)
    formData.append('inicio_listado', inicioListado)
    formData.append('fin_listado', finListado)
    formData.append('inicio_cert', inicioCert)
    formData.append('fin_cert', finCert)

    try {
      const response = await axios.post('/api/procesar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      if (response.data.success) {
        setResultados(response.data.resultados)
        setMostrarResultados(true)
      } else {
        alert('Error: ' + response.data.error)
      }
    } catch (error) {
      console.error('Error al procesar:', error)
      alert('Error al procesar el archivo: ' + error.message)
    } finally {
      setCargando(false)
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    
    // Permitir solo números y campo vacío
    if (value === '' || /^[0-9\b]+$/.test(value)) {
      setRangos(prev => ({
        ...prev,
        [name]: value
      }))
    }
  }

  const handleBlur = (e) => {
    const { name, value } = e.target
    
    // Si el campo está vacío, no hacer nada
    if (value === '') return
    
    let numericValue = parseInt(value)
    
    // Asegurar que el valor esté dentro del rango permitido
    if (numericValue < 1) {
      numericValue = 1
    } else if (numericValue > totalPaginas) {
      numericValue = totalPaginas
    }
    
    setRangos(prev => ({
      ...prev,
      [name]: numericValue.toString()
    }))
  }

  const handleDescargarResultados = () => {
    // Crear contenido CSV
    const headers = ['No.', 'Tipo L', 'Doc L', 'Nombre Listado', 'Tipo C', 'Doc C', 'Nombre Certificado', '%Doc', '%Nombre', 'Estado']
    const csvContent = [
      headers.join(','),
      ...resultados.map(row => row.join(','))
    ].join('\n')
    
    // Crear blob y descargar
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', `resultados_${nombreArchivo.replace('.pdf', '')}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="panel">
      <h2 className="panel-title">
        <span className="icon-single"></span>
        Procesamiento Individual
      </h2>
      
      <div className="form-group">
        <label className="form-label">
          <span className="label-icon">📄</span>
          Seleccionar archivo PDF
        </label>
        <div className="file-input-container">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="file-input"
            disabled={cargando}
            id="fileInput"
          />
          <label htmlFor="fileInput" className="file-input-label">
            <span className="file-input-icon">📂</span>
            Seleccionar archivo
          </label>
        </div>
        {nombreArchivo && (
          <div className="file-info">
            <span className="file-name">{nombreArchivo}</span>
            {totalPaginas > 0 && (
              <span className="page-count"> | {totalPaginas} página{totalPaginas !== 1 ? 's' : ''}</span>
            )}
            {cargandoInfo && <span className="loading-info"> | Obteniendo información...</span>}
          </div>
        )}
      </div>

      {archivo && totalPaginas > 0 && (
        <>
          <div className="panel-subtitle">Configurar rangos de páginas</div>
          
          <div className="ranges-container">
            <div className="range-group">
              <h3 className="range-title">
                <span className="range-icon">📋</span>
                Listado
              </h3>
              <div className="range-inputs">
                <div className="form-group">
                  <label>Página inicial:</label>
                  <input
                    type="text"
                    name="inicio_listado"
                    value={rangos.inicio_listado}
                    onChange={handleInputChange}
                    onBlur={handleBlur}
                    placeholder="1"
                    className="form-control"
                    disabled={cargando}
                  />
                </div>

                <div className="form-group">
                  <label>Página final:</label>
                  <input
                    type="text"
                    name="fin_listado"
                    value={rangos.fin_listado}
                    onChange={handleInputChange}
                    onBlur={handleBlur}
                    placeholder={totalPaginas.toString()}
                    className="form-control"
                    disabled={cargando}
                  />
                </div>
              </div>
            </div>

            <div className="range-group">
              <h3 className="range-title">
                <span className="range-icon">🏆</span>
                Certificados
              </h3>
              <div className="range-inputs">
                <div className="form-group">
                  <label>Página inicial:</label>
                  <input
                    type="text"
                    name="inicio_cert"
                    value={rangos.inicio_cert}
                    onChange={handleInputChange}
                    onBlur={handleBlur}
                    placeholder="1"
                    className="form-control"
                    disabled={cargando}
                  />
                </div>

                <div className="form-group">
                  <label>Página final:</label>
                  <input
                    type="text"
                    name="fin_cert"
                    value={rangos.fin_cert}
                    onChange={handleInputChange}
                    onBlur={handleBlur}
                    placeholder={totalPaginas.toString()}
                    className="form-control"
                    disabled={cargando}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="action-buttons">
            <button 
              onClick={handleProcesar} 
              disabled={cargando}
              className="btn btn-primary process-btn"
            >
              {cargando ? (
                <>
                  <span className="spinner"></span> 
                  Procesando documento...
                </>
              ) : (
                <>
                  <span className="btn-process-icon">⚡</span>
                  Iniciar procesamiento
                </>
              )}
            </button>
          </div>
        </>
      )}

      {resultados.length > 0 && (
        <div className={`results-container ${mostrarResultados ? 'visible' : ''}`}>
          <div className="results-header">
            <h3 className="panel-subtitle">
              <span className="results-icon">📊</span>
              Resultados del análisis ({resultados.length} registros)
            </h3>
          </div>
          
          <div className="table-container">
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
                {resultados.map((fila, index) => {
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
      )}
    </div>
  )
}

export default ModoNormal