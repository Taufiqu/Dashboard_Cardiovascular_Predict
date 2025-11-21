import './Analytics.css'

const Analytics = () => {
  // Ganti URL ini dengan embed URL dari Looker Studio kamu
  const lookerStudioUrl = "https://lookerstudio.google.com/embed/reporting/YOUR_REPORT_ID/page/YOUR_PAGE_ID"

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <h2>Cardiovascular Analytics Dashboard</h2>
        <p>Visualisasi data cardiovascular dari Looker Studio</p>
      </div>
      <div className="analytics-embed">
        <iframe
          src={lookerStudioUrl}
          width="100%"
          height="100%"
          frameBorder="0"
          className="analytics-iframe"
          allowFullScreen
          title="Cardiovascular Analytics"
        />
      </div>
    </div>
  )
}

export default Analytics

