import { useEffect, useState } from 'react';

import { getHealth } from './services/api';

type ApiStatus = 'checking' | 'connected' | 'unavailable';

function App() {
  const [apiStatus, setApiStatus] = useState<ApiStatus>('checking');

  useEffect(() => {
    let isMounted = true;

    getHealth()
      .then(() => {
        if (isMounted) {
          setApiStatus('connected');
        }
      })
      .catch(() => {
        if (isMounted) {
          setApiStatus('unavailable');
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const statusLabel = {
    checking: 'Verificando',
    connected: 'Conectada',
    unavailable: 'No disponible',
  }[apiStatus];

  return (
    <main className="app-shell">
      <section className="intro">
        <p className="eyebrow">Taller de Proyectos 2</p>
        <h1>Paladar Inka AI</h1>
        <p className="description">
          Sistema de gestion de ventas, inventario y atencion al cliente.
        </p>
        <div className={`api-status api-status--${apiStatus}`}>
          <span className="status-dot" aria-hidden="true" />
          <span>Estado de API: {statusLabel}</span>
        </div>
      </section>
    </main>
  );
}

export default App;
