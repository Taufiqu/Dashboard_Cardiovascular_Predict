import { useState, useEffect } from 'react'
import './Logging.css'

interface ApiStatus {
  status: 'checking' | 'online' | 'error'
  message: string
  details?: any
}

interface LogEntry {
  timestamp: string
  type: 'info' | 'success' | 'error' | 'warning'
  message: string
  data?: any
}

const Logging = () => {
  const [apiStatus, setApiStatus] = useState<ApiStatus>({ status: 'checking', message: 'Checking API status...' })
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [isAutoRefresh, setIsAutoRefresh] = useState(false)
  const [testPayload, setTestPayload] = useState({
    age: '50',
    gender: '2',
    height: '170',
    weight: '70',
    ap_hi: '120',
    ap_lo: '80',
    cholesterol: '1',
    gluc: '1',
    smoke: '0',
    alco: '0',
    active: '1'
  })

  const addLog = (type: LogEntry['type'], message: string, data?: any) => {
    const entry: LogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      type,
      message,
      data
    }
    setLogs(prev => [entry, ...prev].slice(0, 100)) // Keep last 100 logs
  }

  const checkApiStatus = async () => {
    addLog('info', 'Checking API status...')
    setApiStatus({ status: 'checking', message: 'Checking...' })

    try {
      const response = await fetch('/api/predict', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setApiStatus({
          status: 'online',
          message: 'API is online',
          details: data
        })
        addLog('success', 'API is online', data)
      } else {
        const errorText = await response.text()
        setApiStatus({
          status: 'error',
          message: `API returned error: ${response.status}`,
          details: errorText
        })
        addLog('error', `API error: ${response.status}`, errorText)
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error'
      setApiStatus({
        status: 'error',
        message: `Failed to connect: ${errorMsg}`,
        details: error
      })
      addLog('error', 'Failed to connect to API', errorMsg)
    }
  }

  const testPredict = async () => {
    addLog('info', 'Testing predict endpoint...')
    
    try {
      const payload = {
        age: parseInt(testPayload.age),
        gender: parseInt(testPayload.gender),
        height: parseFloat(testPayload.height),
        weight: parseFloat(testPayload.weight),
        ap_hi: parseInt(testPayload.ap_hi),
        ap_lo: parseInt(testPayload.ap_lo),
        cholesterol: parseInt(testPayload.cholesterol),
        gluc: parseInt(testPayload.gluc),
        smoke: parseInt(testPayload.smoke),
        alco: parseInt(testPayload.alco),
        active: parseInt(testPayload.active)
      }

      const startTime = Date.now()
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      const endTime = Date.now()
      const duration = endTime - startTime

      if (response.ok) {
        const data = await response.json()
        addLog('success', `Predict successful (${duration}ms)`, data)
      } else {
        const errorText = await response.text()
        addLog('error', `Predict failed: ${response.status} (${duration}ms)`, errorText)
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error'
      addLog('error', 'Predict request failed', errorMsg)
    }
  }

  useEffect(() => {
    checkApiStatus()
  }, [])

  useEffect(() => {
    if (isAutoRefresh) {
      const interval = setInterval(() => {
        checkApiStatus()
      }, 5000) // Check every 5 seconds
      return () => clearInterval(interval)
    }
  }, [isAutoRefresh])

  const clearLogs = () => {
    setLogs([])
    addLog('info', 'Logs cleared')
  }

  return (
    <div className="logging-container">
      <div className="logging-header">
        <h2>🔍 API Logging & Debugging</h2>
        <p>Monitor API status, test endpoints, and view logs</p>
      </div>

      <div className="logging-content">
        {/* API Status Card */}
        <div className="status-card">
          <h3>API Status</h3>
          <div className={`status-indicator ${apiStatus.status}`}>
            <span className="status-dot"></span>
            <span>{apiStatus.message}</span>
          </div>
          {apiStatus.details && (
            <div className="status-details">
              <pre>{JSON.stringify(apiStatus.details, null, 2)}</pre>
            </div>
          )}
          <div className="status-actions">
            <button onClick={checkApiStatus} className="btn-primary">
              Refresh Status
            </button>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={isAutoRefresh}
                onChange={(e) => setIsAutoRefresh(e.target.checked)}
              />
              <span>Auto Refresh (5s)</span>
            </label>
          </div>
        </div>

        {/* Test Predict Card */}
        <div className="test-card">
          <h3>Test Predict Endpoint</h3>
          <div className="test-form">
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="test-age">Age</label>
                <input
                  id="test-age"
                  type="number"
                  value={testPayload.age}
                  onChange={(e) => setTestPayload({ ...testPayload, age: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="test-gender">Gender (1=F, 2=M)</label>
                <input
                  id="test-gender"
                  type="number"
                  value={testPayload.gender}
                  onChange={(e) => setTestPayload({ ...testPayload, gender: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="test-height">Height (cm)</label>
                <input
                  id="test-height"
                  type="number"
                  value={testPayload.height}
                  onChange={(e) => setTestPayload({ ...testPayload, height: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="test-weight">Weight (kg)</label>
                <input
                  id="test-weight"
                  type="number"
                  value={testPayload.weight}
                  onChange={(e) => setTestPayload({ ...testPayload, weight: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="test-ap-hi">Systolic BP</label>
                <input
                  id="test-ap-hi"
                  type="number"
                  value={testPayload.ap_hi}
                  onChange={(e) => setTestPayload({ ...testPayload, ap_hi: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="test-ap-lo">Diastolic BP</label>
                <input
                  id="test-ap-lo"
                  type="number"
                  value={testPayload.ap_lo}
                  onChange={(e) => setTestPayload({ ...testPayload, ap_lo: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="test-cholesterol">Cholesterol (1-3)</label>
                <input
                  id="test-cholesterol"
                  type="number"
                  value={testPayload.cholesterol}
                  onChange={(e) => setTestPayload({ ...testPayload, cholesterol: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="test-gluc">Glucose (1-3)</label>
                <input
                  id="test-gluc"
                  type="number"
                  value={testPayload.gluc}
                  onChange={(e) => setTestPayload({ ...testPayload, gluc: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="test-smoke">Smoke (0/1)</label>
                <input
                  id="test-smoke"
                  type="number"
                  value={testPayload.smoke}
                  onChange={(e) => setTestPayload({ ...testPayload, smoke: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="test-alco">Alcohol (0/1)</label>
                <input
                  id="test-alco"
                  type="number"
                  value={testPayload.alco}
                  onChange={(e) => setTestPayload({ ...testPayload, alco: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="test-active">Active (0/1)</label>
                <input
                  id="test-active"
                  type="number"
                  value={testPayload.active}
                  onChange={(e) => setTestPayload({ ...testPayload, active: e.target.value })}
                />
              </div>
            </div>
            <button onClick={testPredict} className="btn-primary">
              Test Predict
            </button>
          </div>
        </div>

        {/* Logs Card */}
        <div className="logs-card">
          <div className="logs-header">
            <h3>Logs</h3>
            <button onClick={clearLogs} className="btn-secondary">
              Clear Logs
            </button>
          </div>
          <div className="logs-container">
            {logs.length === 0 ? (
              <div className="logs-empty">No logs yet. Perform an action to see logs.</div>
            ) : (
              logs.map((log, index) => (
                <div key={index} className={`log-entry log-${log.type}`}>
                  <span className="log-time">{log.timestamp}</span>
                  <span className="log-message">{log.message}</span>
                  {log.data && (
                    <details className="log-details">
                      <summary>Details</summary>
                      <pre>{JSON.stringify(log.data, null, 2)}</pre>
                    </details>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Logging

