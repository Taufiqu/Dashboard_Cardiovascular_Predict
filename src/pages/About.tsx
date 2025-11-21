import './About.css'

const About = () => {
  return (
    <div className="about-container">
      <div className="about-header">
        <h2>Tentang Dashboard</h2>
        <p>Informasi tentang model prediksi dan dataset cardiovascular disease</p>
      </div>

      <div className="about-content">
        <section className="about-section">
          <h3>📊 Tentang Model</h3>
          <div className="info-card">
            <p>
              Dashboard ini menggunakan <strong>Random Forest Classifier</strong> untuk memprediksi 
              risiko penyakit cardiovascular berdasarkan berbagai faktor kesehatan.
            </p>
            <ul>
              <li><strong>Algoritma:</strong> Random Forest (scikit-learn)</li>
              <li><strong>Preprocessing:</strong> StandardScaler untuk normalisasi data</li>
              <li><strong>Output:</strong> Binary classification (Risiko Tinggi / Risiko Rendah)</li>
            </ul>
          </div>
        </section>

        <section className="about-section">
          <h3>🔬 Fitur yang Digunakan</h3>
          <div className="info-card">
            <p>Model menggunakan <strong>19 fitur</strong> untuk prediksi (termasuk feature engineering):</p>
            <div className="features-grid">
              <div className="feature-item">
                <strong>1. Tinggi Badan (Height)</strong>
                <span>Dalam centimeter (cm)</span>
              </div>
              <div className="feature-item">
                <strong>2. Berat Badan (Weight)</strong>
                <span>Dalam kilogram (kg)</span>
              </div>
              <div className="feature-item">
                <strong>3. Systolic BP (ap_hi)</strong>
                <span>Tekanan darah sistolik (mmHg)</span>
              </div>
              <div className="feature-item">
                <strong>4. Diastolic BP (ap_lo)</strong>
                <span>Tekanan darah diastolik (mmHg)</span>
              </div>
              <div className="feature-item">
                <strong>5. Merokok (Smoke)</strong>
                <span>0 = Tidak, 1 = Ya</span>
              </div>
              <div className="feature-item">
                <strong>6. Alkohol (Alco)</strong>
                <span>0 = Tidak, 1 = Ya</span>
              </div>
              <div className="feature-item">
                <strong>7. Aktif Fisik (Active)</strong>
                <span>0 = Tidak, 1 = Ya</span>
              </div>
              <div className="feature-item">
                <strong>8. Usia (age_years)</strong>
                <span>Usia pasien dalam tahun</span>
              </div>
              <div className="feature-item">
                <strong>9. BMI</strong>
                <span>Body Mass Index (weight / (height/100)²)</span>
              </div>
              <div className="feature-item">
                <strong>10. Selisih Tekanan Darah (bp_diff)</strong>
                <span>Systolic - Diastolic BP</span>
              </div>
              <div className="feature-item">
                <strong>11. Gender Male (gender_male)</strong>
                <span>1 = Laki-laki, 0 = Perempuan</span>
              </div>
              <div className="feature-item">
                <strong>12. Kolesterol Level 2</strong>
                <span>1 jika kolesterol di atas normal</span>
              </div>
              <div className="feature-item">
                <strong>13. Kolesterol Level 3</strong>
                <span>1 jika kolesterol sangat tinggi</span>
              </div>
              <div className="feature-item">
                <strong>14. Glukosa Level 2</strong>
                <span>1 jika glukosa di atas normal</span>
              </div>
              <div className="feature-item">
                <strong>15. Glukosa Level 3</strong>
                <span>1 jika glukosa sangat tinggi</span>
              </div>
              <div className="feature-item">
                <strong>16. Usia Kategori 30-45</strong>
                <span>1 jika usia antara 30-45 tahun</span>
              </div>
              <div className="feature-item">
                <strong>17. Usia Kategori 45-60</strong>
                <span>1 jika usia antara 45-60 tahun</span>
              </div>
              <div className="feature-item">
                <strong>18. Usia Kategori 60+</strong>
                <span>1 jika usia 60 tahun ke atas</span>
              </div>
            </div>
            <p className="feature-note">
              <strong>Catatan:</strong> Model melakukan feature engineering otomatis dari input dasar 
              (usia, gender, tinggi, berat, tekanan darah, dll) menjadi 19 fitur yang digunakan untuk prediksi.
            </p>
          </div>
        </section>

        <section className="about-section">
          <h3>📈 Interpretasi Hasil</h3>
          <div className="info-card">
            <div className="interpretation-item">
              <div className="interpretation-badge risk-low">Risiko Rendah</div>
              <p>
                Hasil prediksi menunjukkan risiko rendah untuk terkena penyakit cardiovascular. 
                Tetap jaga pola hidup sehat dengan olahraga teratur, makan makanan bergizi, 
                dan rutin cek kesehatan.
              </p>
            </div>
            <div className="interpretation-item">
              <div className="interpretation-badge risk-high">Risiko Tinggi</div>
              <p>
                Hasil prediksi menunjukkan risiko tinggi untuk terkena penyakit cardiovascular. 
                Disarankan untuk berkonsultasi dengan dokter untuk pemeriksaan lebih lanjut 
                dan mendapatkan saran medis yang tepat.
              </p>
            </div>
          </div>
        </section>

        <section className="about-section">
          <h3>⚠️ Disclaimer</h3>
          <div className="info-card warning">
            <p>
              <strong>Penting:</strong> Dashboard ini hanya untuk tujuan edukasi dan penelitian. 
              Hasil prediksi tidak menggantikan diagnosis medis profesional. Selalu konsultasikan 
              dengan dokter atau tenaga kesehatan yang kompeten untuk diagnosis dan pengobatan 
              yang tepat.
            </p>
          </div>
        </section>

        <section className="about-section">
          <h3>🛠️ Teknologi</h3>
          <div className="info-card">
            <p>Dashboard ini dibangun menggunakan:</p>
            <ul>
              <li><strong>Frontend:</strong> React + TypeScript + Vite</li>
              <li><strong>Backend:</strong> Python Serverless Functions (Vercel)</li>
              <li><strong>ML Framework:</strong> scikit-learn</li>
              <li><strong>Deployment:</strong> Vercel</li>
              <li><strong>Visualization:</strong> Looker Studio</li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  )
}

export default About

