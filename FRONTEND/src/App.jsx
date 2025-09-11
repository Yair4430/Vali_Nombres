import React, { useState } from 'react'
import ModoNormal from './Componentes/ModoNormal'
import ModoMasivo from './Componentes/ModoMasivo'
import './styles.css'

function App() {
  const [modo, setModo] = useState('normal')

  return (
    <div className="App">
      <h1>Extractor Listado + Certificados</h1>
      
      <div className="mode-selector">
        <button 
          className={`mode-btn ${modo === 'normal' ? 'active' : ''}`}
          onClick={() => setModo('normal')}
        >
          📄 Modo Normal
        </button>
        <button 
          className={`mode-btn ${modo === 'masivo' ? 'active' : ''}`}
          onClick={() => setModo('masivo')}
        >
          📂 Modo Masivo
        </button>
      </div>

      {modo === 'normal' ? <ModoNormal /> : <ModoMasivo />}
    </div>
  )
}

export default App