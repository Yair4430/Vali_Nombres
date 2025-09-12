import React, { useState } from 'react'
import ModoNormal from './Componentes/ModoNormal'
import ModoMasivo from './Componentes/ModoMasivo'
import './styles.css'

function App() {
  const [modo, setModo] = useState('normal')

  return (
    <div className="App">
      <header className="app-header">
        <h1>
          <span className="icon-document"></span>
          Extractor Listado + Certificados
        </h1>
        <p className="app-subtitle">Herramienta de procesamiento y comparación de documentos PDF</p>
      </header>
      
      <div className="mode-selector">
        <button 
          className={`mode-btn ${modo === 'normal' ? 'active' : ''}`}
          onClick={() => setModo('normal')}
        >
          <span className="btn-icon">📄</span>
          <span className="btn-text">Modo Normal</span>
          <span className="btn-description">Procesar un solo archivo</span>
        </button>
        <button 
          className={`mode-btn ${modo === 'masivo' ? 'active' : ''}`}
          onClick={() => setModo('masivo')}
        >
          <span className="btn-icon">📂</span>
          <span className="btn-text">Modo Masivo</span>
          <span className="btn-description">Procesar carpeta completa</span>
        </button>
      </div>

      <main className="main-content">
        {modo === 'normal' ? <ModoNormal /> : <ModoMasivo />}
      </main>

      <footer className="app-footer">
        <p>© {new Date().getFullYear()} Extractor PDF - Todos los derechos reservados</p>
      </footer>
    </div>
  )
}

export default App