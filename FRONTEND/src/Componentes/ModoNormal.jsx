import React, { useState } from 'react'
import axios from 'axios'

const ModoNormal = () => {
  const [archivo, setArchivo] = useState(null)
  const [totalPaginas, setTotalPaginas] = useState(0)
  const [rangos, setRangos] = useState({
    inicio_listado: 1,
    fin_listado: 1,
    inicio_cert: 1,
    fin_cert: 1
  })
  const [resultados, setResultados] = useState([])
  const [cargando, setCargando] = useState(false)

  const handleFileChange = async (e) => {
    const file = e.target.files[0]
    if (file) {
      setArchivo(file)
      
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
          setRangos({
            inicio_listado: 1,
            fin_listado: response.data.total_paginas,
            inicio_cert: 1,
            fin_cert: response.data.total_paginas
          })
        }
      } catch (error) {
        console.error('Error al obtener información del PDF:', error)
      }
    }
  }

  const handleProcesar = async () => {
    if (!archivo) {
      alert('Seleccione un archivo PDF primero')
      return
    }

    setCargando(true)
    
    const formData = new FormData()
    formData.append('file', archivo)
    formData.append('inicio_listado', rangos.inicio_listado)
    formData.append('fin_listado', rangos.fin_listado)
    formData.append('inicio_cert', rangos.inicio_cert)
    formData.append('fin_cert', rangos.fin_cert)

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
      alert('Error al procesar el archivo')
    } finally {
      setCargando(false)
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setRangos(prev => ({
      ...prev,
      [name]: parseInt(value) || 1
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
        />
        {totalPaginas > 0 && (
          <small>Total páginas: {totalPaginas}</small>
        )}
      </div>

      {archivo && (
        <>
          <div className="form-group">
            <label>Listado - Inicio:</label>
            <input
              type="number"
              name="inicio_listado"
              value={rangos.inicio_listado}
              onChange={handleInputChange}
              min="1"
              max={totalPaginas}
              className="form-control"
            />
          </div>

          <div className="form-group">
            <label>Listado - Fin:</label>
            <input
              type="number"
              name="fin_listado"
              value={rangos.fin_listado}
              onChange={handleInputChange}
              min="1"
              max={totalPaginas}
              className="form-control"
            />
          </div>

          <div className="form-group">
            <label>Certificados - Inicio:</label>
            <input
              type="number"
              name="inicio_cert"
              value={rangos.inicio_cert}
              onChange={handleInputChange}
              min="1"
              max={totalPaginas}
              className="form-control"
            />
          </div>

          <div className="form-group">
            <label>Certificados - Fin:</label>
            <input
              type="number"
              name="fin_cert"
              value={rangos.fin_cert}
              onChange={handleInputChange}
              min="1"
              max={totalPaginas}
              className="form-control"
            />
          </div>

          <button 
            onClick={handleProcesar} 
            disabled={cargando}
            className="btn btn-primary"
          >
            {cargando ? 'Procesando...' : '▶ Procesar'}
          </button>

          <button className="btn btn-success">
            🔍 Comparar
          </button>
        </>
      )}

      {resultados.length > 0 && (
        <div className="table-container">
          <h3>Resultados ({resultados.length} registros)</h3>
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