import { useState } from 'react'
import './Predict.css'

interface PredictionResult {
  prediction: number
  probability?: number
}

interface FormErrors {
  [key: string]: string
}

const Predict = () => {
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    height: '',
    weight: '',
    ap_hi: '',
    ap_lo: '',
    cholesterol: '',
    gluc: '',
    smoke: '',
    alco: '',
    active: ''
  })

  const [loading, setLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState('')
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<FormErrors>({})

  // Validasi individual field
  const validateField = (name: string, value: string): string => {
    switch (name) {
      case 'age':
        const age = parseInt(value)
        if (isNaN(age) || age < 1 || age > 120) {
          return 'Usia harus antara 1-120 tahun'
        }
        break
      case 'height':
        const height = parseFloat(value)
        if (isNaN(height) || height < 100 || height > 250) {
          return 'Tinggi badan harus antara 100-250 cm'
        }
        break
      case 'weight':
        const weight = parseFloat(value)
        if (isNaN(weight) || weight < 30 || weight > 200) {
          return 'Berat badan harus antara 30-200 kg'
        }
        break
      case 'ap_hi':
        const apHi = parseInt(value)
        if (isNaN(apHi) || apHi < 80 || apHi > 200) {
          return 'Systolic BP harus antara 80-200 mmHg'
        }
        break
      case 'ap_lo':
        const apLo = parseInt(value)
        if (isNaN(apLo) || apLo < 40 || apLo > 150) {
          return 'Diastolic BP harus antara 40-150 mmHg'
        }
        // Validasi logis: diastolic harus lebih kecil dari systolic
        if (formData.ap_hi && parseInt(formData.ap_hi) <= apLo) {
          return 'Diastolic BP harus lebih kecil dari Systolic BP'
        }
        break
      case 'gender':
      case 'cholesterol':
      case 'gluc':
      case 'smoke':
      case 'alco':
      case 'active':
        if (!value) {
          return 'Field ini wajib diisi'
        }
        break
    }
    return ''
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }))

    // Validasi real-time
    const error = validateField(name, value)
    setFieldErrors((prev) => ({
      ...prev,
      [name]: error
    }))

    // Clear error umum jika ada
    if (error) {
      setError(null)
    }
  }

  const validateForm = (): boolean => {
    const errors: FormErrors = {}
    let isValid = true

    Object.keys(formData).forEach(key => {
      const error = validateField(key, formData[key as keyof typeof formData])
      if (error) {
        errors[key] = error
        isValid = false
      }
    })

    // Validasi tambahan: ap_lo harus < ap_hi
    if (formData.ap_hi && formData.ap_lo) {
      const apHi = parseInt(formData.ap_hi)
      const apLo = parseInt(formData.ap_lo)
      if (apLo >= apHi) {
        errors.ap_lo = 'Diastolic BP harus lebih kecil dari Systolic BP'
        isValid = false
      }
    }

    setFieldErrors(errors)
    return isValid
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setResult(null)

    // Validasi form sebelum submit
    if (!validateForm()) {
      setError('Mohon perbaiki error pada form sebelum melanjutkan')
      return
    }

    setLoading(true)
    setLoadingStep('Mengirim data...')

    try {
      // Konversi data ke format yang sesuai dengan model
      const payload = {
        age: parseInt(formData.age),
        gender: parseInt(formData.gender),
        height: parseFloat(formData.height),
        weight: parseFloat(formData.weight),
        ap_hi: parseInt(formData.ap_hi),
        ap_lo: parseInt(formData.ap_lo),
        cholesterol: parseInt(formData.cholesterol),
        gluc: parseInt(formData.gluc),
        smoke: parseInt(formData.smoke),
        alco: parseInt(formData.alco),
        active: parseInt(formData.active)
      }

      setLoadingStep('Memproses prediksi...')
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      setLoadingStep('Menganalisis hasil...')

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || 'Prediksi gagal. Silakan coba lagi.')
      }

      const data = await response.json()
      setResult(data)
      setLoadingStep('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Terjadi kesalahan saat memproses prediksi')
      setLoadingStep('')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="predict-container">
      <div className="predict-header">
        <h2>Cardiovascular Disease Prediction</h2>
        <p>Masukkan data untuk memprediksi risiko cardiovascular disease</p>
      </div>

      <div className="predict-content">
        <form className="predict-form" onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="age">Usia (tahun)</label>
              <input
                type="number"
                id="age"
                name="age"
                value={formData.age}
                onChange={handleChange}
                required
                min="1"
                max="120"
                className={fieldErrors.age ? 'error' : ''}
              />
              {fieldErrors.age && <span className="error-message">{fieldErrors.age}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="gender">Jenis Kelamin</label>
              <select
                id="gender"
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                required
                className={fieldErrors.gender ? 'error' : ''}
              >
                <option value="">Pilih...</option>
                <option value="1">Perempuan</option>
                <option value="2">Laki-laki</option>
              </select>
              {fieldErrors.gender && <span className="error-message">{fieldErrors.gender}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="height">Tinggi Badan (cm)</label>
              <input
                type="number"
                id="height"
                name="height"
                value={formData.height}
                onChange={handleChange}
                required
                min="100"
                max="250"
                step="0.1"
                className={fieldErrors.height ? 'error' : ''}
              />
              {fieldErrors.height && <span className="error-message">{fieldErrors.height}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="weight">Berat Badan (kg)</label>
              <input
                type="number"
                id="weight"
                name="weight"
                value={formData.weight}
                onChange={handleChange}
                required
                min="30"
                max="200"
                step="0.1"
                className={fieldErrors.weight ? 'error' : ''}
              />
              {fieldErrors.weight && <span className="error-message">{fieldErrors.weight}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="ap_hi">Systolic BP (mmHg)</label>
              <input
                type="number"
                id="ap_hi"
                name="ap_hi"
                value={formData.ap_hi}
                onChange={handleChange}
                required
                min="80"
                max="200"
                className={fieldErrors.ap_hi ? 'error' : ''}
              />
              {fieldErrors.ap_hi && <span className="error-message">{fieldErrors.ap_hi}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="ap_lo">Diastolic BP (mmHg)</label>
              <input
                type="number"
                id="ap_lo"
                name="ap_lo"
                value={formData.ap_lo}
                onChange={handleChange}
                required
                min="40"
                max="150"
                className={fieldErrors.ap_lo ? 'error' : ''}
              />
              {fieldErrors.ap_lo && <span className="error-message">{fieldErrors.ap_lo}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="cholesterol">Kolesterol</label>
              <select
                id="cholesterol"
                name="cholesterol"
                value={formData.cholesterol}
                onChange={handleChange}
                required
                className={fieldErrors.cholesterol ? 'error' : ''}
              >
                <option value="">Pilih...</option>
                <option value="1">Normal</option>
                <option value="2">Di atas normal</option>
                <option value="3">Sangat tinggi</option>
              </select>
              {fieldErrors.cholesterol && <span className="error-message">{fieldErrors.cholesterol}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="gluc">Glukosa</label>
              <select
                id="gluc"
                name="gluc"
                value={formData.gluc}
                onChange={handleChange}
                required
                className={fieldErrors.gluc ? 'error' : ''}
              >
                <option value="">Pilih...</option>
                <option value="1">Normal</option>
                <option value="2">Di atas normal</option>
                <option value="3">Sangat tinggi</option>
              </select>
              {fieldErrors.gluc && <span className="error-message">{fieldErrors.gluc}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="smoke">Merokok</label>
              <select
                id="smoke"
                name="smoke"
                value={formData.smoke}
                onChange={handleChange}
                required
                className={fieldErrors.smoke ? 'error' : ''}
              >
                <option value="">Pilih...</option>
                <option value="0">Tidak</option>
                <option value="1">Ya</option>
              </select>
              {fieldErrors.smoke && <span className="error-message">{fieldErrors.smoke}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="alco">Alkohol</label>
              <select
                id="alco"
                name="alco"
                value={formData.alco}
                onChange={handleChange}
                required
                className={fieldErrors.alco ? 'error' : ''}
              >
                <option value="">Pilih...</option>
                <option value="0">Tidak</option>
                <option value="1">Ya</option>
              </select>
              {fieldErrors.alco && <span className="error-message">{fieldErrors.alco}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="active">Aktif Fisik</label>
              <select
                id="active"
                name="active"
                value={formData.active}
                onChange={handleChange}
                required
                className={fieldErrors.active ? 'error' : ''}
              >
                <option value="">Pilih...</option>
                <option value="0">Tidak</option>
                <option value="1">Ya</option>
              </select>
              {fieldErrors.active && <span className="error-message">{fieldErrors.active}</span>}
            </div>
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? (
              <span className="loading-content">
                <span className="spinner"></span>
                {loadingStep || 'Memproses...'}
              </span>
            ) : (
              'Prediksi'
            )}
          </button>
        </form>

        {error && (
          <div className="result-container error">
            <h3>Error</h3>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className="result-container success">
            <h3>Hasil Prediksi</h3>
            <div className="result-content">
              <div className="result-value">
                {result.prediction === 1 ? (
                  <span className="risk-high">Risiko Tinggi</span>
                ) : (
                  <span className="risk-low">Risiko Rendah</span>
                )}
              </div>
              {result.probability !== undefined && (
                <p className="result-probability">
                  Probabilitas: {(result.probability * 100).toFixed(2)}%
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Predict

