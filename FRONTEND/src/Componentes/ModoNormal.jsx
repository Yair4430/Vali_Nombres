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

  const handleFileChange = async (e) => {
    const file = e.target.files[0]
    if (file) {
      setArchivo(file)
      setNombreArchivo(file.name)
      setCargandoInfo(true)
      
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

  return (
    <div className="panel">
      <h2 className="panel-title">Modo Normal</h2>
      
      <div className="form-group">
        <label>Archivo PDF:</label>
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="form-control"
          disabled={cargando}
        />
        {nombreArchivo && (
          <span className="form-hint">
            Archivo seleccionado: {nombreArchivo}
            {totalPaginas > 0 && ` | Total páginas: ${totalPaginas}`}
            {cargandoInfo && ' | Obteniendo información...'}
          </span>
        )}
      </div>

      {archivo && totalPaginas > 0 && (
        <>
          <div className="panel-subtitle">Configurar rangos de páginas</div>
          
          <div className="flex-row">
            <div className="form-group" style={{flex: 1}}>
              <label>Listado - Inicio:</label>
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

            <div className="form-group" style={{flex: 1}}>
              <label>Listado - Fin:</label>
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

          <div className="flex-row">
            <div className="form-group" style={{flex: 1}}>
              <label>Certificados - Inicio:</label>
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

            <div className="form-group" style={{flex: 1}}>
              <label>Certificados - Fin:</label>
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

          <div className="flex-row">
            <button 
              onClick={handleProcesar} 
              disabled={cargando}
              className="btn btn-primary"
            >
              {cargando ? (
                <>
                  <span className="spinner"></span> Procesando...
                </>
              ) : (
                <>
                  ▶ Procesar
                </>
              )}
            </button>

            <button className="btn btn-success" disabled={cargando}>
              🔍 Comparar
            </button>
          </div>
        </>
      )}

      {resultados.length > 0 && (
        <div className="table-container">
          <h3 className="panel-subtitle">Resultados ({resultados.length} registros)</h3>
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
              {resultados.map((fila, index) => (
                <tr key={index} className={fila[9].toLowerCase()}>
                  {fila.map((celda, cellIndex) => (
                    <td key={cellIndex}>{celda}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default ModoNormal